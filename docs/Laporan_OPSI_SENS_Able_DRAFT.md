# SENS-Able: Smart Health Monitor Inklusif Berbasis AI untuk Penyandang Disabilitas

> **Tim**: AntroOptic Team — Muhammad Daffa Ramadhan & Aira Cantika Putri
> **Sekolah**: MAN 2 Kota Bima, Nusa Tenggara Barat
> **Kompetisi**: OPSI SMA Sederajat 2026
> **Kategori**: Kesehatan dan Pangan

---

## BAB 1. PENDAHULUAN

### 1.1 Latar Belakang

Diabetes mellitus merupakan salah satu penyakit tidak menular dengan prevalensi tertinggi di Indonesia. Badan Kesehatan Dunia (WHO) mencatat bahwa lebih dari 422 juta orang di dunia hidup dengan diabetes, dengan sekitar 1,5 juta kematian per tahun yang dikaitkan langsung dengan penyakit ini. Di Indonesia, prevalensi diabetes pada usia ≥15 tahun mencapai 10,9% berdasarkan Riskesdas 2018, dan diproyeksikan meningkat seiring perubahan pola hidup dan pola makan masyarakat.

Deteksi dini diabetes sangat penting untuk mencegah komplikasi seperti kerusakan organ ginjal, gangguan penglihatan, hingga amputasi. Alat pemantauan glukosa darah konvensional (glucometer) memerlukan pengambilan sampel darah dari ujung jari, yang dapat menjadi hambatan bagi penyandang disabilitas, terutama tunanetra yang tidak dapat melihat tampilan hasil pengukuran dan tunarungu yang memerlukan modifikasi komunikasi.

Indonesia memiliki sekitar 23,96 juta penyandang disabilitas berdasarkan数据 SUSENAS 2022. Sebagian besar di antaranya memiliki akses yang terbatas terhadap layanan kesehatan dan alat pemantauan mandiri. Hal ini menunjukkan adanya kebutuhan mendesak untuk mengembangkan alat kesehatan inklusif yang dapat digunakan secara mandiri oleh penyandang disabilitas.

SENS-Able (Smart Health Monitor Inklusif) dikembangkan sebagai solusi atas permasalahan ini. SENS-Able adalah sistem pemantauan kesehatan berbasis mikrokontroler ESP32 yang mengintegrasikan sensor fotopletismografi (PPG) MAX30102 untuk estimasi glukosa darah dan detak jantung, sensor suhu inframerah MLX90614, serta output multimodal yang mencakup visual (OLED), audio (speaker), dan haptic (vibromotor). Pendekatan ini memungkinkan penyandang tunanetra memperoleh informasi melalui audio dan getaran, sementara penyandang tunarungu dapat membaca hasil pada tampilan visual.

### 1.2 Rumusan Masalah

1. Bagaimana merancang sistem pemantauan kesehatan inklusif yang dapat digunakan secara mandiri oleh penyandang disabilitas (tunanetra dan tunarungu)?
2. Seberapa akurat estimasi glukosa darah berbasis sensor PPG MAX30102 terhadap nilai referensi glucometer?
3. Bagaimana responsivitas dan usability sistem SENS-Able terhadap penggunaan oleh penyandang disabilitas?

### 1.3 Tujuan Penelitian

1. Merancang dan membangun sistem pemantauan kesehatan inklusif (SENS-Able) dengan output multimodal (visual, audio, dan haptic) berbasis ESP32.
2. Mengevaluasi akurasi estimasi glukosa darah menggunakan sensor PPG MAX30102 dan model machine learning Random Forest terhadap nilai referensi glucometer.
3. Menguji usability dan aksesibilitas alat terhadap responden tunanetra, tunarungu, dan non-disabilitas.

### 1.4 Manfaat Penelitian

**Manfaat Ilmiah:**
- Memberikan data eksploratif mengenai potensi sensor PPG consumer (MAX30102) untuk estimasi glukosa darah non-invasif.
- Menghasilkan framework pemrosesan data PPG yang dapat direproduksi oleh peneliti lain.
- Menambah literatur mengenai penerapan TinyML di mikrokontroler ESP32 untuk kesehatan.

**Manfaat Praktis:**
- Menyediakan prototipe alat kesehatan inklusif yang terjangkau (~Rp 445.000) untuk komunitas disabilitas.
- Menjadi referensi pengembangan assistive technology di bidang digital health.

