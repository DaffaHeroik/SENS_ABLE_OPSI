# SENS-Able AI Final — Physical Device Workflow

Folder ini adalah pusat kode AI untuk **alat fisik SENS-Able**. Isinya dipisahkan dari pipeline raw-data umum dan dari firmware collector agar tidak membingungkan fungsi setiap file.

> Status saat ini: **Python model V0.1 sudah berjalan; ESP32 inference belum diaktifkan.** Jangan memasukkan model ke alat sebelum preprocessing, format model, dan pengujian perangkat diverifikasi.

## Struktur

| Folder | Fungsi |
|---|---|
| `config/` | Kontrak target, urutan fitur, normalisasi, dan parameter model |
| `training/` | Training model dan pembuatan artifact offline |
| `improvement/` | Eksperimen tuning dan feature ablation yang tidak boleh menimpa model stabil |
| `evaluation/` | Evaluasi cross-validation, metrik, residual, dan pemeriksaan leakage |
| `deployment_esp32/` | Kerangka preprocessing/inference untuk Arduino/ESP32 |
| `artifacts/` | Model yang sudah dibekukan beserta metadata dan manifest |

## Kontrak model fisik

Input model adalah fitur yang benar-benar tersedia dari collector ESP32 MAX30102 dan sensor suhu. Target penelitian adalah `GlukosaRef` dari glucometer, tetapi target tersebut **tidak dikirim sebagai input model** pada perangkat.

Urutan input V0.1:

```text
Usia, Berat_kg, Tinggi_cm, BMI, TerakhirMakan_jam,
SuhuTubuh, SuhuAmbient, HR_est, SpO2_est,
IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS,
RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS,
Ratio_AC, Ratio_DC, Samples
```

`SubjectID`, `Nama`, `Gender`, `Diabetes`, `GlukosaRef`, dan flag imputasi suhu tidak boleh masuk ke input model.

## Alur kerja

```text
Collector ESP32 MAX30102
        ↓
CSV sesi pengukuran
        ↓
Python cleaning dan validasi
        ↓
Training/improvement model
        ↓
Evaluasi GroupKFold by SubjectID
        ↓
Artifact model + metadata
        ↓
Konversi embedded setelah disetujui
        ↓
Inference pada ESP32
```

## Perintah utama

Jalankan dari root repository:

```bash
python3 scripts/prepare_dataset.py
python3 ai_final/training/train_final_model.py
python3 ai_final/improvement/run_improvement_experiments.py
python3 ai_final/evaluation/evaluate_final_model.py
python3 ai_final/evaluation/plot_final_results.py
python3 -m unittest discover -s tests -v
```

## Aturan versi

`V0.1` adalah model eksploratif yang sudah dibuat. Eksperimen improvement disimpan sebagai hasil kandidat dan tidak otomatis menggantikan V0.1. Model baru hanya boleh disebut `V0.2` jika evaluasinya lebih baik secara konsisten, tidak mengalami leakage, dan konfigurasi serta artifact-nya sudah direview.

## Batasan alat fisik

File `.joblib` dapat digunakan untuk inspeksi Python, tetapi tidak dapat langsung dijalankan oleh Arduino. Deployment ESP32 memerlukan format embedded, preprocessing yang sama, serta pengukuran RAM, flash, waktu inferensi, dan hasil prediksi pada sesi baru. Jika syarat tersebut belum dipenuhi, laporan OPSI harus menyebut TinyML sebagai pengembangan lanjutan.
