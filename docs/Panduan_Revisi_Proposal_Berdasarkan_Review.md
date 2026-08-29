# Panduan Revisi Proposal SENS-Able — Berdasarkan Review

> **Kepada**: AntroOptic Team (Daffa & Aira)
> **Referensi**: Review document dari reviewer OPSI
> **Tanggal**: 29 Agustus 2026

---

## Ringkasan 7 Poin Review

| No | Poin Review | Prioritas | Status Saat Ini |
|---|---|---|---|
| 1 | Analisis deskriptif, belum ada uji statistik inferensial | 🔴 Tinggi | Belum ada |
| 2 | Dataset pelatihan tidak dijelaskan detail | 🔴 Tinggi | Sudah ada datanya, perlu ditulis |
| 3 | Estimasi gula darah dari PPG belum dijelaskan ilmiah | 🔴 Tinggi | Perlu ditambah tinjauan pustaka |
| 4 | Arsitektur model AI belum dijelaskan | 🔴 Tinggi | Sudah ada, perlu ditulis |
| 5 | Validasi klinis masih terbatas | 🟡 Sedang | Eksploratif, perlu framing |
| 6 | Belum ada evaluasi robustness | 🟡 Sedang | Perlu ditambahkan |
| 7 | Kebaruan perlu ditegaskan lebih tajam | 🟡 Sedang | Perlu perbaiki framing |

---

## 📝 Poin 1: Tambah Uji Statistik Inferensial

### Masalah
Analisis saat ini baru deskriptif (MAE, RMSE, rata-rata). Reviewer minta ada uji signifikansi.

### Yang Perlu Ditambah

#### A. Uji Perbandingan antar Kelompok (Kuesioner Usability)
Setelah data uji responden terkumpul (15 orang), tambahkan:

```
Uji Kruskal-Wallis (non-parametrik, cocok untuk Likert 1-5):
  H0: Tidak ada perbedaan skor usability antar kelompok
  H1: Ada perbedaan skor usability antar kelompok
  
  Kelompok: Tunanetra (n=5) vs Tunarungu (n=5) vs Non-disabilitas (n=5)
  
  Jika Kruskal-Wallis signifikan (p < 0.05):
    → Uji Mann-Whitney U pairwise (Bonferroni correction)
```

**Contoh penulisan di BAB 4:**
```
Hasil uji Kruskal-Wallis menunjukkan tidak ada perbedaan signifikan 
skor usability antara ketiga kelompok (H=2.34, p=0.31). Median skor 
tunanetra=4.2, tunarungu=4.0, non-disabilitas=4.4.
```

#### B. Uji Korelasi Pearson / Spearman
```
Korelasi antara:
- MAE sensor vs usia responden (apakah makin tua makin akurat?)
- Skor usability vs waktu respons (apakah lebih cepat = lebih puas?)
- Frekuensi kendala vs kategori disabilitas
```

#### C. Interval Kepercayaan 95%
```
Untuk setiap metrik (MAE, R²), hitung CI 95%:
  CI = mean ± 1.96 × (std / √n)
  
Contoh: MAE = 22.57 ± 6.3 mg/dL (CI 95%)
→ Menunjukkan ketidakpastian model masih besar
```

### Script Python untuk Uji Inferensial
Tambahkan di `scripts/statistical_analysis.py`:

```python
from scipy import stats
import numpy as np

# Contoh: Kruskal-Wallis untuk usability
# scores盲人 = [4.2, 3.8, 4.4, 4.0, 4.6]
# scores_deaf = [3.8, 4.0, 4.2, 3.6, 4.4]
# scores_normal = [4.4, 4.6, 4.0, 4.2, 4.8]
# stat, p = stats.kruskal(scores_blind, scores_deaf, scores_normal)

# Contoh: Uji korelasi Spearman
# r, p = stats.spearmanr(mae_values, age_values)

# Contoh: Mann-Whitney U pairwise
# stat, p = stats.mannwhitneyu(scores_blind, scores_deaf, alternative='two-sided')
```

---

## 📝 Poin 2: Detail Dataset Pelatihan

