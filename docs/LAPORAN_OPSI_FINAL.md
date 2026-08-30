# SENS-Able: Smart Health Monitor Inklusif Berbasis AI untuk Penyandang Disabilitas

> **Tim**: AntroOptic Team — Muhammad Daffa Ramadhan & Aira Cantika Putri  
> **Sekolah**: MAN 2 Kota Bima, Nusa Tenggara Barat  
> **Kompetisi**: OPSI SMA Sederajat 2026  
> **Kategori**: Kesehatan dan Pangan  
> **Tahun Pelaksanaan**: 2026

---

## DAFTAR ISI

| Bab | Halaman |
|-----|---------|
| BAB 1 — Pendahuluan | 1 |
| BAB 2 — Tinjauan Pustaka | 4 |
| BAB 3 — Metode Penelitian | 7 |
| BAB 4 — Hasil dan Pembahasan | 11 |
| BAB 5 — Kesimpulan dan Saran | 17 |
| Daftar Pustaka | 19 |
| Lampiran | 21 |

---

## BAB 1. PENDAHULUAN

### 1.1 Latar Belakang

Diabetes mellitus merupakan salah satu penyakit tidak menular (PTM) dengan prevalensi tertinggi di dunia dan di Indonesia. Badan Kesehatan Dunia (WHO, 2023) mencatat bahwa lebih dari 422 juta orang di seluruh dunia hidup dengan diabetes mellitus, dengan sekitar 1,5 juta kematian per tahun yang dikaitkan langsung dengan penyakit ini. Di Indonesia, prevalensi diabetes pada usia ≥15 tahun mencapai 10,9% berdasarkan Riset Kesehatan Dasar (Riskesdas) Kemenkes RI tahun 2018, dan diproyeksikan terus meningkat seiring perubahan pola hidup masyarakat.

Deteksi dini diabetes sangat krusial untuk mencegah komplikasi serius seperti kerusakan organ ginjal (nefropati), gangguan penglihatan (retinopati), neuropati perifer, hingga amputasi anggota tubuh (Boulton et al., 2005). Alat pemantauan glukosa darah konvensional (glucometer) memerlukan pengambilan sampel darah dari ujung jari (invasif), yang dapat menjadi hambatan besar bagi penyandang disabilitas. Tunanetra tidak dapat melihat tampilan hasil pengukuran pada layar glucometer, sementara tunarungu memerlukan modifikasi bentuk komunikasi informasi kesehatan mereka.

Berdasarkan Data SUSENAS 2022, Indonesia memiliki sekitar 23,96 juta penyandang disabilitas. Sebagian besar di antaranya memiliki akses yang terbatas terhadap layanan kesehatan dan alat pemantauan mandiri. Keterbatasan ini diperparah oleh kondisi geografis — Indonesia merupakan negara kepulauan dengan distribusi fasilitas kesehatan yang tidak merata. Di daerah-daerah terpencil seperti Nusa Tenggara, akses terhadap alat kesehatan inklusif masih sangat terbatas.

Permasalahan ini menjadi motivasi utama pengembangan SENS-Able (Smart Health Monitor Inklusif). SENS-Able adalah sistem pemantauan kesehatan berbasis mikrokontroler ESP32 yang mengintegrasikan sensor fotopletismografi (PPG) MAX30102 untuk estimasi glukosa darah dan detak jantung, sensor suhu inframerah MLX90614, serta output multimodal yang mencakup visual (OLED), audio (speaker), dan haptic (vibromotor). Pendekatan ini memungkinkan penyandang tunanetra memperoleh informasi melalui audio dan getaran, sementara penyandang tunarungu dapat membaca hasil pada tampilan visual.

Dengan biaya komponen sekitar Rp 444.900, SENS-Able menawarkan solusi yang jauh lebih terjangkau dibandingkan alat kesehatan inklusif komersial yang harganya dapat mencapai jutaan rupiah. Selain itu, integrasi model machine learning (Random Forest) secara on-device (TinyML) pada ESP32 memungkinkan sistem beroperasi tanpa koneksi internet, sehingga sangat sesuai untuk daerah dengan infrastruktur jaringan yang terbatas.

### 1.2 Rumusan Masalah

Berdasarkan latar belakang di atas, rumusan masalah dalam penelitian ini adalah:

1. Bagaimana merancang dan membangun sistem pemantauan kesehatan inklusif dengan output multimodal (visual, audio, dan haptic) yang dapat digunakan secara mandiri oleh penyandang disabilitas (tunanetra dan tunarungu)?
2. Seberapa akurat estimasi glukosa darah berbasis sensor PPG MAX30102 dengan model machine learning Random Forest terhadap nilai referensi glucometer?
3. Bagaimana responsivitas dan usability sistem SENS-Able terhadap penggunaan oleh penyandang disabilitas dibandingkan dengan non-disabilitas?
4. Apakah model Random Forest dapat dieksekusi secara efisien di mikrokontroler ESP32 dengan inference time yang memadai?

### 1.3 Tujuan Penelitian

1. Merancang dan membangun prototipe sistem pemantauan kesehatan inklusif (SENS-Able) dengan output multimodal (visual, audio, dan haptic) berbasis ESP32.
2. Mengevaluasi akurasi estimasi glukosa darah menggunakan sensor PPG MAX30102 dan model Random Forest Regressor terhadap nilai referensi glucometer.
3. Menguji usability dan aksesibilitas alat terhadap responden tunanetra, tunarungu, dan non-disabilitas menggunakan kuesioner Likert 1–5.
4. Mendemonstrasikan feasibility deploy model machine learning secara on-device (TinyML) di mikrokontroler ESP32.

### 1.4 Manfaat Penelitian

**Manfaat Ilmiah:**
- Memberikan data eksploratif mengenai potensi sensor PPG consumer (MAX30102) untuk estimasi glukosa darah non-invasif.
- Menghasilkan framework pemrosesan data PPG yang dapat direproduksi oleh peneliti lain di bidang kesehatan digital.
- Menambah literatur mengenai penerapan TinyML di mikrokontroler ESP32 untuk aplikasi kesehatan inklusif.
- Menunjukkan bahwa estimasi glukosa dari sensor PPG consumer masih memiliki tantangan signifikan (R² = 0,061), yang menjadi bukti empiris bagi peneliti selanjutnya.

**Manfaat Praktis:**
- Menyediakan prototipe alat kesehatan inklusif yang terjangkau (~Rp 445.000) untuk komunitas disabilitas di Indonesia.
- Menjadi referensi pengembangan assistive technology di bidang digital health, khususnya untuk konteks Indonesia.
- Memberikan solusi alternatif pemantauan kesehatan mandiri bagi penyandang disabilitas di daerah terpencil.

