# Recheck dan Planning OPSI Tahap 2 — SENS-Able

**Tanggal penyusunan:** 26 Agustus 2026
**Batas unggah laporan:** 31 Agustus 2026
**Tim:** AntroOptic Team — Muhammad Daffa Ramadhan dan Aira Cantika Putri
**Sekolah:** MAN 2 Kota Bima
**Bidang:** FTR dan Sistem Pengukuran & Monitoring Cerdas

> **Kesimpulan utama:** SENS-Able masih sangat mungkin dijadikan laporan OPSI Tahap 2, tetapi bentuk yang paling aman dan paling mungkin berhasil bukan klaim “alat diagnosis diabetes” atau “AI TinyML siap pakai”. Fokus laporan harus dipersempit menjadi **evaluasi awal prototipe pengumpul data PPG dan suhu untuk estimasi glukosa berdasarkan nilai referensi glucometer**, disertai analisis kuantitatif yang jujur, dokumentasi alat, serta evaluasi aksesibilitas hanya sejauh benar-benar sudah diuji.

## 1. Dasar Penentuan Strategi

Panduan resmi OPSI SMA Sederajat 2026 menyatakan bahwa laporan hasil penelitian maksimal 20 halaman di luar lampiran, disertai logbook dan klirens etik bila diperlukan, serta diunggah dalam format PDF maksimal 8 MB [1]. Laporan dinilai terutama dari hasil dan pembahasan sebesar 30%, metodologi sebesar 20%, serta kebaruan dan kemanfaatan masing-masing 10% [1]. Karena penelitian menggunakan responden manusia dan pengukuran kesehatan, panduan tersebut juga mewajibkan perhatian pada etika, privasi, keselamatan, dan persetujuan kelayakan etik sebelum penelitian dilaksanakan [1].

Diskusi yang dibagikan juga mengambil arah yang tepat: data kecil dipakai untuk membangun pipeline dan eksperimen awal, bukan untuk klaim akurasi final. `GlukosaRef` harus menjadi target, sedangkan fitur sensor harus menjadi input. Pelatihan dapat dilakukan secara bertahap ketika data bertambah, tetapi model final tidak boleh diklaim sebelum data dan validasi memadai [2].

## 2. Recheck Kondisi SENS-Able Saat Ini

| Komponen | Bukti saat ini | Implikasi untuk laporan |
|---|---|---|
| Dataset | 237 baris dari 25 file/sheet; setelah normalisasi dan deduplikasi menjadi 46 sesi unik; 6 sesi dikeluarkan karena tangkapan optik gagal; 40 sesi processed tersisa, dengan 32 SubjectID | Lebih banyak data dapat dipakai, tetapi tetap merupakan studi pendahuluan/pilot, belum cukup untuk klaim klinis |
| Referensi gula darah | `GlukosaRef` diperlakukan sebagai nilai glucometer dalam mg/dL | Dapat menjadi target validasi regresi, tetapi sumber alat, waktu ukur, dan pasangan pengukuran harus ditulis jelas |
| Distribusi label | 32 label diabetes 0 dan 1 label diabetes 1 | Jangan menjadikan klasifikasi diabetes sebagai hasil utama; akurasi klasifikasi akan menyesatkan |
| Validasi regresi saat ini | Setelah mempertahankan sesi dengan suhu nol yang optiknya valid dan mengimputasi suhu secara transparan, konfigurasi V0.1 yang sama menghasilkan MAE 22,5716 mg/dL, RMSE 27,0552 mg/dL, R² 0,0614 dengan GroupKFold berdasarkan `SubjectID` | Hasil ini masih eksploratif; belum memenuhi target MAE <15 mg/dL dan tidak boleh disebut akurasi klinis |
| Firmware | Kode collector menyimpan fitur MAX30100/MLX90614 dan `GlukosaRef` ke LittleFS | Alur akuisisi data dapat menjadi kontribusi teknis yang nyata |
| Kesesuaian hardware | Proposal menyebut MAX30102, sedangkan firmware memakai library dan objek `MAX30100` | Harus diverifikasi dari modul fisik; laporan tidak boleh menyebut MAX30102 bila hardware sebenarnya MAX30100 |
| Output inklusif | Audio dan vibrasi sudah terintegrasi pada satu perangkat fisik SENS-Able menurut konfirmasi peneliti; data uji fungsi dan usability formal belum tersedia | Implementasi fisik boleh dijelaskan sebagai komponen alat. Klaim efektivitas, aksesibilitas, dan usability harus menunggu bukti pengujian |
| TinyML | Belum ada bukti `model.tflite`, `model.h`, sketch inference, waktu inference, atau penggunaan RAM di ESP32 | Jadikan pekerjaan lanjutan, bukan hasil yang sudah selesai |
| Privasi | Repository sudah private; raw dataset tetap berisi identitas dan data kesehatan | Jangan membuka repository; laporan/presentasi gunakan SubjectID atau data agregat |

