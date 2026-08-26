# Evaluation

Folder ini menyimpan evaluasi model yang akan menjadi sumber angka untuk laporan dan pengujian alat.

```bash
python3 ai_final/evaluation/evaluate_final_model.py
python3 ai_final/evaluation/plot_final_results.py
```

`evaluate_final_model.py` memakai 5-fold GroupKFold berdasarkan `SubjectID`, menyimpan metrik di `ai_final/evaluation/evaluation_v0_1.json`, dan menyimpan prediksi out-of-fold di `ai_final/evaluation/predictions_v0_1.csv`.

Angka laporan harus diambil dari prediksi out-of-fold, bukan dari prediksi training pada data yang sama. Jika ada perbedaan antara dua script, gunakan evaluator yang memakai kontrak model V0.1 dan dokumentasikan penyebab perbedaannya sebelum menulis laporan.
