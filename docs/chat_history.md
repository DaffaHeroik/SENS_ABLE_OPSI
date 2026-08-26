# Chat History — Pengolahan Data SENS-Able

Tanggal: 12 Agustus 2025

## Timeline Diskusi

### 1. Upload Data Awal
- File: `SENSABLE Final.xlsx` (13 baris, 11 responden)
- File: Proposal penelitian PDF
- Data berisi: Nama, Usia, Gender, Berat, Tinggi, BMI, Diabetes, GlukosaRef, TerakhirMakan, SuhuTubuh, SuhuAmbient, HR_est, SpO2_est, IR/RED sensor data

### 2. Analisis Data Awal
- Ditemukan: Semua `Diabetes=0` (tidak ada positif)
- Ditemukan: Duplikat identik (beberapa orang muncul 2×)
- Ditemukan: Data terlalu sedikit untuk training (13 baris)

### 3. Upload Data Tambahan (Batch 1)
- 11 file CSV (dataset 21-31)
- Total bertambah: 16 baris baru
- Ditemukan: 1 positif diabetes (Arsyik, Glukosa=138)
- Ditemukan: 5 baris SuhuTubuh=0 (sensor error)

### 4. Pembersihan Data
- **SuhuTubuh=0**: 
  - Arsyik & Rudi → punya data ulang valid, baris gagal dihapus
  - Putri & Mas kawi → tidak ada data ulang, diisi rata-rata 32.92°C
- **Duplikat identik** → dihapus

### 5. Upload Data Tambahan (Batch 2)
- 3 file CSV baru (dataset 1-3)
- Total: 24 baris, 22 responden

### 6. Upload Data Tambahan (Batch 3)
- 26 file CSV (dataset 1-31 + beberapa variasi)
- Total mentah: 98 baris

### 7. Pembersihan Lanjutan
- **Marisa** (Glukosa=6.0) → dihapus (mustahil, salah input)
- **MUHAMMAD DAFFA RAMADHAN** (IR_Mean=223) → dihapus (sensor off)
- **Daffa Heroik** (IR_Mean=223) → dihapus (duplikat Daffa)
- **Pertama** (IR_Mean=79) → dihapus (sensor off, nama placeholder)
- **Dua** (IR_Mean=79) → dihapus (sensor off, nama placeholder)
- **Aandidiini** (IR_Mean=6044, HR=200) → dihapus (sensor kurang nempel)

### 8. Format Seragam
- Angka diseragamkan (int vs float)
- Duplikat dihapus
- Final: 33 baris, 30 responden

### 9. Training Model
- **v1**: Data sendiri saja (33 sampel, augmented → 63)
  - Random Forest: 100% akurat (overfitting expected)
  - Fitur terpenting: Usia, HR_est, Berat_kg, GlukosaRef
  
- **v2**: Gabungan PIMA + SENS-Able
  - PIMA (768 sampel): Random Forest 76.3%
  - SENS-Able augmented: Random Forest 100%
  
- **v3**: PIMA (train) → SENS-Able (validate)
  - Training CV: 75.1% ± 4.9%
  - Validasi: 90.9% akurat
  - Fitur terpenting: Glucose (0.43), BMI (0.31), Age (0.26)

### 10. Keputusan Desain
- Data sendiri digunakan sebagai **validasi**, bukan training
- Model dilatih pada **PIMA Indians Diabetes** (public, 768 sampel)
- Strategi ini lebih valid: train/validation split, tidak overfitting

## Dataset Final

| Statistik | Nilai |
|---|---|
| Total baris | 33 |
| Responden unik | 30 |
| Diabetes=0 | 32 |
| Diabetes=1 | 1 |
| SuhuTubuh=0 | 0 |
| Sensor error | 0 |
| Duplikat | 0 |

## File Penting

| File | Keterangan |
|---|---|
| `data/sensable_final.csv` | Dataset bersih final |
| `train.py` | Script training v3 (utama) |
| `model.pkl` | Model terlatih |
| `report.json` | Laporan training |


## 11. Ingestion & Pembersihan Dataset Baru (26 Agustus 2026)

- Seluruh file CSV/XLSX yang tersedia disalin apa adanya ke `data/raw/` dan diberi manifest SHA-256.
- Semua sumber memiliki skema 26 kolom yang sama; total input yang diproses adalah 237 baris dari 25 file/sheet yang tersedia di workspace.
- Setelah normalisasi format angka dan penghapusan salinan identik, tersisa 46 baris unik.
- Tiga belas baris dikeluarkan karena sensor gagal atau data suhu nol/tidak valid; baris tidak diimputasi.
- Dataset processed berisi 33 baris dan 31 `SubjectID` pseudonim.
- `GlukosaRef` dipertahankan tanpa perubahan dan ditetapkan sebagai nilai referensi gula darah dari glucometer dalam mg/dL.
- Validasi regresi dilakukan terpisah melalui `scripts/validate_glucometer.py`; `GlukosaRef` tidak digunakan sebagai fitur input.
- Hasil validasi saat ini bersifat eksploratif: MAE 23.7345 mg/dL, RMSE 28.4437 mg/dL, dan R² -0.0102 pada GroupKFold berdasarkan `SubjectID`.
