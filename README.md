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
├── configs/
│   └── glucose_model_v0_1.json # Kontrak fitur, target, dan parameter model
├── scripts/
│   ├── prepare_dataset.py # Raw → processed, deduplikasi, audit kualitas
│   ├── validate_glucometer.py # Validasi regresi terhadap GlukosaRef
│   ├── compare_glucose_models.py # Banding baseline dan model regresi
│   └── plot_model_results.py # Buat grafik actual-vs-predicted dan residual
├── models/
│   ├── glucose_model_v0_1.joblib # Artifact RF eksploratif
│   └── glucose_model_v0_1_metadata.json # Metadata artifact
├── requirements.txt       # Dependensi Python
├── firmware/
│   └── SENS_ABLE_Data_Collector/ # Kode Arduino/ESP32 pengambil data
├── ai_final/              # Pusat AI untuk alat fisik SENS-Able
│   ├── training/          # Training artifact V0.1
│   ├── improvement/       # Tuning, ablation, robust search, dan dataset publik
│   ├── evaluation/        # Evaluasi dan prediksi out-of-fold
│   └── deployment_esp32/  # Kontrak input dan scaffold inference
├── data/
│   ├── raw/               # Salinan input asli, tidak diubah
│   ├── processed/         # Dataset hasil pembersihan dan laporan kualitas
│   └── README.md          # Kontrak data dan catatan privasi
├── model.pkl              # Artifact lokal hasil training; tidak ditrack
├── report.json            # Laporan baseline klasifikasi
├── reports/
│   ├── glucometer_validation.json # Hasil validasi terhadap glucometer
│   ├── model_comparison.json # Hasil perbandingan V0.1
│   ├── external_public_ppg_experiment.json # Uji augmentasi dataset PPG publik
│   ├── modeling_v0_1_summary.md # Ringkasan faktual untuk laporan
│   ├── MANIFEST_v0_1.sha256 # Hash dataset/model/laporan V0.1
│   └── figures/             # Grafik untuk laporan penelitian
├── docs/
│   ├── proposal.pdf       # Proposal penelitian
│   ├── model_building_guide.md # Panduan pembuatan dan penggunaan model
│   ├── ml_modeling_plan_summary.md # Planning modeling lengkap
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
python3 scripts/compare_glucose_models.py
python3 scripts/plot_model_results.py
python3 scripts/validate_glucometer.py
python3 ai_final/training/train_final_model.py
python3 ai_final/evaluation/evaluate_final_model.py
python3 ai_final/improvement/run_improvement_experiments.py
python3 ai_final/improvement/run_feature_ablation.py
python3 ai_final/improvement/robust_model_search.py
python3 -m unittest discover -s tests -v
```

`prepare_dataset.py` membaca seluruh file di `data/raw/`, tidak mengubahnya, lalu membuat dataset processed. `compare_glucose_models.py` membaca kontrak fitur dari `configs/glucose_model_v0_1.json`, membandingkan baseline/Linear Regression/Random Forest dengan GroupKFold, menyimpan laporan dan artifact model eksploratif. `validate_glucometer.py` menggunakan `GlukosaRef` sebagai target/referensi gula darah dari glucometer, bukan sebagai fitur input. Dengan demikian tidak terjadi kebocoran label dari nilai glucometer ke prediksi model.

Eksperimen dataset publik dijalankan terpisah melalui `ai_final/improvement/external_public_ppg_experiment.py`. Data publik tidak dimasukkan ke `data/processed/` dan tidak mengubah model V0.1. Script hanya menguji apakah data PPG publik membantu ketika ditambahkan ke data training, sementara data uji SENS-Able tetap dipisahkan berdasarkan `SubjectID`.

## Tahap Pemodelan V0.1

| Komponen | Lokasi |
|---|---|
| Kontrak fitur dan parameter | `configs/glucose_model_v0_1.json` |
| Script perbandingan model | `scripts/compare_glucose_models.py` |
| Script grafik | `scripts/plot_model_results.py` |
| Model exploratory artifact | `models/glucose_model_v0_1.joblib` |
| Metadata model | `models/glucose_model_v0_1_metadata.json` |
| Laporan model | `reports/model_comparison.json` dan `reports/modeling_v0_1_summary.md` |
| Hash untuk reproducibility | `reports/MANIFEST_v0_1.sha256` |
| Panduan penggunaan | `docs/model_building_guide.md` |

Model V0.1 menggunakan `GlukosaRef` sebagai target glucometer dan `GroupKFold` berdasarkan `SubjectID`. Kandidat terbaik sementara adalah `RandomForestRegressor` dengan MAE 22,5716 mg/dL, tetapi statusnya masih eksploratif dan bukan validasi klinis. Folder `ai_final/` adalah pusat kode AI untuk alat fisik, termasuk training, evaluasi, eksperimen improvement, dan kontrak input ESP32.

## Strategi Training

Eksperimen PIMA yang masih ada di root repository adalah **baseline klasifikasi historis** dan bukan sumber training untuk model glukosa final. Model penelitian yang dipakai sekarang adalah regresi langsung terhadap referensi glucometer `GlukosaRef` menggunakan data SENS-Able yang telah diproses.

### Validasi Regresi Glukosa dengan Glukometer

Validasi gula darah dilakukan secara terpisah melalui `scripts/validate_glucometer.py`. Kolom `GlukosaRef` diperlakukan sebagai **target referensi glucometer dalam mg/dL**. Fitur input hanya berasal dari data demografi dan sinyal sensor; `GlukosaRef`, `Nama`, `SubjectID`, dan `Diabetes` tidak digunakan sebagai fitur. Evaluasi menggunakan `GroupKFold` berdasarkan `SubjectID` dan melaporkan MAE, RMSE, serta R². Hasilnya bersifat eksploratif dan belum merupakan validasi klinis.

### Uji Dataset Publik

Dataset publik PPG dapat dipakai sebagai eksperimen augmentasi atau benchmark, tetapi tidak boleh dianggap identik dengan sensor MAX30102 SENS-Able. Karena perbedaan perangkat, panjang sinyal, populasi, dan cara memperoleh label, hasilnya dilaporkan terpisah. Validasi final SENS-Able tetap menggunakan `GroupKFold` berdasarkan `SubjectID` dan `GlukosaRef` tidak pernah menjadi fitur.

## Hasil Baseline Klasifikasi

> Bagian ini adalah hasil historis dari pipeline klasifikasi lama. Fokus penelitian yang direkomendasikan sekarang adalah estimasi regresi terhadap `GlukosaRef`, bukan klasifikasi diabetes.

> Catatan penting: skor akurasi di bawah bukan bukti akurasi deteksi diabetes. Dataset memiliki hanya satu label positif, sehingga recall/F1 dan confusion matrix harus diprioritaskan.


### Training (PIMA, 5-fold CV)
- Accuracy: 75.1% ± 4.9%
- F1 Score: 0.691 ± 0.043

### Validasi Klasifikasi Historis (SENS-Able, 33 sesi sebelum pemulihan suhu)
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

1. ✅ Pengumpulan dan penggabungan data sensor (40 sesi processed dari 46 sesi unik)
2. ✅ Pipeline training/validasi terpisah (PIMA → train, SENS-Able → evaluasi lama)
3. ✅ Pembersihan dataset, pemulihan suhu nol secara transparan, dan pemisahan `GlukosaRef` sebagai referensi glucometer
4. 🔲 Kalibrasi sensor vs alat standar (target MAE HR<3bpm, Suhu<0.3°C, Glukosa<15mg/dL)
5. 🔲 Uji 15 responden (5 tunanetra, 5 tunarungu, 5 non-disabilitas)
6. 🔲 Kuesioner usability Likert 1-5 (target skor ≥4)
7. 🔲 Evaluasi terpisah dengan dataset publik yang modalitasnya sesuai; jangan mencampurkan tanpa uji domain shift
8. 🔲 Konversi model ke TensorFlow Lite
9. 🔲 Deploy ke ESP32 via TinyML
10. 🔲 Penyusunan laporan akhir

📋 Lihat [docs/planning.md](docs/planning.md) untuk detail lengkap & checklist.

## Catatan Privasi dan Keselamatan

File di `data/raw/` merupakan arsip input yang dapat mengandung identitas dan data kesehatan. Jangan push repository ini sebagai public sebelum semua identitas dianonimkan dan izin publikasi dipastikan. Output SENS-Able adalah prototipe penelitian dan bukan alat diagnosis atau pengganti pemeriksaan medis.

## License

Penelitian untuk MAN 2 Kota Bima — Tahun 2026