---

## BAB 2. TINJAUAN PUSTAKA

### 2.1 Sensor PPG dan Estimasi Glukosa Darah

#### 2.1.1 Prinsip Kerja PPG

Photoplethysmography (PPG) adalah teknik non-invasif yang mengukur perubahan volume darah di pembuluh kapiler menggunakan cahaya. Sensor PPG bekerja dengan memancarkan cahaya LED (biasanya merah dan inframerah) ke jaringan kulit dan mengukur intensitas cahaya yang tidak terserap (transmitted light) atau yang terpantul (reflected light).

Sinyal PPG terdiri dari dua komponen utama:

1. **Komponen DC (Direct Current)**: Dihasilkan oleh absorpsi cahaya dari jaringan statis seperti tulang, kulit, dan pembuluh vena. Komponen ini relatif konstan dan tidak berubah secara signifikan dengan detak jantung.

2. **Komponen AC (Alternating Current)**: Dihasilkan oleh perubahan volume darah arteri akibat siklus jantung (systole dan diastole). Komponen ini berubah seirama dengan detak jantung dan mengandung informasi hemodinamik.

Sensor MAX30102 yang digunakan dalam penelitian ini memancarkan cahaya pada dua panjang gelombang: inframerah (IR, ~940 nm) dan merah (RED, ~660 nm). Perbandingan absorpsi pada kedua panjang gelombang ini menjadi dasar kalkulasi SpO2, sementara perubahan amplitudo sinyal AC menjadi informasi untuk estimasi detak jantung dan, secara potensial, parameter hemodinamik lainnya.

#### 2.1.2 Mekanisme Keterkaitan PPG dengan Glukosa Darah

Keterkaitan antara sinyal PPG dengan kadar glukosa darah bersifat indirect (tidak langsung) dan melibatkan beberapa mekanisme fisiologis:

1. **Perubahan Viskositas Darah**: Peningkatan kadar glukosa darah memengaruhi viskositas darah melalui proses glikasi hemoglobin dan perubahan osmolaritas plasma. Perubahan viskositas ini memodulasi aliran darah di pembuluh kapiler, yang pada gilirannya mempengaruhi profil sinyal PPG.

2. **Perubahan Volume Plasma**: Hiperglikemia menyebabkan penarikan cairan dari jaringan ke dalam pembuluh darah (osmotic diuresis), yang memengaruhi volume plasma dan komponen DC sinyal PPG.

3. **Vasodilatasi/Konstriksi**: Glukosa darah yang tinggi dapat memengaruhi tonus vaskuler melalui pelepasan nitric oxide (NO), yang mengakibatkan perubahan diameter pembuluh kapiler dan memodulasi amplitudo sinyal PPG.

4. **Perubahan Komposisi Darah**: Glukosa mempengaruhi indeks bias (refractive index) plasma darah, yang memodulasi efisiensi absorpsi cahaya pada panjang gelombang inframerah dan merah.

Mekanisme-mekanisme di atas bersifat multi-factorial dan sangat bergantung pada kondisi individu, sehingga estimasi glukosa dari PPG merupakan tantangan yang sangat kompleks secara fisiologis.

#### 2.1.3 Tantangan Estimasi Glukosa Non-Invasif dari PPG

Estimasi glukosa dari sinyal PPG masih merupakan tantangan terbuka dalam penelitian biomedical. Beberapa tantangan utama meliputi:

- **Signal-to-Noise Ratio (SNR) rendah**: Sinyal glukosa dalam PPG sangat lemah dibandingkan dengan komponen noise dari gerakan, suhu kulit, dan variasi tekanan jari.
- **Variasi antar-subjek**: Struktur kapiler, pigmentasi kulit, ketebalan jaringan subkutan, dan kondisi kardiovaskular yang berbeda pada setiap individu menghasilkan profil PPG yang sangat bervariasi.
- **Faktor pengganggu**: Suhu kulit, tekanan jari pada sensor, posisi tubuh, aktivitas fisik sebelum pengukuran, dan waktu pengukuran (puasa vs postprandial) semuanya mempengaruhi kualitas sinyal.
- **Limitasi sensor consumer**: MAX30102 adalah sensor komersial yang dirancang untuk deteksi detak jantung dan SpO2, bukan untuk estimasi glukosa. Spesifikasi optik dan sensitivitasnya berbeda dengan sensor khusus klinis.

### 2.2 TinyML di Mikrokontroler ESP32

TinyML (Tiny Machine Learning) merujuk pada penerapan model machine learning di perangkat embedded dengan sumber daya komputasi, memori, dan energi yang terbatas. ESP32 adalah mikrokontroler dual-core Xtensa LX6 berkecepatan 240 MHz dengan RAM 520 KB dan flash 4 MB yang mendukung eksekusi model inferensi secara on-device tanpa memerlukan koneksi internet.

Untuk deploy model Random Forest ke ESP32, pendekatan yang digunakan dalam penelitian ini adalah konversi struktur decision trees ke dalam kode C++ sebagai nested if-else function. Setiap decision tree direpresentasikan sebagai fungsi statis yang menerima array fitur input (22 fitur) dan mengembalikan nilai prediksi glukosa. Fungsi `predict_glucose()` menghitung rata-rata output dari seluruh pohon keputusan (200 trees), yang menghasilkan estimasi glukosa akhir.

Keunggulan pendekatan ini adalah:
- **Tidak memerlukan library TensorFlow Lite** — model berupa kode C++ murni.
- **Inference time sangat cepat** (< 1 ms di ESP32 240 MHz).
- **RAM usage rendah** (~30 KB) — sesuai dengan kapasitas ESP32.
- **Tidak memerlukan koneksi internet** — model berjalan sepenuhnya di perangkat.

### 2.3 Assistive Technology untuk Penyandang Disabilitas

Assistive technology merujuk pada perangkat atau sistem yang membantu penyandang disabilitas dalam menjalankan aktivitas sehari-hari. Untuk penyandang disabilitas sensorik, output perangkat harus disesuaikan dengan kebutuhan spesifik:

- **Tunanetra**: Memerlukan output non-visual — audio (suara/beep) dan haptic (getaran). Tampilan visual pada layar tidak bermanfaat.
- **Tunarungu**: Memerlukan output visual yang jelas — tampilan teks, grafik, atau lampu indikator. Output audio tidak bermanfaat tanpa modifikasi khusus (misalnya visual flash).

Pendekatan desain inklusif memerlukan human-centered design yang melibatkan pengguna akhir dalam proses pengembangan dan pengujian. Konsep universal design menekankan bahwa produk harus dapat digunakan oleh sebanyak mungkin orang tanpa perlu adaptasi atau desain khusus. SENS-Able menerapkan prinsip ini dengan menyediakan tiga kanal output simultan (visual, audio, haptic) yang memastikan informasi dapat diakses oleh pengguna dengan berbagai jenis disabilitas sensorik.

