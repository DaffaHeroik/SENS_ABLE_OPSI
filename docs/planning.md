# SENS-Able — Planning Detail & Konfirmasi Plan

> **Proyek**: SENS-Able: Smart Health Monitor Inklusif berbasis AI
> **Tim**: AntroOptic Team (Muhammad Daffa Ramadhan & Aira Cantika Putri)
> **Sekolah**: MAN 2 Kota Bima, NTB
> **Tahun**: 2026

---

## 📅 Timeline Spesifik

| No | Tahap | Waktu | Durasi | Status |
|---|---|---|---|---|
| 1 | Penyusunan Judul | 1-7 Maret 2026 | 1 minggu | ✅ |
| 2 | Pengajuan Proposal | 8-21 Maret 2026 | 2 minggu | ✅ |
| 3 | Pengadaan Komponen | 22-28 Maret 2026 | 1 minggu | ✅ |
| 4 | Rangkai & Program ESP32 | 29 Maret - 4 April 2026 | 1 minggu | ✅ |
| 5 | Pengumpulan Data Sensor | 5-25 April 2026 | 3 minggu | ✅ |
| 6 | Pengolahan Data & Training | 26 April - 9 Mei 2026 | 2 minggu | ✅ |
| 7 | **Kalibrasi Sensor** | **10-16 Mei 2026** | **1 minggu** | ❌ |
| 8 | **Uji Responden** | **17-30 Mei 2026** | **2 minggu** | ❌ |
| 9 | **Analisis Hasil** | **31 Mei - 6 Juni 2026** | **1 minggu** | ❌ |
| 10 | **Deploy ke ESP32** | **7-13 Juni 2026** | **1 minggu** | ❌ |
| 11 | **Penyusunan Laporan** | **14-27 Juni 2026** | **2 minggu** | ❌ |
| 12 | **Revisi & Finalisasi** | **28-30 Juni 2026** | **3 hari** | ❌ |

---

## 🔬 Tahap 7: Kalibrasi Sensor (10-16 Mei 2026)

### Tujuan
Validasi akurasi 3 sensor SENS-Able terhadap alat standar medis.

### Alat yang Dibutuhkan
| No | Alat Standar | Untuk Mengkalibrasi | Harga Estimasi |
|---|---|---|---|
| 1 | Glukometer (ACCU-CHEK / EasyTouch) | Estimasi glukosa dari MAX30102 | Rp 150.000 - 300.000 |
| 2 | Pulse Oximeter (Yuwell / Omron) | HR & SpO2 dari MAX30102 | Rp 100.000 - 250.000 |
| 3 | Termometer Digital (Omron / Beurer) | Suhu dari MLX90614 | Rp 50.000 - 150.000 |

### Prosedur Kalibrasi

#### 7a. Kalibrasi Glukosa (MAX30102 vs Glukometer)
```
1. Siapkan 10 responden (beragam usia & kondisi)
2. Minta responden cuci tangan, keringkan
3. Ukur dengan glukometer (ambil darah ujung jari)
4. Langsung ukur dengan SENS-Able (jari yang sama)
5. Catat: Glukometer = referensi, SENS-Able = prediksi
6. Ulangi 3× per responden (pagi, siang, malam)
7. Total: 30 pasang data
```

#### 7b. Kalibrasi HR & SpO2 (MAX30102 vs Pulse Oximeter)
```
1. Responden duduk tenang selama 2 menit
2. Pasang pulse oximeter di jari tangan kiri
3. Pasang sensor MAX30102 di jari tangan kanan
4. Baca kedua alat secara bersamaan
5. Catat: Pulse Oximeter = referensi, MAX30102 = prediksi
6. Ulangi 3× per responden (istirahat, setelah jalan, setelah naik tangga)
7. Total: 30 pasang data
```

#### 7c. Kalibrasi Suhu (MLX90614 vs Termometer Digital)
```
1. Responden duduk di ruangan 25-27°C selama 5 menit
2. Ukur dahi dengan termometer digital
3. Ukur dahi dengan MLX90614 (jarak 3-5 cm)
4. Catat: Termometer = referensi, MLX90614 = prediksi
5. Ulangi 3× per responden
6. Total: 30 pasang data
```

