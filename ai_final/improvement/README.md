# Model Improvement Experiments

Eksperimen di folder ini bertujuan mencari perbaikan yang masuk akal tanpa memanipulasi data. Tidak ada eksperimen yang boleh memasukkan `GlukosaRef` sebagai fitur, membuat data sintetis, atau menghapus prediksi buruk setelah melihat hasil.

## Eksperimen tersedia

```bash
python3 ai_final/improvement/run_improvement_experiments.py
python3 ai_final/improvement/run_feature_ablation.py
python3 ai_final/improvement/robust_model_search.py
```

Output:

- `reports/model_improvement_experiment.json` berisi nested GroupKFold untuk tuning Random Forest, Random Forest dengan feature selection, dan Extra Trees.
- `reports/feature_ablation_experiment.json` berisi perbandingan kelompok fitur.
- `reports/robust_model_search.json` berisi pencarian fitur turunan sensor, Gradient Boosting, dan Ridge dengan nested GroupKFold.

Nested tuning menggunakan outer GroupKFold untuk skor uji dan inner GroupKFold untuk pemilihan parameter. Hasil terbaik hanya merupakan kandidat eksploratif. Eksperimen tidak otomatis mengganti `ai_final/artifacts/glucose_model_v0_1.joblib`.

## Aturan promosi ke V0.2

Kandidat hanya boleh dipromosikan jika performanya mengalahkan baseline dan V0.1 secara konsisten, daftar fitur tetap tersedia di alat fisik, hasil tidak berubah drastis antar-fold, dan artifact dapat direproduksi. Jika hasil hanya lebih baik pada satu konfigurasi atau satu fold, simpan sebagai eksperimen dan jangan sebut sebagai model final.