## 3. Fokus Penelitian yang Paling Memungkinkan

### Judul yang Direkomendasikan

**SENS-Able: Evaluasi Awal Fitur Sinyal PPG dan Suhu pada Prototipe Pemantauan Kesehatan Inklusif untuk Estimasi Glukosa Berbasis Referensi Glucometer**

Judul ini lebih defensible karena menekankan evaluasi awal dan referensi glucometer. Judul tersebut tidak menyatakan bahwa MAX30100 telah menjadi pengganti glucometer, tidak menyatakan diagnosis, dan tetap mempertahankan unsur inklusivitas dari proposal tahap 1.

### Rumusan Masalah Baru

1. Apakah fitur sinyal PPG dan suhu yang dikumpulkan oleh prototipe SENS-Able memiliki hubungan yang cukup untuk digunakan dalam eksperimen awal estimasi `GlukosaRef`?
2. Berapa besar galat estimasi glukosa SENS-Able terhadap nilai referensi glucometer pada data uji yang tersedia?
3. Apakah proses pengumpulan data dengan antarmuka SENS-Able dapat dilakukan secara konsisten dan terdokumentasi pada kondisi uji yang ditetapkan?

Pertanyaan mengenai peningkatan kemandirian tunanetra/tunarungu tetap dapat dicantumkan sebagai arah manfaat, tetapi jangan dijadikan hasil utama kecuali pengujian pengguna dan datanya benar-benar tersedia.

### Tujuan yang Dapat Dibuktikan

Penelitian bertujuan membangun pipeline pengumpulan data sensor dan nilai referensi glucometer, membersihkan data secara terdokumentasi, membandingkan beberapa model regresi sebagai eksperimen awal, serta mengukur MAE, RMSE, dan R² dengan pembagian berbasis subjek. Penelitian tidak bertujuan menetapkan diagnosis diabetes atau menggantikan pemeriksaan glucometer.

### Hipotesis Eksploratif

Model regresi yang menggunakan fitur PPG, suhu, dan karakteristik dasar responden dapat menghasilkan galat estimasi yang lebih rendah daripada baseline sederhana berupa prediksi rata-rata `GlukosaRef`. Hipotesis ini bersifat eksploratif dan dapat ditolak berdasarkan hasil pengujian.

## 4. Rancangan Metode Final

### 4.1 Variabel dan Data

`GlukosaRef` harus dijelaskan sebagai **nilai gula darah dari glucometer asli dalam mg/dL** yang diambil pada sesi pengukuran yang sama atau sedekat mungkin dengan rekaman sensor. Nilai tersebut adalah variabel target/referensi `y`, bukan input `X`. Fitur input dapat terdiri atas `Usia`, `Berat_kg`, `Tinggi_cm`, `BMI`, `TerakhirMakan_jam`, `SuhuTubuh`, `SuhuAmbient`, `HR_est`, `SpO2_est`, fitur IR, fitur RED, `Ratio_AC`, `Ratio_DC`, dan `Samples`—dengan catatan fitur yang tidak benar-benar berasal dari pengukuran valid harus dikeluarkan.

Satu baris data harus mewakili satu sesi pengukuran yang jelas. Jika satu subjek memiliki beberapa sesi, semua sesi harus diberi `SubjectID` yang sama dan tidak boleh diperlakukan sebagai subjek baru pada evaluasi.

### 4.2 Pembersihan Data