### Template Pencatatan Kalibrasi

| No | Nama | Usia | Waktu | Glukometer | SENS-Able | Selisih |
|---|---|---|---|---|---|---|
| 1 | ... | ... | Pagi | ... | ... | ... |
| 2 | ... | ... | Siang | ... | ... | ... |
| 3 | ... | ... | Malam | ... | ... | ... |

### Perhitungan yang Harus Dilakukan

```
MAE = Σ|nilai_referensi - nilai_prediksi| / n
RMSE = √(Σ(nilai_referensi - nilai_prediksi)² / n)
Korelasi Pearson = r(X,Y)
```

### Target Keberhasilan

| Parameter | Target MAE | Target Korelasi |
|---|---|---|
| Glukosa | < 15 mg/dL | r > 0.8 |
| HR | < 3 bpm | r > 0.9 |
| SpO2 | < 2% | r > 0.8 |
| Suhu | < 0.3°C | r > 0.9 |

### Output Kalibrasi
- [ ] Tabel MAE per parameter
- [ ] Grafik korelasi (scatter plot referensi vs prediksi)
- [ ] Tabel selisih per pengukuran
- [ ] Kesimpulan: sensor lolos/tidak lolos kalibrasi

---

## 👥 Tahap 8: Uji Responden (17-30 Mei 2026)

### Tujuan
Uji apakah penyandang disabilitas bisa menggunakan alat secara mandiri.

### Responden

| Kategori | Jumlah | Kriteria Inklusi | Kriteria Eklusi |
|---|---|---|---|
| Tunanetra | 5 | Usia 15-60, tinggal di Bima | Buta total + tuli |
| Tunarungu | 5 | Usia 15-60, tinggal di Bima | Tuli total + buta |
| Non-disabilitas | 5 | Usia 15-60, sehat | Gangguan motorik |

**Total**: 15 responden × 30 pengukuran = 450 data per parameter

### Prosedur Uji per Responden

```
LANGKAH 1: Persiapan (5 menit)
├── Perkenalkan diri & tujuan penelitian
├── Minta izin (form consent)
├── Jelaskan alat: "Ini alat untuk mengukur gula darah, detak jantung, dan suhu"
└── Tunjukkan komponen: sensor, OLED, speaker, vibromotor

LANGKAH 2: Demonstrasi (5 menit)
├── Taruh jari di sensor MAX30102
├── Tunjukkan hasil di OLED: "Gula darah Anda 100, normal"
├── Putar audio: "Gula darah Anda seratus, kondisi normal"
├── Rasakan getaran: 1 getaran pendek = normal
└── Tanya: "Paham cara pakainya?"

LANGKAH 3: Uji Mandiri (10 menit)
├── Minta responden coba sendiri TANPA bantuan
├── Catat:
│   ├── Berhasil pasang jari? (Ya/Tidak)
│   ├── Berhasil baca hasil? (Ya/Tidak)
│   ├── Waktu dari pasang jari sampai paham hasil (detik)
│   ├── Butuh bantuan? (Ya/Tidak, berapa kali)
│   └── Kendala apa? (catat detail)
└── Ulangi 3× per responden

LANGKAH 4: Kuesioner (5 menit)
├── Isi kuesioner Likert 1-5
├── Untuk tunanetra: dibacakan oleh peneliti
├── Untuk tunarungu: ditulis di kertas besar
└── Tunjukkan skala dengan gestur/jari

LANGKAH 5: Wawancara Singkat (5 menit)
├── "Bagaimana pengalaman menggunakan alat ini?"
├── "Apa yang paling mudah/sulit?"
├── "Ada saran untuk perbaikan?"
└── "Mau pakai alat ini setiap hari?"
```

### Template Pencatatan Uji Responden

| No | Nama | Kategori | Usia | Gender | Berhasil Pasang | Berhasil Baca | Waktu (detik) | Butuh Bantuan | Kendala |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ... | Tunanetra | ... | ... | Ya/Tidak | Ya/Tidak | ... | Ya(×)/Tidak | ... |

### Kuesioner Usability (Likert 1-5)