### Masalah
Reviewer tidak tahu detail data yang dipakai untuk training model AI.

### Yang Perlu Ditulis (berdasarkan data aktual)

#### A. Statistik Dataset

```
Jumlah data mentah    : 237 baris (dari 25 file CSV/XLSX)
Setelah deduplikasi   : 46 sesi unik
Setelah cleaning      : 40 sesi (8 tersisa dari 46)
Sesi dikeluarkan      : 6 (gagal sensor optik)
Responden unik        : 32 orang
```

#### B. Distribusi Data

```
Parameter          | Min     | Max     | Rata-rata | Std Dev
------------------|---------|---------|-----------|--------
Glukosa (mg/dL)   | 72      | 187     | 107.6     | 27.4
Usia (tahun)      | 15      | 76      | 31.2      | 18.7
BMI (kg/m²)       | 14.3    | 35.6    | 22.8      | 5.1
Suhu Tubuh (°C)   | 28.4    | 35.3    | 32.6      | 1.8
HR (bpm)          | 60.6    | 72.3    | 63.0      | 2.4
IR_Mean           | 37,550  | 56,003  | 46,528    | 4,827
RED_Mean          | 25,620  | 41,970  | 33,962    | 3,851
```

#### C. Distribusi Target (Glukosa)

```
Kategori           | Jumlah | Persentase
------------------|--------|----------
Normal (<100)     | 15     | 37.5%
Pre-DM (100-125)  | 14     | 35.0%
DM (≥126)         | 11     | 27.5%
```

#### D. Pipeline Preprocessing

```
Langkah 1: Penggabungan 25 file mentah → 237 baris
Langkah 2: Normalisasi nama kolom & tipe data
Langkah 3: Deduplikasi → 46 sesi unik
Langkah 4: Validasi kualitas data:
  - Suhu tubuh/ambient = 0 → imputasi rata-rata (7 baris tubuh, 6 ambient)
  - IR_Mean atau RED_Mean < 10.000 → eksklusi (6 baris)
  - Suhu negatif → eksklusi
  - HR ≤ 0 atau SpO2 di luar 70-100 → eksklusi
Langkah 5: Penggantian nama → SubjectID pseudonim (SHA-256)
Output: 40 sesi bersih, 32 SubjectID unik
```

---

## 📝 Poin 3: Tinjauan Ilmiah PPG → Glukosa

### Masalah
Estimasi gula darah dari PPG belum dijelaskan secara ilmiah mendalam.

### Yang Perlu Ditulis

#### A. Prinsip Fisika PPG dan Glukosa

```
Photoplethysmography (PPG) mengukur perubahan volume darah 
di pembuluh kapiler jari menggunakan cahaya. 

Mekanisme keterkaitan PPG dengan glukosa:
1. Peningkatan glukosa darah → perubahan viskositas darah
2. Perubahan viskositas → perubahan aliran di kapiler
3. Perubahan aliran → perubahan absorpsi cahaya IR dan RED
4. Perubahan absorpsi → perubahan sinyal PPG (amplitudo, bentuk gelombang)

Sinyal PPG memiliki komponen:
- DC component: absorpsi oleh jaringan statis (tulang, kulit, vena)
- AC component: absorpsi oleh darah arteri (berkaitan dengan detak)
- Rasio AC/DC berkorelasi dengan SpO2 dan hemodinamik
```

#### B. Tantangan Estimasi Glukosa Non-Invasif

```
Masalah utama:
1. Sinyal glukosa dalam PPG sangat lemah (SNR rendah)
2. Banyak faktor pengganggu: suhu kulit, tekanan jari, posisi, aktivitas
3. Variasi antar-subjek tinggi (kulit berbeda, struktur kapiler berbeda)
4. MAX30102 adalah sensor consumer (bukan klinis)

Bandingkan dengan studi lain:
| Peneliti          | Sensor      | Metode       | MAE (mg/dL) | Sampel |
|------------------|-------------|--------------|-------------|--------|
| SENS-Able (ini)  | MAX30102    | RF Regressor | 22.57       | 40     |
| Castillo et al.  | ADPD6010    | LSTM         | 18.3        | 43     |
| Prema et al.     | ECG + PPG   | CNN-LSTM     | 12.5        | 150    |
| Tamura et al.    | ECG + PPG   | ANN          | 15.2        | 240    |

Catatan: Perbandingan ini tidak apples-to-apples karena jumlah data, 
sensor, dan metode berbeda. Namun menunjukkan bahwa estimasi glukosa 
dari sinyal optik masih merupakan tantangan terbuka.
```