Pipeline `scripts/prepare_dataset.py` dipakai sebagai sumber kebenaran. Pipeline tersebut mempertahankan raw input, menghapus salinan identik setelah normalisasi angka, mempertahankan sesi dengan suhu nol bila fitur optiknya valid, mengimputasi suhu nol dengan rata-rata positif yang dihitung terpisah per kolom, menambahkan flag provenance, menolak tangkapan optik yang jelas gagal, serta mengganti nama dengan `SubjectID` pada dataset processed. Setiap baris yang dikeluarkan harus tetap tercatat dalam `excluded_records.csv` beserta alasannya.

Nilai `GlukosaRef` tidak boleh diubah untuk memperbaiki hasil model. Jika nilai glucometer salah input atau tidak dapat dipastikan, baris tersebut harus ditandai dan dikeluarkan, bukan dikoreksi berdasarkan prediksi sensor.

### 4.3 Model dan Evaluasi

Bandingkan sekurang-kurangnya tiga pendekatan: baseline prediksi rata-rata, regresi linear, dan Random Forest Regressor. Gradient Boosting dapat ditambahkan jika waktu cukup. Semua preprocessing dan pemilihan model harus dilakukan di dalam pipeline dan fold pelatihan.

Gunakan `GroupKFold` berdasarkan `SubjectID`. Laporkan jumlah subjek, jumlah sesi, rentang `GlukosaRef`, MAE, RMSE, R², median absolute error, variasi antar-fold, dan grafik nilai referensi versus prediksi. Hasil negatif atau buruk tetap dilaporkan karena itu adalah hasil penelitian yang sah. Jangan memakai data sintetis untuk menambah jumlah subjek dan jangan memilih model berdasarkan hasil terbaik tanpa menjelaskan prosesnya.

### 4.4 Pengujian Alat

Untuk setiap sesi, logbook minimal harus mencatat tanggal/waktu, kode subjek, kondisi makan, nilai glucometer, kondisi sensor, jumlah sampel, nilai suhu, dan catatan kegagalan. Bila mengumpulkan data baru, lakukan pengukuran glucometer dan perekaman sensor pada sesi yang sama. Jangan mengambil label glucometer dari perkiraan sensor.

Jika pengujian usability dilakukan, gunakan indikator yang benar-benar dapat diukur, misalnya waktu memahami hasil, jumlah bantuan, keberhasilan mengikuti prosedur, dan skor kuesioner. Jangan menulis klaim “ramah tunanetra/tunarungu” hanya berdasarkan desain antarmuka; klaim tersebut harus didukung oleh observasi atau pengujian pengguna.

## 5. Apa yang Harus Dihentikan atau Diubah

| Klaim/metode lama | Keputusan |
|---|---|
| “Akurasi diabetes 90,9%” sebagai hasil utama | Hentikan. Confusion matrix sebelumnya memiliki TP = 0 dan F1 = 0,0; gunakan regresi glukosa sebagai fokus utama. |
| `GlukosaRef` sebagai fitur untuk memprediksi diabetes | Jangan digunakan pada model estimasi glukosa; itu adalah target referensi. |
| Suhu nol langsung dibuang | Jangan langsung dibuang bila fitur optik valid. Imputasi mean hanya pada kolom suhu yang nol, tandai provenance, dan jangan mengubah `GlukosaRef`. |
| “Model sudah berjalan di ESP32 via TinyML” | Jangan diklaim sebelum ada `model.tflite`/`model.h`, sketch inference, dan pengukuran performa. |
| MAX30102 dan MAX30100 dipakai bergantian dalam dokumen | Verifikasi modul fisik dan pilih satu nama/library yang benar. |
| Audio dan vibrasi dianggap sudah tervalidasi | Implementasi fisiknya sudah ada, tetapi jangan menyatakan efektif atau tervalidasi sebelum ada uji fungsi, uji respons, dan uji usability dengan bukti. |
| Data nama asli di laporan/poster | Ganti dengan `SubjectID`, tabel agregat, atau hapus identitas. Raw hanya untuk arsip private. |
| Mengubah nilai lama agar terlihat bersih | Jangan. Simpan raw, log perubahan, dan keluarkan baris sensor gagal secara transparan. |

## 6. Rencana Kerja 26–31 Agustus 2026