| No | Pernyataan | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 1 | Alat ini mudah digunakan setelah 1 demonstrasi | ○ | ○ | ○ | ○ | ○ |
| 2 | Output audio cukup jelas untuk memahami hasil | ○ | ○ | ○ | ○ | ○ |
| 3 | Output visual cukup jelas untuk memahami hasil | ○ | ○ | ○ | ○ | ○ |
| 4 | Output getaran cukup jelas untuk memahami hasil | ○ | ○ | ○ | ○ | ○ |
| 5 | Alat ini membantu saya memantau kesehatan mandiri | ○ | ○ | ○ | ○ | ○ |
| 6 | Saya merasa aman menggunakan alat ini | ○ | ○ | ○ | ○ | ○ |
| 7 | Alat ini cocok untuk penyandang disabilitas | ○ | ○ | ○ | ○ | ○ |

**Keterangan**: 1=Sangat Tidak Setuju, 2=Tidak Setuju, 3=Netral, 4=Setuju, 5=Sangat Setuju

### Target Keberhasilan

| Indikator | Target | Cara Hitung |
|---|---|---|
| Skor usability rata-rata | ≥ 4.0 | Rata-rata semua pertanyaan |
| Responden bisa mandiri | ≥ 80% | (Berhasil mandiri / Total responden) × 100 |
| Waktu respons | < 10 detik | Rata-rata waktu pasang jari → paham hasil |
| Kendala minimal | < 20% | (Ada kendala / Total responden) × 100 |

### Output Uji Responden
- [ ] Tabel data per responden (15 baris)
- [ ] Tabel kuesioner per responden (15 baris × 7 pertanyaan)
- [ ] Grafik skor usability per kategori
- [ ] Grafik waktu respons per kategori
- [ ] Rekap kendala & saran
- [ ] Kesimpulan: lolos/tidak lolos uji usability

---

## 📊 Tahap 9: Analisis Hasil (31 Mei - 6 Juni 2026)

### Analisis Kuantitatif

| Analisis | Metode | Tool |
|---|---|---|
| Akurasi sensor | MAE, RMSE | Excel / Python |
| Korelasi sensor vs referensi | Pearson r | Excel / Python |
| Skor usability | Rata-rata Likert | Excel |
| Perbandingan kategori | ANOVA / Kruskal-Wallis | Python (scipy) |
| Waktu respons | Rata-rata, min, max, std | Excel / Python |

### Analisis Kualitatif

| Data | Metode |
|---|---|
| Kendala responden | Kategorisasi (sensor/audio/visual/getaran) |
| Saran responden | Klasterisasi tema |
| Observasi penggunaan | Deskripsi naratif |

### Output Analisis
- [ ] Tabel ringkasan statistik
- [ ] Grafik MAE per parameter
- [ ] Grafik korelasi (scatter plot)
- [ ] Grafik skor usability per kategori
- [ ] Grafik waktu respons per kategori
- [ ] Tabel perbandingan kategori disabilitas
- [ ] Pembahasan: apakah target tercapai?

---

## 🖥️ Tahap 10: Deploy ke ESP32 (7-13 Juni 2026)

### Tujuan
Model AI berjalan di ESP32 dengan TensorFlow Lite Micro.

### Langkah Detail

```
1. Persiapan Model
   ├── Buka train.py → pastikan model.pkl ada
   ├── Install: pip install tensorflow
   ├── Load model.pkl → konversi ke SavedModel
   └── Konversi ke TFLite: converter = tf.lite.TFLiteConverter

2. Optimasi Model
   ├── Quantization (INT8) → kurangi ukuran
   ├── Cek ukuran file (target < 100KB)
   └── Cek akurasi setelah quantization (target ≥ 70%)

3. Konversi ke C Array
   ├── xxd -i model.tflite > model.h
   ├── Cek isi model.h (array of bytes)
   └── Copy model.h ke folder Arduino project

4. Arduino Sketch
   ├── Include: TensorFlowLite_ESP32.h
   ├── Include: model.h
   ├── Setup: load model, allocate tensor
   ├── Loop: baca sensor → inference → output
   └── Output: OLED + Speaker + Vibromotor

5. Flash & Test
   ├── Upload ke ESP32 via USB
   ├── Buka Serial Monitor (115200 baud)
   ├── Test dengan jari → cek hasil
   ├── Catat: inference time (ms)
   ├── Catat: memory usage (bytes)
   └── Bandingkan dengan akurasi di PC

6. Dokumentasi
   ├── Foto setup hardware
   ├── Screenshot Serial Monitor
   ├── Video demo alat berjalan
   └── Tabel perbandingan akurasi (PC vs ESP32)
```