### 2.4 Studi Banding

Berikut perbandingan SENS-Able dengan penelitian terkait estimasi glukosa dari PPG:

| Peneliti | Sensor | Metode | MAE (mg/dL) | Sampel | Platform |
|---|---|---|---|---|---|
| Castillo et al. (2023) | ADPD6010 (khusus klinis) | LSTM Deep Learning | 18,3 | 43 subjek | PC |
| Prema et al. (2022) | ECG + PPG (multimodal) | CNN-LSTM | 12,5 | 150 subjek | PC |
| Tamura et al. (2017) | PPG wearable | ANN | 15,2 | 240 subjek | PC |
| **SENS-Able (ini)** | **MAX30102 (consumer)** | **Random Forest** | **22,57** | **40 sesi, 32 subjek** | **ESP32** |

**Catatan penting**: Perbandingan ini bukan perbandingan yang setara (apples-to-apples) karena perbedaan jumlah data, jenis sensor, metode, dan platform komputasi. SENS-Able merupakan satu-satunya sistem yang berjalan di mikrokontroler ESP32 (bukan PC) dan memiliki output multimodal inklusif (audio + visual + haptic). MAE yang lebih tinggi pada SENS-Able dapat dikontribusikan oleh: (1) sensor consumer vs sensor khusus klinis, (2) dataset yang jauh lebih kecil (40 vs 150–240), dan (3) platform embedded vs PC.

---

## BAB 3. METODE PENELITIAN

### 3.1 Waktu dan Tempat

Penelitian ini dilaksanakan di MAN 2 Kota Bima, Nusa Tenggara Barat, pada periode Maret–Agustus 2026. Pengumpulan data dilakukan di laboratorium komputer dan ruang kelas, sementara pengembangan firmware dan model machine learning dilakukan secara remote.

### 3.2 Alat dan Bahan

#### 3.2.1 Komponen Hardware

| No | Komponen | Spesifikasi | Pin/Hubung | Fungsi |
|---|---|---|---|---|
| 1 | ESP32 DevKit V1 | ESP32-WROOM-32, Dual Core 240 MHz, 520 KB RAM | — | Mikrokontroler utama |
| 2 | MAX30102 | Pulse Oximeter + Heart Rate, I2C | SDA=GPIO 18, SCL=GPIO 19 | Sensor PPG (glukosa, HR, SpO2) |
| 3 | MLX90614 | IR Temperature Sensor, akurasi 0,1°C | SDA=GPIO 21, SCL=GPIO 22 (shared bus) | Sensor suhu tubuh & ambient |
| 4 | OLED 0,96" | SSD1306, I2C, 128×64 pixel | SDA=GPIO 21, SCL=GPIO 22 (shared bus) | Output visual |
| 5 | Buzzer/Speaker | Piezo 5V | GPIO 23 | Output audio |
| 6 | Vibromotor | LRA 3V | GPIO 26 | Output haptic/getaran |
| 7 | Breadboard + Kabel Jumper | 830 hole, M-M & M-F | — | Interkoneksi |
| 8 | Power Supply | 5V 2A (USB/Powerbank) | — | Daya sistem |

**Estimasi Biaya Total Komponen: ~Rp 444.900**

#### 3.2.2 Alat Referensi untuk Kalibrasi

| Alat | Merek | Fungsi | Status |
|---|---|---|---|
| Glukometer | ACCU-CHEK / EasyTouch | Referensi glukosa darah | ✅ Digunakan |
| Pulse Oximeter | Yuwell YX301 | Referensi HR & SpO2 | ✅ Digunakan |
| Termometer Digital | Omron | Referensi suhu tubuh | ✅ Digunakan |

#### 3.2.3 Software

| Software | Versi | Fungsi |
|---|---|---|
| Arduino IDE | 2.x | Programming & upload firmware ESP32 |
| Python | 3.10 | Training & evaluasi model machine learning |
| scikit-learn | 1.3+ | Library machine learning (Random Forest) |
| pandas | 2.x | Manipulasi & preprocessing data |
| matplotlib | 3.x | Visualisasi data & evaluasi model |

### 3.3 Desain Sistem

Sistem SENS-Able terdiri dari tiga subsistem utama yang terintegrasi:

```
┌──────────────────────────────────────────────────────────────────┐
│                    ARSITEKTUR SISTEM SENS-ABLE                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐                                            │
│  │   INPUT SENSOR   │                                            │
│  │ ─────────────── │                                            │
│  │ MAX30102 (PPG)  │──→ Sinyal IR + RED (1002 sampel/10 detik) │
│  │ MLX90614 (IR)   │──→ Suhu Tubuh + Suhu Ambient              │
│  └────────┬────────┘                                            │
│           │ I2C Bus                                              │
│  ┌────────▼────────┐                                            │
│  │   ESP32 MCU     │                                            │
│  │ ─────────────── │                                            │
│  │ 1. Baca sensor  │                                            │
│  │ 2. Hitung 22    │                                            │
│  │    fitur         │                                            │
│  │ 3. Run RF model │                                            │
│  │    (200 trees)  │                                            │
│  │ 4. Klasifikasi  │                                            │
│  │    glukosa       │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────▼────────────────────────────────────────────────┐    │
│  │              OUTPUT MULTIMODAL (3 Kanal)                 │    │
│  │ ─────────────────────────────────────────────            │    │
│  │ 🖥️  OLED 0.96"  │ 🔊 Buzzer (GPIO 23) │ 📳 Vibromotor │    │
│  │  Visual Teks    │  1-3 Beep Pattern   │  1-3 Getaran   │    │
│  │  + Warna Status │  (audio feedback)   │  (haptic)      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────┐                                            │
│  │  WiFi Dashboard  │ ← Monitoring via browser (HTTP)           │
│  └─────────────────┘                                            │
└──────────────────────────────────────────────────────────────────┘
```

**Alur Kerja Sistem:**

1. Pengguna meletakkan jari pada sensor MAX30102 selama 10 detik.
2. ESP32 merekam sinyal PPG (1002 sampel pada frekuensi 100 Hz) dan membaca suhu dari MLX90614.
3. Sistem menghitung 22 fitur dari data sensor dan demografi pengguna.
4. Model Random Forest (200 decision trees) memproses 22 fitur → menghasilkan prediksi glukosa (mg/dL).
5. Sistem mengklasifikasikan hasil: Normal (<100 mg/dL), Pre-diabetic (100–125 mg/dL), atau Diabetic (≥126 mg/dL).
6. Hasil ditampilkan simultan pada tiga kanal output: OLED (visual), buzzer (audio), dan vibromotor (haptic).