#### C. Referensi yang Perlu Dikutip

```
[1] Castillo et al. (2023). "Non-invasive blood glucose monitoring 
    using PPG: A deep learning approach." IEEE Sensors Journal.
    
[2] Prema et al. (2022). "Prediction of blood glucose from 
    multimodal physiological signals." Biomedical Signal Processing.

[3] Tamura et al. (2017). "Wearable photoplethysmographic sensors—
    Past and present." Electronics, 6(2), 23.

[4] Yadav et al. (2022). "A review on non-invasive blood glucose 
    monitoring techniques." IEEE Reviews in Biomedical Engineering.

[5] Max30102 Datasheet (2022). Maxim Integrated. (untuk spesifikasi sensor)
```

---

## 📝 Poin 4: Arsitektur Model AI

### Masalah
Reviewer tidak tahu model apa yang dipakai, parameter, dan cara training.

### Yang Perlu Ditulis (berdasarkan data aktual)

#### A. Arsitektur Model

```
Model: Random Forest Regressor
Framework: scikit-learn 1.3+
Jumlah pohon (n_estimators): 200
Kedalaman maksimum (max_depth): 6
Minimum sampel per daun (min_samples_leaf): 2
Random state: 42
Parallel jobs: -1 (semua core)

Total fitur input: 22
  Demografi: Usia, Berat_kg, Tinggi_cm, BMI
  Kondisi: TerakhirMakan_jam, SuhuTubuh, SuhuAmbient
  Vital: HR_est, SpO2_est
  PPG IR: IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS
  PPG RED: RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS
  Ratio: Ratio_AC, Ratio_DC, Samples

Target: GlukosaRef (mg/dL) dari glucometer
```

#### B. Proses Training

```
1. Load dataset: 40 sesi, 32 SubjectID
2. Split: GroupKFold 5-fold (group by SubjectID)
   - Setiap fold: test 6-7 subjek unik, train 25-26 subjek
   - Tidak ada data leakage (subjek test tidak ada di train)
3. Training: Random Forest fit pada data train
4. Prediksi: cross_val_predict pada data test
5. Metrik: MAE, RMSE, median absolute error, R²
```

#### C. Konversi ke TinyML (ESP32)

```
Pipeline konversi:
1. Train RF model → simpan sebagai .joblib (Python)
2. Ekstrak struktur 200 decision trees → buat script Python
3. Generate header file C++ (model_glucose_inference.h)
   - 200 fungsi static tree_X(const float input[22])
   - Setiap tree = nested if-else berdasarkan threshold fitur
   - Fungsi predict_glucose() = average semua tree
4. Size hasil: ~186 KB (200 trees × ~930 bytes/tree)
5. Inferensi: O(1) untuk setiap tree, O(200) total
   - Inference time: < 1 ms di ESP32 (240 MHz dual-core)
```

---

## 📝 Poin 5: Penguatan Validasi Klinis

### Masalah
Validasi saat ini terbatas pada 40 data eksploratif.

### Yang Perlu Ditulis

#### A. Framing yang Jujur

```
Status penelitian: EKSPLORATIF
- Dataset kecil (40 sesi) → belum cukup untuk validasi klinis
- MAE 22.57 mg/dL → di atas target Proposal (< 15 mg/dL)
- R² = 0.0614 → model menjelaskan hanya 6% variansi

Yang DIDUKUNG oleh bukti:
✅ Sensor MAX30102 dapat membaca sinyal PPG
✅ MLX90614 dapat mengukur suhu secara akurat
✅ Pipeline data processing berjalan dengan baik
✅ Model dapat memprediksi glukosa lebih baik dari rata-rata

Yang BELUM didukung oleh bukti:
❌ Estimasi glukosa dengan akurasi klinis
❌部署 TinyML yang sudah tervalidasi
❌ Perbandingan dengan glukometer standar medis
❌ Robustness terhadap variasi kondisi
```