### Target Deploy

| Metrik | Target |
|---|---|
| Ukuran model | < 100 KB |
| Inference time | < 100 ms |
| RAM usage | < 50 KB |
| Akurasi di ESP32 | ≥ 70% |

### Output Deploy
- [ ] File model.h (C array)
- [ ] Arduino sketch (.ino)
- [ ] Foto hardware berjalan
- [ ] Video demo
- [ ] Tabel performa (ukuran, waktu, memori, akurasi)

---

## 📝 Tahap 11-12: Penyusunan Laporan (14-30 Juni 2026)

### Struktur Laporan

```
HALAMAN DEPAN
├── Judul
├── Nama tim & sekolah
├── Tahun
└── Logo sekolah (opsional)

KATA PENGANTAR
DAFTAR ISI
DAFTAR TABEL
DAFTAR GAMBAR

BAB 1. PENDAHULUAN
├── 1.1 Latar Belakang
├── 1.2 Rumusan Masalah
├── 1.3 Tujuan Penelitian
└── 1.4 Manfaat Penelitian

BAB 2. TINJAUAN PUSTAKA
├── 2.1 Landasan Teori
└── 2.2 Studi Pustaka

BAB 3. METODE PENELITIAN
├── 3.1 Waktu dan Tempat
├── 3.2 Alat dan Bahan
├── 3.3 Prosedur Penelitian
└── 3.4 Pengolahan Data

BAB 4. HASIL DAN PEMBAHASAN
├── 4.1 Hasil Kalibrasi Sensor
│   ├── Tabel MAE per parameter
│   ├── Grafik korelasi
│   └── Pembahasan akurasi
├── 4.2 Hasil Uji Responden
│   ├── Tabel data per responden
│   ├── Grafik skor usability
│   ├── Grafik waktu respons
│   └── Pembahasan inklusivitas
├── 4.3 Hasil Training Model AI
│   ├── Tabel akurasi model
│   ├── Feature importance
│   └── Pembahasan performa
└── 4.4 Hasil Deploy ESP32
    ├── Tabel performa embedded
    ├── Foto/video demo
    └── Pembahasan feasibility

BAB 5. KESIMPULAN DAN SARAN
├── 5.1 Kesimpulan
└── 5.2 Saran

DAFTAR PUSTAKA
LAMPIRAN
├── Lampiran 1: Kuesioner Usability
├── Lampiran 2: Data Kalibrasi
├── Lampiran 3: Data Responden
├── Lampiran 4: Foto Alat
├── Lampiran 5: Kode Program
└── Lampiran 6: Bukti Ethics Approval (opsional)
```

### Checklist Laporan

| Bagian | Deadline | Status |
|---|---|---|
| BAB 1 (Pendahuluan) | 14 Juni | ❌ Sudah ada di proposal, sesuaikan |
| BAB 2 (Tinjauan Pustaka) | 15 Juni | ❌ Sudah ada di proposal, tambahkan |
| BAB 3 (Metode) | 16 Juni | ❌ Sudah ada di proposal, update |
| BAB 4.1 (Kalibrasi) | 20 Juni | ❌ Butuh data kalibrasi |
| BAB 4.2 (Responden) | 22 Juni | ❌ Butuh data uji responden |
| BAB 4.3 (Training AI) | 23 Juni | ❌ Sudah ada, tinggal tulis |
| BAB 4.4 (Deploy ESP32) | 24 Juni | ❌ Butuh data deploy |
| BAB 5 (Kesimpulan) | 25 Juni | ❌ |
| Daftar Pustaka | 26 Juni | ❌ |
| Lampiran | 27 Juni | ❌ |
| Revisi | 28-29 Juni | ❌ |
| Finalisasi & Cetak | 30 Juni | ❌ |

---

## ✅ Master Checklist

