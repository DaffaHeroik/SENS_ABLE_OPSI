# SENS-Able

**Smart Health Monitor Inklusif berbasis AI dengan Audio, Visual dan Vibrasi yang Ramah Bagi Pengguna Disabilitas**

## Tentang

SENS-Able adalah alat pemantau kesehatan inklusif yang dirancang untuk penyandang disabilitas (tunanetra dan tunarungu). Alat ini mengukur:

- **Glukosa darah** (via sensor MAX30102 PPG + AI prediction)
- **Detak jantung** (via sensor MAX30102 PPG)
- **Suhu tubuh** (via sensor MLX90614 infrared)

Dengan 3 kanal output:
- **Visual** (OLED 0.96")
- **Audio** (Speaker/Buzzer - GPIO 23)
- **Getaran** (Vibromotor - GPIO 26)

## Tim

**AntroOptic Team**
- Muhammad Daffa Ramadhan
- Aira Cantika Putri

**Madrasah Aliyah Negeri 2 Kota Bima**
Kota Bima, Nusa Tenggara Barat — 2026

## 🚀 Fitur Utama

### Embedded AI Glucose Prediction
- Model: Random Forest Regressor (200 trees)
- Input: 22 fitur dari sensor PPG
- Output: Prediksi glukosa dalam mg/dL
- Status: Normal, Pre-diabetic, Diabetic, Low (Hypoglycemia)

### Accessibility Features
- **Audio Feedback**: Pattern beep berbeda untuk setiap status
  - 1 beep: Normal
  - 2 beep: Pre-diabetic
  - 3 beep panjang: Diabetic
  - 5 beep cepat: Low (Hypoglycemia)
- **Vibration Feedback**: Pattern getaran untuk tunarungu
- **OLED Display**: Tampilan hasil prediksi yang jelas

## 📊 Status Hardware

| Komponen | Pin | Status |
|---|---|---|
| ESP32 DevKit | - | ✅ Terpasang |
| MAX30102 (PPG) | SDA=18, SCL=19 | ✅ Terpasang |
| MLX90614 (Suhu IR) | SDA=21, SCL=22 | ✅ Terpasang |
| OLED 0.96" SSD1306 | SDA=21, SCL=22 | ✅ Terpasang |
| Speaker/Buzzer | GPIO 23 | ✅ Terpasang |
| Vibromotor | GPIO 26 | ❓ Belum |

## 📁 Struktur Repository

```
SENS_ABLE_OPSI/
├── firmware/                              # ESP32 Arduino sketches
│   ├── SENS_ABLE_Glucose_Predictor.ino   # Firmware utama dengan AI inference
│   ├── SENS_ABLE_Data_Collector_v6_4.ino # Data collector untuk training
│   ├── SENS_ABLE_Gateway_Client.ino      # Gateway untuk multiple collectors
│   ├── model_glucose_inference.h          # Model AI (200 decision trees)
│   └── model_contract_v0_1.h             # Kontrak fitur model
│
├── scripts/                               # Python ML Pipeline
│   ├── prepare_dataset.py                 # Pembersihan data
│   ├── train_final_model.py               # Training model
│   ├── validate_glucometer.py             # Validasi prediksi
│   ├── export_model_to_cpp.py             # Convert model ke C++
│   └── ... (30+ scripts lainnya)
│
├── data/
│   ├── raw/                              # Data original (CSV, XLSX, PDF)
│   └── processed/                        # Data bersih untuk training
│       └── sensable_final.csv            # 40 sampel, 32 responden
│
├── web/                                  # Dashboard monitoring
│   ├── App.tsx                           # React frontend
│   ├── gateway.ts                        # Backend gateway
│   ├── schema.ts                         # Database schema
│   └── migrations/                       # SQL migrations
│
├── results/                              # Hasil evaluasi
│   ├── glucose_model_v0_1.json           # Metadata model
│   ├── evaluation_v0_1.json              # Metrik evaluasi
│   └── glucometer_validation.json        # Validasi dengan glukometer
│
└── docs/                                 # Dokumentasi
    ├── SENS-Able Project Memory.md
    ├── planning.md
    └── ... (20+ dokumen lainnya)
```

## 🤖 Cara Upload Firmware

### Prasyarat
1. Install Arduino IDE
2. Install ESP32 board: `Boards Manager → esp32 by Espressif`
3. Install libraries:
   - `Adafruit SSD1306`
   - `Adafruit GFX`
   - `MAX30100_PulseOximeter`

### Upload Glucose Predictor
```bash
1. Buka: firmware/SENS_ABLE_Glucose_Predictor.ino
2. Pilih Board: ESP32 Dev Module
3. Pilih Port: USB-COM yang terhubung
4. Klik Upload
```

### Upload Data Collector (untuk training)
```bash
1. Buka: firmware/SENS_ABLE_Data_Collector_v6_4.ino
2. Pilih Board: ESP32 Dev Module
3. Upload
```

## 🧪 Cara Penggunaan

### Mode Glucose Predictor
1. Colokkan ESP32 via USB atau powerbank
2. Letakkan jari di sensor MAX30102
3. Tunggu 10 detik untuk pengukuran
4. Baca hasil di OLED:
   ```
   === GLUCOSE ===
   105.3 mg/dL
   Pre-diabetic
   Temp: 33.2C
   ```
5. Dengarkan audio feedback (beep pattern)
6. Rasakan vibrasi feedback (jika terpasang)

### Mode Data Collector
1. Hubungkan HP ke WiFi `SENS-Able` (password: sensable123)
2. Buka browser: `http://192.168.4.1`
3. Isi data responden (nama, usia, berat, dll)
4. Klik "Mulai Rekam" dan letakkan jari
5. Download hasil CSV untuk training

## 📊 Hasil Model AI

### Model: Random Forest Regressor v0.1
- **Training**: 40 sampel, 32 responden unik
- **Validasi**: 5-fold GroupKFold by SubjectID
- **Fitur**: 22 fitur dari sensor PPG + data demografis

### Metrik Evaluasi
| Metrik | Nilai | Target |
|---|---|---|
| MAE | 22.57 mg/dL | < 15 mg/dL |
| RMSE | 27.06 mg/dL | - |
| R² | 0.0614 | > 0.5 |

### Status Prediksi
| Status | Rentang | Feedback |
|---|---|---|
| Normal | 70-99 mg/dL | 1 beep pendek |
| Pre-diabetic | 100-125 mg/dL | 2 beep |
| Diabetic | ≥126 mg/dL | 3 beep panjang |
| Low (Hypoglycemia) | <70 mg/dL | 5 beep cepat (alarm) |

## 🎯 Indikator Keberhasilan

| Indikator | Target | Status |
|---|---|---|
| MAE HR | < 3 bpm | ⏳ Perlu kalibrasi |
| MAE Suhu | < 0.3°C | ⏳ Perlu kalibrasi |
| MAE Glukosa | < 15 mg/dL | ⚠️ 22.57 (perlu improve) |
| Skor Usability | ≥ 4 (Likert 1-5) | ⏳ Perlu uji responden |
| Mandiri setelah 1 demo | ≥ 80% | ⏳ Perlu observasi |

## 📋 Langkah Selanjutnya

### Prioritas Tinggi
1. ✅ Firmware dengan AI inference
2. ⏳ Upload firmware ke ESP32
3. ⏳ Test prediksi glucose di OLED
4. ⏳ Kalibrasi sensor vs glukometer nyata

### Prioritas Menengah
5. ⏳ Pasang vibromotor untuk feedback getaran
6. ⏳ Uji 15 responden (5 tunanetra, 5 tunarungu, 5 non-disabilitas)
7. ⏳ Kuesioner usability Likert 1-5

### Prioritas Rendah
8. ⏳ Optimasi model (tambah data, kurangi MAE)
9. ⏳ Deploy web dashboard
10. ⏳ Penyusunan laporan akhir

## 🛒 Komponen yang Dibutuhkan

### Sudah Terpasang
- [x] ESP32 DevKit
- [x] MAX30102 (PPG Sensor)
- [x] MLX90614 (IR Temperature)
- [x] OLED 0.96" SSD1306
- [x] Buzzer/Speaker (GPIO 23)

### Perlu Ditambah
- [ ] Vibromotor (GPIO 26)
- [ ] Transistor 2N2222 (untuk driver vibromotor)
- [ ] Resistor 1kΩ

## 📚 Dokumentasi

- [Planning & Timeline](docs/planning.md)
- [Chat History](docs/chat_history.md)
- [Proposal Penelitian](docs/proposal.pdf)
- [Project Memory](docs/SENS-Able%20Project%20Memory.md)
- [Repository Review](docs/SENS%20ABLE%20Repository%20Review.md)

## ⚠️ Catatan Penting

- **Data Privacy**: File `data/raw/` berisi nama asli + data kesehatan. Pastikan repository private atau anonymize sebelum push public.
- **Status Eksploratif**: Model ini masih eksploratif, bukan validasi klinis. Jangan klaim sebagai alat medis.
- **Kalibrasi Diperlukan**: Hasil prediksi perlu divalidasi dengan glukometer nyata sebelum digunakan.

## 📄 License

Penelitian untuk MAN 2 Kota Bima — Tahun 2026

---

**Dikembangkan dengan ❤️ oleh AntroOptic Team**