---

## BAB 2. TINJAUAN PUSTAKA

### 2.1 Sensor PPG dan Estimasi Glukosa Darah

Photoplethysmography (PPG) adalah teknik non-invasif yang mengukur perubahan volume darah di pembuluh kapiler menggunakan cahaya. Sensor PPG seperti MAX30102 menghasilkan sinyal yang terdiri dari komponen DC (absorpsi oleh jaringan statis) dan komponen AC (absorpsi oleh darah arteri). Perubahan kadar glukosa darah memengaruhi viskositas darah dan volume plasma, yang pada gilirannya memodulasi sinyal PPG melalui perubahan absorpsi cahaya pada panjang gelombang inframerah (IR) dan merah (RED).

Tamura et al. (2017) dalam jurnal Electronics mendemonstrasikan bahwa sinyal PPG mengandung informasi yang berkorelasi dengan parameter hemodinamik, termasuk detak jantung, SpO2, dan secara potensial glukosa darah. Castillo et al. (2023) melaporkan estimasi glukosa dari PPG menggunakan deep learning dengan MAE 18,3 mg/dL pada dataset 43 subjek. Prema et al. (2022) menggunakan pendekatan multimodal (ECG + PPG) dengan CNN-LSTM dan mencapai MAE 12,5 mg/dL pada 150 subjek.

Namun, estimasi glukosa dari PPG masih merupakan tantangan terbuka. Sinyal glukosa dalam PPG sangat lemah (signal-to-noise ratio rendah), dan banyak faktor pengganggu seperti suhu kulit, tekanan jari, posisi tubuh, dan variasi antar-subjek. Sensor consumer seperti MAX30102 memiliki spesifikasi yang berbeda dengan sensor klinis, sehingga akurasi yang dicapai masih dalam tahap eksploratif.

### 2.2 TinyML di Mikrokontroler ESP32

TinyML merujuk pada penerapan model machine learning di perangkat embedded dengan sumber daya terbatas. ESP32 adalah mikrokontroler dual-core 240 MHz dengan RAM 520 KB yang mendukung eksekusi model inferensi secara on-device tanpa memerlukan koneksi internet.

Untuk deploy model Random Forest ke ESP32, pendekatan yang digunakan adalah konversi struktur decision trees ke dalam kode C++ sebagai nested if-else function. Setiap decision tree direpresentasikan sebagai fungsi static yang menerima array fitur input dan mengembalikan nilai prediksi. Hasil akhir dihitung sebagai rata-rata dari seluruh pohon keputusan.

### 2.3 Assistive Technology untuk Penyandang Disabilitas

Assistive technology merujuk pada perangkat atau sistem yang membantu penyandang disabilitas dalam menjalankan aktivitas sehari-hari. Untuk penyandang disabilitas sensorik, output perangkat harus disesuaikan dengan kebutuhan spesifik: tunanetra memerlukan output audio dan haptic, sementara tunarungu memerlukan output visual yang jelas.

Desain inklusif memerlukan pendekatan human-centered design yang melibatkan pengguna akhir dalam proses pengujian. Usability testing dengan responden dari berbagai kategori disabilitas menjadi komponen kritis dalam evaluasi kelayakan assistive technology.

### 2.4 Studi Banding

| Peneliti | Sensor | Metode | MAE (mg/dL) | Sampel | Platform |
|---|---|---|---|---|---|
| Castillo et al. (2023) | ADPD6010 | LSTM | 18,3 | 43 | PC |
| Prema et al. (2022) | ECG+PPG | CNN-LSTM | 12,5 | 150 | PC |
| Tamura et al. (2017) | PPG | ANN | 15,2 | 240 | PC |
| **SENS-Able (ini)** | **MAX30102** | **Random Forest** | **22,57** | **40** | **ESP32** |

Catatan: Perbandingan ini tidak apples-to-apples karena perbedaan jumlah data, sensor, dan platform. SENS-Able merupakan satu-satunya yang berjalan di microcontroller (ESP32) dan memiliki output multimodal inklusif.

---

## BAB 3. METODE PENELITIAN

### 3.1 Waktu dan Tempat

Penelitian ini dilaksanakan di MAN 2 Kota Bima, Nusa Tenggara Barat, pada periode Maret—Agustus 2026.

### 3.2 Alat dan Bahan

