# Draf Revisi Proposal Penelitian OPSI — SENS-Able

**Catatan:** Ini adalah draf kerja berbasis bukti untuk disusun ulang dengan bahasa dan pemahaman peserta sendiri. Jangan mengunggahnya tanpa pemeriksaan Muhammad Daffa Ramadhan, Aira Cantika Putri, dan guru pembimbing.

## Judul Revisi

**SENS-Able: Evaluasi Awal Fitur Sinyal PPG dan Suhu pada Prototipe Pemantauan Kesehatan untuk Estimasi Glukosa Berbasis Referensi Glucometer**

## Latar Belakang — Arah Revisi

Pertahankan alasan pentingnya pemantauan kesehatan dan aksesibilitas, tetapi ubah klaim dari “alat diagnosis” menjadi “prototipe pemantauan dan penelitian awal”. Jelaskan bahwa sensor PPG dan suhu menghasilkan fitur yang dianalisis, sedangkan glucometer menjadi alat referensi. Hindari menyatakan bahwa sensor optik telah terbukti mengukur glukosa secara klinis.

## Rumusan Masalah

1. Bagaimana prototipe SENS-Able mengumpulkan fitur sinyal PPG, suhu, dan informasi kondisi pengukuran?
2. Bagaimana performa awal model regresi dalam mengestimasi `GlukosaRef` dari fitur yang dikumpulkan prototipe?
3. Apa keterbatasan kualitas data dan prototipe yang harus diperbaiki sebelum pengembangan TinyML dan fitur aksesibilitas lanjutan?

## Tujuan Penelitian

1. Mengembangkan dan mendokumentasikan collector ESP32 berbasis MAX30102 serta sensor suhu.
2. Menyusun dataset processed dari sesi pengukuran yang memiliki referensi glucometer.
3. Membandingkan MeanBaseline, Linear Regression, dan Random Forest dengan validasi `GroupKFold` berdasarkan `SubjectID`.
4. Mengukur MAE, RMSE, median absolute error, dan R² secara eksploratif.
5. Mengidentifikasi keterbatasan pengukuran dan rencana pengembangan berikutnya.

## Hipotesis Eksploratif

Fitur PPG, suhu, dan kondisi dasar pengukuran dapat menghasilkan estimasi `GlukosaRef` yang lebih baik daripada baseline prediksi rata-rata. Hipotesis dapat ditolak berdasarkan data.

## Batasan Penelitian

Penelitian ini tidak menetapkan diagnosis diabetes, tidak menggantikan glucometer, dan bukan validasi klinis. Audio dan vibrasi belum menjadi fitur yang diuji. TinyML inference langsung di ESP32 belum dinyatakan selesai. Data penelitian terdiri atas 40 sesi processed dan 32 SubjectID dari data yang tersedia.

## Metode yang Disarankan

### Perangkat

Gunakan ESP32 DevKit, modul **MAX30102** sesuai hardware yang dikonfirmasi peneliti, sensor suhu yang benar-benar digunakan, OLED, dan laptop. Jika kode memakai library bernama `MAX30100`, jelaskan kompatibilitasnya dengan modul MAX30102 dan verifikasi sebelum laporan final.

### Data

Target adalah `GlukosaRef` dari glucometer dalam mg/dL. Fitur meliputi usia, berat, tinggi, BMI, `TerakhirMakan_jam`, suhu, HR/SpO2, fitur IR/RED, ratio AC/DC, dan jumlah sampel. `GlukosaRef`, `SubjectID`, `Diabetes`, dan flag imputasi tidak dipakai sebagai fitur.

### Cleaning

Dari 237 baris raw diperoleh 46 sesi unik setelah normalisasi dan deduplikasi. Dataset processed mempertahankan 40 sesi dan mengeluarkan 6 sesi karena sinyal optik rendah. Tujuh suhu tubuh nol dan enam suhu ambient nol dipulihkan menggunakan rata-rata observasi positif per kolom dan diberi flag provenance. Nilai `GlukosaRef` tidak diubah.

### Pemodelan

Gunakan `configs/glucose_model_v0_1.json` sebagai kontrak fitur dan parameter. Jalankan `scripts/compare_glucose_models.py` untuk perbandingan dan simpan hasil di `reports/model_comparison.json`. Gunakan `GroupKFold` berdasarkan `SubjectID` untuk mencegah sesi dari subject yang sama masuk ke fold yang berbeda secara tidak tepat.

## Hasil Awal yang Sudah Tersedia

| Model | MAE (mg/dL) | RMSE (mg/dL) | R² |
|---|---:|---:|---:|
| MeanBaseline | 24,2937 | 29,0975 | -0,0856 |
| LinearRegression | 57,8532 | 71,9372 | -5,6353 |
| RandomForestRegressor | 22,5716 | 27,0552 | 0,0614 |

Random Forest adalah kandidat terbaik pada perbandingan V0.1, tetapi selisihnya terhadap baseline kecil. Hasil ini harus disebut eksploratif dan belum memenuhi target awal MAE di bawah 15 mg/dL.

## Indikator Keberhasilan Revisi

| Indikator | Cara membaca hasil |
|---|---|
| Pipeline dapat dijalankan ulang | Semua script dan test berhasil |
| Target tidak bocor ke fitur | `GlukosaRef` tidak ada di daftar fitur |
| Kualitas capture dapat diaudit | Exclusion log dan flag imputasi tersedia |
| Model mengungguli baseline | Bandingkan MAE/RMSE pada fold yang sama |
| Akurasi pengukuran | Hanya disimpulkan jika ada referensi dan prosedur pengukuran yang memadai |
| Aksesibilitas | Hanya diklaim jika audio/vibrasi dan usability benar-benar diuji |

## Jadwal Revisi

Gunakan tanggal aktual kegiatan. Jangan mempertahankan jadwal Maret–Juni jika kegiatan sebenarnya berjalan sampai Agustus. Masukkan tanggal cleaning, training V0.1, pembuatan grafik, penulisan laporan, review pembimbing, dan unggah tahap 2.

## Bagian yang Dipindahkan ke Pengembangan Lanjutan

Audio, motor vibrasi, TinyML embedded, kalibrasi yang lebih luas, penambahan responden, timestamp otomatis, dan uji usability terstruktur dipindahkan ke saran/pengembangan lanjutan apabila belum memiliki bukti hasil.

## File Pendukung

- `reports/opsi_stage2_report_framework.md`
- `reports/modeling_v0_1_summary.md`
- `docs/model_building_guide.md`
- `docs/opsi_stage2_recheck_plan.md`
- `data/processed/quality_report.json`
- `reports/model_comparison.json`
