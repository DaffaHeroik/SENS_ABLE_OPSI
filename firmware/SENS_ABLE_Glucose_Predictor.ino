/*
 * SENS-ABLE Glucose Predictor v1.2
 * ESP32 + MAX30100 + MLX90614 + OLED + Speaker + Vibrator
 *
 * Library: MAX30100 by Kontakt (Connor Huffine)
 * API: begin(pulseWidth, ledCurrent, sampleRate), readSensor(), sensor.IR/RED
 *
 * Hardware Connections:
 *   OLED    : SDA=21, SCL=22
 *   MLX90614: SDA=21, SCL=22 (same bus as OLED)
 *   MAX30100: SDA=18, SCL=19 (separate bus)
 *   Speaker : GPIO 23
 *   Vibrator: GPIO 26
 */

#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30100.h>
#include <math.h>

// Include the embedded ML model
#include "model_glucose_inference.h"

// ===================== CONFIGURATION =====================
const char* AP_SSID = "SENS-Able";
const char* AP_PASS = "sensable123";

// Pin Definitions
#define OLED_SDA    21
#define OLED_SCL    22
#define MAX_SDA     18
#define MAX_SCL     19
#define MLX_ADDR    0x5A
#define SPEAKER_PIN 23
#define VIBRO_PIN   26

// Measurement Settings
#define RECORD_SEC    10
#define MAX_SAMPLES   1200
#define MIN_SAMPLES   100

// ===================== OBJECTS =====================
TwoWire BusOLED   = TwoWire(0);
TwoWire BusSensor = TwoWire(1);
Adafruit_SSD1306 display(128, 64, &BusOLED, -1);
MAX30100 sensor;
WebServer server(80);

// ===================== STATE =====================
enum State { IDLE, RECORDING, PREDICTING, SHOWING_RESULT };
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
    float hr;
    float spo2;
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

// ===================== MLX90614 MANUAL READ =====================
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

// ===================== AUDIO FEEDBACK =====================
void playBeep(int count, int durationMs = 100, int pauseMs = 50) {
    for (int i = 0; i < count; i++) {
        digitalWrite(SPEAKER_PIN, HIGH);
        delay(durationMs);
        digitalWrite(SPEAKER_PIN, LOW);
        if (i < count - 1) delay(pauseMs);
    }
}

void playGlucoseBeep(int status) {
    switch (status) {
        case 0:  playBeep(1, 100); break;
        case 1:  playBeep(2, 150, 100); break;
        case 2:  playBeep(3, 300, 200); break;
        case 3:  playBeep(5, 100, 50); break;
    }
}

// ===================== VIBRATION FEEDBACK =====================
void vibrate(int durationMs = 200) {
    digitalWrite(VIBRO_PIN, HIGH);
    delay(durationMs);
    digitalWrite(VIBRO_PIN, LOW);
}

void vibratePattern(int status) {
    switch (status) {
        case 0:  vibrate(100); break;
        case 1:  vibrate(150); delay(100); vibrate(150); break;
        case 2:  vibrate(200); delay(100); vibrate(200); delay(100); vibrate(200); break;
        case 3:  for (int i = 0; i < 5; i++) { vibrate(150); delay(50); } break;
    }
}

// ===================== COMPUTE FEATURES =====================
void computeFeatures() {
    if (sampleCount < MIN_SAMPLES) {
        Serial.println("Not enough samples!");
        return;
    }
    
    // IR statistics
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
    
    // RED statistics
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
    
    // AC/DC components
    features.ratioAC = (features.irMax - features.irMin) / features.irMean;
    features.ratioDC = (features.redMax - features.redMin) / features.redMean;
    
    features.samples = sampleCount;
    
    Serial.printf("Features: IR[%.1f, %.1f, %.1f] RED[%.1f, %.1f, %.1f]\n",
                  features.irMean, features.irMin, features.irMax,
                  features.redMean, features.redMin, features.redMax);
}

