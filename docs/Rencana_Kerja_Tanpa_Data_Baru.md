# Rencana Kerja SENS-Able — Tanpa Data Glukosa Baru

> **Kondisi**: Chip glukometer habis. Tidak bisa tambah data GlukosaRef baru.
> **Data saat ini**: 40 sesi, 32 subjek, MAE 22.57 mg/dL, R² 0.06
> **Deadline OPSI**: 31 Agustus 2026

---

## 🎯 Yang HARUS Kamu Fokuskan SEKARANG

### Prioritas 1: Uji Responden + Usability (PALING PENTING!)

Ini **nilai jual terbesar** proposal kamu — alat inklusif untuk disabilitas. Banyak peneliti buat PPG-glucose, tapi **hampir tidak ada yang uji dengan tunanetra & tunarungu**.

**Yang perlu dilakukan:**
```
1. Hubungi 15 responden:
   - 5 tunanetra (hubungi SLB / yayasan disabilitas di Bima)
   - 5 tunarungu (hubungi SLB / YPLAB)
   - 5 non-disabilitas (teman sebaya)

2. Jadwalkan sesi uji (30 menit per orang):
   - Persiapan + consent (5 menit)
   - Demonstrasi alat (5 menit)
   - Uji mandiri (10 menit)
   - Kuesioner Likert (5 menit)
   - Wawancara singkat (5 menit)

3. Yang DICATAT:
   - Berhasil pasang jari? (Ya/Tidak)
   - Waktu pasang → paham hasil (detik)
   - Butuh bantuan? (Ya/Tidak, berapa kali)
   - Kendala apa? (detail)
   - Skor kuesioner 7 pertanyaan × 1-5

4. Rekam VIDEO demo:
   - Tunanetra pakai alat (dengar audio)
   - Tunarungu pakai alat (lihat OLED + getaran)
   - Non-disabilitas pakai alat
```

**Target:**
| Indikator | Target |
|---|---|
| Skor usability rata-rata | ≥ 4.0 |
| Bisa mandiri | ≥ 80% (12 dari 15 orang) |
| Waktu respons | < 10 detik |

---

### Prioritas 2: Kalibrasi Sensor HR, SpO2, Suhu

**Tanpa chip glukometer, kamu MASIH BISA kalibrasi 3 sensor lain:**

| Sensor | Alat Referensi | Harga | Target |
|---|---|---|---|
| MAX30102 → HR | Pulse Oximeter | Rp 100-250rb | MAE < 3 bpm |
| MAX30102 → SpO2 | Pulse Oximeter | (sama) | MAE < 2% |
| MLX90614 → Suhu | Termometer Digital | Rp 50-150rb | MAE < 0.3°C |

**Prosedur:**
```
1. Siapkan 10 responden (bisa responden yang sama)
2. Ukur HR & SpO2:
   - Pulse Oximeter di tangan kiri
   - SENS-Able (MAX30102) di tangan kanan
   - Catat kedua nilai → hitung MAE, korelasi
3. Ukur Suhu:
   - Termometer digital di dahi
   - MLX90614 di dahi (jarak 3-5cm)
   - Catat → hitung MAE, korelasi
4. Total: 30 pasang data per parameter
```

**Output untuk laporan:**
- Tabel MAE per parameter
- Grafik scatter plot (referensi vs prediksi)
- Kesimpulan: sensor lolos/tidak lolos

---

### Prioritas 3: Deploy Firmware + Rekam Video Demo

**Firmware sudah siap di GitHub!** Yang perlu kamu lakukan:

```
1. Buka Arduino IDE
2. Pull: firmware/SENS_ABLE_Glucose_Predictor.ino
3. Install library:
   - ESP32 by Espressif
   - Adafruit SSD1306
   - Adafruit GFX
   - MAX30100 by Kontakt
4. Upload ke ESP32
5. Test:
   - Colokkan jari ke MAX30102
   - Tunggu 10 detik
   - Lihat hasil di OLED
   - Dengar beep dari buzzer (GPIO 23)
6. Catat untuk laporan:
   - Inference time (ms)
   - Memory usage (bytes)
   - Konsistensi hasil (test 10×)
```

**Video demo (30-60 detik):**
```
[0-10s]  Foto rangkaian alat (ESP32 + sensor + OLED + buzzer)
[10-20s] Seseorang letakkan jari di sensor
[20-30s] Tampilan OLED: "Glucose: 105 mg/dL, Pre-diabetic"
[30-40s] Buzzer berbunyi: 2 beep (= pre-diabetic)
[40-50s] Tampilan web dashboard via WiFi
[50-60s] Penjelasan singkat: "Ini SENS-Able, alat kesehatan inklusif"
```

---

### Prioritas 4: Optimasi Model (Tanpa Data Baru)

**Karena R² masih 0.06, coba pendekatan berbeda:**

#### Opsi A: Klasifikasi (Bukan Regresi)
```
Daripada prediksi angka mg/dL → klasifikasikan:
- Normal (<100 mg/dL)     → 15 orang
- Pre-DM (100-125 mg/dL)  → 14 orang  
- DM (≥126 mg/dL)         → 11 orang

Keuntungan: klasifikasi lebih mudah dari regresi untuk data kecil
```