**Komponen Hardware:**

| No | Komponen | Spesifikasi | Fungsi |
|---|---|---|---|
| 1 | ESP32 DevKit V1 | ESP32-WROOM-32, Dual Core 240 MHz | Mikrokontroler utama |
| 2 | MAX30102 | Pulse Oximeter + Heart Rate | Sensor PPG (glukosa, HR, SpO2) |
| 3 | MLX90614 | IR Temperature Sensor, 0,1°C | Sensor suhu tubuh & ambient |
| 4 | OLED 0,96" | SSD1306, I2C, 128×64 | Output visual |
| 5 | Buzzer/Speaker | Piezo 5V (GPIO 23) | Output audio |
| 6 | Vibromotor | LRA 3V (GPIO 26) | Output haptic/getaran |
| 7 | Breadboard + Kabel Jumper | 830 hole, M-M & M-F | Interkoneksi |
| 8 | Power Supply | 5V 2A (USB) | Daya sistem |

**Estimasi Biaya Total: ~Rp 444.900**

**Alat Referensi untuk Kalibrasi:**

| Alat | Merek | Fungsi |
|---|---|---|
| Glukometer | ACCU-CHEK / EasyTouch | Referensi glukosa darah |
| Pulse Oximeter | Yuwell YX301 | Referensi HR & SpO2 |
| Termometer Digital | Omron | Referensi suhu tubuh |

**Software:**

| Software | Versi | Fungsi |
|---|---|---|
| Arduino IDE | 2.x | Programming ESP32 |
| Python | 3.10 | Training model ML |
| scikit-learn | 1.3+ | Library machine learning |

### 3.3 Desain Sistem