// ===================== RUN INFERENCE =====================
void runInference() {
    sensorData.bodyTemp = readMLXObject();
    sensorData.ambientTemp = readMLXAmbient();
    sensorData.hr = 70.0;
    sensorData.spo2 = 98.0;
    
    float inputFeatures[GLUCOSE_MODEL_FEATURES] = {
        features.age,
        features.weight,
        features.height,
        features.bmi,
        features.lastMeal,
        sensorData.bodyTemp,
        sensorData.ambientTemp,
        sensorData.hr,
        sensorData.spo2,
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
    
    String statusStr = glucose_status_text(glucoseStatus);
    Serial.printf("Predicted: %.1f mg/dL (%s)\n", predictedGlucose, statusStr.c_str());
}

// ===================== SHOW RESULT =====================
void showResult() {
    String line1 = "=== GLUCOSE ===";
    String line2 = String(predictedGlucose, 1) + " mg/dL";
    String line3 = glucose_status_text(glucoseStatus);
    String line4 = "Temp: " + String(sensorData.bodyTemp, 1) + "C";
    
    oledShow(line1, line2, line3, line4);
    
    playGlucoseBeep(glucoseStatus);
    vibratePattern(glucoseStatus);
    
    Serial.println("=== RESULT ===");
    Serial.printf("Glucose: %.1f mg/dL\n", predictedGlucose);
    String statusStr = glucose_status_text(glucoseStatus);
    Serial.printf("Status: %s\n", statusStr.c_str());
    Serial.printf("Body Temp: %.1f C\n", sensorData.bodyTemp);
}

// ===================== WEB HANDLERS =====================
String buildHTML(String content = "") {
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
    html += "<title>SENS-Able Glucose Predictor</title>";
    html += "<style>";
    html += "body{font-family:Arial;background:#1a1a2e;color:#fff;margin:0;padding:20px;}";
    html += ".header{background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;border-radius:10px;margin-bottom:20px;}";
    html += ".card{background:#16213e;padding:20px;border-radius:10px;margin-bottom:15px;}";
    html += ".btn{background:#667eea;color:#fff;border:none;padding:15px 30px;border-radius:5px;font-size:16px;cursor:pointer;width:100%;}";
    html += ".btn:hover{background:#764ba2;}";
    html += ".result{font-size:48px;text-align:center;padding:20px;}";
    html += ".normal{color:#4ade80;}";
    html += ".prediabetic{color:#fbbf24;}";
    html += ".diabetic{color:#f87171;}";
    html += ".low{color:#ff0000;font-weight:bold;}";
    html += "</style></head><body>";
    
    html += "<div class='header'>";
    html += "<h1>SENS-Able Glucose Predictor</h1>";
    html += "<p>AI-powered blood glucose estimation from PPG sensor</p>";
    html += "</div>";
    
    if (content.length() > 0) {
        html += content;
    }
    
    html += "<div class='card'>";
    html += "<h3>Last Prediction</h3>";
    html += "<div class='result ";
    
    switch (glucoseStatus) {
        case 0: html += "normal"; break;
        case 1: html += "prediabetic"; break;
        case 2: html += "diabetic"; break;
        case 3: html += "low"; break;
    }
    
    html += "'>" + String(predictedGlucose, 1) + " mg/dL</div>";
    
    String statusText = glucose_status_text(glucoseStatus);
    html += "<p>Status: " + statusText + "</p>";
    html += "<p>Body Temp: " + String(sensorData.bodyTemp, 1) + " C</p>";
    html += "</div>";
    
    html += "<div class='card'>";
    html += "<h3>New Measurement</h3>";
    html += "<p>Place your finger on the MAX30100 sensor, then click Start.</p>";
    html += "<form method='POST' action='/measure'>";
    html += "<button type='submit' class='btn'>Start Measurement</button>";
    html += "</form>";
    html += "</div>";
    
    html += "<div class='card'>";
    html += "<h3>Export Data</h3>";
    html += "<a href='/csv'><button class='btn'>Download CSV</button></a>";
    html += "</div>";
    
    html += "</body></html>";
    return html;
}

void handleRoot() {
    server.send(200, "text/html", buildHTML());
}

void handleMeasure() {
    state = RECORDING;
    sampleCount = 0;
    recStart = millis();
    
    oledShow("Measuring...", "Place finger on", "MAX30100 sensor", "");
    
    server.send(200, "text/html", buildHTML("<div class='card'><p>Measurement started. Wait 10 seconds...</p></div>"));
}

void handleCSV() {
    String statusText = glucose_status_text(glucoseStatus);
    
    String csv = "PredictedGlucose,Status,BodyTemp,AmbientTemp,IR_Mean,RED_Mean\n";
    csv += String(predictedGlucose, 1) + ",";
    csv += statusText + ",";
    csv += String(sensorData.bodyTemp, 1) + ",";
    csv += String(sensorData.ambientTemp, 1) + ",";
    csv += String(features.irMean, 1) + ",";
    csv += String(features.redMean, 1) + "\n";
    
    server.sendHeader("Content-Disposition", "attachment; filename=glucose_prediction.csv");
    server.send(200, "text/csv", csv);
}

// ===================== SETUP =====================
void setup() {
    Serial.begin(115200);
    
    // Initialize pins
    pinMode(SPEAKER_PIN, OUTPUT);
    pinMode(VIBRO_PIN, OUTPUT);
    digitalWrite(SPEAKER_PIN, LOW);
    digitalWrite(VIBRO_PIN, LOW);
    
    // Initialize OLED on Bus 0
    BusOLED.begin(OLED_SDA, OLED_SCL);
    BusOLED.setClock(100000);
    
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("OLED failed!");
        while (1);
    }
    
    oledShow("SENS-Able v1.2", "Glucose Predictor", "Booting...", "");
    
    // Initialize MAX30100 on Bus 1
    // Library uses global Wire, so we assign BusSensor to Wire first
    BusSensor.begin(MAX_SDA, MAX_SCL);
    BusSensor.setClock(400000);
    Wire = BusSensor;
    
    // begin(pulseWidth, ledCurrent, sampleRate)
    sensor.begin(pw1600, i50, sr100);
    
    // Reassign Wire back to OLED bus for OLED/MLX operations
    Wire = BusOLED;
    
    // Set default user data
    features.age = 25.0;
    features.weight = 60.0;
    features.height = 165.0;
    features.bmi = features.weight / ((features.height / 100.0) * (features.height / 100.0));
    features.lastMeal = 2.0;
    
    // Initialize WiFi
    WiFi.softAP(AP_SSID, AP_PASS);
    String ip = WiFi.softAPIP().toString();
    Serial.println("AP IP: " + ip);
    
    // Setup web server
    server.on("/", HTTP_GET, handleRoot);
    server.on("/measure", HTTP_POST, handleMeasure);
    server.on("/csv", HTTP_GET, handleCSV);
    server.begin();
    
    oledShow("SENS-Able READY", "WiFi: SENS-Able", "Pass: sensable123", "IP: " + ip);
    
    playBeep(2, 100, 100);
    
    Serial.println("=== SENS-Able Glucose Predictor v1.2 ===");
    Serial.println("Ready for measurements!");
}

