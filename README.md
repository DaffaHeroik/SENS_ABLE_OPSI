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
SENS_ABLE/
├── README.md              # File ini
├── train.py               # Training script v3 (PIMA → train, SENS-Able → validate)
├── train_v1.py            # Training script v1 (data sendiri saja)
├── train_v2.py            # Training script v2 (gabungan PIMA + SENS-Able)
├── model.pkl              # Model terlatih (Random Forest)
├── report.json            # Laporan training
├── data/
│   └── sensable_final.csv # Dataset bersih (33 sampel, 30 responden)
├── docs/
│   ├── proposal.pdf       # Proposal penelitian
│   └── chat_history.md    # History diskusi pengolahan data
└── .gitignore
```

## Cara Training

```bash
pip install scikit-learn pandas numpy
python3 train.py
```

## Strategi Training

| | Training | Validasi |
|---|---|---|
| **Dataset** | PIMA Indians Diabetes (public) | SENS-Able (data sendiri) |
| **Sampel** | 768 | 33 |
| **Fitur** | Age, BMI, Glucose | Usia, BMI, GlukosaRef |

Model dilatih pada data publik (PIMA), lalu divalidasi pada data sensor sendiri. Strategi ini lebih valid karena:
- Data training terpisah dari data validasi
- Model belajar dari pola umum diabetes (768 sampel)
- Data sensor sendiri jadi test set nyata
- Tidak overfitting pada data kecil

## Hasil Training

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

1. Tambah data SENS-Able (target 100+ sampel)
2. Uji kalibrasi sensor vs alat standar
3. Kuesioner usability (Likert 1-5)
4. Konversi model ke TensorFlow Lite
5. Deploy ke ESP32 via TinyML
6. Uji responden (5 tunanetra, 5 tunarungu, 5 non-disabilitas)

## License

Penelitian untuk MAN 2 Kota Bima — Tahun 2026