#### B.rencana Validasi Mendatang

```
Tahap 1 (Saat Ini): Eksplorasi awal
  - 40 data, MAE 22.57, R² 0.06
  - Status: SELESAI

Tahap 2: Validasi lanjutan
  - Target: 100-200 data
  - Target: MAE < 20 mg/dL, R² > 0.3
  - Status: BERJALAN

Tahap 3: Validasi klinis (jangka panjang)
  - Target: 500+ data
  - Kolaborasi dengan rumah sakit/klinik
  - IRB approval
  - Status: REncANA
```

---

## 📝 Poin 6: Evaluasi Robustness

### Masalah
Belum ada pengujian terhadap variasi kondisi.

### Yang Perlu Ditambah

#### A. Faktor yang Mempengaruhi Robustness

```
Faktor Sensor:
- Variasi tekanan jari pada sensor
- Posisi jari (tegak/miring)
- Suhu jari (dingin/panas)
- Kelembaban kulit
- Kontak sensor longgar

Faktor Lingkungan:
- Suhu ruangan (AC/kipas/non-AC)
- Pencahayaan (gelap/terang)
- Gangguan elektromagnetik (WiFi, Bluetooth)

Faktor Pengguna:
- Usia (kulit tipis/tebal pada lansia)
- Warna kulit (absorpsi cahaya berbeda)
- Kondisi kesehatan (sirkulasi darah)
- Aktivitas sebelum pengukuran (istirahat/olahraga)
```

#### B. Percobaan Robustness yang Bisa Dilakukan

```
Percobaan 1: Variasi Suhu Ruangan
  - Ukur di ruangan 24°C vs 28°C vs 32°C
  - Bandingkan MAE per kondisi

Percobaan 2: Variasi Tekanan Jari
  - Ukur dengan jari menekan kuat vs ringan
  - Bandingkan hasil

Percobaan 3: Ulang Ukur (Test-Retest)
  - Ukur orang yang sama 3× berturut-turut
  - Hitung koefisien variasi (CV)

Percobaan 4: Variasi Waktu
  - Ukur pagi (puasa) vs siang (postprandial)
  - Bandingkan variasi
```

#### C. Template Analisis Robustness

```
Untuk setiap faktor, hitung:
1. MAE per kondisi
2. Standard deviation per kondisi
3. Koefisien variasi (CV = std/mean × 100%)
4. Uji Mann-Whitney U antar kondisi

Kriteria keberhasilan:
- CV < 10% → cukup robust
- p > 0.05 → tidak ada perbedaan signifikan antar kondisi
```

---

## 📝 Poin 7: Penguatan Kebaruan

### Masalah
Reviewer minta kebaruan ditegaskan lebih tajam.

### Framing Kebaruan yang Diperkuat

#### A. Posisi SENS-Able di Peta Penelitian

```
Kebaruan SENS-Able pada 3 dimensi:

1. INKLUSIVITAS (assistive technology)
   Sebagian besar penelitian PPG-glucose untuk orang umum.
   SENS-Able dirancang KHUSUS untuk penyandang disabilitas
   dengan output multimodal (audio + visual + vibrasi).

2. INTEGRASI ON-DEVICE AI (TinyML)
   Sebagian besar penelitian PPG-glucose berjalan di PC/cloud.
   SENS-Able menjalankan model AI LANGSUNG di ESP32 tanpa internet.

3. MULTI-PARAMETER HEALTH MONITORING
   Sebagian besar penelitian fokus pada SATU parameter.
   SENS-Able mengintegrasikan glukosa + detak jantung + suhu 
   dalam SATU alat yang kompak dan affordable.
```

#### B. Perbandingan dengan Karya Sebelumnya