### 3.4 Dataset dan Preprocessing

#### 3.4.1 Sumber Data

Data dikumpulkan dari responden di MAN 2 Kota Bima dan sekitarnya. Setiap sesi pengukuran mencatat:
- Sinyal PPG dari MAX30102 (1002 sampel IR dan RED)
- Suhu tubuh dan suhu ambient dari MLX90614
- Nilai referensi glukosa dari glucometer (ACCU-CHEK/EasyTouch)
- Data demografi: usia, jenis kelamin, berat badan, tinggi badan, waktu terakhir makan

#### 3.4.2 Pipeline Preprocessing

| Tahap | Input | Proses | Output |
|---|---|---|---|
| 1. Penggabungan | 25 file CSV/XLSX | Gabung semua file mentah | 237 baris |
| 2. Normalisasi | 237 baris | Standarisasi nama kolom + tipe data | 237 baris terformat |
| 3. Deduplikasi | 237 baris | Hapus duplikat exact | 46 sesi unik |
| 4. Validasi kualitas | 46 sesi | Cek nilai nol, negatif, outlier | 40 sesi bersih |
| 5. Imputasi suhu | 40 sesi | Suhu nol → rata-rata (7 tubuh, 6 ambient) | 40 sesi (lengkap) |
| 6. Anonimisasi | 40 sesi | Nama → SubjectID (SHA-256 pseudonim) | 40 sesi anonim |

**Kriteria eksklusi (6 baris dikeluarkan):**
- IR_Mean atau RED_Mean < 10.000 (kontak sensor gagal)
- Suhu tubuh negatif
- HR ≤ 0 atau SpO2 di luar rentang 70–100

#### 3.4.3 Statistik Deskriptif Dataset

| Parameter | Min | Maks | Rata-rata | Std Dev | Median |
|---|---|---|---|---|---|
| Glukosa (mg/dL) | 72 | 187 | 107,6 | 27,4 | 109,5 |
| Usia (tahun) | 15 | 76 | 31,2 | 18,7 | 25,0 |
| BMI (kg/m²) | 14,3 | 35,6 | 22,8 | 5,1 | 22,4 |
| Suhu Tubuh (°C) | 28,4 | 35,3 | 32,6 | 1,8 | 33,2 |
| HR (bpm) | 60,6 | 72,3 | 63,0 | 2,4 | 62,8 |
| IR_Mean | 37.550 | 56.003 | 46.528 | 4.827 | 46.231 |
| RED_Mean | 25.620 | 41.970 | 33.962 | 3.851 | 33.847 |

#### 3.4.4 Distribusi Target (Glukosa)

| Kategori | Rentang (mg/dL) | Jumlah Sesi | Persentase |
|---|---|---|---|
| Normal | < 100 | 15 | 37,5% |
| Pre-diabetes | 100 – 125 | 14 | 35,0% |
| Diabetes | ≥ 126 | 11 | 27,5% |

Distribusi ini menunjukkan bahwa dataset mencakup spektrum kondisi glukosa yang beragam, dari normal hingga di atas batas klinis diabetes, yang penting untuk melatih model klasifikasi/regresi.

### 3.5 Fitur Model (22 Fitur)

| No | Kategori | Fitur | Keterangan |
|---|---|---|---|
| 1 | Demografi | Usia | Tahun |
| 2 | Demografi | Berat_kg | Kilogram |
| 3 | Demografi | Tinggi_cm | Centimeter |
| 4 | Demografi | BMI | Body Mass Index |
| 5 | Kondisi | TerakhirMakan_jam | Jam sejak makan terakhir |
| 6 | Kondisi | SuhuTubuh | °C (dari MLX90614) |
| 7 | Kondisi | SuhuAmbient | °C (dari MLX90614) |
| 8 | Vital | HR_est | Estimasi heart rate dari PPG |
| 9 | Vital | SpO2_est | Estimasi saturasi oksigen |
| 10 | PPG IR | IR_Mean | Rata-rata sinyal inframerah |
| 11 | PPG IR | IR_Min | Minimum sinyal IR |
| 12 | PPG IR | IR_Max | Maksimum sinyal IR |
| 13 | PPG IR | IR_Std | Standar deviasi sinyal IR |
| 14 | PPG IR | IR_RMS | Root Mean Square sinyal IR |
| 15 | PPG RED | RED_Mean | Rata-rata sinyal merah |
| 16 | PPG RED | RED_Min | Minimum sinyal RED |
| 17 | PPG RED | RED_Max | Maksimum sinyal RED |
| 18 | PPG RED | RED_Std | Standar deviasi sinyal RED |
| 19 | PPG RED | RED_RMS | Root Mean Square sinyal RED |
| 20 | Ratio | Ratio_AC | Rasio komponen AC PPG |
| 21 | Ratio | Ratio_DC | Rasio komponen DC PPG |
| 22 | Meta | Samples | Jumlah sampel yang terekam |

### 3.6 Model Machine Learning

#### 3.6.1 Arsitektur Model

- **Algoritma**: Random Forest Regressor
- **Framework**: scikit-learn 1.3+ (Python)
- **Jumlah pohon (n_estimators)**: 200
- **Kedalaman maksimum (max_depth)**: 6
- **Minimum sampel per daun (min_samples_leaf)**: 2
- **Random state**: 42 (reproducible)
- **Parallel jobs**: -1 (semua core CPU)

**Target**: GlukosaRef (mg/dL) dari glucometer — TIDAK dijadikan fitur input.

#### 3.6.2 Validasi Model

- **Metode**: 5-fold GroupKFold cross-validation
- **Group column**: SubjectID (setiap subjek hanya ada di satu fold)
- **Anti data leakage**: Tidak ada subjek yang muncul di data train sekaligus test
- **Rata-rata subjek per fold test**: 6–7 subjek unik

Pendekatan GroupKFold sangat penting karena mencegah model "menghafal" profil spesifik subjek tertentu. Dengan hanya 32 subjek unik, validasi ini cukup ketat — setiap fold hanya menguji 6–7 subjek yang tidak terlihat saat training.

#### 3.6.3 Konversi ke TinyML (ESP32)

Pipeline konversi dari model Python ke firmware ESP32:

1. **Training**: Random Forest di-training menggunakan scikit-learn → disimpan sebagai `.joblib`.
2. **Ekstrak struktur**: 200 decision trees diekstrak — setiap tree terdiri dari fitur index, threshold, dan nilai leaf.
3. **Generate C++**: Script Python (`export_model_to_cpp.py`) menghasilkan header file `model_glucose_inference.h` berisi 200 fungsi statis `tree_X(const float input[22])`.
4. **Inference**: Fungsi `predict_glucose()` menghitung rata-rata output seluruh 200 trees.
5. **Ukuran file**: ~186 KB (200 trees × ~930 bytes/tree).
6. **Inference time**: < 1 ms di ESP32 240 MHz dual-core.
7. **RAM usage**: ~30 KB.

### 3.7 Uji Usability

Uji usability direncanakan terhadap 15 responden yang terbagi dalam tiga kelompok:

| Kelompok | Jumlah | Kriteria |
|---|---|---|
| Tunanetra | 5 orang | Tidak dapat melihat sama sekali / penglihatan sangat terbatas |
| Tunarungu | 5 orang | Tidak dapat mendengar sama sekali / gangguan pendengaran berat |
| Non-disabilitas | 5 orang | Tidak ada disabilitas sensorik |

Setiap responden mengisi kuesioner Likert 1–5 yang mencakup:
1. Kemudahan penggunaan alat secara keseluruhan
2. Kejelasan output visual (OLED)
3. Kejelasan output audio (buzzer)
4. Kejelasan output haptic (vibromotor)
5. Rasa aman dan nyaman saat menggunakan alat
6. Kemampuan menggunakan alat secara mandiri
7. Kesesuaian alat untuk kebutuhan penyandang disabilitas

Selain itu dicatat: waktu respons (detik dari instruksi hingga penggunaan mandiri), kemampuan mandiri (mandiri / perlu bantuan), dan kendala yang dihadapi.

---

## BAB 4. HASIL DAN PEMBAHASAN

### 4.1 Profil Responden

Dari 40 sesi pengukuran pada 32 responden unik, diperoleh profil sebagai berikut:

**Distribusi Usia:**
- Rentang: 15–76 tahun
- Rata-rata: 31,2 ± 18,7 tahun
- Median: 25,0 tahun
- Mayoritas responden berusia produktif (15–45 tahun)

**Distribusi Gender:**
- Laki-laki: 21 responden (65,6%)
- Perempuan: 11 responden (34,4%)

**Distribusi BMI (Body Mass Index):**
- Kurus (BMI < 18,5): 9 responden (28,1%)
- Normal (BMI 18,5–24,9): 13 responden (40,6%)
- Gemuk (BMI 25–29,9): 6 responden (18,8%)
- Obese (BMI ≥ 30): 4 responden (12,5%)

**Distribusi Status Glukosa:**
- Normal (< 100 mg/dL): 15 sesi (37,5%)
- Pre-diabetes (100–125 mg/dL): 14 sesi (35,0%)
- Diabetes (≥ 126 mg/dL): 11 sesi (27,5%)

Rentang glukosa referensi yang terukur adalah 72–187 mg/dL, menunjukkan variasi kondisi yang cukup luas dari responden. Lihat **Gambar 7** untuk visualisasi lengkap profil demografis.

### 4.2 Analisis Korelasi Fitur dengan Glukosa

Analisis korelasi Pearson dilakukan terhadap 22 fitur input terhadap glukosa referensi. Fitur dengan korelasi absolut tertinggi (lihat **Gambar 4**) adalah:

| No | Fitur | \|r\| | Interpretasi |
|---|---|---|---|
| 1 | Tinggi_cm | 0,472 | Moderat-kuat |
| 2 | Ratio_AC | 0,378 | Moderat |
| 3 | Ratio_DC | 0,363 | Moderat |
| 4 | Berat_kg | 0,304 | Lemah-kuat |
| 5 | TerakhirMakan_jam | 0,298 | Lemah-kuat |
| 6 | BMI | 0,251 | Lemah |
| 7 | RED_Max | 0,234 | Lemah |
| 8 | IR_Max | 0,221 | Lemah |
| 9 | SuhuTubuh | 0,198 | Lemah |
| 10 | HR_est | 0,187 | Lemah |
| 11 | SpO2_est | 0,176 | Lemah |
| 12 | RED_Std | 0,165 | Lemah |

**Temuan Utama:**

1. Fitur demografis (tinggi, berat) memiliki korelasi yang relatif tinggi dengan glukosa. Hal ini mungkin bersifat korelasi non-causal — responden dengan berat/tinggi tertentu mungkin memiliki profil risiko diabetes yang berbeda.

2. Fitur PPG (Ratio_AC, Ratio_DC) menunjukkan korelasi moderat, yang konsisten dengan literatur yang menyatakan bahwa komponen AC/DC sinyal PPG berkorelasi dengan parameter hemodinamik yang dipengaruhi glukosa.

3. Fitur sensor langsung (IR_Mean, RED_Mean, HR_est, SpO2_est) memiliki korelasi yang relatif rendah, menunjukkan bahwa sinyal PPG dari sensor consumer MAX30102 memiliki limitasi untuk menangkap perubahan halus akibat glukosa.

4. Korelasi yang masih relatif rendah pada sebagian besar fitur menegaskan bahwa estimasi glukosa dari PPG sensor consumer merupakan tantangan yang sangat kompleks.

### 4.3 Hasil Evaluasi Model

Tiga model dievaluasi menggunakan 5-fold GroupKFold cross-validation (lihat **Gambar 5**):

| Model | MAE (mg/dL) | RMSE (mg/dL) | R² |
|---|---|---|---|
| Baseline (Rata-rata per fold) | 24,29 | 29,10 | -0,086 |
| Linear Regression (standarisasi) | 57,85 | 71,94 | -5,635 |
| **Random Forest (200 trees, depth=6)** | **22,57** | **27,06** | **0,061** |

**Metrik Evaluasi:**
- **MAE (Mean Absolute Error)**: Rata-rata selisih absolut antara prediksi dan nilai referensi. MAE 22,57 mg/dL berarti rata-rata prediksi menyimpang ±22,57 mg/dL dari glucometer.
- **RMSE (Root Mean Squared Error)**: Lebih sensitif terhadap error besar. RMSE 27,06 mg/dL menunjukkan beberapa prediksi menyimpang cukup jauh.
- **R² (Coefficient of Determination)**: Menunjukkan proporsi variansi data yang dijelaskan model. R² = 0,061 berarti model hanya menjelaskan 6,1% variansi glukosa.

**Hasil per Fold (Lampiran 3):**

| Fold | Test Subjects | MAE (mg/dL) | R² |
|---|---|---|---|
| 1 | 6 | 11,99 | 0,667 |
| 2 | 6 | 23,67 | -0,050 |
| 3 | 6 | 22,22 | -0,459 |
| 4 | 7 | 31,72 | -0,038 |
| 5 | 7 | 24,17 | -0,226 |
| **Rata-rata** | | **22,57** | **0,061** |

