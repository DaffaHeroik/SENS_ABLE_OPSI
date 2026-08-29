# SENS ABLE — Handoff Report

**Tanggal:** 26 Agustus 2026  
**Repository:** `DaffaHeroik/SENS_ABLE_OPSI`  
**Branch:** `data-cleaning-glucometer-validation`  
**Commit:** `35f07108157d32c9b7ff333a1936f7e8e923bf6a`  
**Status repository:** Private  

## Perubahan yang Sudah Dipush

Seluruh file dataset yang tersedia disimpan sebagai salinan raw di `data/raw/` tanpa mengubah isi. Dataset lama dari repository juga dipindahkan ke arsip raw. File `data/raw/MANIFEST.sha256` menyimpan hash SHA-256 untuk memeriksa integritas salinan tersebut.

Pembersihan deterministik ditambahkan melalui `scripts/prepare_dataset.py`. Dari 25 file/sheet dan 237 baris input, terdapat 46 baris unik setelah normalisasi format angka dan penghapusan salinan identik. Sebanyak 13 baris dikeluarkan karena suhu nol/tidak valid atau tangkapan sinyal optik bermasalah. Dataset processed berisi 33 baris, menggunakan `SubjectID` pseudonim dan tidak membawa kolom nama asli.

Kolom `GlukosaRef` dipertahankan tanpa perubahan dan didokumentasikan sebagai nilai gula darah asli dari **glucometer** dalam mg/dL. Script `scripts/validate_glucometer.py` menggunakan kolom tersebut sebagai target referensi, bukan sebagai fitur input, sehingga tidak terjadi kebocoran label.

## Hasil Validasi Eksploratif

| Metrik | Hasil |
|---|---:|
| Jumlah baris processed | 33 |
| SubjectID unik | 31 |
| Rentang `GlukosaRef` | 72–187 mg/dL |
| MAE | 23.7345 mg/dL |
| RMSE | 28.4437 mg/dL |
| R² | -0.0102 |
| Metode | 5-fold GroupKFold berdasarkan SubjectID |

Hasil tersebut masih **eksploratif** dan belum dapat dianggap sebagai akurasi klinis. Dataset masih kecil dan distribusi label diabetes tetap sangat tidak seimbang, yaitu 32 label 0 dan 1 label 1.

## File Penting

| File | Fungsi |
|---|---|
| `data/raw/` | Arsip input asli |
| `data/processed/sensable_validation.csv` | Dataset hasil pembersihan dan anonimisasi |
| `data/processed/excluded_records.csv` | Baris yang dikeluarkan dan alasannya |
| `data/processed/quality_report.json` | Ringkasan kualitas data |
| `scripts/prepare_dataset.py` | Pipeline raw ke processed |
| `scripts/validate_glucometer.py` | Validasi gula darah terhadap glucometer |
| `reports/glucometer_validation.json` | Hasil MAE/RMSE/R² dan prediksi per baris |
| `tests/test_dataset_pipeline.py` | Tes schema, anonimisasi, dan isolasi target |
| `requirements.txt` | Dependensi Python |

## Quality Gates

| Pemeriksaan | Hasil |
|---|---|
| Python syntax check | PASS |
| Dataset regression tests | PASS — 3 tests |
| Dataset preparation rerun | PASS |
| Glucometer validation rerun | PASS |
| Git diff check untuk file non-raw | PASS |
| Fresh clone verification | PASS |
| Repository visibility | PASS — PRIVATE |
| Working tree setelah push | CLEAN |

## Catatan Keamanan

Repository sudah diubah menjadi private sesuai persetujuan. File raw masih mengandung identitas dan data kesehatan, sehingga jangan mengubah repository menjadi public sebelum seluruh identitas dianonimkan dan izin publikasi dipastikan.