```
| Aspek              | Studi Sebelumnya        | SENS-Able              |
|-------------------|------------------------|------------------------|
| Platform          | PC / Cloud / Smartphone | ESP32 (embedded)       |
| Output            | Layar saja              | Audio + Visual + Haptic|
| Target pengguna   | Umum                   | Disabilitas            |
| Estimasi          | Satu parameter          | Multi-parameter        |
| Biaya             | Mahal (> Rp 1 juta)    | Terjangkau (~Rp 445k) |
| Konektivitas      | Butuh internet          | Standalone             |
```

#### C. Kontribusi Keilmiah

```
1. Bukti empiris bahwa PPG dari MAX30102 (sensor consumer) 
   memiliki korelasi dengan glukosa (meski masih lemah)
   
2. Framework pemrosesan data PPG yang dapat direproduksi 
   untuk peneliti lain
   
3. Arsitektur TinyML untuk inference RF di ESP32 yang efisien
   
4. Desain UI/UX inklusif yang mempertimbangkan kebutuhan 
   penyandang disabilitas sensorik
```

---

## 📋 Checklist Revisi Dokumen

### Proposal/Laporan yang Perlu Diupdate:

- [ ] **BAB 2 (Tinjauan Pustaka)**
  - [ ] Tambah tinjauan PPG → Glukosa (Poin 3)
  - [ ] Tambah referensi Castillo et al., Tamura et al.
  - [ ] Jelaskan mekanisme fisika PPG dan keterkaitannya dengan glukosa

- [ ] **BAB 3 (Metode)**
  - [ ] Detail dataset: jumlah, sumber, distribusi, preprocessing (Poin 2)
  - [ ] Detail model: arsitektur RF, parameter, training (Poin 4)
  - [ ] Tambah rencana uji robustness (Poin 6)

- [ ] **BAB 4 (Hasil)**
  - [ ] Tambah uji statistik inferensial (Poin 1)
  - [ ] Framing jujur tentang validasi (Poin 5)
  - [ ] Tambah interval kepercayaan untuk metrik

- [ ] **BAB 5 (Kesimpulan)**
  - [ ] Perkuat kebaruan (Poin 7)
  - [ ] Jelaskan keterbatasan dan rencana mendatang

- [ ] **Daftar Pustaka**
  - [ ] Tambah minimal 5 referensi PPG-glucose
  - [ ] Tambah referensi TinyML/ESP32
  - [ ] Tambah referensi assistive technology

---

## 💡 Tips Penulisan

### Gunakan Bahasa yang Tepat:

```
❌ "SENS-Able memiliki akurasi 90% dalam mendeteksi diabetes"
✅ "Model eksploratif SENS-Able menunjukkan MAE 22.57 mg/dL 
    dalam estimasi glukosa berbasis PPG pada 40 sesi data"

❌ "Alat ini sudah siap digunakan di rumah sakit"
✅ "Prototipe ini menunjukkan potensi sebagai alat skrining awal 
    yang memerlukan validasi klinis lebih lanjut"

❌ "PPG dapat menggantikan glukometer"
✅ "Estimasi glukosa dari PPG masih merupakan tantangan terbuka; 
    hasil eksploratif ini menunjukkan arah yang menjanjikan"
```

### Struktur Paragraf yang Baik:

```
1. Klaim (apa yang ditemukan)
2. Bukti (angka/data)
3. Interpretasi (apa artinya)
4. Keterbatasan (apa yang belum)
5. Implikasi (apa selanjutnya)
```

---

## 🚀 Timeline Revisi

| Minggu | Tugas | Output |
|---|---|---|
| Minggu 1 | Tulis BAB 2 (Pustaka PPG-Glukosa) | 3-5 halaman tinjauan |
| Minggu 1 | Tulis detail dataset (BAB 3) | Tabel + pipeline |
| Minggu 2 | Tulis arsitektur model (BAB 3) | Diagram + parameter |
| Minggu 2 | Jalankan uji inferensial | Hasil statistical test |
| Minggu 3 | Tulis BAB 4 (Hasil + Pembahasan) | Dengan CI + p-value |
| Minggu 3 | Tambah robustness evaluation | Hasil percobaan |
| Minggu 4 | Perkuat kebaruan (BAB 5) | Peta kebaruan |
| Minggu 4 | Finalisasi & cetak | PDF final |
