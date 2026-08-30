/*
 * SENS-Able KALIBRASI TEST v1.0
 * 
 * Firmware untuk TEST PERBANDINGAN: Prediksi AI vs Glukometer Nyata
 * 
 * CARA PAKAI:
 * 1. Upload ke ESP32
 * 2. Buka Serial Monitor (115200 baud)
 * 3. Letakkan jari di MAX30102 → tunggu 10 detik
 * 4. Sistem prediksi glukosa dari sensor PPG
 * 5. Ukur glukosa dengan glukometer NYATA
 * 6. Ketik nilai glukometer di Serial Monitor
 * 7. Sistem hitung error otomatis
 * 8. Ulangi untuk 3 pengukuran (hemat chip!)
 * 
 * Output di Serial:
 *   PREDIKSI | GLUKOMETER | ERROR | STATUS
 * 
 * Output di OLED:
 *   Prediksi AI | Status | Suhu
 * 
 * Hardware:
 *   ESP32 + MAX30102 + MLX90614 + OLED + Buzzer
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30100.h>
#include <math.h>

// Include the embedded ML model
#include "model_glucose_inference.h"

// ===================== PIN DEFINITIONS =====================
#define OLED_SDA    21
#define OLED_SCL    22
#define MAX_SDA     18
#define MAX_SCL     19
#define MLX_ADDR    0x5A
#define SPEAKER_PIN 23

// ===================== MEASUREMENT SETTINGS =====================
#define RECORD_SEC    10
#define MAX_SAMPLES   1200
#define MIN_SAMPLES   100

// ===================== OBJECTS =====================
TwoWire BusOLED   = TwoWire(0);
TwoWire BusSensor = TwoWire(1);
Adafruit_SSD1306 display(128, 64, &BusOLED, -1);
MAX30100 sensor;

// ===================== STATE =====================
enum State { IDLE, RECORDING, PREDICTING, SHOWING_RESULT, WAITING_REFERENCE };
State state = IDLE;

// ===================== BUFFERS =====================
float irBuf[MAX_SAMPLES];
float redBuf[MAX_SAMPLES];
int sampleCount = 0;
unsigned long recStart = 0;

// ===================== SENSOR DATA =====================
struct SensorData {
    float bodyTemp;
    float ambientTemp;
} sensorData;

// ===================== FEATURES =====================
struct Features {
    float irMean, irMin, irMax, irStd, irRMS;
    float redMean, redMin, redMax, redStd, redRMS;
    float ratioAC, ratioDC;
    float age;
    float weight;
    float height;
    float bmi;
    float lastMeal;
    int samples;
} features;

// ===================== PREDICTION =====================
float predictedGlucose = 0;
int glucoseStatus = 0;

// ===================== CALIBRATION LOG =====================
struct CalibrationEntry {
    float predicted;
    float reference;
    float error;
    float bodyTemp;
    unsigned long timestamp;
};

CalibrationEntry log[10]; // max 10 entries
int logCount = 0;
int testNumber = 0;
float referenceInput = 0;
String inputBuffer = "";

// ===================== MLX90614 READ =====================
float readMLXObject() {
    BusOLED.beginTransmission(MLX_ADDR);
    BusOLED.write(0x07);
    BusOLED.endTransmission(false);
    BusOLED.requestFrom(MLX_ADDR, 3);
    if (BusOLED.available() >= 3) {
        uint8_t lo = BusOLED.read();
        uint8_t hi = BusOLED.read();
        BusOLED.read();
        uint16_t raw = ((uint16_t)hi << 8) | lo;
        return raw * 0.02 - 273.15;
    }
    return 0;
}

float readMLXAmbient() {
    BusOLED.beginTransmission(MLX_ADDR);
    BusOLED.write(0x06);
    BusOLED.endTransmission(false);
    BusOLED.requestFrom(MLX_ADDR, 3);
    if (BusOLED.available() >= 3) {
        uint8_t lo = BusOLED.read();
        uint8_t hi = BusOLED.read();
        BusOLED.read();
        uint16_t raw = ((uint16_t)hi << 8) | lo;
        return raw * 0.02 - 273.15;
    }
    return 0;
}

// ===================== OLED DISPLAY =====================
void oledShow(String line1, String line2 = "", String line3 = "", String line4 = "") {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);  display.println(line1);
    display.setCursor(0, 16); display.println(line2);
    display.setCursor(0, 32); display.println(line3);
    display.setCursor(0, 48); display.println(line4);
    display.display();
}

// ===================== AUDIO =====================
void playBeep(int count, int durationMs = 100, int pauseMs = 50) {
    for (int i = 0; i < count; i++) {
        digitalWrite(SPEAKER_PIN, HIGH);
        delay(durationMs);
        digitalWrite(SPEAKER_PIN, LOW);
        if (i < count - 1) delay(pauseMs);
    }
}

// ===================== COMPUTE FEATURES =====================
void computeFeatures() {
    if (sampleCount < MIN_SAMPLES) {
        Serial.println("ERROR: Not enough samples!");
        return;
    }
    
    float irSum = 0, irSumSq = 0;
    features.irMin = irBuf[0];
    features.irMax = irBuf[0];
    
    for (int i = 0; i < sampleCount; i++) {
        irSum += irBuf[i];
        irSumSq += irBuf[i] * irBuf[i];
        if (irBuf[i] < features.irMin) features.irMin = irBuf[i];
        if (irBuf[i] > features.irMax) features.irMax = irBuf[i];
    }
    
    features.irMean = irSum / sampleCount;
    features.irStd = sqrt((irSumSq / sampleCount) - (features.irMean * features.irMean));
    features.irRMS = sqrt(irSumSq / sampleCount);
    
    float redSum = 0, redSumSq = 0;
    features.redMin = redBuf[0];
    features.redMax = redBuf[0];
    
    for (int i = 0; i < sampleCount; i++) {
        redSum += redBuf[i];
        redSumSq += redBuf[i] * redBuf[i];
        if (redBuf[i] < features.redMin) features.redMin = redBuf[i];
        if (redBuf[i] > features.redMax) features.redMax = redBuf[i];
    }
    
    features.redMean = redSum / sampleCount;
    features.redStd = sqrt((redSumSq / sampleCount) - (features.redMean * features.redMean));
    features.redRMS = sqrt(redSumSq / sampleCount);
    
    features.ratioAC = (features.irMax - features.irMin) / features.irMean;
    features.ratioDC = (features.redMax - features.redMin) / features.redMean;
    features.samples = sampleCount;
}

// ===================== RUN INFERENCE =====================
void runInference() {
    sensorData.bodyTemp = readMLXObject();
    sensorData.ambientTemp = readMLXAmbient();
    
    float inputFeatures[GLUCOSE_MODEL_FEATURES] = {
        features.age,
        features.weight,
        features.height,
        features.bmi,
        features.lastMeal,
        sensorData.bodyTemp,
        sensorData.ambientTemp,
        70.0,  // HR placeholder
        98.0,  // SpO2 placeholder
        features.irMean,
        features.irMin,
        features.irMax,
        features.irStd,
        features.irRMS,
        features.redMean,
        features.redMin,
        features.redMax,
        features.redStd,
        features.redRMS,
        features.ratioAC,
        features.ratioDC,
        (float)features.samples
    };
    
    predictedGlucose = predict_glucose(inputFeatures);
    glucoseStatus = interpret_glucose(predictedGlucose);
}

// ===================== SHOW RESULT ON OLED =====================
void showResult() {
    String line1 = "=== PREDIKSI AI ===";
    String line2 = String(predictedGlucose, 1) + " mg/dL";
    String line3 = glucose_status_text(glucoseStatus);
    String line4 = "Suhu: " + String(sensorData.bodyTemp, 1) + "C";
    
    oledShow(line1, line2, line3, line4);
    
    // Audio feedback
    switch (glucoseStatus) {
        case 0:  playBeep(1, 100); break;  // Normal
        case 1:  playBeep(2, 150, 100); break;  // Pre-DM
        case 2:  playBeep(3, 300, 200); break;  // DM
        case 3:  playBeep(5, 100, 50); break;  // Low
    }
}

// ===================== SERIAL OUTPUT =====================
void printHeader() {
    Serial.println();
    Serial.println("╔══════════════════════════════════════════════════╗");
    Serial.println("║     SENS-Able KALIBRASI TEST - Data Logging     ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.println("║ Test | AI (mg/dL) | Glukometer | Error | Status  ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
}

void printTestResult(int testNum, float predicted, float reference, float error, String status) {
    Serial.printf("║  %d   |   %6.1f   |   %6.1f   | %5.1f | %-8s ║\n",
                  testNum, predicted, reference, error, status.c_str());
}

void printSummary() {
    if (logCount == 0) return;
    
    float totalError = 0;
    float maxError = 0;
    float minError = 999;
    int accurateCount = 0; // error < 15
    
    for (int i = 0; i < logCount; i++) {
        float err = abs(log[i].error);
        totalError += err;
        if (err > maxError) maxError = err;
        if (err < minError) minError = err;
        if (err < 15) accurateCount++;
    }
    
    float avgError = totalError / logCount;
    float accuracy = (float)accurateCount / logCount * 100;
    
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.println("║                  RINGKASAN                       ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.printf("║ Jumlah test   : %d                               ║\n", logCount);
    Serial.printf("║ Rata-rata error: %.1f mg/dL                      ║\n", avgError);
    Serial.printf("║ Error terkecil: %.1f mg/dL                       ║\n", minError);
    Serial.printf("║ Error terbesar: %.1f mg/dL                       ║\n", maxError);
    Serial.printf("║ Akurasi (<15) : %.0f%%                            ║\n", accuracy);
    Serial.println("╚══════════════════════════════════════════════════╝");
    
    // Also print in CSV format for easy copy
    Serial.println();
    Serial.println("=== CSV FORMAT (copy paste ke Excel) ===");
    Serial.println("Test,AI_Prediction,Glukometer_Reference,Error,Status,Body_Temp");
    for (int i = 0; i < logCount; i++) {
        String status = glucose_status_text(interpret_glucose(log[i].predicted));
        Serial.printf("%d,%.1f,%.1f,%.1f,%s,%.1f\n",
                      i + 1, log[i].predicted, log[i].reference, 
                      log[i].error, status.c_str(), log[i].bodyTemp);
    }
}

// ===================== SETUP =====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    // Initialize pins
    pinMode(SPEAKER_PIN, OUTPUT);
    digitalWrite(SPEAKER_PIN, LOW);
    
    // Initialize OLED on Bus 0
    BusOLED.begin(OLED_SDA, OLED_SCL);
    BusOLED.setClock(100000);
    
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("OLED failed!");
        while (1);
    }
    
    oledShow("SENS-Able KALIBRASI", "Test Prediksi AI", "vs Glukometer", "Booting...");
    
    // Initialize MAX30100 on Bus 1
    BusSensor.begin(MAX_SDA, MAX_SCL);
    BusSensor.setClock(400000);
    Wire = BusSensor;
    sensor.begin(pw1600, i50, sr100);
    Wire = BusOLED;
    
    // Set default user data
    features.age = 25.0;
    features.weight = 60.0;
    features.height = 165.0;
    features.bmi = features.weight / ((features.height / 100.0) * (features.height / 100.0));
    features.lastMeal = 2.0;
    
    // Welcome message
    Serial.println();
    Serial.println("╔══════════════════════════════════════════════════╗");
    Serial.println("║   SENS-Able KALIBRASI TEST v1.0                  ║");
    Serial.println("║   Perbandingan Prediksi AI vs Glukometer         ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.println("║ CARA PAKAI:                                      ║");
    Serial.println("║ 1. Letakkan jari di MAX30102 (10 detik)          ║");
    Serial.println("║ 2. Catat prediksi AI dari OLED                   ║");
    Serial.println("║ 3. Ukur glukosa dengan glukometer                ║");
    Serial.println("║ 4. Ketik nilai glukometer di Serial (angka saja) ║");
    Serial.println("║ 5. Tekan ENTER                                   ║");
    Serial.println("║ 6. Ulangi untuk test berikutnya                  ║");
    Serial.println("║ 7. Ketik 'hasil' untuk lihat ringkasan           ║");
    Serial.println("╚══════════════════════════════════════════════════╝");
    Serial.println();
    
    oledShow("SENS-Able KALIBRASI", "Tekan ENTER di", "Serial Monitor", "untuk mulai test!");
    
    // Ready beep
    playBeep(2, 100, 100);
    
    state = IDLE;
}

// ===================== LOOP =====================
void loop() {
    // Check for serial input
    while (Serial.available()) {
        char c = Serial.read();
        
        if (c == '\n' || c == '\r') {
            if (inputBuffer.length() > 0) {
                if (inputBuffer.equalsIgnoreCase("hasil") || inputBuffer.equalsIgnoreCase("summary")) {
                    printSummary();
                } else if (inputBuffer.equalsIgnoreCase("mulai") || inputBuffer.equalsIgnoreCase("start")) {
                    // Start new measurement
                    state = RECORDING;
                    sampleCount = 0;
                    recStart = millis();
                    oledShow("Mulaiukur...", "Letakkan jari", "di MAX30102", "Tunggu 10 detik");
                    Serial.println("\n>>> Mulai pengukuran... Letakkan jari di sensor!");
                } else {
                    // Try to parse as glucose reference value
                    float ref = inputBuffer.toFloat();
                    if (ref > 0 && ref < 500) {
                        referenceInput = ref;
                        
                        // Calculate and log
                        float error = predictedGlucose - referenceInput;
                        String status = glucose_status_text(glucoseStatus);
                        
                        log[logCount].predicted = predictedGlucose;
                        log[logCount].reference = referenceInput;
                        log[logCount].error = error;
                        log[logCount].bodyTemp = sensorData.bodyTemp;
                        log[logCount].timestamp = millis();
                        logCount++;
                        testNumber++;
                        
                        // Print result
                        printTestResult(testNumber, predictedGlucose, referenceInput, error, status);
                        
                        // Show on OLED
                        String line1 = "Test #" + String(testNumber) + " SELESAI";
                        String line2 = "AI: " + String(predictedGlucose, 1) + " mg/dL";
                        String line3 = "Real: " + String(referenceInput, 1) + " mg/dL";
                        String line4 = "Error: " + String(abs(error), 1) + " mg/dL";
                        oledShow(line1, line2, line3, line4);
                        
                        // Audio feedback based on error
                        if (abs(error) < 10) {
                            playBeep(2, 100, 50);  // Good accuracy
                        } else if (abs(error) < 20) {
                            playBeep(1, 200);  // Moderate
                        } else {
                            playBeep(3, 100, 100);  // High error
                        }
                        
                        Serial.println(">>> Tersimpan! Ketik 'start' untuk test berikutnya.");
                        Serial.println(">>> Ketik 'hasil' untuk lihat ringkasan.");
                        
                        state = IDLE;
                    } else {
                        Serial.println(">>> Input tidak valid! Ketik angka glukometer (contoh: 105)");
                    }
                }
            }
            inputBuffer = "";
        } else if (c >= '0' && c <= '9' || c == '.' || c == '-') {
            inputBuffer += c;
        }
    }
    
    // Recording state
    if (state == RECORDING) {
        // Switch to sensor bus
        Wire = BusSensor;
        
        if (sampleCount < MAX_SAMPLES) {
            int avail = sensor.getNumSamp();
            if (avail > 0) {
                sensor.readSensor();
                irBuf[sampleCount] = (float)sensor.IR;
                redBuf[sampleCount] = (float)sensor.RED;
                sampleCount++;
            }
        }
        
        // Switch to OLED bus
        Wire = BusOLED;
        
        // Update progress
        static unsigned long lastUpdate = 0;
        if (millis() - lastUpdate > 500) {
            int elapsed = (millis() - recStart) / 1000;
            int progress = (elapsed * 100) / RECORD_SEC;
            
            String line1 = "Merekam... " + String(elapsed) + "/" + String(RECORD_SEC) + " dtk";
            String line2 = "Sampel: " + String(sampleCount);
            String line3 = "Progress: " + String(progress) + "%";
            String line4 = "";
            
            // Draw progress bar
            oledShow(line1, line2, line3, line4);
            lastUpdate = millis();
        }
        
        // Check if recording complete
        if ((millis() - recStart) >= (RECORD_SEC * 1000)) {
            state = PREDICTING;
            oledShow("Memproses...", "Menghitung fitur", "Menjalankan AI", "");
            
            computeFeatures();
            runInference();
            showResult();
            
            // Prompt for glucometer reading
            Serial.println();
            Serial.println("╔══════════════════════════════════════════════════╗");
            Serial.printf("║ Prediksi AI: %.1f mg/dL (%s)              \n", 
                         predictedGlucose, glucose_status_text(glucoseStatus).c_str());
            Serial.println("╠══════════════════════════════════════════════════╣");
            Serial.println("║ Sekarang ukur dengan glukometer!                 ║");
            Serial.println("║ Ketik hasil glukometer (angka) lalu tekan ENTER  ║");
            Serial.println("╚══════════════════════════════════════════════════╝");
            Serial.print(">>> Glukometer: ");
            
            // Show on OLED
            String line1 = "PREDIKSI AI:";
            String line2 = String(predictedGlucose, 1) + " mg/dL";
            String line3 = glucose_status_text(glucoseStatus);
            String line4 = "Ketik glukometer!";
            oledShow(line1, line2, line3, line4);
            
            state = WAITING_REFERENCE;
        }
        
        delay(10);
    }
    
    delay(10);
}