| Tanggal | Fokus wajib | Output yang harus selesai |
|---|---|---|
| **26 Agustus** | Bekukan scope, cocokkan proposal dengan bukti, verifikasi modul MAX30100/MAX30102, cek status izin/klirens etik, dan tetapkan judul baru | Judul final, rumusan masalah, metode final, checklist etika, daftar bukti yang tersedia |
| **27 Agustus** | Jika izin dan kondisi lapangan memungkinkan, lakukan pengukuran tambahan yang berpasangan: glucometer lalu sensor; jika tidak, jangan memaksakan responden baru dan gunakan dataset pilot yang ada | Logbook, foto setup, data sesi baru yang valid, atau keputusan tertulis memakai dataset existing |
| **28 Agustus** | Jalankan cleaning final, bandingkan baseline/linear/random forest, buat tabel metrik, scatter plot, residual plot, dan tabel excluded records | Dataset processed final, notebook/script final, grafik, tabel hasil |
| **29 Agustus** | Tulis Bab 3, Bab 4, dan Bab 5 berdasarkan hasil nyata; sinkronkan anggaran dan kegiatan; lengkapi dokumentasi alat | Draft laporan maksimal 20 halaman di luar lampiran |
| **30 Agustus** | Pemeriksaan mentor dan tim: angka, label gambar, sumber pustaka, etika, anonimisasi, orisinalitas, AI declaration, logbook, dan ukuran PDF | PDF final, logbook final, klirens/surat pendukung, poster draft, backup berkas |
| **31 Agustus** | Unggah lebih awal melalui portal OPSI, cek file dapat dibuka dan semua lampiran terbaca; simpan bukti unggah | Bukti submission sebelum batas resmi |

Jika data tambahan tidak dikumpulkan sebelum tenggat, gunakan fallback yang jujur: **laporan studi pendahuluan berbasis 40 sesi processed dan 32 SubjectID**, dengan keterbatasan eksplisit bahwa data kecil dan belum cukup untuk validasi klinis. Lebih baik laporan pilot yang metodologinya bersih daripada laporan dengan angka besar yang tidak dapat dipertanggungjawabkan.

## 7. Struktur Laporan Tahap 2

Struktur berikut mengikuti panduan laporan OPSI dan menyesuaikan isi yang benar-benar tersedia [1].

1. **Halaman Sampul** — judul, kode peserta, nama tim, sekolah, bidang, dan tahun.
2. **Abstrak** — latar singkat, tujuan, metode, jumlah data, metrik utama, dan kesimpulan terbatas. Tulis setelah Bab 4 selesai.
3. **BAB 1 Pendahuluan** — latar belakang yang lebih fokus, rumusan masalah, tujuan, hipotesis eksploratif, dan manfaat.
4. **BAB 2 Landasan Teori dan Studi Pustaka** — PPG, glucometer sebagai reference measurement, estimasi glukosa, evaluasi regresi, TinyML sebagai rencana lanjutan, dan aksesibilitas.
5. **BAB 3 Metode Penelitian** — desain penelitian, lokasi/waktu, hardware dan versi sensor yang benar, alur pengukuran berpasangan, data dictionary, cleaning rules, feature/target separation, GroupKFold, dan etika.
6. **BAB 4 Hasil dan Pembahasan** — profil data, baris yang dikeluarkan, distribusi `GlukosaRef`, hasil baseline dan model, grafik referensi versus prediksi, error, analisis kegagalan, serta hubungan hasil dengan penelitian terdahulu.
7. **BAB 5 Anggaran Biaya dan Kegiatan** — realisasi biaya dan kegiatan yang benar-benar dilakukan; jangan menyalin jadwal rencana lama tanpa pembaruan.
8. **BAB 6 Kesimpulan dan Saran** — kesimpulan langsung dari data, keterbatasan, kebutuhan data lebih banyak, kalibrasi, dan rencana deployment yang belum selesai.
9. **Daftar Pustaka** — hanya sumber yang benar-benar dikutip.
10. **Lampiran** — logbook, klirens etik/surat terkait, tabel data anonymized, daftar komponen, foto alat, screenshot collector, kode inti, dan grafik tambahan.

Panduan resmi menampilkan dua bagian yang sama-sama disebut Bab 5 pada ringkasan struktur laporan. Untuk menjaga keterbacaan, laporan dapat menomori anggaran sebagai **BAB 5** dan kesimpulan sebagai **BAB 6**, atau mengikuti template portal bila template tersebut menentukan penomoran lain.

