# RINGKASAN EKSEKUTIF — SENS-Able

## SENS-Able: Smart Health Monitor Inklusif Berbasis AI untuk Penyandang Disabilitas

**Tim**: AntroOptic Team — Muhammad Daffa Ramadhan & Aira Cantika Putri  
**Sekolah**: MAN 2 Kota Bima, NTB | **Kompetisi**: OPSI 2026 | **Kategori**: Kesehatan dan Pangan

---

### MASALAH

Diabetes mellitus menjangkit 10,9% populasi Indonesia dewasa (Riskesdas 2018, Kemenkes RI). Deteksi dini memerlukan pemantauan glukosa darah rutin, namun alat konvensional (glucometer) memerlukan pengambilan darah dari jari — sulit digunakan oleh **23,96 juta penyandang disabilitas** Indonesia: tunanetra tidak bisa melihat hasil pada layar, tunarungu memerlukan modifikasi komunikasi. Alat kesehatan inklusif komersial masih mahal (> Rp 1 juta) dan sulit diakses di daerah terpencil seperti Nusa Tenggara.

### SOLUSI

**SENS-Able** — sistem pemantauan kesehatan **inklusif** berbasis ESP32 + AI (TinyML) yang mengintegrasikan:

| Komponen | Detail |
|---|---|
| **Sensor** | MAX30102 (PPG → glukosa, HR, SpO2) + MLX90614 (suhu inframerah) |
| **AI** | Random Forest Regressor (200 trees, 22 fitur) → estimasi glukosa on-device |
| **Output** | OLED 0.96" (visual) + Speaker/Buzzer (audio) + Vibromotor (haptic) |
| **Platform** | ESP32 — berjalan offline tanpa internet |
| **Biaya** | ~Rp 444.900 (terjangkau untuk komunitas disabilitas) |

### CARA KERJA

```
┌──────────────────────────────────────────────────────────┐
│  Jari di MAX30102 → Rekam PPG 10 detik (1002 sampel)    │
│  → Baca suhu MLX90614 → Hitung 22 fitur                 │
│  → RF 200 trees prediksi glukosa (< 1 ms)               │
│  → Output simultan: Tampilan + Beep + Getaran            │
│                                                              │
│  Tunanetra → Dengar beep (1=normal, 2=pre-DM, 3=DM)     │
│  Tunarungu → Lihat teks + angka di OLED                  │
│  Keduanya → Dapat konfirmasi via vibromotor               │
└──────────────────────────────────────────────────────────┘
```

### HASIL UTAMA

| Parameter | Hasil | Status |
|---|---|---|
| Dataset | 40 sesi, 32 responden, 22 fitur | ✅ Selesai |
| Pipeline data | 237 raw → 46 unik → 40 bersih | ✅ Validated |
| Estimasi Glukosa | MAE 22,57 mg/dL, R² 0,061 | ⚠️ Eksploratif |
| Deploy ESP32 | Inference < 1 ms, RAM ~30 KB, 0 error | ✅ Feasible |
| Firmware | v1.2, compile clean, 186 KB model | ✅ Ter-upload |

**Interpretasi Jujur:**

- MAE 22,57 mg/dL → rata-rata prediksi menyimpang ±22,57 mg/dL dari glucometer.
- R² = 0,061 → model menjelaskan hanya 6,1% variansi glukosa.
- **Kesimpulan**: Prototipe membuktikan pipeline PPG → AI → multimodal output BERHASIL diimplementasikan di ESP32. Namun, estimasi glukosa dari PPG sensor consumer masih sangat eksploratif dan memerlukan validasi klinis lebih lanjut.

### KEUNGGULAN — 3 Dimensi Kebaruan

| Dimensi | SENS-Able | Studi Lain |
|---|---|---|
| **Inklusivitas** | Audio + Visual + Haptic (3 kanal) | Visual saja (1 kanal) |
| **Platform** | ESP32 embedded, offline, standalone | PC / Cloud / Smartphone |
| **Multi-param** | Glukosa + HR + SpO2 + Suhu | Fokus 1 parameter |
| **Biaya** | ~Rp 445.000 | > Rp 1.000.000 |

### PERBANDINGAN DENGAN STUDI LAIN

| Peneliti | Sensor | Metode | MAE | Sampel | Platform |
|---|---|---|---|---|---|
| Castillo et al. (2023) | ADPD6010 (klinis) | LSTM | 18,3 | 43 | PC |
| Prema et al. (2022) | ECG+PPG | CNN-LSTM | 12,5 | 150 | PC |
| Tamura et al. (2017) | PPG | ANN | 15,2 | 240 | PC |
| **SENS-Able (ini)** | **MAX30102 (consumer)** | **RF** | **22,57** | **40** | **ESP32** |

### KETERBATASAN (Diakui dengan Jujur)

1. Dataset kecil (40 sesi) — belum validasi klinis, memerlukan 200–500 data
2. R² = 0,061 — model menjelaskan hanya 6% variansi
3. Sensor consumer — MAX30102 dirancang untuk HR/SpO2, bukan glukosa
4. Variasi antar-fold tinggi — R² berkisar dari +0,667 hingga -0,459
5. Uji usability dan kalibrasi sensor perlu dilengkapi dengan data lapangan

### POTENSI DAMPAK

SENS-Able menjadi **prototipe awal** alat kesehatan inklusif yang terjangkau untuk komunitas disabilitas di Indonesia. Dengan pengembangan lebih lanjut (dataset lebih besar, sensor klinis, validasi klinis), sistem ini berpotensi menjadi solusi skrining dini yang accessible dan affordable — khususnya untuk daerah terpencil dengan infrastruktur kesehatan terbatas.

---

**Repository**: https://github.com/DaffaHeroik/SENS_ABLE_OPSI  
**Status**: Prototipe eksploratif — bukan alat klinis, belum untuk diagnosis  
**Tim**: AntroOptic — Daffa & Aira, MAN 2 Kota Bima