### Persiapan
- [ ] Komponen lengkap & berfungsi
- [ ] ESP32 terprogram & terkalibrasi
- [ ] Template pencatatan siap
- [ ] Kuesioner dicetak (15 lembar)
- [ ] Form consent disiapkan
- [ ] Izin dari pihak sekolah
- [ ] Jadwal responden dikonfirmasi

### Kalibrasi (Tahap 7)
- [ ] Glukometer tersedia & berfungsi
- [ ] Pulse oximeter tersedia & berfungsi
- [ ] Termometer digital tersedia & berfungsi
- [ ] 10 responden kalibrasi siap
- [ ] Ruangan 25-27°C tersedia
- [ ] Data kalibrasi terkumpul (30 pasang per parameter)
- [ ] MAE dihitung
- [ ] Korelasi dihitung
- [ ] Keputusan: lolos/tidak lolos

### Uji Responden (Tahap 8)
- [ ] 5 tunanetra terkonfirmasi
- [ ] 5 tunarungu terkonfirmasi
- [ ] 5 non-disabilitas terkonfirmasi
- [ ] Skrip demonstrasi siap
- [ ] Kuesioner tercetak
- [ ] Form consent ditandatangani
- [ ] Data uji terkumpul (450 data)
- [ ] Kuesioner terkumpul (15 lembar)
- [ ] Wawancara tercatat

### Analisis (Tahap 9)
- [ ] MAE, RMSE, korelasi dihitung
- [ ] Skor usability dihitung
- [ ] Perbandingan kategori dianalisis
- [ ] Grafik dibuat
- [ ] Tabel ringkasan dibuat
- [ ] Kesimpulan ditulis

### Deploy ESP32 (Tahap 10)
- [ ] Model dikonversi ke TFLite
- [ ] Quantization dilakukan
- [ ] C array dibuat
- [ ] Arduino sketch ditulis
- [ ] ESP32 diflash
- [ ] Inference time diukur
- [ ] Memory usage diukur
- [ ] Akurasi dicek
- [ ] Demo video direkam

### Laporan (Tahap 11-12)
- [ ] BAB 1-3 diperbarui
- [ ] BAB 4 ditulis lengkap
- [ ] BAB 5 ditulis
- [ ] Daftar pustaka dilengkapi
- [ ] Lampiran dikumpulkan
- [ ] Revisi dosen/pembimbing
- [ ] Finalisasi & cetak

---

## ⚠️ Risiko & Mitigasi Spesifik

| No | Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|---|
| 1 | Glukometer tidak tersedia | Sedang | Tinggi | Pinjam dari Puskesmas / beli bersama |
| 2 | Responden tunanetra sulit dihubungi | Sedang | Tinggi | Hubungi Dinas Sosial / yayasan disabilitas |
| 3 | Sensor MAX30102 tidak akurat | Rendah | Tinggi | Ganti sensor / kalibrasi ulang |
| 4 | Model terlalu besar untuk ESP32 | Sedang | Sedang | Quantize INT8 / kurangi fitur |
| 5 | Responden menolak ikut | Rendah | Sedang | Siapkan pengganti + motivasi |
| 6 | Waktu mepet | Sedang | Tinggi | Mulai laporan paralel dengan uji |
| 7 | ESP32 memory overflow | Rendah | Tinggi | Optimasi kode / pakai ESP32-S3 |
| 8 | Audio tidak jelas di ruangan ramai | Sedang | Sedang | Tambah volume / pakai headphone |
| 9 | Getaran terlalu lemah | Rendah | Sedang | Ganti vibromotor yang lebih kuat |
| 10 | Listrik mati saat uji | Rendah | Rendah | Siapkan powerbank 5V-2A |

---

## 📁 File Terkait

| File | Keterangan |
|---|---|
| `train.py` | Script training model |
| `data/processed/sensable_validation.csv` | Dataset processed (40 sesi, 32 SubjectID; suhu nol yang recoverable diberi flag imputasi) |
| `report.json` | Hasil baseline klasifikasi historis |
| `reports/glucometer_validation.json` | Hasil validasi regresi terhadap `GlukosaRef` dari glucometer |
| `docs/proposal.pdf` | Proposal penelitian |
| `docs/chat_history.md` | History pengolahan data |
| `docs/planning.md` | File ini |
