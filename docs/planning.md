# SENS-Able — Planning & Timeline

## 📅 Timeline Penelitian

| Tahap | Kegiatan | Target | Status |
|---|---|---|---|
| **1. Persiapan** | Penyusunan & Pengajuan Judul | Maret 2026 | ✅ Selesai |
| **2. Proposal** | Pengajuan Proposal | Maret 2026 | ✅ Selesai |
| **3. Pengumpulan Data** | Pengambilan data sensor responden | April 2026 | ✅ Selesai (33 sampel) |
| **4. Pengolahan Data** | Cleaning, analisis, training model | April-Mei 2026 | ✅ Selesai |
| **5. Kalibrasi Sensor** | Uji akurasi vs alat standar | Mei 2026 | ❌ Belum |
| **6. Uji Responden** | 15 responden × 3 kategori | Mei 2026 | ❌ Belum |
| **7. Kuesioner Usability** | Likert 1-5, observasi mandiri | Mei 2026 | ❌ Belum |
| **8. Deploy ke ESP32** | Konversi TFLite → TinyML | Juni 2026 | ❌ Belum |
| **9. Penyusunan Laporan** | Revisi & finalisasi | Juni 2026 | ❌ Belum |

---

## 📋 Rencana Detail Per Tahap

### Tahap 5: Kalibrasi Sensor
**Tujuan**: Validasi akurasi sensor terhadap alat standar

| Sensor | Alat Standar | Target MAE |
|---|---|---|
| MAX30102 (HR) | Pulse Oximeter | < 3 bpm |
| MLX90614 (Suhu) | Termometer Digital | < 0.3°C |
| MAX30102 (Glukosa) | Glukometer | < 15 mg/dL |

**Prosedur**:
1. Ukur 10 orang dengan sensor SENS-Able
2. Ukur orang yang sama dengan alat standar
3. Hitung MAE, RMSE, korelasi
4. Dokumentasikan selisih per pengukuran

---

### Tahap 6: Uji Responden
**Tujuan**: Uji keberhasilan inklusif

| Kategori | Jumlah | Kriteria |
|---|---|---|
| Tunanetra | 5 | Usia 15-60, punya diabetes/risiko |
| Tunarungu | 5 | Usia 15-60, punya diabetes/risiko |
| Non-disabilitas | 5 | Usia 15-60, kontrol |

**Prosedur**:
1. Demonstrasi penggunaan alat 1×
2. Responden mencoba mandiri
3. Catat: berhasil/gagal, waktu, kendala
4. Kuesioner usability

---

### Tahap 7: Kuesioner Usability
**Tujuan**: Ukur kemudahan penggunaan (Likert 1-5)

**Pertanyaan**:
1. Alat mudah digunakan setelah 1 demonstrasi
2. Output audio cukup jelas untuk memahami hasil
3. Output visual cukup jelas untuk memahami hasil
4. Output getaran cukup jelas untuk memahami hasil
5. Alat membantu saya memantau kesehatan secara mandiri
6. Saya merasa aman menggunakan alat ini
7. Alat cocok untuk penyandang disabilitas

**Indikator**: Skor rata-rata ≥ 4.0

---

### Tahap 8: Deploy ke ESP32
**Tujuan**: Model AI berjalan di mikrokontroler

**Langkah**:
1. Convert model ke TensorFlow Lite
2. Konversi ke C array (xxd -i model.tflite > model.h)
3. Include di Arduino sketch
4. Flash ke ESP32
5. Uji inference time & memory usage

**Target**:
- Inference time < 100ms
- Memory usage < 50KB
- Akurasi tetap ≥ 70%

---

## ✅ Konfirmasi Plan

### Checklist Persiapan Uji

#### Sebelum Uji Kalibrasi
- [ ] Siapkan alat standar (glukometer, pulse oximeter, termometer)
- [ ] Kalibrasi sensor SENS-Able (zero-point calibration)
- [ ] Siapkan template pencatatan data
- [ ] Tentukan 10 responden kalibrasi
- [ ] Siapkan ruangan (25-27°C)

#### Sebelum Uji Responden
- [ ] Pastikan alat berfungsi normal (power, sensor, output)
- [ ] Siapkan skrip demonstrasi (cara pakai alat)
- [ ] Cetak kuesioner Likert (15 lembar)
- [ ] Koordinasi dengan pihak sekolah
- [ ] Dapatkan izin responden/orang tua
- [ ] Siapkan ruangan uji (25-27°C, tenang)
- [ ] Siapkan timer/stopwatch

#### Sebelum Deploy ESP32
- [ ] Install TensorFlow Lite Micro library
- [ ] Siapkan ESP32 + kabel USB
- [ ] Test model.pkl → konversi ke TFLite
- [ ] Flash & test inference di ESP32
- [ ] Dokumentasikan hasil (akurasi, waktu, memori)

#### Sebelum Penyusunan Laporan
- [ ] Kumpulkan semua data (kalibrasi, responden, kuesioner)
- [ ] Hitung statistik (MAE, rata-rata, simpangan baku)
- [ ] Buat grafik/chart hasil pengujian
- [ ] Foto alat & pengujian
- [ ] Draft BAB 4 (Hasil & Pembahasan)
- [ ] Draft BAB 5 (Kesimpulan & Saran)

---

## 📊 Milestone & Deliverables

| Milestone | Deliverable | Deadline |
|---|---|---|
| Data Terkumpul | sensable_final.csv | ✅ Selesai |
| Model Trained | model.pkl + report.json | ✅ Selesai |
| Kalibrasi Selesai | Tabel MAE per sensor | Mei 2026 |
| Uji Responden Selesai | Data 15 responden + kuesioner | Mei 2026 |
| ESP32 Deployed | Firmware + demo video | Juni 2026 |
| Laporan Final | PDF laporan penelitian | Juni 2026 |

---

## ⚠️ Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Sensor tidak akurat | MAE melebihi target | Kalibrasi ulang, ganti sensor |
| Responden sulit mandiri | Skor usability < 4 | Tambah demonstrasi, perbaiki UI |
| Model tidak fit di ESP32 | Memory overflow | Kurangi fitur, quantize model |
| Data kurang representatif | Model bias | Tambah responden beragam |
| Waktu mepet | Laporan terburu-buru | Mulai laporan paralel dengan uji |

---

## 📁 File Terkait

| File | Keterangan |
|---|---|
| `train.py` | Script training model |
| `data/sensable_final.csv` | Dataset bersih |
| `report.json` | Hasil training |
| `docs/proposal.pdf` | Proposal penelitian |
| `docs/chat_history.md` | History pengolahan data |
