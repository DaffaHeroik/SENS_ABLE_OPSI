/*
 * SENS-ABLE Data Collector v6.4 (LittleFS Storage)
 * ESP32 Access Point + Web Server
 * Kumpul data PPG (IR, RED) + Suhu untuk training AI gula darah
 * Data aman dari reset/mati lampu.
 * 
 * Koneksi:
 * OLED    : SDA=21, SCL=22 (sama dengan MLX)
 * MLX90614: SDA=21, SCL=22
 * MAX30100: SDA=18, SCL=19
 */

#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Preferences.h>
#ifndef SENSABLE_GATEWAY_CERTIFICATE_PRESENT
#define SENSABLE_GATEWAY_CERTIFICATE_PRESENT 0
#endif
#if SENSABLE_GATEWAY_CERTIFICATE_PRESENT
#include "gateway_certificate.h"
#endif
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30100.h>
#include <math.h>
#include <LittleFS.h> // Library untuk memori internal permanen

// ===================== KONFIGURASI WiFi AP =====================
const char* AP_SSID = "SENS-Able";
const char* AP_PASS = "sensable123";

// Gateway reporting is test-only. A release build must include a reviewed
// root-CA header for the final HTTPS gateway. Do not use client.setInsecure().
Preferences gatewayPrefs;
String gatewaySsid = "", gatewayPassword = "", gatewayOrigin = "", gatewayDeviceId = "", gatewayDeviceToken = "";
const char* GATEWAY_NAMESPACE = "gateway";
const char* GATEWAY_FIRMWARE_VERSION = "v0.7.0-gateway";

// ===================== PIN =====================
#define OLED_SDA  21
#define OLED_SCL  22
#define MAX_SDA   18
#define MAX_SCL   19
#define MLX_ADDR  0x5A

// ===================== OBJEK =====================
TwoWire BusOLED   = TwoWire(0);
TwoWire BusSensor = TwoWire(1);
Adafruit_SSD1306 display(128, 64, &BusOLED, -1);
MAX30100 sensor;
WebServer server(80);

// ===================== STATE =====================
enum State { IDLE, RECORDING, DONE };
State state = IDLE;

// ===================== BUFFER =====================
#define MAX_SAMPLES 1200
#define RECORD_SEC  10
#define MAX_NAME_LENGTH 64
#define MAX_GLUCOSE_REFERENCE 1000.0f
#define MIN_SAMPLES 100

float irBuf[MAX_SAMPLES];
float redBuf[MAX_SAMPLES];
int sampleCount = 0;
unsigned long recStart = 0;

// ===================== FITUR HASIL =====================
struct Features {
  float irMean, irMin, irMax, irStd, irRMS;
  float redMean, redMin, redMax, redStd, redRMS;
  float ratioAC, ratioDC;
  float bodyTemp, ambientTemp;
  int samples;
} feat;

// ===================== DATA RESPONDEN =====================
String respName     = "";
String respAge      = "";
String respGender   = "";
float  glucoseRef   = 0;
float  respBerat    = 0;
float  respTinggi   = 0;
bool   respDiabetes = false;
float  respLastMeal = 0;
bool   dataReady    = false;

const char* DATA_FILE = "/dataset.csv";
const char* CSV_HEADER = "Nama,Usia,Gender,Berat_kg,Tinggi_cm,BMI,Diabetes,GlukosaRef,TerakhirMakan_jam,SuhuTubuh,SuhuAmbient,HR_est,SpO2_est,IR_Mean,IR_Min,IR_Max,IR_Std,IR_RMS,RED_Mean,RED_Min,RED_Max,RED_Std,RED_RMS,Ratio_AC,Ratio_DC,Samples\n";

// ===================== BACA MLX MANUAL =====================
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

