# Cara Membuat Model SENS-Able

## Status saat ini

Model SENS-Able yang paling tepat untuk penelitian saat ini adalah **model regresi**. Model menerima fitur sensor PPG, suhu, dan beberapa karakteristik dasar sebagai input, kemudian mengestimasi nilai gula darah. Nilai yang menjadi jawaban pembanding adalah `GlukosaRef`, yaitu nilai gula darah dari glucometer dalam mg/dL.

Model ini belum boleh disebut alat diagnosis, pengganti glucometer, atau model dengan akurasi klinis. Dengan 40 sesi dan 32 SubjectID, eksperimen saat ini masih merupakan studi pendahuluan.

## 1. Alur model

```text
Data raw ESP32 + nilai glucometer
              |
              v
scripts/prepare_dataset.py
              |
              v
data/processed/sensable_validation.csv
              |
              v
Pilih fitur sensor sebagai X
GlukosaRef sebagai y
              |
              v
GroupKFold berdasarkan SubjectID
              |
              v
Bandingkan baseline, Linear Regression, Random Forest
              |
              v
MAE, RMSE, median absolute error, R²
              |
              v
Model terbaik untuk eksperimen lanjutan
              |
              v
Baru pertimbangkan ekspor ke ESP32/TinyML
```

## 2. Target dan fitur

### Target `y`

Gunakan:

```text
GlukosaRef
```

Nilai ini berasal dari glucometer dan hanya berfungsi sebagai target/referensi. Nilai ini tidak boleh masuk ke fitur `X`.

### Fitur `X`

Fitur yang saat ini dipakai oleh pipeline adalah:

```text
Usia, Berat_kg, Tinggi_cm, BMI, TerakhirMakan_jam,
SuhuTubuh, SuhuAmbient, HR_est, SpO2_est,
IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS,
RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS,
Ratio_AC, Ratio_DC, Samples
```

`SubjectID` hanya dipakai untuk grouping cross-validation. `SuhuTubuh_Imputed` dan `SuhuAmbient_Imputed` hanya merupakan flag audit dan tidak dipakai sebagai fitur. `Diabetes` tidak menjadi target penelitian utama.

## 3. Menyiapkan dataset

Jalankan dari root repository:

```bash
python3 scripts/prepare_dataset.py
```

Pipeline ini melakukan normalisasi angka, menghapus salinan identik, menyimpan alasan eksklusi, mempertahankan sesi dengan suhu nol jika sinyal optiknya valid, dan mengisi suhu nol dengan rata-rata observasi positif yang dihitung terpisah per kolom. Flag imputasi ditambahkan agar perubahan dapat dilacak.

Pipeline tidak mengubah `data/raw/` dan tidak mengubah `GlukosaRef`.

## 4. Menjalankan validasi utama

Validasi Random Forest yang sudah ada dapat dijalankan dengan:

```bash
python3 scripts/validate_glucometer.py
```

Perbandingan tiga pendekatan dapat dijalankan dengan:

```bash
python3 scripts/compare_glucose_models.py
```

Hasil perbandingan disimpan di:

```text
reports/model_comparison.json
```

## 5. Mengapa memakai GroupKFold

Satu SubjectID dapat memiliki lebih dari satu sesi. Jika sesi dari orang yang sama masuk ke data training dan data test, hasil dapat terlihat lebih baik secara tidak wajar. `GroupKFold` menjaga semua sesi dari satu SubjectID tetap berada dalam grup yang sama pada satu fold.

Model tidak boleh dinilai hanya dari satu `train_test_split`, terutama karena jumlah sesi masih kecil.

## 6. Hasil eksperimen saat ini

| Model | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² |
|---|---:|---:|---:|---:|
| MeanBaseline | 24,2937 | 29,0975 | 23,9062 | -0,0856 |
| LinearRegression | 57,8532 | 71,9372 | 47,5700 | -5,6353 |
| RandomForestRegressor | 22,5716 | 27,0552 | 20,5580 | 0,0614 |

Pada eksperimen ini, Random Forest sedikit mengungguli baseline rata-rata. Linear Regression menghasilkan performa lebih buruk, kemungkinan karena jumlah fitur relatif besar dibandingkan jumlah sesi. Hasil tersebut bukan bukti bahwa Random Forest sudah akurat secara klinis; hasilnya masih sangat sensitif terhadap ukuran dataset dan kualitas pairing sensor–glucometer.

## 7. Cara membaca hasil

- **MAE** menunjukkan rata-rata kesalahan absolut dalam mg/dL. Nilai lebih kecil lebih baik.
- **RMSE** memberi penalti lebih besar terhadap kesalahan besar. Nilai lebih kecil lebih baik.
- **R²** menunjukkan seberapa besar variasi target yang dapat dijelaskan model. Nilai negatif berarti model lebih buruk daripada baseline rata-rata pada evaluasi tersebut.
- Model hanya layak dibandingkan jika semua model memakai dataset, fold, target, dan aturan cleaning yang sama.

Hasil buruk tetap harus dilaporkan. Jangan menghapus baris hanya karena prediksinya salah dan jangan mengubah `GlukosaRef` untuk memperbaiki skor.

## 8. Tahap berikutnya sebelum model dibawa ke ESP32

1. Pastikan data sensor dan glucometer berasal dari sesi pengukuran yang sama sesuai catatan pengambilan data.
2. Tambahkan data nyata secara bertahap tanpa membuat data sintetis.
3. Simpan versi dataset dan hasil model, misalnya V0.1, V0.2, dan V0.3.
4. Bandingkan model baru terhadap MeanBaseline, bukan hanya terhadap model lama.
5. Pilih fitur yang benar-benar tersedia dan stabil pada firmware MAX30102.
6. Bekukan model dan preprocessing hanya setelah jumlah data, validasi, dan hasil cukup stabil.
7. Konversi model ke format yang sesuai untuk embedded inference.
8. Uji ukuran model, penggunaan RAM/flash, waktu inferensi, dan hasil prediksi pada ESP32.

Tahap ESP32/TinyML tidak boleh dilakukan dengan hanya menyalin `model.pkl`, karena pickle/scikit-learn tidak dapat langsung dijalankan pada Arduino. Diperlukan model embedded yang kompatibel dan preprocessing yang identik dengan preprocessing saat training.

## 9. Perintah quality gate

```bash
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/prepare_dataset.py
python3 scripts/validate_glucometer.py
python3 scripts/compare_glucose_models.py
python3 -m unittest discover -s tests -v
git diff --check
```

Jika seluruh perintah berhasil, hasil belum otomatis berarti model sudah siap klinis. Quality gate hanya memastikan pipeline dapat dijalankan ulang, target tidak bocor ke fitur, dan perubahan data terdokumentasi.

## Visual QA of V0.1 Figures

The generated actual-versus-predicted and residual figures were visually checked. Both are readable, use Indonesian axis labels with mg/dL units, show the ideal-prediction reference line, and communicate the spread of errors without hiding outliers. The Random Forest plot shows predictions concentrated near the central range rather than tracking the full reference range closely; this supports the documented conclusion that V0.1 is exploratory and not clinically accurate.
