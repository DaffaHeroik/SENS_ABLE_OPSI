# Data SENS-Able

## Struktur

| Lokasi | Isi | Status |
|---|---|---|
| `data/raw/` | Salinan file CSV/XLSX yang diterima, tanpa perubahan isi | Arsip asli; jangan dipakai langsung untuk training |
| `data/processed/sensable_validation.csv` | Dataset hasil normalisasi dan pembersihan | Input yang didukung untuk eksperimen |
| `data/processed/excluded_records.csv` | Baris unik yang dikeluarkan beserta alasan dan sumbernya | Audit trail pembersihan |
| `data/processed/quality_report.json` | Ringkasan jumlah baris, distribusi label, dan aturan pembersihan | Metadata |
| `data/raw/MANIFEST.sha256` | Hash SHA-256 file raw | Integritas arsip |

## Aturan Pembersihan

Pembersihan dilakukan secara deterministik oleh `scripts/prepare_dataset.py`. Nilai numerik dinormalisasi dan semua file CSV/XLSX harus memiliki skema yang sama. Baris yang merupakan salinan identik setelah normalisasi numerik digabungkan. Baris dengan nilai suhu nol atau negatif, denyut jantung tidak valid, SpO2 di luar rentang pemeriksaan, rentang sinyal terbalik, atau tangkapan optik dengan `IR_Mean`/`RED_Mean` terlalu rendah dikeluarkan. Kegagalan sensor tidak diimputasi.

Kolom `Nama` tidak dibawa ke file processed. Sebagai gantinya digunakan `SubjectID` pseudonim yang stabil. Nama asli tetap berada di `data/raw/` untuk kebutuhan arsip internal dan **tidak boleh dipublikasikan pada repository public tanpa anonimisasi dan izin yang sesuai**.

## Referensi Glukometer

`GlukosaRef` adalah **nilai gula darah asli dari glucometer dalam mg/dL** berdasarkan keterangan pemilik proyek. Nilai ini menjadi target atau referensi validasi dan **tidak boleh dimasukkan sebagai fitur input model**. Pengujian regresi dilakukan dengan:

```bash
python3 scripts/validate_glucometer.py
```

Skrip tersebut menghitung MAE, RMSE, dan R² menggunakan `GroupKFold` berdasarkan `SubjectID`, sehingga pengukuran dari subjek yang sama tidak tersebar secara sembarangan di antara fold. Hasilnya bersifat eksploratif; dataset kecil ini belum cukup untuk menyatakan akurasi klinis.

## Privacy Notice

File raw berisi data kesehatan dan identitas yang dikirimkan untuk pemrosesan. Simpan repository sebagai private atau anonimisasi file raw sebelum melakukan push ke repository public. File processed sudah menghapus nama, tetapi nilai kesehatan tetap sensitif.
