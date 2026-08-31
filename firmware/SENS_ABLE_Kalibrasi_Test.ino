/*
 * SENS-Able KALIBRASI TEST v2.0
 * 
 * Fixed: log[] rename, MAX30100 dual-library support, const char* handling
 * 
 * CARA PAKAI:
 * 1. Upload ke ESP32
 * 2. Buka Serial Monitor (115200 baud)
 * 3. Ketik 'start' → letakkan jari di MAX30102 (10 detik)
 * 4. Catat prediksi AI dari OLED
 * 5. Ukur glukosa dengan glukometer NYATA
 * 6. Ketik hasil glukometer di Serial (angka saja) → ENTER
 * 7. Ulangi 3x (hemat chip!)
 * 8. Ketik 'hasil' untuk ringkasan
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <math.h>

// ===================== MAX30100 LIBRARY =====================
// Include MAX30100.h directly — works with BOTH Kontakt and OXullo
#include <MAX30100.h>

// Detect which library: Kontakt defines pw1600, OXullo does not
#if defined(pw1600)
  #define MAX30100_KONTAKT 1
  // Kontakt: begin(pw1600, i50, sr100), readSensor(), sensor.IR, sensor.RED, getNumSamp()
#else
  #define MAX30100_OXULLO 1
  // OXullo: begin(), update(), getIR(), getRed(), getFIFOSamples()
#endif

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

// ===================== CALIBRATION DATA (renamed from 'log' to avoid math.h conflict) =====================
struct CalibEntry {
    float predicted;
    float reference;
    float error;
    float bodyTemp;
    unsigned long timestamp;
};

CalibEntry calibData[10]; // renamed from 'log' to 'calibData'
int calibCount = 0;
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

// ===================== READ PPG SAMPLE (handles both libraries) =====================
bool readPPGSample(float *irOut, float *redOut) {
#ifdef MAX30100_KONTAKT
    // Kontakt library: begin(pw1600, i50, sr100), readSensor(), sensor.IR, sensor.RED
    int avail = sensor.getNumSamp();
    if (avail > 0) {
        sensor.readSensor();
        *irOut = (float)sensor.IR;
        *redOut = (float)sensor.RED;
        return true;
    }
    return false;
#else
    // OXullo library: begin(), update(), getIR(), getRed()
    sensor.update();
    *irOut = (float)sensor.getIR();
    *redOut = (float)sensor.getRed();
    return true;
#endif
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
    String line3 = String(glucose_status_text(glucoseStatus)); // wrap in String()
    String line4 = "Suhu: " + String(sensorData.bodyTemp, 1) + "C";
    
    oledShow(line1, line2, line3, line4);
    
    switch (glucoseStatus) {
        case 0:  playBeep(1, 100); break;
        case 1:  playBeep(2, 150, 100); break;
        case 2:  playBeep(3, 300, 200); break;
        case 3:  playBeep(5, 100, 50); break;
    }
}

// ===================== SERIAL OUTPUT =====================
void printTestResult(int testNum, float predicted, float reference, float err, const char* status) {
    Serial.printf("║  %d   |   %6.1f   |   %6.1f   | %5.1f | %-8s ║\n",
                  testNum, predicted, reference, err, status);
}

void printSummary() {
    if (calibCount == 0) {
        Serial.println(">>> Belum ada data test! Ketik 'start' untuk mulai.");
        return;
    }
    
    float totalError = 0;
    float maxError = 0;
    float minError = 999;
    int accurateCount = 0;
    
    for (int i = 0; i < calibCount; i++) {
        float err = fabs(calibData[i].error);
        totalError += err;
        if (err > maxError) maxError = err;
        if (err < minError) minError = err;
        if (err < 15) accurateCount++;
    }
    
    float avgError = totalError / calibCount;
    float accuracy = (float)accurateCount / calibCount * 100;
    
    Serial.println();
    Serial.println("╔══════════════════════════════════════════════════╗");
    Serial.println("║              RINGKASAN KALIBRASI                 ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.printf("║ Jumlah test    : %d                              ║\n", calibCount);
    Serial.printf("║ Rata-rata error: %.1f mg/dL                     ║\n", avgError);
    Serial.printf("║ Error terkecil : %.1f mg/dL                     ║\n", minError);
    Serial.printf("║ Error terbesar : %.1f mg/dL                     ║\n", maxError);
    Serial.printf("║ Akurasi (<15)  : %.0f%%                           ║\n", accuracy);
    Serial.println("╚══════════════════════════════════════════════════╝");
    
    Serial.println();
    Serial.println("=== CSV (copy ke Excel) ===");
    Serial.println("Test,AI_Prediction,Glukometer,Error,Status,Body_Temp");
    for (int i = 0; i < calibCount; i++) {
        const char* status = glucose_status_text(interpret_glucose(calibData[i].predicted));
        Serial.printf("%d,%.1f,%.1f,%.1f,%s,%.1f\n",
                      i + 1, calibData[i].predicted, calibData[i].reference,
                      calibData[i].error, status, calibData[i].bodyTemp);
    }
}

// ===================== SETUP =====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(SPEAKER_PIN, OUTPUT);
    digitalWrite(SPEAKER_PIN, LOW);
    
    BusOLED.begin(OLED_SDA, OLED_SCL);
    BusOLED.setClock(100000);
    
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("OLED failed!");
        while (1);
    }
    
    oledShow("SENS-Able KALIBRASI", "v2.0 - Fixed", "Booting...", "");
    
    // Initialize MAX30100
    BusSensor.begin(MAX_SDA, MAX_SCL);
    BusSensor.setClock(400000);
    Wire = BusSensor;
    
#ifdef MAX30100_KONTAKT
    Serial.println("Library: Kontakt MAX30100");
    sensor.begin(pw1600, i50, sr100);
#else
    Serial.println("Library: OXullo MAX30100");
    sensor.begin();
#endif
    
    Wire = BusOLED;
    
    features.age = 25.0;
    features.weight = 60.0;
    features.height = 165.0;
    features.bmi = features.weight / ((features.height / 100.0) * (features.height / 100.0));
    features.lastMeal = 2.0;
    
    Serial.println();
    Serial.println("╔══════════════════════════════════════════════════╗");
    Serial.println("║   SENS-Able KALIBRASI TEST v2.0                 ║");
    Serial.println("╠══════════════════════════════════════════════════╣");
    Serial.println("║ CARA PAKAI:                                      ║");
    Serial.println("║ 1. Ketik 'start'                                 ║");
    Serial.println("║ 2. Letakkan jari di MAX30102 (10 detik)          ║");
    Serial.println("║ 3. Catat prediksi AI dari OLED                   ║");
    Serial.println("║ 4. Ukur glukometer → ketik angka → ENTER         ║");
    Serial.println("║ 5. Ulangi 3x → ketik 'hasil' untuk ringkasan     ║");
    Serial.println("╚══════════════════════════════════════════════════╝");
    Serial.println();
    
    oledShow("SENS-Able READY", "Ketik 'start'", "di Serial Monitor", "untuk mulai test!");
    
    playBeep(2, 100, 100);
    state = IDLE;
}

// ===================== LOOP =====================
void loop() {
    while (Serial.available()) {
        char c = Serial.read();
        
        if (c == '\n' || c == '\r') {
            if (inputBuffer.length() > 0) {
                if (inputBuffer.equalsIgnoreCase("hasil") || inputBuffer.equalsIgnoreCase("summary")) {
                    printSummary();
                } else if (inputBuffer.equalsIgnoreCase("mulai") || inputBuffer.equalsIgnoreCase("start")) {
                    state = RECORDING;
                    sampleCount = 0;
                    recStart = millis();
                    oledShow("Mulaiukur...", "Letakkan jari", "di MAX30102", "Tunggu 10 detik");
                    Serial.println("\n>>> Mulai pengukuran... Letakkan jari di sensor!");
                } else {
                    float ref = inputBuffer.toFloat();
                    if (ref > 0 && ref < 500) {
                        referenceInput = ref;
                        
                        float err = predictedGlucose - referenceInput;
                        const char* status = glucose_status_text(glucoseStatus);
                        
                        calibData[calibCount].predicted = predictedGlucose;
                        calibData[calibCount].reference = referenceInput;
                        calibData[calibCount].error = err;
                        calibData[calibCount].bodyTemp = sensorData.bodyTemp;
                        calibData[calibCount].timestamp = millis();
                        calibCount++;
                        testNumber++;
                        
                        printTestResult(testNumber, predictedGlucose, referenceInput, err, status);
                        
                        String line1 = "Test #" + String(testNumber) + " SELESAI";
                        String line2 = "AI: " + String(predictedGlucose, 1) + " mg/dL";
                        String line3 = "Real: " + String(referenceInput, 1) + " mg/dL";
                        String line4 = "Error: " + String(fabs(err), 1) + " mg/dL";
                        oledShow(line1, line2, line3, line4);
                        
                        if (fabs(err) < 10) {
                            playBeep(2, 100, 50);
                        } else if (fabs(err) < 20) {
                            playBeep(1, 200);
                        } else {
                            playBeep(3, 100, 100);
                        }
                        
                        Serial.println(">>> Tersimpan! Ketik 'start' untuk test berikutnya.");
                        Serial.println(">>> Ketik 'hasil' untuk lihat ringkasan.");
                        
                        state = IDLE;
                    } else {
                        Serial.println(">>> Input tidak valid! Ketik angka glukometer.");
                    }
                }
            }
            inputBuffer = "";
        } else if ((c >= '0' && c <= '9') || c == '.' || c == '-') {
            inputBuffer += c;
        }
    }
    
    if (state == RECORDING) {
        Wire = BusSensor;
        
        if (sampleCount < MAX_SAMPLES) {
            float ir, red;
            if (readPPGSample(&ir, &red)) {
                irBuf[sampleCount] = ir;
                redBuf[sampleCount] = red;
                sampleCount++;
            }
        }
        
        Wire = BusOLED;
        
        static unsigned long lastUpdate = 0;
        if (millis() - lastUpdate > 500) {
            int elapsed = (millis() - recStart) / 1000;
            oledShow("Merekam... " + String(elapsed) + "/" + String(RECORD_SEC) + " dtk",
                     "Sampel: " + String(sampleCount),
                     "Progress: " + String((elapsed * 100) / RECORD_SEC) + "%",
                     "");
            lastUpdate = millis();
        }
        
        if ((millis() - recStart) >= (RECORD_SEC * 1000)) {
            state = PREDICTING;
            oledShow("Memproses...", "Menghitung fitur", "Menjalankan AI", "");
            
            computeFeatures();
            runInference();
            showResult();
            
            Serial.println();
            Serial.printf(">>> Prediksi AI: %.1f mg/dL (%s)\n", 
                         predictedGlucose, glucose_status_text(glucoseStatus));
            Serial.println(">>> Sekarang ukur dengan glukometer!");
            Serial.print(">>> Ketik hasil glukometer: ");
            
            oledShow("PREDIKSI AI:", String(predictedGlucose, 1) + " mg/dL",
                     String(glucose_status_text(glucoseStatus)),
                     "Ketik glukometer!");
            
            state = WAITING_REFERENCE;
        }
        
        delay(10);
    }
    
    delay(10);
}