// Browser Web Serial provisioning command:
// CONFIG|<SSID>|<PASSWORD>|<HTTPS_ORIGIN>|<DEVICE_ID>|<DEVICE_TOKEN>
// Values are only written to local ESP32 Preferences, never to the web gateway.
String gatewayField(const String &source, int index) {
  int start = 0;
  for (int i = 0; i < index; i++) {
    start = source.indexOf('|', start) + 1;
    if (start == 0) return "";
  }
  int end = source.indexOf('|', start);
  return end < 0 ? source.substring(start) : source.substring(start, end);
}

bool validGatewayValue(const String &value, int minLength, int maxLength) {
  return value.length() >= minLength && value.length() <= maxLength && value.indexOf('|') < 0 && value.indexOf('\r') < 0 && value.indexOf('\n') < 0;
}

void loadGatewayConfig() {
  gatewayPrefs.begin(GATEWAY_NAMESPACE, true);
  gatewaySsid = gatewayPrefs.getString("ssid", "");
  gatewayPassword = gatewayPrefs.getString("pass", "");
  gatewayOrigin = gatewayPrefs.getString("origin", "");
  gatewayDeviceId = gatewayPrefs.getString("device", "");
  gatewayDeviceToken = gatewayPrefs.getString("token", "");
  gatewayPrefs.end();
}

bool saveGatewayConfig(const String &ssid, const String &password, const String &origin, const String &deviceId, const String &token) {
  if (!validGatewayValue(ssid, 1, 32) || !validGatewayValue(password, 8, 64) || !origin.startsWith("https://") || !validGatewayValue(origin, 12, 160) || !validGatewayValue(deviceId, 3, 48) || !validGatewayValue(token, 32, 128)) return false;
  gatewayPrefs.begin(GATEWAY_NAMESPACE, false);
  gatewayPrefs.putString("ssid", ssid); gatewayPrefs.putString("pass", password); gatewayPrefs.putString("origin", origin); gatewayPrefs.putString("device", deviceId); gatewayPrefs.putString("token", token);
  gatewayPrefs.end(); loadGatewayConfig(); return true;
}

void handleGatewaySerialProvisioning() {
  static String command = "";
  while (Serial.available()) {
    char received = (char)Serial.read();
    if (received == '\n') {
      command.trim();
      if (command.startsWith("CONFIG|")) {
        if (saveGatewayConfig(gatewayField(command, 1), gatewayField(command, 2), gatewayField(command, 3), gatewayField(command, 4), gatewayField(command, 5))) Serial.println("GATEWAY_CONFIG_SAVED");
        else Serial.println("GATEWAY_CONFIG_REJECTED");
      }
      command = "";
    } else if (command.length() < 450) command += received;
    else command = "";
  }
}

bool connectGatewayWiFi() {
  if (gatewaySsid.length() == 0 || gatewayPassword.length() == 0) return false;
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.begin(gatewaySsid.c_str(), gatewayPassword.c_str());
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 12000UL) delay(250);
  return WiFi.status() == WL_CONNECTED;
}

bool reportTestReadingToGateway(float hrEst, float spo2Est) {
  if (gatewayOrigin.length() == 0 || gatewayDeviceId.length() == 0 || gatewayDeviceToken.length() == 0 || !connectGatewayWiFi()) return false;
  WiFiClientSecure secureClient;
#if SENSABLE_GATEWAY_CERTIFICATE_PRESENT
  secureClient.setCACert(SENSABLE_GATEWAY_ROOT_CA);
#else
  Serial.println("GATEWAY_TLS_CA_REQUIRED"); return false;
#endif
  HTTPClient https; String endpoint = gatewayOrigin + "/api/ingest/v1/readings";
  if (!https.begin(secureClient, endpoint)) return false;
  https.setConnectTimeout(8000); https.addHeader("Content-Type", "application/json"); https.addHeader("X-Device-Token", gatewayDeviceToken);
  String payload = "{\"device_id\":\"" + gatewayDeviceId + "\",\"firmware_version\":\"" + GATEWAY_FIRMWARE_VERSION + "\",";
  payload += "\"ir_mean\":" + String(feat.irMean, 2) + ",\"red_mean\":" + String(feat.redMean, 2) + ",";
  payload += "\"heart_rate_bpm\":" + String(hrEst, 1) + ",\"spo2_pct\":" + String(spo2Est, 2) + ",";
  payload += "\"temperature_c\":" + String(feat.bodyTemp, 2) + ",\"uptime_ms\":" + String(millis()) + "}";
  int status = https.POST(payload); https.end();
  Serial.println(status == 202 ? "GATEWAY_REPORT_ACCEPTED" : "GATEWAY_REPORT_FAILED");
  return status == 202;
}

