# Ringkasan Eksperimen Perbaikan Model SENS-Able

**Tanggal:** 26 Agustus 2026
**Dataset:** 40 sesi, 32 SubjectID
**Target:** `GlukosaRef` glucometer
**Validasi:** nested 5-fold outer GroupKFold dan 4-fold inner GroupKFold berdasarkan `SubjectID`
**Data sintetis:** tidak digunakan

## Hasil Perbandingan

| Kandidat | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² | Keputusan |
|---|---:|---:|---:|---:|---|
| MeanBaseline | 24,2937 | 29,0975 | 23,9062 | -0,0856 | Pembanding |
| Random Forest V0.1 | 22,5716 | 27,0552 | 20,5580 | 0,0614 | Model fisik saat ini |
| Tuned Random Forest | 23,2412 | 27,6333 | 19,8324 | 0,0209 | Tidak dipromosikan |
| Tuned RF + feature selection | **21,4932** | **26,3387** | **18,0284** | **0,1105** | Kandidat eksperimen |
| Tuned Extra Trees | 22,0374 | 26,8809 | 20,9140 | 0,0735 | Kandidat eksperimen |

Feature selection menghasilkan penurunan MAE sekitar 1,08 mg/dL dibandingkan V0.1, atau sekitar 4,8% secara relatif terhadap MAE V0.1. Namun, jumlah data kecil dan fitur terpilih tidak konsisten antar-fold: nilai `k` yang dipilih adalah 8, 12, 5, 12, dan 5. Karena itu, model tersebut belum dipromosikan menjadi model fisik final.

## Hasil Feature Ablation

Eksperimen ablation dengan Random Forest V0.1 menunjukkan:

| Kelompok fitur | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² | Arti |
|---|---:|---:|---:|---:|---|
| Semua fitur | 22,5716 | 27,0552 | 20,5580 | 0,0614 | Model fisik V0.1 |
| PPG saja | 28,2246 | 34,1112 | 26,6946 | -0,4919 | Sinyal saja belum cukup pada data ini |
| PPG + suhu/vital | 26,8472 | 31,2955 | 23,0122 | -0,2558 | Tambahan fisiologi belum cukup |
| Context saja | 18,7840 | 24,3522 | 14,7891 | 0,2396 | Bukan model sensor; perlu interpretasi hati-hati |

Kelompok `context_only` berisi usia, berat, tinggi, BMI, dan waktu sejak makan. Hasilnya tidak boleh disebut bukti sensor MAX30102 lebih akurat karena kelompok tersebut tidak memakai sinyal PPG. Nilai tersebut lebih tepat diperlakukan sebagai analisis tambahan dan indikasi kemungkinan confounding pada dataset kecil.

## Keputusan

Model fisik resmi tetap **RandomForestRegressor V0.1** dengan seluruh fitur yang tersedia di collector. Kandidat tuned RF + feature selection disimpan sebagai eksperimen dan tidak menggantikan V0.1. Promosi ke V0.2 memerlukan data lebih banyak, fitur yang stabil, validasi pada sesi/subject baru, dan keputusan fitur yang dapat diimplementasikan secara konsisten di ESP32.

## Cara Menjalankan

```bash
python3 ai_final/improvement/run_improvement_experiments.py
python3 ai_final/improvement/run_feature_ablation.py
```

Output detail:

- `reports/model_improvement_experiment.json`
- `reports/feature_ablation_experiment.json`

## Larangan untuk Laporan

Jangan menulis “akurasi naik menjadi 21,49%”. Angka 21,4932 adalah MAE dalam mg/dL, bukan persentase akurasi. Jika kandidat disebutkan, tulis sebagai eksperimen nested yang masih eksploratif dan jelaskan bahwa model belum memenuhi validasi klinis.

## Pencarian Robust Fitur dan Model Tambahan

Pencarian nested tambahan menguji enam fitur turunan sensor (`IR_Range`, `RED_Range`, `IR_CV`, `RED_CV`, `IR_RED_Mean_Ratio`, dan `IR_RED_Std_Ratio`) bersama Random Forest, Gradient Boosting, dan Ridge. Hasilnya tidak mengalahkan V0.1:

| Kandidat | MAE (mg/dL) | RMSE (mg/dL) | R² |
|---|---:|---:|---:|
| Tuned Random Forest + fitur turunan | 23,8180 | 28,1903 | -0,0190 |
| Tuned Gradient Boosting + fitur turunan | 23,7454 | 28,6622 | -0,0534 |
| Tuned Ridge + fitur dasar | 26,5771 | 30,6880 | -0,2075 |

Dengan demikian, penambahan fitur turunan tersebut tidak dipromosikan. Hasil ini penting untuk laporan karena menunjukkan bahwa tidak semua fitur tambahan meningkatkan model. Model fisik tetap V0.1, sedangkan `TunedRandomForestWithFeatureSelection` disimpan sebagai kandidat eksperimen dengan catatan ketidakstabilan fitur.