## 8. Bukti yang Wajib Dikumpulkan

| Bukti | Minimal yang harus ada |
|---|---|
| Alat | Foto rangkaian, foto sensor ditempelkan dengan benar, label komponen, dan bukti versi modul |
| Data | File raw private, dataset processed anonymized, data dictionary, exclusion log, dan flag suhu yang diimputasi |
| Glucometer | Foto/identitas alat bila diizinkan, prosedur, satuan mg/dL, waktu pasangan pengukuran, dan logbook |
| Firmware | Kode original, supported sketch, konfigurasi pin, library, dan screenshot serial/web collector |
| Analisis | Script reproducible, konfigurasi V0.1, artifact model, tabel metrik, grafik, baseline, dan penjelasan keterbatasan |
| Etika | Klirens etik atau dokumen kelayakan/izin yang diminta panitia, surat pengantar sekolah, dan consent sesuai arahan pembimbing |
| Aksesibilitas | Foto/video atau demo audio-vibrasi untuk bukti integrasi, lalu prosedur uji, peserta/kriteria, observasi, dan hasil kuesioner jika efektivitas/usability diklaim |
| Pelaporan | Logbook, versi dataset/model, manifest hash, foto kegiatan, dan backup lokal/cloud private |

## 9. Quality Gate Sebelum Unggah

Laporan hanya boleh dinyatakan siap jika seluruh jawaban berikut “ya”.

| Pertanyaan pemeriksaan | Status yang ditargetkan |
|---|---|
| Apakah setiap hasil glukosa berasal dari `GlukosaRef` glucometer yang dijelaskan prosedurnya? | Ya |
| Apakah `GlukosaRef` tidak masuk sebagai fitur input model? | Ya |
| Apakah pembagian evaluasi menjaga subjek yang sama tetap berada dalam grup yang benar? | Ya |
| Apakah semua angka di Bab 4 dapat dihasilkan ulang dari script dan dataset processed? | Ya |
| Apakah hasil buruk, outlier, dan data yang dikeluarkan tetap dilaporkan? | Ya |
| Apakah hardware yang ditulis sama dengan modul fisik yang digunakan? | Ya |
| Apakah klaim audio, vibrasi, TinyML, dan aksesibilitas memiliki bukti masing-masing? | Ya atau klaim dihapus/dibatasi |
| Apakah identitas responden di laporan dan poster sudah dianonimkan? | Ya |
| Apakah klirens etik/izin dan logbook sudah diperiksa pembimbing? | Ya |
| Apakah PDF laporan ≤20 halaman di luar lampiran dan ≤8 MB? | Ya |
| Apakah laporan ditulis dan dianalisis sendiri oleh peserta serta penggunaan AI dinyatakan sesuai panduan? | Ya |

## 10. Keputusan Feasibility

**Status: PASS WITH LIMITATIONS.** SENS-Able masih feasible untuk OPSI Tahap 2 jika diposisikan sebagai **studi pendahuluan dan evaluasi awal prototipe**, bukan perangkat diagnosis dan bukan TinyML production deployment. Kontribusi paling kuat yang dapat dipertanggungjawabkan sebelum 31 Agustus adalah pipeline akuisisi data yang nyata, penggunaan glucometer sebagai reference target, pembersihan data yang dapat diaudit, evaluasi regresi yang tidak mengalami label leakage, dan pembahasan keterbatasan secara ilmiah.

Kontribusi yang belum boleh dinyatakan selesai adalah akurasi klinis, penggantian glucometer, diagnosis diabetes, inferensi TinyML di ESP32, serta efektivitas audio/vibrasi jika bukti implementasi dan pengujiannya belum tersedia.

## Referensi

[1]: https://pusatprestasinasional.kemendikdasmen.go.id/uploads/lampiran_pengumuman/Panduan%20OPSI%20SMA%20Sederajat%202026.pdf "Panduan OPSI SMA Sederajat 2026, Pusat Prestasi Nasional"
[2]: https://chatgpt.com/share/6a8e73de-e2d8-83ec-862e-2a66175ed9cc "Shared discussion: Alat SENS-Able"
[3]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/tree/data-cleaning-glucometer-validation "SENS-Able repository, data-cleaning-glucometer-validation branch"
