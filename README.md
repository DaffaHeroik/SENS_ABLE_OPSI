# SENS-Able

**Smart Health Monitor Inklusif berbasis AI dengan Audio, Visual dan Vibrasi yang Ramah Bagi Pengguna Disabilitas**

## Tentang

SENS-Able adalah alat pemantau kesehatan inklusif yang dirancang untuk penyandang disabilitas (tunanetra dan tunarungu). Alat ini mengukur:

- **Glukosa darah** (via sensor MAX30102 PPG)
- **Detak jantung** (via sensor MAX30102 PPG)
- **Suhu tubuh** (via sensor MLX90614 infrared)

Dengan 3 kanal output:
- **Visual** (OLED 0.96")
- **Audio** (Speaker PAS-0158)
- **Getaran** (Vibromotor SEN-0085)

## Tim

**AntroOptic Team**
- Muhammad Daffa Ramadhan
- Aira Cantika Putri

**Madrasah Aliyah Negeri 2 Kota Bima**
Kota Bima, Nusa Tenggara Barat — 2026

## Hardware

| Komponen | Fungsi |
|---|---|
| ESP32 DevKit | Mikrokontroler utama |
| MAX30102 | Sensor PPG (detak jantung + estimasi glukosa) |
| MLX90614 | Sensor suhu tubuh infrared |
| OLED 0.96" I2C | Display visual |
| PAS-0158 | Speaker (audio feedback) |
| SEN-0085 | Motor vibrasi (haptic feedback) |

## Struktur Repository

```
SENS_ABLE_OPSI/
├── README.md              # File ini
├── train.py               # Klasifikasi baseline PIMA → SENS-Able
├── train_v1.py            # Arsip: training dari data sendiri
├── train_v2.py            # Arsip: eksperimen gabungan
├── scripts/
│   ├── prepare_dataset.py # Raw → processed, deduplikasi, audit kualitas
│   └── validate_glucometer.py # Validasi regresi terhadap GlukosaRef
├── requirements.txt       # Dependensi Python
├── data/
│   ├── raw/               # Salinan input asli, tidak diubah
│   ├── processed/         # Dataset hasil pembersihan dan laporan kualitas
│   └── README.md          # Kontrak data dan catatan privasi
├── model.pkl              # Artifact lokal hasil training; tidak ditrack
├── report.json            # Laporan baseline klasifikasi
├── reports/
│   └── glucometer_validation.json # Hasil validasi terhadap glucometer
├── docs/
│   ├── proposal.pdf       # Proposal penelitian
│   ├── chat_history.md    # History diskusi pengolahan data
│   └── planning.md        # Planning & konfirmasi plan
└── .gitignore
```

## Cara Menjalankan

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/prepare_dataset.py
python3 train.py
python3 scripts/validate_glucometer.py
```

`prepare_dataset.py` membaca seluruh file di `data/raw/`, tidak mengubahnya, lalu membuat dataset processed. `validate_glucometer.py` menggunakan `GlukosaRef` sebagai target/referensi gula darah dari glucometer, bukan sebagai fitur input. Dengan demikian tidak terjadi kebocoran label dari nilai glucometer ke prediksi model.

## Strategi Training

| | Training | Validasi |
|---|---|---|
| **Dataset** | PIMA Indians Diabetes (public) | SENS-Able (data sendiri) |
| **Sampel** | 768 | Dataset processed; lihat `data/processed/quality_report.json` |
| **Fitur** | Age, BMI, Glucose | Usia, BMI, GlukosaRef (baseline klasifikasi lama) |

Tabel di atas menjelaskan baseline klasifikasi diabetes yang masih dipertahankan untuk perbandingan historis. Untuk **model estimasi gula darah**, gunakan alur regresi berikut.

### Validasi Regresi Glukosa dengan Glukometer

Validasi gula darah dilakukan secara terpisah melalui `scripts/validate_glucometer.py`. Kolom `GlukosaRef` diperlakukan sebagai **target referensi glucometer dalam mg/dL**. Fitur input hanya berasal dari data demografi dan sinyal sensor; `GlukosaRef`, `Nama`, `SubjectID`, dan `Diabetes` tidak digunakan sebagai fitur. Evaluasi menggunakan `GroupKFold` berdasarkan `SubjectID` dan melaporkan MAE, RMSE, serta R². Hasilnya bersifat eksploratif dan belum merupakan validasi klinis.

Model dilatih pada data publik (PIMA), lalu divalidasi pada data sensor sendiri. Strategi ini lebih valid karena:
- Data training terpisah dari data validasi
- Model belajar dari pola umum diabetes (768 sampel)
- Data sensor sendiri jadi test set nyata
- Tidak overfitting pada data kecil

## Hasil Baseline Klasifikasi

> Catatan penting: skor akurasi di bawah bukan bukti akurasi deteksi diabetes. Dataset memiliki hanya satu label positif, sehingga recall/F1 dan confusion matrix harus diprioritaskan.


### Training (PIMA, 5-fold CV)
- Accuracy: 75.1% ± 4.9%
- F1 Score: 0.691 ± 0.043

### Validasi (SENS-Able, 33 sampel)
- Accuracy: 90.9%
- True Negative: 30
- False Positive: 2
- False Negative: 1
- True Positive: 0

### Feature Importance
1. Glucose (0.4319)
2. BMI (0.3066)
3. Age (0.2615)

## Indikator Keberhasilan (sesuai Proposal)

| Indikator | Target | Status |
|---|---|---|
| MAE HR | < 3 bpm | Perlu uji kalibrasi |
| MAE Suhu | < 0.3°C | Perlu uji kalibrasi |
| MAE Glukosa | < 15 mg/dL | Perlu uji kalibrasi |
| Skor Usability | ≥ 4 (Likert 1-5) | Perlu kuesioner |
| Mandiri setelah 1 demo | ≥ 80% | Perlu observasi |

## Langkah Selanjutnya

1. ✅ ~~Pengumpulan data sensor~~ (33 sampel)
2. ✅ ~~Training model~~ (PIMA → train, SENS-Able → validate)
3. ✅ Pembersihan dataset dan pemisahan `GlukosaRef` sebagai referensi glucometer
4. 🔲 Kalibrasi sensor vs alat standar (target MAE HR<3bpm, Suhu<0.3°C, Glukosa<15mg/dL)
5. 🔲 Uji 15 responden (5 tunanetra, 5 tunarungu, 5 non-disabilitas)
6. 🔲 Kuesioner usability Likert 1-5 (target skor ≥4)
7. 🔲 Konversi model ke TensorFlow Lite
8. 🔲 Deploy ke ESP32 via TinyML
9. 🔲 Penyusunan laporan akhir

📋 Lihat [docs/planning.md](docs/planning.md) untuk detail lengkap & checklist.

## Catatan Privasi dan Keselamatan

File di `data/raw/` merupakan arsip input yang dapat mengandung identitas dan data kesehatan. Jangan push repository ini sebagai public sebelum semua identitas dianonimkan dan izin publikasi dipastikan. Output SENS-Able adalah prototipe penelitian dan bukan alat diagnosis atau pengganti pemeriksaan medis.

## License

Penelitian untuk MAN 2 Kota Bima — Tahun 2026
