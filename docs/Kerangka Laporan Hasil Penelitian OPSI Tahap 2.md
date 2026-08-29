# Kerangka Laporan Hasil Penelitian OPSI Tahap 2

**Catatan integritas:** Dokumen ini adalah kerangka kerja dan kumpulan fakta terverifikasi. Narasi akhir, interpretasi ilmiah, dan jawaban wawancara harus ditulis serta dipahami oleh peserta sendiri sesuai ketentuan OPSI. Jangan menyalin kerangka ini secara mentah ke naskah final.

## Halaman Sampul

Gunakan judul kerja berikut dan sesuaikan dengan format resmi:

**SENS-Able: Evaluasi Awal Fitur Sinyal PPG dan Suhu pada Prototipe Pemantauan Kesehatan untuk Estimasi Glukosa Berbasis Referensi Glucometer**

Isi kode peserta, nama Muhammad Daffa Ramadhan dan Aira Cantika Putri, MAN 2 Kota Bima, bidang FTR dan Sistem Pengukuran & Monitoring Cerdas, serta tahun 2026.

## Abstrak — Ditulis oleh Peserta Setelah Bab 4 Selesai

Isi empat unsur: latar belakang masalah akses pemantauan kesehatan; tujuan evaluasi awal; metode dan jumlah data; hasil utama dan kesimpulan terbatas. Wajib menyebutkan bahwa `GlukosaRef` berasal dari glucometer, bahwa data berisi 40 sesi dan 32 SubjectID, serta bahwa hasil belum merupakan validasi klinis.

## BAB 1 — Pendahuluan

### Latar Belakang

Pertahankan gagasan tentang kebutuhan pemantauan kesehatan yang mudah diakses, tetapi hindari kalimat yang menyatakan alat sudah mampu mendiagnosis diabetes atau menggantikan glucometer. Jelaskan bahwa PPG dan suhu digunakan sebagai sumber fitur prototipe, sedangkan glucometer digunakan sebagai alat pembanding.

### Rumusan Masalah

1. Bagaimana prototipe SENS-Able mengumpulkan fitur PPG dan suhu serta menyimpan nilai referensi glucometer?
2. Bagaimana performa awal model regresi dalam mengestimasi `GlukosaRef` dari fitur sensor?
3. Apa keterbatasan data, perangkat, dan pipeline yang perlu diperbaiki sebelum pengembangan TinyML dan fitur aksesibilitas lebih lanjut?

### Tujuan

Tuliskan tujuan yang dapat dibuktikan: membangun collector ESP32; membersihkan dan mendokumentasikan dataset; membandingkan baseline, Linear Regression, dan Random Forest; serta menganalisis error terhadap `GlukosaRef`.

### Hipotesis Eksploratif

Fitur PPG, suhu, dan kondisi dasar pengukuran dapat memberikan estimasi yang lebih baik daripada baseline prediksi rata-rata. Hipotesis ini dapat ditolak berdasarkan hasil pengujian.

## BAB 2 — Landasan Teori dan Studi Pustaka

Bahas PPG dan fitur sinyal IR/RED, prinsip glucometer sebagai reference measurement, regresi machine learning, MAE/RMSE/R², GroupKFold, kualitas capture sensor, dan kebutuhan aksesibilitas. Verifikasi semua referensi yang digunakan; jangan memasukkan referensi yang tidak benar-benar dibaca.

## BAB 3 — Metode Penelitian

### Desain

Gunakan metode eksperimen kuantitatif untuk mengevaluasi pipeline pengumpulan data dan estimasi glukosa. Nyatakan bahwa penelitian ini merupakan evaluasi awal/pilot, bukan uji klinis.

### Perangkat

Tuliskan ESP32 DevKit dan **MAX30102** sesuai konfirmasi hardware pengguna. Jelaskan library yang dipakai firmware apabila nama library/objek masih menggunakan `MAX30100`, dan lakukan verifikasi kompatibilitas sebelum penulisan final. Sertakan MLX90614 hanya jika benar-benar digunakan pada capture yang dianalisis.

### Akuisisi Data

Jelaskan bahwa satu sesi berisi capture sensor dan nilai `GlukosaRef` glucometer yang dicatat oleh peneliti. `TerakhirMakan_jam` menunjukkan durasi sejak makan terakhir dan digunakan sebagai informasi kondisi sebelum pengukuran. Dataset CSV tidak memiliki timestamp kalender eksplisit; jika tanggal hanya ada pada logbook terpisah, jelaskan sumbernya secara terpisah.

### Data dan Cleaning

| Tahap | Jumlah |
|---|---:|
| Baris dari 25 file/sumber raw | 237 |
| Sesi unik setelah normalisasi/deduplikasi | 46 |
| Sesi processed | 40 |
| SubjectID pseudonim | 32 |
| Sesi dikeluarkan | 6 |
| Suhu tubuh nol dipulihkan | 7 |
| Suhu ambient nol dipulihkan | 6 |