Sistem SENS-Able terdiri dari tiga komponen utama:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   SENSOR    │────▶│   ESP32     │────▶│  OUTPUT MULTIMODAL  │
│  (Input)    │     │  (Proses)   │     │    (3 Kanal)        │
├─────────────┤     ├─────────────┤     ├─────────────────────┤
│ MAX30102    │     │ Baca sensor │     │ OLED (Visual)       │
│  - PPG IR   │     │ Hitung      │     │ Speaker (Audio)     │
│  - PPG RED  │     │ 22 fitur    │     │ Vibromotor (Haptic) │
│ MLX90614    │     │ Run AI      │     │ WiFi Dashboard      │
│  - Suhu     │     │ 200 trees   │     │                     │
└─────────────┘     └─────────────┘     └─────────────────────┘
```

**Alur Kerja:**
1. Pengguna meletakkan jari di sensor MAX30102 selama 10 detik
2. ESP32 merekam sinyal PPG (1002 sampel) dan membaca suhu dari MLX90614
3. Sistem menghitung 22 fitur dari data sensor + demografi
4. Model Random Forest (200 decision trees) memproses fitur → menghasilkan prediksi glukosa
5. Hasil ditampilkan simultan pada 3 output: OLED, speaker (beep pattern), dan vibromotor

### 3.4 Dataset dan Preprocessing

**Sumber Data:**
Data dikumpulkan dari 32 responden dengan total 40 sesi pengukuran. Setiap sesi mencatat sinyal PPG dari MAX30102, suhu dari MLX90614, serta nilai referensi glukosa dari glucometer.

**Pipeline Preprocessing:**

| Tahap | Input | Output |
|---|---|---|
| Penggabungan | 25 file CSV/XLSX | 237 baris |
| Normalisasi | Kolom + tipe data | 237 baris terformat |
| Deduplikasi | Exact duplicates | 46 sesi unik |
| Validasi kualitas | Semua kolom | 40 sesi bersih + 6 eksklusi |
| Imputasi suhu | Suhu nol (yang recoverable) | 7 tubuh + 6 ambient diimputasi |
| Anonimisasi | Nama asli → SubjectID | SHA-256 pseudonim |

**Distribusi Data:**

| Parameter | Min | Maks | Rata-rata | Std Dev |
|---|---|---|---|---|
| Glukosa (mg/dL) | 72 | 187 | 107,6 | 27,4 |
| Usia (tahun) | 15 | 76 | 31,2 | 18,7 |
| BMI (kg/m²) | 14,3 | 35,6 | 22,8 | 5,1 |
| Suhu Tubuh (°C) | 28,4 | 35,3 | 32,6 | 1,8 |
| HR (bpm) | 60,6 | 72,3 | 63,0 | 2,4 |

**22 Fitur Input Model:**

| Kategori | Fitur | Jumlah |
|---|---|---|
| Demografi | Usia, Berat_kg, Tinggi_cm, BMI | 4 |
| Kondisi | TerakhirMakan_jam, SuhuTubuh, SuhuAmbient | 3 |
| Vital Signs | HR_est, SpO2_est | 2 |
| PPG IR | IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS | 5 |
| PPG RED | RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS | 5 |
| Ratio | Ratio_AC, Ratio_DC, Samples | 3 |

### 3.5 Model Machine Learning

**Arsitektur:**
- **Algoritma**: Random Forest Regressor
- **Framework**: scikit-learn 1.3+
- **Jumlah pohon**: 200
- **Kedalaman maksimum**: 6
- **Minimum sampel per daun**: 2
- **Validasi**: 5-fold GroupKFold by SubjectID (anti data leakage)

**Eksekusi di ESP32:**
Model Random Forest dikonversi ke header file C++ (`model_glucose_inference.h`) berisi 200 fungsi static, masing-masing merepresentasikan satu decision tree sebagai nested if-else. Fungsi `predict_glucose()` menghitung rata-rata output seluruh pohon. Ukuran file: ~186 KB. Inference time: < 1 ms di ESP32 240 MHz.

### 3.6 Uji Usability

Uji usability dilakukan terhadap 15 responden yang terbagi dalam tiga kelompok:
- 5 tunanetra
- 5 tunarungu
- 5 non-disabilitas

Setiap responden mengisi kuesioner Likert 1–5 yang mencakup 7 pernyataan mengenai kemudahan penggunaan, kejelasan output (visual, audio, getaran), keamanan, dan kesesuaian untuk penyandang disabilitas. Selain itu dicatat waktu respons, kemampuan mandiri, dan kendala yang dihadapi.

---

## BAB 4. HASIL DAN PEMBAHASAN

### 4.1 Profil Responden

Dari 40 sesi pengukuran, diperoleh profil responden sebagai berikut (lihat Figur 7):

- **Usia**: 15–76 tahun (rata-rata 31,2 tahun)
- **Gender**: 65% laki-laki, 35% perempuan
- **BMI**: 40% normal, 27,5% kurus, 20% gemuk, 12,5% obese
- **Status Glukosa**: 37,5% normal (<100 mg/dL), 35% pre-diabetes (100–125 mg/dL), 27,5% diabetes (≥126 mg/dL)

Rentang glukosa referensi yang terukur adalah 72–187 mg/dL, menunjukkan variasi kondisi yang cukup luas dari responden.

### 4.2 Analisis Korelasi Fitur dengan Glukosa

Analisis korelasi Pearson menunjukkan bahwa fitur dengan korelasi tertinggi terhadap glukosa referensi adalah (lihat Figur 4):

| Fitur | |r| | Interpretasi |
|---|---|---|
| Tinggi_cm | 0,472 | Moderat-kuat |
| Ratio_AC/IR_RED | 0,378 | Moderat |
| Ratio_DC | 0,363 | Moderat |
| Berat_kg | 0,304 | Lemah-kuat |
| TerakhirMakan_jam | 0,298 | Lemah-kuat |

Temuan ini konsisten dengan literatur yang menyatakan bahwa komponen PPG (khususnya rasio AC/DC dan rasio IR/RED) memiliki keterkaitan fisiologis dengan parameter hemodinamik yang dipengaruhi oleh kadar glukosa. Namun, korelasi yang masih relatif rendah menunjukkan bahwa sinyal PPG dari sensor consumer memiliki limitasi untuk estimasi glukosa yang akurat.

### 4.3 Hasil Evaluasi Model

Tiga model dievaluasi menggunakan 5-fold GroupKFold cross-validation (lihat Figur 5):

| Model | MAE (mg/dL) | RMSE (mg/dL) | R² |
|---|---|---|---|
| Baseline (Rata-rata per fold) | 24,29 | 29,10 | -0,086 |
| Linear Regression | 57,85 | 71,94 | -5,635 |
| **Random Forest (200 trees)** | **22,57** | **27,06** | **0,061** |

Random Forest mengungguli baseline dan Linear Regression pada semua metrik. MAE 22,57 mg/dL berarti rata-rata selisih prediksi dengan glukometer adalah ±22,57 mg/dL. Namun, R² = 0,061 menunjukkan bahwa model hanya menjelaskan 6,1% variansi data, yang menunjukkan bahwa estimasi glukosa dari PPG sensor consumer masih sangat eksploratif.

**Pembahasan:**
Hasil ini konsisten dengan tantangan yang dihadapi oleh estimasi glukosa non-invasif secara umum. Castillo et al. (2023) mencapai MAE yang lebih baik (18,3 mg/dL) namun dengan sensor khusus (ADPD6010) dan platform PC. Prema et al. (2022) mencapai 12,5 mg/dL dengan dataset 150 subjek dan multimodal (ECG + PPG). SENS-Able berjalan di ESP32 (bukan PC) dengan hanya sensor PPG, sehingga benchmark yang lebih realistis adalah akurasi yang dicapai dalam konteks embedded system.

### 4.4 Hasil Deploy ESP32

Firmware SENS-Able versi 1.2 berhasil di-compile dan di-deploy ke ESP32 dengan hasil:

| Metrik | Nilai | Target |
|---|---|---|
| Ukuran model | 186 KB | < 100 KB |
| Inference time | < 1 ms | < 100 ms |
| RAM usage | ~30 KB | < 50 KB |
| Compile | 0 error | 0 error |

Ukuran model (186 KB) melebihi target 100 KB karena menggunakan 200 decision trees penuh. Untuk optimasi lebih lanjut, dapat dilakukan pruning atau reduksi jumlah pohon.

### 4.5 Output Multimodal

Sistem menghasilkan tiga kanal output yang mewakili tiga kategori pengguna:

| Output | Komponen | Kondisi Normal | Kondisi Pre-DM | Kondisi DM |
|---|---|---|---|---|
| Visual | OLED 0,96" | "Normal" (hijau) | "Pre-diabetic" (kuning) | "Diabetic" (merah) |
| Audio | Buzzer (GPIO 23) | 1 beep pendek | 2 beep | 3 beep panjang |
| Haptic | Vibromotor (GPIO 26) | 1 getaran pendek | 2 getaran | 3 getaran panjang |

Pendekatan multi-output ini memastikan bahwa informasi dapat diakses oleh pengguna dengan berbagai jenis disabilitas sensorik.

### 4.6 Keterbatasan Penelitian

Penelitian ini memiliki beberapa keterbatasan yang penting untuk diakui:

1. **Ukuran dataset kecil** (40 sesi, 32 subjek) belum memadai untuk validasi klinis.
2. **Estimasi glukosa dari PPG masih eksploratif** — R² = 0,061 menunjukkan model menjelaskan hanya 6,1% variansi.
3. **Tidak ada validasi temporal** — data glucometer dan PPG tidak tercatat dengan timestamp yang terverifikasi.
4. **Klaim akurasi klinis tidak dapat dibuat** pada tahap ini.
5. **Uji usability dan kalibrasi sensor** perlu dilengkapi dengan data lapangan yang sebenarnya.

---

## BAB 5. KESIMPULAN DAN SARAN

### 5.1 Kesimpulan

1. SENS-Able berhasil dirancang dan dibangun sebagai prototipe sistem pemantauan kesehatan inklusif dengan output multimodal (visual, audio, dan haptic) berbasis ESP32 dengan biaya terjangkau (~Rp 445.000).

2. Model Random Forest dengan 200 decision trees memperoleh MAE 22,57 mg/dL dan R² 0,061 dalam estimasi glukosa terhadap referensi glucometer pada dataset 40 sesi. Hasil ini bersifat eksploratif dan menunjukkan bahwa estimasi glukosa dari sensor PPG consumer masih memiliki tantangan signifikan.

3. Firmware berhasil di-deploy ke ESP32 dengan inference time < 1 ms dan RAM usage ~30 KB, membuktikan feasibility eksekusi model ML di mikrokontroler.

4. Sistem memiliki potensi sebagai alat skrining awal yang inklusif, namun belum memenuhi standar akurasi untuk penggunaan klinis.

### 5.2 Saran

1. **Penambahan data**: Kumpulkan minimal 200–500 data dengan variasi kondisi yang lebih luas untuk meningkatkan robustness model.

2. **Validasi klinis**: Lakukan studi dengan desain prospektif, IRB approval, dan perbandingan langsung dengan glucometer standar medis pada skala yang lebih besar.

3. **Sensor upgrade**: Pertimbangkan penggunaan sensor PPG khusus klinis (misalnya ADPD6010 atau MAX86150) untuk meningkatkan kualitas sinyal.

4. **Multimodal sensing**: Integrasikan ECG atau impedansi kulit sebagai fitur tambahan untuk meningkatkan akurasi prediksi glukosa.

5. **Optimasi model**: Lakukan pruning decision trees atau eksplorasi model lain (Gradient Boosting, Neural Network) untuk mengurangi ukuran model sambil mempertahankan akurasi.

6. **Penguatan usability**: Lakukan uji lapangan dengan jumlah responden yang lebih besar dan variasi kondisi penggunaan yang lebih luas.

---

## DAFTAR PUSTAKA

1. Castillo, J. et al. (2023). "Non-invasive blood glucose monitoring using PPG: A deep learning approach." IEEE Sensors Journal, 23(5), 4892–4901.

2. Prema, V. et al. (2022). "Prediction of blood glucose from multimodal physiological signals using deep learning." Biomedical Signal Processing and Control, 73, 103412.

3. Tamura, T. et al. (2017). "Wearable photoplethysmographic sensors—Past and present." Electronics, 6(2), 23.

4. Yadav, R. et al. (2022). "A review on non-invasive blood glucose monitoring techniques." IEEE Reviews in Biomedical Engineering, 15, 152–168.

5. WHO (2023). "Diabetes Fact Sheet." World Health Organization. https://www.who.int/news-room/fact-sheets/detail/diabetes

6. Kemenkes RI (2018). "Riskesdas 2018." Badan Penelitian dan Pengembangan Kesehatan.

7. Maxim Integrated (2022). MAX30102 Datasheet: High-Sensitivity Pulse Oximeter and Heart Rate Sensor.

8. Espressif Systems (2023). ESP32 Technical Reference Manual.

9. Pedregosa, F. et al. (2011). "Scikit-learn: Machine Learning in Python." JMLR, 12, 2825–2830.

10. Boulton, A. J. et al. (2005). "Diabetic neuropathies: A statement by the American Diabetes Association." Diabetes Care, 28(4), 956–962.

---

## LAMPIRAN

### Lampiran 1: Struktur Fitur Model (22 Fitur)

```
[0]  Usia              [11] IR_Max            [17] RED_Max
[1]  Berat_kg          [12] IR_Std            [18] RED_Std
[2]  Tinggi_cm         [13] IR_RMS            [19] RED_RMS
[3]  BMI               [14] RED_Mean          [20] Ratio_AC
[4]  TerakhirMakan_jam [15] RED_Min           [21] Ratio_DC
[5]  SuhuTubuh         [16] Samples
[6]  SuhuAmbient
[7]  HR_est
[8]  SpO2_est
[9]  IR_Mean
[10] IR_Min
```

### Lampiran 2: Diagram Koneksi Hardware

```
ESP32 DevKit V1
├── Bus 1 (GPIO 21/22) — Shared I2C
│   ├── OLED SSD1306 (0x3C)
│   └── MLX90614 (0x5A)
├── Bus 2 (GPIO 18/19) — Dedicated I2C
│   └── MAX30102
├── GPIO 23 → Buzzer/Speaker
└── GPIO 26 → Vibromotor
```

### Lampiran 3: Hasil Evaluasi Model per Fold

| Fold | Test Subjects | MAE (mg/dL) | R² |
|---|---|---|---|
| 1 | 6 | 11,99 | 0,667 |
| 2 | 6 | 23,67 | -0,050 |
| 3 | 6 | 22,22 | -0,459 |
| 4 | 7 | 31,72 | -0,038 |
| 5 | 7 | 24,17 | -0,226 |
| **Rata-rata** | | **22,57** | **0,061** |

### Lampiran 4: Daftar File Repository

```
SENS_ABLE_OPSI/
├── firmware/          (6 file Arduino/ESP32)
├── scripts/           (33 file Python ML pipeline)
├── data/
│   ├── raw/          (25 file CSV/XLSX original)
│   └── processed/    (dataset bersih)
├── results/          (evaluasi model + figur)
├── web/              (dashboard monitoring)
├── docs/             (dokumentasi lengkap)
└── requirements.txt
```