// ===================== HITUNG FITUR =====================
void computeFeatures() {
  if (sampleCount == 0) return;

  float sumIR = 0, sumRED = 0;
  for (int i = 0; i < sampleCount; i++) {
    sumIR  += irBuf[i];
    sumRED += redBuf[i];
  }
  feat.irMean  = sumIR  / sampleCount;
  feat.redMean = sumRED / sampleCount;

  feat.irMin  = irBuf[0];  feat.irMax  = irBuf[0];
  feat.redMin = redBuf[0]; feat.redMax = redBuf[0];
  float sumIRvar = 0, sumREDvar = 0;
  float sumIRsq  = 0, sumREDsq  = 0;

  for (int i = 0; i < sampleCount; i++) {
    if (irBuf[i]  < feat.irMin)  feat.irMin  = irBuf[i];
    if (irBuf[i]  > feat.irMax)  feat.irMax  = irBuf[i];
    if (redBuf[i] < feat.redMin) feat.redMin = redBuf[i];
    if (redBuf[i] > feat.redMax) feat.redMax = redBuf[i];
    sumIRvar  += (irBuf[i]  - feat.irMean)  * (irBuf[i]  - feat.irMean);
    sumREDvar += (redBuf[i] - feat.redMean) * (redBuf[i] - feat.redMean);
    sumIRsq   += irBuf[i]  * irBuf[i];
    sumREDsq  += redBuf[i] * redBuf[i];
  }

  feat.irStd   = sqrt(sumIRvar  / sampleCount);
  feat.redStd  = sqrt(sumREDvar / sampleCount);
  feat.irRMS   = sqrt(sumIRsq   / sampleCount);
  feat.redRMS  = sqrt(sumREDsq  / sampleCount);

  float irAC   = feat.irMax  - feat.irMin;
  float redAC  = feat.redMax - feat.redMin;
  feat.ratioAC = (irAC > 0)        ? (redAC / irAC)              : 0;
  feat.ratioDC = (feat.irMean > 0) ? (feat.redMean / feat.irMean) : 0;

  feat.bodyTemp    = readMLXObject();
  feat.ambientTemp = readMLXAmbient();
  feat.samples     = sampleCount;

  Serial.println("=== DEBUG SENSOR ===");
  Serial.print("sampleCount: "); Serial.println(sampleCount);
  Serial.print("IR Mean: ");     Serial.println(feat.irMean);
  Serial.print("RED Mean: ");    Serial.println(feat.redMean);
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

// ===================== SAFE TEXT HELPERS =====================
String csvSafe(String value) {
  value.replace(",", " ");
  value.replace("\r", " ");
  value.replace("\n", " ");
  return value;
}

String htmlSafe(String value) {
  value.replace("&", "&amp;");
  value.replace("<", "&lt;");
  value.replace(">", "&gt;");
  value.replace("\"", "&quot;");
  value.replace("'", "&#39;");
  return value;
}

// ===================== BUILD HTML =====================
String buildHTML(String msg = "") {

  String html = "<!DOCTYPE html><html lang='id'><head>";
  html += "<meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<title>SENS-Able Data Collector</title>";
  html += "<style>";
  html += "* { box-sizing: border-box; margin: 0; padding: 0; }";
  html += "body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }";
  html += ".header { background: linear-gradient(135deg,#1e3a5f,#0f172a); padding: 20px; text-align: center; border-bottom: 2px solid #38bdf8; }";
  html += ".header h1 { color: #38bdf8; font-size: 1.6em; letter-spacing: 2px; }";
  html += ".header p  { color: #94a3b8; font-size: 0.85em; margin-top: 4px; }";
  html += ".container { max-width: 520px; margin: 24px auto; padding: 0 16px; }";
  html += ".card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #334155; }";
  html += ".card h2 { color: #38bdf8; font-size: 1em; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px; }";
  html += ".row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }";
  html += "label { display: block; font-size: 0.8em; color: #94a3b8; margin-bottom: 4px; margin-top: 10px; }";
  html += "input, select { width: 100%; padding: 10px 12px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #e2e8f0; font-size: 0.95em; }";
  html += "input:focus, select:focus { outline: none; border-color: #38bdf8; }";
  html += ".btn { width: 100%; padding: 14px; border: none; border-radius: 10px; font-size: 1em; font-weight: bold; cursor: pointer; margin-top: 14px; letter-spacing: 1px; }";
  html += ".btn-record { background: linear-gradient(135deg,#0ea5e9,#2563eb); color: white; }";
  html += ".btn-csv    { background: linear-gradient(135deg,#059669,#047857); color: white; }";
  html += ".btn-reset  { background: #334155; color: #94a3b8; }";
  html += ".msg { padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 16px; font-weight: bold; }";
  html += ".msg-ok  { background: #064e3b; color: #34d399; border: 1px solid #059669; }";
  html += ".msg-err { background: #450a0a; color: #f87171; border: 1px solid #dc2626; }";
  html += ".sec { font-size: 0.72em; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; margin-top: 18px; margin-bottom: 6px; border-bottom: 1px solid #1e3a5f; padding-bottom: 4px; }";
  html += ".g3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 8px; }";
  html += ".g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }";
  html += ".sb { background: #0f172a; border-radius: 8px; padding: 10px; text-align: center; border: 1px solid #334155; }";
  html += ".sv { font-size: 1.1em; font-weight: bold; color: #38bdf8; }";
  html += ".sl { font-size: 0.68em; color: #64748b; margin-top: 2px; }";
  html += ".csv-count { text-align: center; color: #94a3b8; font-size: 0.85em; margin-top: 8px; }";
  html += ".tag-d { background: #450a0a; color: #f87171; border-radius: 6px; padding: 2px 10px; font-size: 0.8em; font-weight: bold; }";
  html += ".tag-n { background: #064e3b; color: #34d399; border-radius: 6px; padding: 2px 10px; font-size: 0.8em; font-weight: bold; }";
  html += ".warmup { background: #1e3a5f; color: #38bdf8; border-radius: 8px; padding: 10px; text-align: center; font-size: 0.85em; margin-top: 10px; border: 1px solid #0284c7; }";
  html += "</style></head><body>";

  html += "<div class='header'><h1>&#9877; SENS-Able</h1>";
  html += "<p>Data Collector untuk Training AI Gula Darah</p></div>";
  html += "<div class='container'>";

  if (msg != "") html += msg;

  // ---- FORM ----
  html += "<div class='card'><h2>Data Responden</h2>";
  html += "<form method='POST' action='/record' autocomplete='off'>";

  html += "<div class='sec'>Identitas</div>";
  html += "<label>Nama Responden</label>";
  html += "<input type='text' name='nama' placeholder='Contoh: Budi Santoso' required>";

  html += "<div class='row2'>";
  html += "<div><label>Usia (tahun)</label>";
  html += "<input type='number' name='usia' placeholder='45' required min='1' max='120'></div>";
  html += "<div><label>Jenis Kelamin</label>";
  html += "<select name='gender'>";
  html += "<option value='L'>Laki-laki</option>";
  html += "<option value='P'>Perempuan</option>";
  html += "</select></div>";
  html += "</div>";

  html += "<div class='row2'>";
  html += "<div><label>Berat Badan (kg)</label>";
  html += "<input type='number' name='berat' step='0.1' placeholder='65.0' required min='1'></div>";
  html += "<div><label>Tinggi Badan (cm)</label>";
  html += "<input type='number' name='tinggi' step='0.1' placeholder='170.0' required min='1'></div>";
  html += "</div>";

  html += "<div class='sec'>Kondisi Kesehatan</div>";
  html += "<label>Status Diabetes</label>";
  html += "<select name='diabetes'>";
  html += "<option value='0'>Tidak Diabetes</option>";
  html += "<option value='1'>Diabetes</option>";
  html += "</select>";

  html += "<label>Gula Darah Referensi (mg/dL) dari Glukometer</label>";
  html += "<input type='number' name='glukosa' step='0.1' placeholder='112.5' required min='0.1'>";

  html += "<label>Terakhir Makan (jam yang lalu)</label>";
  html += "<input type='number' name='lastmeal' step='0.5' placeholder='2.5' required min='0' max='24'>";

  html += "<div class='warmup'>&#9432; Setelah submit, sensor warm-up 2 detik lalu rekam 10 detik. Total ~12 detik.</div>";
  html += "<button class='btn btn-record' type='submit'>&#9654; Mulai Rekam Sensor</button>";
  html += "</form></div>";

  // ---- HASIL TERAKHIR ----
  if (dataReady) {
    String safeRespName = htmlSafe(respName);
    float tinggiM = respTinggi / 100.0;
    float bmi     = (tinggiM > 0) ? (respBerat / (tinggiM * tinggiM)) : 0;
    float spo2est = 110.0 - 25.0 * feat.ratioAC;
    if (spo2est > 100) spo2est = 100;
    if (spo2est < 80)  spo2est = 80;
    float hrEst = 60.0 + (feat.irMean > 0 ? (feat.irStd / feat.irMean) * 300.0 : 0);
    if (hrEst > 200) hrEst = 200;
    if (hrEst < 40)  hrEst = 40;

    html += "<div class='card'><h2>Hasil Terakhir &mdash; " + safeRespName + " &nbsp;";
    html += "<span class='" + String(respDiabetes ? "tag-d" : "tag-n") + "'>";
    html += String(respDiabetes ? "Diabetes" : "Non-Diabetes") + "</span></h2>";

    html += "<div class='sec'>Identitas &amp; Antropometri</div>";
    html += "<div class='g2'>";
    html += "<div class='sb'><div class='sv'>" + htmlSafe(respAge) + " th &nbsp;|&nbsp;" + htmlSafe(respGender) + "</div><div class='sl'>Usia &amp; Gender</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(bmi, 1) + "</div><div class='sl'>BMI (" + String(respBerat, 1) + "kg / " + String(respTinggi, 0) + "cm)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(glucoseRef, 0) + " mg/dL</div><div class='sl'>Gula Darah (Ref)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(respLastMeal, 1) + " jam</div><div class='sl'>Terakhir Makan</div></div>";
    html += "</div>";

    html += "<div class='sec'>Suhu &amp; Vital</div>";
    html += "<div class='g3'>";
    html += "<div class='sb'><div class='sv'>" + String(feat.bodyTemp, 1) + " &deg;C</div><div class='sl'>Suhu Tubuh (BT)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.ambientTemp, 1) + " &deg;C</div><div class='sl'>Suhu Ruangan (RT)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(hrEst, 0) + " bpm</div><div class='sl'>HR (estimasi)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(spo2est, 1) + " %</div><div class='sl'>SpO2 (estimasi)</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.ratioAC, 4) + "</div><div class='sl'>Ratio AC</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.samples) + "</div><div class='sl'>Total Samples</div></div>";
    html += "</div>";

    html += "<div class='sec'>IR Channel</div>";
    html += "<div class='g3'>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irMean, 0) + "</div><div class='sl'>IR Mean</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irMin, 0) + "</div><div class='sl'>IR Min</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irMax, 0) + "</div><div class='sl'>IR Max</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irStd, 1) + "</div><div class='sl'>IR Std Dev</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irRMS, 0) + "</div><div class='sl'>IR RMS</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.irMax - feat.irMin, 0) + "</div><div class='sl'>IR AC (pk-pk)</div></div>";
    html += "</div>";

    html += "<div class='sec'>RED Channel</div>";
    html += "<div class='g3'>";
    html += "<div class='sb'><div class='sv'>" + String(feat.redMean, 0) + "</div><div class='sl'>RED Mean</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.redMin, 0) + "</div><div class='sl'>RED Min</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.redMax, 0) + "</div><div class='sl'>RED Max</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.redStd, 1) + "</div><div class='sl'>RED Std Dev</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.redRMS, 0) + "</div><div class='sl'>RED RMS</div></div>";
    html += "<div class='sb'><div class='sv'>" + String(feat.ratioDC, 4) + "</div><div class='sl'>Ratio DC</div></div>";
    html += "</div>";

    html += "</div>";
  }

  // ---- HITUNG BARIS DARI FILE LITTLEFS ----
  int rows = 0;
  File file = LittleFS.open(DATA_FILE, "r");
  if (file) {
    while (file.available()) {
      if (file.read() == '\n') rows++;
    }
    file.close();
  }
  rows -= 1; // Kurangi 1 karena baris pertama adalah Header
  if (rows < 0) rows = 0;

  html += "<div class='card'><h2>Dataset CSV (Permanen)</h2>";
  html += "<p class='csv-count'>Total data tersimpan: <b>" + String(rows) + " baris</b></p>";
  html += "<a href='/csv'><button class='btn btn-csv' type='button'>&#11015; Download CSV</button></a>";
  html += "<form method='POST' action='/reset'>";
  html += "<button class='btn btn-reset' type='submit' onclick=\"return confirm('Reset semua data yang tersimpan?')\">&#128465; Reset Data</button>";
  html += "</form></div>";

  html += "</div></body></html>";
  return html;
}