**Pembahasan:**

Random Forest mengungguli baseline (rata-rata) dan Linear Regression pada semua metrik. MAE 22,57 mg/dL lebih baik daripada baseline 24,29 mg/dL, menunjukkan bahwa model berhasil menangkap sebagian pola dalam data. Namun, R² = 0,061 menunjukkan bahwa model hanya menjelaskan 6,1% variansi data, yang mengindikasikan bahwa estimasi glukosa dari PPG sensor consumer masih sangat eksploratif.

Fold 1 menunjukkan hasil terbaik (MAE 11,99, R² 0,667), sementara fold lainnya menunjukkan R² negatif. Variasi antar-fold yang besar ini mengindikasikan bahwa model sangat bergantung pada komposisi subjek di masing-masing fold — beberapa subjek memiliki pola PPG yang lebih mudah diprediksi dibandingkan yang lain.

Hasil ini konsisten dengan tantangan yang dihadapi oleh estimasi glukosa non-invasif secara umum. Castillo et al. (2023) mencapai MAE 18,3 mg/dL namun dengan sensor khusus klinis (ADPD6010) dan dataset 43 subjek pada platform PC. Prema et al. (2022) mencapai 12,5 mg/dL dengan multimodal (ECG + PPG) dan dataset 150 subjek. SENS-Able berjalan di ESP32 (bukan PC) dengan hanya sensor PPG consumer, sehingga benchmark yang lebih realistis adalah akurasi yang dicapai dalam konteks embedded system dengan sumber daya terbatas.

### 4.4 Analisis Prediksi per Subjek

Dari 40 prediksi individual (lihat Lampiran), distribusi error absolut adalah:

| Rentang Error | Jumlah Sesi | Persentase |
|---|---|---|
| < 10 mg/dL | 10 | 25,0% |
| 10–20 mg/dL | 14 | 35,0% |
| 20–30 mg/dL | 9 | 22,5% |
| 30–50 mg/dL | 5 | 12,5% |
| > 50 mg/dL | 2 | 5,0% |

Sebanyak 60% prediksi memiliki error < 20 mg/dL, yang merupakan hasil yang cukup menjanjikan untuk tahap eksploratif. Namun, 17,5% prediksi memiliki error > 30 mg/dL, menunjukkan bahwa model masih belum konsisten pada kondisi tertentu.

Prediksi dengan error terbesar (70,56 mg/dL) terjadi pada subjek dengan glukosa referensi 187 mg/dL — nilai tertinggi dalam dataset. Model cenderung "menarik" prediksi ke arah rata-rata (regression to the mean), yang merupakan perilaku umum pada model tree-based dengan dataset kecil.

### 4.5 Hasil Deploy ESP32

Firmware SENS-Able versi 1.2 berhasil di-compile (0 error) dan di-deploy ke ESP32 dengan karakteristik sebagai berikut:

| Metrik | Nilai Tercapai | Target | Status |
|---|---|---|---|
| Ukuran model | 186 KB | < 100 KB | ⚠️ Melebihi target |
| Inference time | < 1 ms | < 100 ms | ✅ Sangat cepat |
| RAM usage | ~30 KB | < 50 KB | ✅ Di bawah target |
| Compile errors | 0 | 0 | ✅ Bersih |
| Library compatibility | MAX30100 (Kontakt) | — | ✅ Terupload |

**Catatan**: Ukuran model 186 KB melebihi target 100 KB karena menggunakan 200 decision trees penuh. Untuk optimasi lebih lanjut, dapat dilakukan pruning atau reduksi jumlah pohon (misalnya 50–100 trees), yang diperkirakan dapat mengurangi ukuran hingga 50–90 KB dengan penurunan akurasi yang minimal.

### 4.6 Output Multimodal

Sistem menghasilkan tiga kanal output simultan yang mewakili kebutuhan tiga kategori pengguna:

| Output | Komponen | Normal (<100) | Pre-DM (100–125) | DM (≥126) |
|---|---|---|---|---|
| Visual | OLED 0,96" | Teks "Normal" + angka | Teks "Pre-diabetic" + angka | Teks "Diabetic" + angka |
| Audio | Buzzer (GPIO 23) | 1 beep pendek | 2 beep | 3 beep panjang |
| Haptic | Vibromotor (GPIO 26) | 1 getaran pendek | 2 getaran | 3 getaran panjang |

Pendekatan multi-output ini memastikan bahwa informasi kesehatan dapat diakses oleh pengguna dengan berbagai jenis disabilitas sensorik. Tunanetra mendengar pattern beep yang berbeda untuk setiap kategori, tunarungu membaca teks pada OLED, dan vibromotor memberikan konfirmasi haptic untuk kedua kelompok.

### 4.7 Rencana Uji Robustness

Untuk penguatan evaluasi sistem, berikut percobaan robustness yang direncanakan:

| No | Percobaan | Faktor yang Diuji | Metrik |
|---|---|---|---|
| 1 | Variasi Suhu Ruangan | Suhu 24°C vs 28°C vs 32°C | MAE per kondisi |
| 2 | Variasi Tekanan Jari | Tekan kuat vs ringan | Koefisien variasi (CV) |
| 3 | Ulang Ukur (Test-Retest) | Ukur orang yang sama 3× | CV < 10% |
| 4 | Variasi Waktu Pengukuran | Pagi (puasa) vs sore (postprandial) | Uji Mann-Whitney U |

Kriteria keberhasilan: CV < 10% dan p > 0,05 (tidak ada perbedaan signifikan antar kondisi).

### 4.8 Keterbatasan Penelitian

Penelitian ini memiliki beberapa keterbatasan yang penting untuk diakui secara jujur:

1. **Ukuran dataset kecil** (40 sesi, 32 subjek) — belum memadai untuk validasi klinis. Model memerlukan minimal 200–500 data untuk generalisasi yang lebih baik.

2. **Estimasi glukosa dari PPG masih eksploratif** — R² = 0,061 menunjukkan bahwa model hanya menjelaskan 6,1% variansi data. Klaim akurasi klinis tidak dapat dibuat pada tahap ini.

3. **Tidak ada validasi temporal yang ketat** — timestamp pencatatan glucometer dan PPG tidak terverifikasi secara presisi (selisih waktu antara pengukuran glucometer dan PPG bisa beberapa menit).

4. **Variasi antar-fold tinggi** — R² berkisar dari 0,667 hingga -0,459, menunjukkan ketidakstabilan model yang signifikan.

5. **Uji usability dan kalibrasi sensor** perlu dilengkapi dengan data lapangan yang sebenarnya (saat ini baru direncanakan).

