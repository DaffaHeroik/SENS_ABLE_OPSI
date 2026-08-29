# RINGKASAN EKSEKUTIF — SENS-Able

## SENS-Able: Smart Health Monitor Inklusif Berbasis AI untuk Penyandang Disabilitas

**Tim**: AntroOptic Team — Muhammad Daffa Ramadhan & Aira Cantika Putri
**Sekolah**: MAN 2 Kota Bima, NTB | **Tahun**: 2026

---

### MASALAH
Diabetes mellitus menjangkit 10,9% populasi Indonesia (Riskesdas 2018). Deteksi dini memerlukan pemantauan glukosa darah rutin, namun alat konvensional (glucometer) sulit digunakan oleh **23,96 juta penyandang disabilitas** — tunanetra tidak bisa melihat hasil, tunarungu memerlukan modifikasi komunikasi. Harga alat kesehatan khusus disabilitas masih mahal dan sulit diakses.

### SOLUSI
**SENS-Able** — sistem pemantauan kesehatan **inklusif** berbasis ESP32 + AI yang mengintegrasikan:
- **Sensor**: MAX30102 (PPG → glukosa, HR, SpO2) + MLX90614 (suhu inframerah)
- **AI**: Random Forest 200 trees → estimasi glukosa dari sinyal PPG
- **Output Multimodal**: OLED (visual) + Speaker (audio) + Vibromotor (haptic/getaran)
- **Biaya**: ~Rp 444.900 (terjangkau untuk komunitas disabilitas)

### CARA KERJA
```
Jari di sensor → ESP32 baca PPG (10 detik)
→ Hitung 22 fitur → Model AI prediksi glukosa
→ Output simultan: Tampilan OLED + Beep + Getaran
```

### HASIL UTAMA

| Parameter | Hasil | Status |
|---|---|---|
| Dataset | 40 sesi, 32 responden, 22 fitur | ✅ |
| Estimasi Glukosa | MAE 22,57 mg/dL, R² 0,061 | ⚠️ Eksploratif |
| Deploy ESP32 | Inference < 1 ms, RAM 30 KB | ✅ |
| Compile Firmware | 0 error, 186 KB model | ✅ |

**Interpretasi jujur**: Model bersifat eksploratif. Sensor PPG consumer memiliki limitasi untuk estimasi glukosa akurat. Namun, prototipe membuktikan bahwa pipeline PPG → AI → multimodal output BERHASIL diimplementasikan di ESP32.

### KEUNGGULAN (3 Dimensi Kebaruan)

| Dimensi | SENS-Able | Studi Lain |
|---|---|---|
| **Inklusivitas** | Audio + Visual + Haptic | Visual saja |
| **Platform** | ESP32 (embedded, offline) | PC / Cloud |
| **Multi-param** | Glukosa + HR + SpO2 + Suhu | 1 parameter |
| **Biaya** | ~Rp 445.000 | > Rp 1.000.000 |

### KETERBATASAN (Diakui dengan Jujur)
1. Dataset kecil (40 sesi) — belum validasi klinis
2. R² 0,061 — model menjelaskan hanya 6% variansi
3. Tidak ada timestamp pairing sensor-glucometer
4. Audio/vibrasi perlu uji lapangan formal

### REKOMENDASI
1. Kumpulkan 200–500 data untuk validasi lebih kuat
2. Upgrade sensor PPG ke tipe klinis (ADPD6010/MAX86150)
3. Integrasi ECG sebagai fitur multimodal tambahan
4. Lakukan uji klinis dengan IRB approval

### POTENSI DAMPAK
SENS-Able menjadi **prototipe awal** alat kesehatan inklusif yang terjangkau untuk komunitas disabilitas di Indonesia. Dengan pengembangan lebih lanjut, sistem ini berpotensi menjadi solusi skrining dini yang accessible dan affordable.

---

**Repository**: https://github.com/DaffaHeroik/SENS_ABLE_OPSI
**Status**: Prototipe eksploratif — belum untuk penggunaan klinis