// ===================== ROUTE HANDLERS =====================
void handleRoot() {
  server.send(200, "text/html", buildHTML());
}

void handleRecord() {
  if (server.method() != HTTP_POST) {
    server.sendHeader("Location", "/");
    server.send(303);
    return;
  }

  // Reset semua variabel responden
  respName     = "";
  respAge      = "";
  respGender   = "";
  glucoseRef   = 0;
  respBerat    = 0;
  respTinggi   = 0;
  respDiabetes = false;
  respLastMeal = 0;

  // Reset buffer dan fitur
  sampleCount = 0;
  memset(irBuf,  0, sizeof(irBuf));
  memset(redBuf, 0, sizeof(redBuf));
  memset(&feat,  0, sizeof(feat));

  // Baca form
  respName     = csvSafe(server.arg("nama"));
  respAge      = server.arg("usia");
  respGender   = server.arg("gender");
  glucoseRef   = server.arg("glukosa").toFloat();
  respBerat    = server.arg("berat").toFloat();
  respTinggi   = server.arg("tinggi").toFloat();
  respDiabetes = (server.arg("diabetes") == "1");
  respLastMeal = server.arg("lastmeal").toFloat();

  if (respName.length() == 0 || respName.length() > MAX_NAME_LENGTH ||
      respAge.toInt() < 1 || respAge.toInt() > 120 ||
      (respGender != "L" && respGender != "P") ||
      glucoseRef <= 0 || glucoseRef > MAX_GLUCOSE_REFERENCE ||
      respBerat <= 0 || respTinggi <= 0 || respLastMeal < 0 || respLastMeal > 24) {
    server.send(200, "text/html", buildHTML("<div class='msg msg-err'>&#10060; Isi semua field dengan benar!</div>"));
    return;
  }

  // ---- WARM-UP SENSOR 2 DETIK ----
  state = RECORDING;
  oledShow("WARM-UP...", respName, "Tempel jari!", "Siap-siap...");

  Wire = BusSensor;
  
  // === RESET SENSOR MAX30100 AGAR TIDAK MENGHASILKAN NILAI 0 ===
  sensor.begin();
  sensor.setMode(MAX30100_MODE_SPO2_HR);
  sensor.setLedsCurrent(MAX30100_LED_CURR_50MA, MAX30100_LED_CURR_27_1MA);
  sensor.setLedsPulseWidth(MAX30100_SPC_PW_1600US_16BITS);
  sensor.setSamplingRate(MAX30100_SAMPRATE_100HZ);
  // =============================================================

  unsigned long warmup = millis();
  while (millis() - warmup < 2000) {
    sensor.update();
    uint16_t ir, red;
    while (sensor.getRawValues(&ir, &red)) {} // buang data warm-up
    delay(10);
  }

  // ---- REKAM 10 DETIK ----
  sampleCount = 0;
  recStart = millis();
  oledShow("RECORDING...", respName, "Tempel jari!", "10 detik...");

  while ((millis() - recStart) < (RECORD_SEC * 1000UL)) {
    sensor.update();
    uint16_t ir, red;
    while (sampleCount < MAX_SAMPLES && sensor.getRawValues(&ir, &red)) {
      irBuf[sampleCount]  = (float)ir;
      redBuf[sampleCount] = (float)red;
      sampleCount++;
    }
    delay(5);
  }
  Wire = BusOLED;

  computeFeatures();
  state     = IDLE;
  dataReady = false;

  if (sampleCount < MIN_SAMPLES || feat.bodyTemp <= 0 || feat.ambientTemp <= 0 ||
      feat.irMean < 10000 || feat.redMean < 10000) {
    server.send(422, "text/html", buildHTML("<div class='msg msg-err'>&#10060; Rekaman sensor tidak memenuhi kualitas minimum dan tidak disimpan.</div>"));
    return;
  }

  // Hitung turunan
  float tinggiM = respTinggi / 100.0;
  float bmi     = (tinggiM > 0) ? (respBerat / (tinggiM * tinggiM)) : 0;
  float spo2est = 110.0 - 25.0 * feat.ratioAC;
  if (spo2est > 100) spo2est = 100;
  if (spo2est < 80)  spo2est = 80;
  float hrEst = 60.0 + (feat.irMean > 0 ? (feat.irStd / feat.irMean) * 300.0 : 0);
  if (hrEst > 200) hrEst = 200;
  if (hrEst < 40)  hrEst = 40;

  // Tulis CSV format baru
  String newRow = respName + "," + respAge + "," + respGender + ",";
  newRow += String(respBerat, 1) + "," + String(respTinggi, 1) + "," + String(bmi, 2) + ",";
  newRow += String(respDiabetes ? 1 : 0) + "," + String(glucoseRef, 1) + "," + String(respLastMeal, 1) + ",";
  newRow += String(feat.bodyTemp, 2) + "," + String(feat.ambientTemp, 2) + ",";
  newRow += String(hrEst, 1) + "," + String(spo2est, 2) + ",";
  newRow += String(feat.irMean,  2) + "," + String(feat.irMin,  2) + "," + String(feat.irMax,  2) + ",";
  newRow += String(feat.irStd,  2) + "," + String(feat.irRMS,  2) + ",";
  newRow += String(feat.redMean, 2) + "," + String(feat.redMin, 2) + "," + String(feat.redMax, 2) + ",";
  newRow += String(feat.redStd,  2) + "," + String(feat.redRMS, 2) + ",";
  newRow += String(feat.ratioAC, 6) + "," + String(feat.ratioDC, 6) + ",";
  newRow += String(feat.samples) + "\n";

  // APPEND KE MEMORI INTERNAL (LittleFS)
  File dataFile = LittleFS.open(DATA_FILE, "a");
  if (dataFile) {
    dataFile.print(newRow);
    dataFile.close();
    dataReady = true;
  } else {
    Serial.println("Gagal menulis ke memori internal");
    state = IDLE;
    server.send(500, "text/html", buildHTML("<div class='msg msg-err'>&#10060; Data sensor gagal disimpan ke LittleFS.</div>"));
    return;
  }

  // Test-only gateway payload deliberately excludes names, demographics, and GlukosaRef.
  reportTestReadingToGateway(hrEst, spo2est);

  oledShow("SELESAI!", respName, "Gula: " + String(glucoseRef, 0) + " mg/dL", "Cek web!");

  String okMsg = "<div class='msg msg-ok'>&#10003; Data <b>" + htmlSafe(respName) + "</b> berhasil direkam! (" + String(sampleCount) + " samples)</div>";
  server.send(200, "text/html", buildHTML(okMsg));
}