// ===================== LOOP =====================
void loop() {
    server.handleClient();
    
    if (state == RECORDING) {
        // Switch to sensor bus for MAX30100
        Wire = BusSensor;
        
        // Kontakt library: getNumSamp() checks FIFO, readSensor() reads IR+RED
        if (sampleCount < MAX_SAMPLES) {
            int avail = sensor.getNumSamp();
            if (avail > 0) {
                sensor.readSensor();
                irBuf[sampleCount] = (float)sensor.IR;
                redBuf[sampleCount] = (float)sensor.RED;
                sampleCount++;
            }
        }
        
        // Switch to OLED bus for display
        Wire = BusOLED;
        
        // Update display with progress
        if (millis() % 500 < 20) {
            int elapsed = (millis() - recStart) / 1000;
            oledShow("Recording...", 
                     String(elapsed) + "/" + String(RECORD_SEC) + " sec", 
                     "Samples: " + String(sampleCount), "");
        }
        
        // Check if recording complete
        if ((millis() - recStart) >= (RECORD_SEC * 1000)) {
            state = PREDICTING;
            oledShow("Processing...", "Computing features", "Running AI model", "");
            
            computeFeatures();
            runInference();
            showResult();
            
            state = SHOWING_RESULT;
        }
        
        delay(10);
    }
    
    delay(10);
}