Enam sesi dikeluarkan karena `IR_Mean` atau `RED_Mean` terlalu rendah. Suhu nol pada capture optik yang masih valid diimputasi dengan rata-rata observasi positif per kolom dan diberi flag provenance. `GlukosaRef` tidak diubah.

### Variabel

Target `y` adalah `GlukosaRef`. Fitur `X` terdiri atas usia, berat, tinggi, BMI, `TerakhirMakan_jam`, suhu, HR/SpO2, fitur IR, fitur RED, ratio AC/DC, dan jumlah sampel. `GlukosaRef`, `SubjectID`, `Diabetes`, serta flag imputasi tidak digunakan sebagai fitur.

### Evaluasi

Gunakan 5-fold `GroupKFold` berdasarkan `SubjectID`. Bandingkan MeanBaseline, Linear Regression, dan Random Forest dengan konfigurasi yang tersimpan di `configs/glucose_model_v0_1.json`. Semua preprocessing harus dipelajari pada bagian training fold.

## BAB 4 — Hasil dan Pembahasan

### Profil Data

Masukkan tabel cleaning di Bab 3, distribusi `GlukosaRef`, rentang nilai, dan penjelasan enam sesi yang dikeluarkan. Jelaskan bahwa SubjectID digunakan untuk mencegah sesi dari orang yang sama tersebar secara tidak tepat di fold.

### Hasil Perbandingan Model

| Model | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² |
|---|---:|---:|---:|---:|
| MeanBaseline | 24,2937 | 29,0975 | 23,9062 | -0,0856 |
| LinearRegression | 57,8532 | 71,9372 | 47,5700 | -5,6353 |
| RandomForestRegressor | **22,5716** | **27,0552** | **20,5580** | **0,0614** |

Random Forest menjadi kandidat terbaik pada perbandingan V0.1 karena MAE paling rendah. Namun, selisih terhadap baseline masih kecil dan R² masih rendah. Jelaskan bahwa hasil ini belum cukup untuk menyatakan akurasi klinis atau penggantian glucometer.

### Grafik

Gunakan figure dari `reports/figures/`:

- `actual_vs_predicted_randomforestregressor.png` untuk hubungan referensi dan prediksi;
- `residuals_randomforestregressor.png` untuk error per sesi;
- grafik model lain sebagai pembanding di lampiran.

Tuliskan interpretasi grafik dengan kalimat sendiri. Jangan menyembunyikan sesi dengan error besar.

### Keterbatasan

Bahas ukuran dataset, tidak adanya timestamp eksplisit di CSV, penggunaan imputasi suhu, kualitas sensor optik, belum adanya TinyML inference yang terverifikasi di ESP32, serta audio/vibrasi yang belum diuji.

## BAB 5 — Anggaran dan Kegiatan

Isi dengan realisasi pengeluaran dan kegiatan yang benar-benar dilakukan, bukan hanya menyalin RAB proposal. Sesuaikan tanggal kegiatan berdasarkan catatan yang tersedia.

## BAB 6 — Kesimpulan dan Saran

Kesimpulan harus menjawab rumusan masalah berdasarkan hasil nyata. Nyatakan bahwa pipeline SENS-Able berhasil menghasilkan dataset processed dan model regresi eksperimen, tetapi performa belum mencapai target awal dan belum dapat dipakai sebagai alat diagnosis. Saran meliputi penambahan subjek, pencatatan timestamp/logbook yang konsisten, verifikasi sensor, pengujian audio/vibrasi, dan pengembangan TinyML.

## Lampiran

Siapkan logbook, dokumen izin/etik yang diminta, foto perangkat, foto sensor saat pengukuran, screenshot collector, data dictionary, exclusion log, tabel processed anonymized, konfigurasi model, dan grafik tambahan. Jangan masukkan nama atau kontak responden ke laporan utama.

## Reproduction Commands

```bash
python3 scripts/prepare_dataset.py
python3 scripts/compare_glucose_models.py
python3 scripts/plot_model_results.py
python3 scripts/validate_glucometer.py
python3 -m unittest discover -s tests -v
```

## Submission Checklist

- [ ] Narasi akhir ditulis ulang dan dipahami oleh peserta.
- [ ] `GlukosaRef` dijelaskan sebagai referensi glucometer.
- [ ] Tidak ada klaim diagnosis atau validasi klinis.
- [ ] MAX30102 konsisten dengan hardware dan bukti foto.
- [ ] Audio/vibrasi hanya ditulis jika benar-benar diuji.
- [ ] TinyML tidak diklaim sudah deploy tanpa bukti.
- [ ] Semua angka Bab 4 cocok dengan `reports/modeling_v0_1_summary.md`.
- [ ] Identitas responden dianonimkan.
- [ ] Logbook dan dokumen izin diperiksa pembimbing.
- [ ] Laporan mengikuti batas halaman dan ukuran PDF OPSI.