#### Opsi B: Ridge Regression dengan Fitur Terpilih
```
Kurangi dari 22 fitur → 5-8 fitur terbaik:
1. Tinggi_cm (r=0.47)
2. IR_RED_ratio (r=0.38)
3. Ratio_DC (r=0.36)
4. Berat_kg (r=0.30)
5. TerakhirMakan_jam (r=0.30)
```

#### Opsi C: Model Lebih Sederhana
```
Random Forest 200 trees terlalu kompleks untuk 40 data.
Coba:
- Decision Tree (max_depth=3) → lebih interpretable
- Ridge Regression (alpha=10) → regularisasi
```

---

### Prioritas 5: Tulis Laporan

**Struktur yang realistis:**

```
BAB 1: Pendahuluan (2-3 halaman)
  - Latar belakang: diabetes + disabilitas
  - Rumusan masalah
  - Tujuan penelitian

BAB 2: Tinjauan Pustaka (3-4 halaman)
  2.1 Sensor PPG dan keterkaitannya dengan glukosa
  2.2 TinyML di microcontroller (ESP32)
  2.3 Assistive technology untuk disabilitas
  2.4 Studi banding dengan penelitian sejenis

BAB 3: Metode (2-3 halaman)
  3.1 Desain sistem (hardware + software)
  3.2 Dataset (40 sesi, 32 subjek, distribusi)
  3.3 Pipeline preprocessing
  3.4 Arsitektur model (Random Forest)
  3.5 Uji usability (kuesioner Likert)

BAB 4: Hasil dan Pembahasan (4-5 halaman)
  4.1 Kalibrasi sensor HR/SpO2/Suhu
  4.2 Estimasi glukosa (eksploratif)
  4.3 Uji usability responden
  4.4 Deploy ESP32

BAB 5: Kesimpulan dan Saran (1-2 halaman)
  5.1 Kesimpulan
  5.2 Keterbatasan (JUJUR!)
  5.3 Saran pengembangan
```

**Framing yang JUJUR:**
```
✅ "Penelitian ini merupakan evaluasi EKSPLORATIF awal..."
✅ "Sensor MAX30102 menunjukkan potensi untuk estimasi glukosa..."
✅ "Uji usability menunjukkan alat ini dapat digunakan mandiri..."
✅ "Perlu penelitian lebih lanjut dengan data yang lebih besar..."

❌ JANGAN klaim: "Alat ini akurat 90%"
❌ JANGAN klaim: "Siap digunakan di klinik"
```

---

## 📅 Timeline Realistis (Agustus 2026)

| Minggu | Tugas | Output |
|---|---|---|
| **Minggu 1** | Uji 15 responden + Kalibrasi HR/SpO2/Suhu | Data kuesioner + data kalibrasi |
| **Minggu 2** | Deploy ESP32 + Rekam video demo | Video + data performa |
| **Minggu 3** | Tulis BAB 1-3 (Pendahuluan + Pustaka + Metode) | Draft 8-10 halaman |
| **Minggu 4** | Tulis BAB 4-5 (Hasil + Kesimpulan) | Draft 6-8 halaman |
| **Minggu 5** | Finalisasi + Cetak + Kumpul | PDF final |

---

## 💡 Tips untuk Memaksimalkan Skor OPSI

### Yang Dinilai Tinggi:
```
1. METODOLOGI → pipeline data → preprocessing → training → evaluasi
2. KEKUATAN DATA → jelaskan 40 data, distribusi, cleaning rules
3. KEBARUAN → inklusivitas + TinyML + multi-parameter
4. KETERBATASAN JUJUR → "eksploratif" lebih baik dari klaim berlebihan
5. DOKUMENTASI → video demo, foto, data kalibrasi, kuesioner
```

### Yang HARUS ADA:
```
[ ] Tabel distribusi data
[ ] Pipeline preprocessing (flowchart)
[ ] Tabel perbandingan model
[ ] Feature importance / korelasi
[ ] Tabel kalibrasi HR/SpO2/Suhu
[ ] Tabel usability per responden
[ ] Grafik scatter plot
[ ] Foto alat berjalan
[ ] Video demo (30-60 detik)
[ ] Daftar pustaka minimal 10 referensi
```

---

## 🛒 Yang Perlu Dibeli

| No | Alat | Harga | Untuk |
|---|---|---|---|
| 1 | Pulse Oximeter (Yuwell YX301) | Rp 150.000 | Kalibrasi HR & SpO2 |
| 2 | Termometer Digital (Omron) | Rp 75.000 | Kalibrasi suhu |
| 3 | Kertas kuesioner (15 lembar) | Rp 5.000 | Uji usability |
| 4 | Form consent (15 lembar) | Rp 5.000 | Etika penelitian |
| | **Total** | **~Rp 235.000** | |

---

## ⚡ Mulai dari SEKARANG

1. **Hari ini**: Hubungi responden (15 orang)
2. **Besok**: Beli pulse oximeter + termometer
3. **Minggu ini**: Mulai uji responden
4. **Minggu depan**: Deploy ESP32 + rekam video
5. **Minggu berikutnya**: Mulai tulis laporan

**Kamu sudah punya semua yang dibutuhkan. Tinggal EKSEKUSI!** 💪
