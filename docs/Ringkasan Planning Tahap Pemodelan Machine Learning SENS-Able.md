# Ringkasan Planning Tahap Pemodelan Machine Learning SENS-Able

**Status dataset:** siap untuk eksperimen pemodelan awal  
**Dataset:** 40 sesi processed, 32 SubjectID  
**Target:** `GlukosaRef` dari glucometer, satuan mg/dL  
**Status model:** eksperimen awal; belum validasi klinis dan belum siap langsung dideploy ke ESP32

## 1. Tujuan Pemodelan

Tujuan tahap ini adalah membuat model regresi yang mempelajari hubungan antara fitur sensor MAX30102, suhu, kondisi sebelum pengukuran, dan nilai referensi glucometer. Model tidak digunakan untuk mendiagnosis diabetes dan tidak dimaksudkan menggantikan glucometer.

Pertanyaan utama yang dijawab adalah: **seberapa dekat estimasi model terhadap `GlukosaRef` ketika diuji pada subject yang tidak digunakan untuk melatih model pada fold tersebut?**

## 2. Kondisi Dataset Sebelum Modeling

| Komponen | Nilai/status |
|---|---:|
| Baris input dari seluruh raw file | 237 |
| Sesi unik setelah normalisasi dan deduplikasi | 46 |
| Sesi processed yang dipakai | **40** |
| SubjectID unik | **32** |
| Sesi dikeluarkan | 6, karena sinyal optik terlalu rendah |
| Suhu tubuh yang diimputasi | 7 |
| Suhu ambient yang diimputasi | 6 |
| Nilai `GlukosaRef` yang diubah | Tidak ada |
| Data sintetis | Tidak digunakan |

Suhu nol hanya dipulihkan pada sesi yang sinyal optiknya masih valid. Nilai `GlukosaRef` tidak boleh diubah atau diperkirakan dari sensor.

## 3. Definisi Target dan Fitur

### Target `y`

```text
GlukosaRef
```

`GlukosaRef` adalah nilai gula darah dari glucometer dalam mg/dL. Nilai ini merupakan target/referensi, bukan fitur input.

### Fitur `X`

Fitur awal yang dapat diuji adalah:

```text
Usia
Berat_kg
Tinggi_cm
BMI
TerakhirMakan_jam
SuhuTubuh
SuhuAmbient
HR_est
SpO2_est
IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS
RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS
Ratio_AC
Ratio_DC
Samples
```

Kolom berikut tidak boleh menjadi fitur:

```text
GlukosaRef
SubjectID
Nama
Gender
Diabetes
SuhuTubuh_Imputed
SuhuAmbient_Imputed
```

`SubjectID` digunakan untuk grouping ketika validasi. Flag imputasi digunakan untuk audit, bukan untuk memberi model petunjuk tentang proses cleaning.

## 4. Urutan Eksperimen

### Tahap A — Bekukan dataset dan kontrak data

Jalankan:

```bash
python3 scripts/prepare_dataset.py
```

Periksa `data/processed/quality_report.json`, `sensable_validation.csv`, dan `excluded_records.csv`. Setelah angka dan aturan disetujui, dataset tersebut menjadi versi baseline modeling. Jangan mengubah label hanya karena model menghasilkan prediksi yang buruk.

### Tahap B — Buat baseline sederhana

Baseline pertama adalah prediksi rata-rata `GlukosaRef` pada data training setiap fold. Baseline harus dihitung ulang hanya dari data training fold agar tidak terjadi kebocoran informasi dari fold test.

Model baru dianggap memberi nilai tambah jika MAE dan RMSE-nya lebih baik daripada baseline pada skema fold yang sama.

### Tahap C — Bandingkan model regresi

Model minimum yang dibandingkan:

1. **MeanBaseline** sebagai pembanding paling sederhana.
2. **Linear Regression** sebagai model hubungan linear yang mudah dijelaskan.
3. **Random Forest Regressor** sebagai model non-linear untuk eksperimen awal.
4. **Gradient Boosting Regressor** sebagai opsi tambahan jika waktu dan stabilitas data mencukupi.

Jalankan perbandingan saat ini dengan:

```bash
python3 scripts/compare_glucose_models.py
```

Output disimpan di:

```text
reports/model_comparison.json
```

### Tahap D — Gunakan validasi berbasis subject

Gunakan `GroupKFold` berdasarkan `SubjectID`. Semua sesi dari satu subject harus tetap berada di satu kelompok pada setiap pembagian. Jangan menggunakan random split biasa jika satu subject memiliki lebih dari satu sesi.

Semua preprocessing, scaling, dan pemilihan parameter harus dilakukan di dalam fold training. Data test fold hanya digunakan untuk mengukur performa.

### Tahap E — Hitung metrik

Metrik yang wajib dilaporkan:

| Metrik | Fungsi | Arah yang lebih baik |
|---|---|---|
| MAE | Rata-rata selisih absolut dari glucometer | Lebih kecil |
| RMSE | Memberi penalti lebih besar pada error besar | Lebih kecil |
| Median absolute error | Menunjukkan error tipikal yang lebih tahan terhadap outlier | Lebih kecil |
| R² | Proporsi variasi target yang dijelaskan | Lebih besar, tetapi dapat negatif |

Laporkan metrik keseluruhan, metrik tiap fold, jumlah sesi, jumlah subject, rentang glukosa, dan jumlah nilai suhu yang diimputasi.

## 5. Hasil Eksperimen Saat Ini

Pada dataset 40 sesi dan 32 SubjectID, `scripts/compare_glucose_models.py` menghasilkan:

| Model | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² |
|---|---:|---:|---:|---:|
| MeanBaseline | 24,2937 | 29,0975 | 23,9062 | -0,0856 |
| LinearRegression | 57,8532 | 71,9372 | 47,5700 | -5,6353 |
| RandomForestRegressor | **22,5716** | **27,0552** | **20,5580** | **0,0614** |

Random Forest sedikit lebih baik daripada baseline. Namun, hasil ini masih eksploratif karena jumlah data kecil. Sebelum angka dipakai pada laporan OPSI, konfigurasi model dan evaluator harus dibekukan agar tidak ada dua script yang menghasilkan angka berbeda untuk model yang disebut sama.

## 6. Analisis yang Harus Dibuat

Setelah model dibandingkan, buat analisis berikut:

1. Tabel distribusi `GlukosaRef`, termasuk minimum, maksimum, rata-rata, median, dan simpangan baku.
2. Grafik nilai glucometer aktual versus prediksi model.
3. Grafik residual atau error absolut per sesi.
4. Tabel hasil tiap fold.
5. Perbandingan model dengan MeanBaseline.
6. Analisis apakah baris dengan suhu diimputasi menghasilkan pola error yang berbeda.
7. Analisis sesi dengan error paling besar berdasarkan kondisi sensor, jumlah sampel, dan kualitas capture.
8. Penjelasan mengapa Linear Regression lebih buruk jika memang hasilnya tetap seperti eksperimen saat ini.

Analisis ini ditulis sebagai pembahasan ilmiah. Jangan menghapus error besar hanya untuk memperbaiki grafik.

## 7. Kriteria Pemilihan Model

Model dapat dipilih sebagai model eksperimen terbaik jika:

- target tidak masuk sebagai fitur;
- evaluasi memakai GroupKFold berbasis SubjectID;
- preprocessing tidak bocor dari test fold;
- performanya mengalahkan MeanBaseline pada metrik utama;
- konfigurasi dan random seed terdokumentasi;
- hasil dapat dijalankan ulang dari script dan dataset processed;
- keterbatasan dataset disebutkan secara terbuka.

Dengan hasil saat ini, Random Forest adalah kandidat model eksperimen terbaik, tetapi belum boleh disebut model final atau model siap medis.

## 8. Reproducibility dan Versioning

Setiap eksperimen harus diberi versi:

```text
Model V0.1 — dataset 40 sesi, fitur awal, GroupKFold
Model V0.2 — dataset tambahan atau cleaning yang disetujui
Model V0.3 — fitur/model yang dibekukan untuk pengujian embedded
```

Setiap versi harus menyimpan dataset yang digunakan, script, parameter model, seed, hasil metrik, dan tanggal pemrosesan. Jangan menimpa hasil versi lama.

Quality gate minimal:

```bash
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/prepare_dataset.py
python3 scripts/compare_glucose_models.py
python3 scripts/validate_glucometer.py
python3 -m unittest discover -s tests -v
git diff --check
```

## 9. Jalur Menuju ESP32 TinyML

`model.pkl` dari scikit-learn tidak dapat langsung dijalankan pada Arduino. Jalur deployment harus dilakukan setelah model dan preprocessing cukup stabil:

1. Bekukan daftar fitur dan urutannya.
2. Bekukan aturan scaling, imputasi, dan pembulatan.
3. Latih model dengan seluruh data training yang diizinkan setelah evaluasi selesai.
4. Pilih format embedded yang kompatibel, misalnya model yang dapat dikonversi ke TensorFlow Lite Micro atau implementasi regresi yang ringan.
5. Uji ukuran model, penggunaan flash/RAM, dan waktu inferensi di ESP32.
6. Pastikan preprocessing di ESP32 identik dengan preprocessing Python.
7. Uji prediksi ESP32 terhadap data holdout atau sesi baru yang tidak dipakai ketika training.
8. Laporkan hasil embedded secara terpisah dari hasil cross-validation Python.

Jika tahap-tahap tersebut belum selesai, laporan cukup menyatakan bahwa TinyML adalah rencana pengembangan berikutnya.

## 10. Batasan yang Wajib Ditulis

Dataset kecil dan sebagian sesi memiliki nilai suhu yang dipulihkan. Nilai `GlukosaRef` berasal dari catatan glucometer pemilik data, tetapi CSV tidak memuat timestamp eksplisit. Karena itu, laporan harus menjelaskan keterbatasan dokumentasi waktu sesi jika tidak ada logbook terpisah.

Model tidak boleh digunakan untuk diagnosis atau keputusan medis. Target awal MAE <15 mg/dL belum tercapai pada eksperimen saat ini. Audio, vibrasi, usability, dan aksesibilitas belum menjadi hasil yang tervalidasi karena alat saat ini baru digunakan sebagai alat pengukuran.

## 11. Output Akhir Tahap Modeling

Tahap modeling dianggap selesai jika tersedia:

- `data/processed/sensable_validation.csv` versi yang dibekukan;
- `data/processed/quality_report.json`;
- `data/processed/excluded_records.csv`;
- script model comparison yang reproducible;
- `reports/model_comparison.json`;
- tabel metrik dan grafik untuk laporan;
- catatan konfigurasi model dan seed;
- pembahasan error dan keterbatasan;
- keputusan apakah model hanya untuk analisis Python atau diteruskan ke TinyML;
- catatan pada `MEMORY.md`.

## Keputusan Saat Ini

**Model kandidat:** Random Forest Regressor.  
**Peran:** model eksperimen untuk estimasi `GlukosaRef`.  
**Status:** belum final dan belum siap deployment medis/embedded.  
**Langkah terdekat:** bekukan evaluator, buat tabel/grafik hasil, lalu masukkan hasil aktual ke Bab Metode serta Bab Hasil dan Pembahasan laporan OPSI.