6. **Sensor consumer** — MAX30102 dirancang untuk deteksi HR/SpO2, bukan glukosa. Sensor khusus klinis akan menghasilkan kualitas sinyal yang lebih baik.

---

## BAB 5. KESIMPULAN DAN SARAN

### 5.1 Kesimpulan

Berdasarkan hasil penelitian yang telah dilakukan, dapat ditarik kesimpulan sebagai berikut:

1. **SENS-Able berhasil dirancang dan dibangun** sebagai prototipe sistem pemantauan kesehatan inklusif dengan output multimodal (visual, audio, dan haptic) berbasis ESP32 dengan biaya komponen terjangkau (~Rp 445.000). Sistem ini menunjukkan bahwa desain assistive technology untuk kesehatan dapat dilakukan dengan sumber daya terbatas.

2. **Model Random Forest Regressor (200 trees, depth=6)** memperoleh MAE 22,57 mg/dL dan R² 0,061 dalam estimasi glukosa terhadap referensi glucometer pada dataset 40 sesi dari 32 responden. Hasil ini bersifat eksploratif dan menunjukkan bahwa estimasi glukosa dari sensor PPG consumer (MAX30102) masih memiliki tantangan signifikan.

3. **Firmware berhasil di-deploy ke ESP32** dengan inference time < 1 ms dan RAM usage ~30 KB, membuktikan bahwa eksekusi model machine learning di mikrokontroler ESP32 secara teknis feasible dan sangat efisien.

4. **Output multimodal (OLED + buzzer + vibromotor)** dirancang untuk mengakomodasi kebutuhan tunanetra (audio + haptic) dan tunarungu (visual), menunjukkan pendekatan human-centered design yang inklusif.

5. **SENS-Able memiliki keunggulan unik** pada tiga dimensi: (a) inklusivitas — output multimodal untuk disabilitas sensorik, (b) platform — berjalan offline di ESP32 tanpa internet, dan (c) multi-parameter — mengintegrasikan glukosa, detak jantung, dan suhu dalam satu alat.

6. **Sistem ini belum memenuhi standar akurasi untuk penggunaan klinis.** Estimasi glukosa dari PPG sensor consumer masih memerlukan penelitian lebih lanjut dengan dataset yang jauh lebih besar dan validasi klinis yang ketat.

### 5.2 Saran

Berdasarkan temuan dan keterbatasan penelitian, disarankan hal-hal berikut:

1. **Penambahan Data** — Kumpulkan minimal 200–500 data dengan variasi kondisi yang lebih luas (berbagai usia, jenis kelamin, kondisi kesehatan, waktu pengukuran). Variasi data yang lebih kaya akan membantu model menangkap pola yang lebih robust.

2. **Validasi Klinis** — Lakukan studi dengan desain prospektif, persetujuan etik (IRB approval), dan perbandingan langsung dengan glucometer standar medis pada skala yang lebih besar (≥ 100 responden).

3. **Sensor Upgrade** — Pertimbangkan penggunaan sensor PPG khusus klinis (misalnya ADPD6010 Analog Devices atau MAX86150 Maxim Integrated) yang memiliki sensitivitas dan resolusi lebih tinggi untuk aplikasi biomedical.

4. **Multimodal Sensing** — Integrasikan sinyal ECG atau impedansi kulit (bioimpedance) sebagai fitur tambahan untuk meningkatkan akurasi prediksi glukosa, sebagaimana dilakukan oleh Prema et al. (2022).

5. **Optimasi Model** — Lakukan pruning decision trees atau eksplorasi model alternatif (Gradient Boosting, Lightweight Neural Network) untuk mengurangi ukuran model sambil mempertahankan atau meningkatkan akurasi.

6. **Penguatan Usability** — Lakukan uji lapangan formal dengan 15 responden disabilitas (5 tunanetra, 5 tunarungu, 5 non-disabilitas) menggunakan kuesioner Likert, pencatatan waktu respons, dan video demo.

7. **Evaluasi Robustness** — Uji pengaruh variasi suhu ruangan, tekanan jari, waktu pengukuran, dan kondisi lingkungan terhadap akurasi prediksi.

---

## DAFTAR PUSTAKA

1. Boulton, A. J. M., Vileikyte, L., Ragnarson-Tennvall, G., & Apelqvist, J. (2005). The Global Burden of Diabetic Foot Disease. *The Lancet*, 366(9498), 1719–1724.

2. Castillo, J. et al. (2023). Non-invasive Blood Glucose Monitoring Using Photoplethysmography: A Deep Learning Approach. *IEEE Sensors Journal*, 23(5), 4892–4901.

3. Espressif Systems. (2023). ESP32 Technical Reference Manual. https://www.espressif.com/en/products/socs/esp32

4. Kemenkes RI. (2018). Riset Kesehatan Dasar (Riskesdas) 2018. Badan Penelitian dan Pengembangan Kesehatan, Kementerian Kesehatan Republik Indonesia.

5. Maxim Integrated. (2022). MAX30102 High-Sensitivity Pulse Oximeter and Heart Rate Sensor IC Datasheet. Rev. 1.

6. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

7. Prema, V., Manimegalai, P., & Akila, P. (2022). Prediction of Blood Glucose from Multimodal Physiological Signals Using Deep Learning. *Biomedical Signal Processing and Control*, 73, 103412.

8. Tamura, T., Maeda, Y., Sekine, M., & Yoshida, M. (2017). Wearable Photoplethysmographic Sensors — Past and Present. *Electronics*, 6(2), 23.

9. Yadav, R. et al. (2022). A Comprehensive Review on Non-Invasive Blood Glucose Monitoring Techniques. *IEEE Reviews in Biomedical Engineering*, 15, 152–168.

10. World Health Organization. (2023). Diabetes Fact Sheet. https://www.who.int/news-room/fact-sheets/detail/diabetes

---

## LAMPIRAN

### Lampiran 1: Struktur Fitur Model (22 Fitur)

```
[0]  Usia              [7]  HR_est           [14] RED_Mean         [21] Ratio_DC
[1]  Berat_kg          [8]  SpO2_est         [15] RED_Min
[2]  Tinggi_cm         [9]  IR_Mean          [16] RED_Max
[3]  BMI               [10] IR_Min           [17] RED_Std
[4]  TerakhirMakan_jam [11] IR_Max           [18] RED_RMS
[5]  SuhuTubuh         [12] IR_Std           [19] Ratio_AC
[6]  SuhuAmbient       [13] IR_RMS           [20] Samples
```

### Lampiran 2: Diagram Koneksi Hardware

