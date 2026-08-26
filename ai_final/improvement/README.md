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

## Eksperimen dataset PPG publik

Dataset publik yang paling dekat dengan SENS-Able yang berhasil ditemukan adalah **Photoplethysmography (PPG) Dataset for Non-Invasive Blood Glucose Monitoring** dari Zenodo. Dataset ini berisi 125 rekaman dari 24 subjek, enam kanal PPG pada 530/655/940 nm, akselerometer, dan referensi glukosa kapiler. Lisensinya CC0. Dataset berbeda dari MAX30102 SENS-Able, sehingga tidak dimasukkan ke `data/processed/` dan tidak menggantikan model V0.1.

Unduh dataset dan file QC dari halaman resmi `https://zenodo.org/records/21978226`, ekstrak arsipnya, lalu jalankan:

```bash
python3 ai_final/improvement/external_public_ppg_experiment.py \
  --public-root /path/to/wfdb_data \
  --qc-records /path/to/qc_records.csv
```

Script menggunakan hanya fitur yang tersedia pada kedua sumber data, mengubah label publik dari mmol/L ke mg/dL dengan faktor 18.0182, dan mempertahankan label `GlukosaRef` SENS-Able apa adanya. Validasi data SENS-Able tetap menggunakan GroupKFold berdasarkan `SubjectID`; data publik hanya masuk ke bagian training pada eksperimen augmentasi.

Pada uji yang dilakukan 26 Agustus 2026, 105 dari 125 rekaman publik lolos QC dan dapat diparsing. Model yang dilatih dari data publik saja memperoleh MAE 49.6547 mg/dL. Pada holdout SENS-Able, model dengan data SENS-Able saja memperoleh MAE 22.1055 mg/dL, sedangkan setelah ditambah data publik MAE menjadi 25.8117 mg/dL. Pembobotan data publik juga diuji; bobot terbaik 0.1 menghasilkan MAE 23.1664 mg/dL, masih lebih buruk daripada 22.1055 mg/dL. Kesimpulannya, dataset publik ini berguna sebagai benchmark dan pembanding, tetapi belum membantu meningkatkan model fisik SENS-Able karena perbedaan sensor, populasi, dan distribusi data.