void handleCSV() {
  File file = LittleFS.open(DATA_FILE, "r");
  if (!file) {
    server.send(500, "text/plain", "File data tidak ditemukan pada memori internal.");
    return;
  }
  
  // Fitur Stream ini akan langsung mengirimkan file dari memori ke browser
  server.sendHeader("Content-Disposition", "attachment; filename=sensable_dataset.csv");
  server.streamFile(file, "text/csv");
  file.close();
}

void handleReset() {
  // Buka file dengan mode "w" (write) untuk menimpa file yang sudah ada
  File file = LittleFS.open(DATA_FILE, "w");
  if (file) {
    file.print(CSV_HEADER);
    file.close();
  }
  dataReady = false;
  server.sendHeader("Location", "/");
  server.send(303);
}

// ===================== SETUP =====================
void setup() {
  Serial.begin(115200);

  BusOLED.begin(OLED_SDA, OLED_SCL);
  BusOLED.setClock(100000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED gagal!");
    while (1);
  }
  oledShow("SENS-Able v6.4", "Booting...", "Mounting FS...");

  // ==== INISIALISASI LITTLEFS ====
  if (!LittleFS.begin(false)) { // Jangan format otomatis agar data tidak hilang saat mount gagal
    Serial.println("Mounting LittleFS Gagal!");
    oledShow("ERROR!", "Memori Internal", "Gagal Diakses");
    while (1);
  }

  // Cek apakah file dataset sudah ada, jika belum, buat file dan isi dengan Header
  if (!LittleFS.exists(DATA_FILE)) {
    File file = LittleFS.open(DATA_FILE, "w");
    if (file) {
      file.print(CSV_HEADER);
      file.close();
      Serial.println("File dataset baru dibuat.");
    }
  }

  BusSensor.begin(MAX_SDA, MAX_SCL);
  BusSensor.setClock(400000);
  Wire = BusSensor;
  if (!sensor.begin()) {
    oledShow("ERROR!", "MAX30100 gagal");
    while (1);
  }
  sensor.setMode(MAX30100_MODE_SPO2_HR);
  sensor.setLedsCurrent(MAX30100_LED_CURR_50MA, MAX30100_LED_CURR_27_1MA);
  sensor.setLedsPulseWidth(MAX30100_SPC_PW_1600US_16BITS);
  sensor.setSamplingRate(MAX30100_SAMPRATE_100HZ);
  Wire = BusOLED;

  loadGatewayConfig();
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(AP_SSID, AP_PASS);
  String ip = WiFi.softAPIP().toString();
  Serial.println("AP IP: " + ip);

  server.on("/",       HTTP_GET,  handleRoot);
  server.on("/record", HTTP_POST, handleRecord);
  server.on("/csv",    HTTP_GET,  handleCSV);
  server.on("/reset",  HTTP_POST, handleReset);
  server.begin();

  oledShow("SENS-Able SIAP", "WiFi: SENS-Able", "Pass: sensable123", "IP: " + ip);
  Serial.println("Server started!");
}

// ===================== LOOP =====================
void loop() {
  server.handleClient();                     
  handleGatewaySerialProvisioning();

  if (state == IDLE) {
    Wire = BusSensor;
    sensor.update();
    Wire = BusOLED;
  }

  delay(10);
}