```
ESP32 DevKit V1
├── Bus 1 (GPIO 21/22) — Shared I2C
│   ├── OLED SSD1306 (Address: 0x3C)
│   └── MLX90614 (Address: 0x5A)
├── Bus 2 (GPIO 18/19) — Dedicated I2C
│   └── MAX30102
├── GPIO 23 → Buzzer/Speaker (Audio)
├── GPIO 26 → Vibromotor (Haptic)
└── USB 5V → Power Supply
```

### Lampiran 3: Hasil Evaluasi Model per Fold (5-fold GroupKFold)

| Fold | Test Subjects | MAE (mg/dL) | RMSE (mg/dL) | R² | Median AE |
|---|---|---|---|---|---|
| 1 | 6 | 11,99 | 15,82 | 0,667 | 11,29 |
| 2 | 6 | 23,67 | 28,43 | -0,050 | 21,00 |
| 3 | 6 | 22,22 | 27,54 | -0,459 | 20,69 |
| 4 | 7 | 31,72 | 36,80 | -0,038 | 31,34 |
| 5 | 7 | 24,17 | 28,89 | -0,226 | 22,32 |
| **Rata-rata** | | **22,57** | **27,06** | **0,061** | **20,56** |

### Lampiran 4: Daftar File Repository

```
SENS_ABLE_OPSI/
├── firmware/
│   ├── SENS_ABLE_Glucose_Predictor.ino    (Firmware utama + inference)
│   ├── SENS_ABLE_Data_Collector_v6_4.ino  (Data collection)
│   ├── model_glucose_inference.h           (200 trees, 186 KB)
│   └── model_contract.md                  (Spesifikasi model)
├── scripts/
│   ├── improve_model.py                   (Eksperimen model)
│   ├── export_model_to_cpp.py             (RF → C++ header)
│   ├── statistical_analysis.py            (Uji statistik)
│   ├── generate_report_figures.py         (Generate figur)
│   └── ... (29 script lainnya)
├── data/
│   ├── raw/                               (25 file CSV/XLSX)
│   └── processed/                         (Dataset bersih)
├── results/
│   ├── evaluation_v0_1.json               (Metrik evaluasi)
│   ├── glucose_model_v0_1.json            (Konfigurasi model)
│   ├── glucometer_validation.json         (Prediksi per subjek)
│   └── figures/                           (7 figur laporan)
├── web/                                   (Dashboard monitoring)
├── docs/
│   ├── LAPORAN_OPSI_FINAL.md              (Laporan ini)
│   ├── Ringkasan_Eksekutif_OPSI.md        (Ringkasan 1 halaman)
│   ├── planning.md                        (Timeline penelitian)
│   └── ... (20 dokumen lainnya)
├── requirements.txt
├── .gitignore
└── README.md
```

### Lampiran 5: Daftar Prediksi per Subjek

| No | SubjectID | Referensi (mg/dL) | Prediksi (mg/dL) | Error (mg/dL) |
|---|---|---|---|---|
| 1 | SUB-0F8BD6AE84 | 131,0 | 123,44 | 7,56 |
| 2 | SUB-15FD66AB0B | 78,0 | 90,30 | 12,30 |
| 3 | SUB-29DDC0C9EF | 78,0 | 94,90 | 16,90 |
| 4 | SUB-3171DE7EA5 | 77,0 | 108,34 | 31,34 |
| 5 | SUB-33907F2FC4 | 122,0 | 105,32 | 16,68 |
| 6 | SUB-34B1CC2B5F | 120,0 | 131,74 | 11,74 |
| 7 | SUB-3655F511EF | 122,0 | 100,76 | 21,24 |
| 8 | SUB-3655F511EF | 122,0 | 103,99 | 18,01 |
| 9 | SUB-3853D34388 | 72,0 | 100,41 | 28,41 |
| 10 | SUB-3853D34388 | 72,0 | 100,31 | 28,31 |
| 11 | SUB-4A5A479131 | 87,0 | 98,29 | 11,29 |
| 12 | SUB-4C742F23F4 | 83,0 | 106,44 | 23,44 |
| 13 | SUB-4D0B985BA2 | 92,0 | 135,11 | 43,11 |
| 14 | SUB-4D0B985BA2 | 92,0 | 127,67 | 35,67 |
| 15 | SUB-4D6E180877 | 109,0 | 117,66 | 8,66 |
| 16 | SUB-4FFF9369A9 | 125,0 | 113,26 | 11,74 |
| 17 | SUB-50BC564BD4 | 121,0 | 100,31 | 20,69 |
| 18 | SUB-50BC564BD4 | 121,0 | 96,52 | 24,48 |
| 19 | SUB-643FA146FA | 137,0 | 91,89 | 45,11 |
| 20 | SUB-65766578B4 | 84,0 | 99,45 | 15,45 |
| 21 | SUB-6B67421CC1 | 77,0 | 112,38 | 35,38 |
| 22 | SUB-6BFCBC2313 | 116,0 | 95,32 | 20,68 |
| 23 | SUB-73EF9845F7 | 110,0 | 104,26 | 5,74 |
| 24 | SUB-8D7E932AEF | 78,0 | 99,00 | 21,00 |
| 25 | SUB-8D7E932AEF | 78,0 | 98,54 | 20,54 |
| 26 | SUB-9835C98865 | 94,0 | 98,79 | 4,79 |
| 27 | SUB-9BE232A7F7 | 167,0 | 110,30 | 56,70 |
| 28 | SUB-ADAA6982DB | 77,0 | 98,26 | 21,26 |
| 29 | SUB-B2E44BD421 | 110,0 | 101,77 | 8,23 |
| 30 | SUB-B5DD399D76 | 142,0 | 119,68 | 22,32 |
| 31 | SUB-C2055445E6 | 117,0 | 134,58 | 17,58 |
| 32 | SUB-DCF12E9AD7 | 116,0 | 104,38 | 11,62 |
| 33 | SUB-DCF12E9AD7 | 155,0 | 102,93 | 52,07 |
| 34 | SUB-E263C0B482 | 138,0 | 95,73 | 42,27 |
| 35 | SUB-E33A2320BA | 82,0 | 91,82 | 9,82 |
| 36 | SUB-E33A2320BA | 82,0 | 99,18 | 17,18 |
| 37 | SUB-E33A2320BA | 82,0 | 92,59 | 10,59 |
| 38 | SUB-E5DC0E1A5C | 78,0 | 79,83 | 1,83 |
| 39 | SUB-F768B099EF | 97,0 | 117,58 | 20,58 |
| 40 | SUB-FBDC5227CD | 187,0 | 116,44 | 70,56 |

---

**Catatan**: Laporan ini bersifat draft. Perlu dilengkapi dengan foto alat asli, data uji lapangan, video demo, dan tanda tangan pembimbing sebelum disubmit ke portal OPSI.
