# Catatan riset dataset publik untuk SENS-Able

Tanggal pencarian: 26 Agustus 2026.

## Kandidat 1: Mazandaran PPG Blood Glucose Dataset

Sumber resmi: https://data.mendeley.com/datasets/37pm7jk7jn/1

Halaman Mendeley Data menyatakan dataset ini berisi 67 sinyal PPG mentah dari 23 relawan, direkam pada 2175 Hz, dengan label usia, jenis kelamin, kadar glukosa darah invasif (mg/dL), tinggi, dan berat. Referensi glukosa diambil menggunakan Accu-Check Active. Sensor memakai LED hijau 550 nm dan photodiode APDS9008, bukan MAX30102. File tersedia sebagai arsip ZIP berisi folder RawData, Labels, dan Figures. Lisensi yang ditampilkan adalah CC BY 4.0. Dataset ini berpotensi untuk pretraining/benchmark sinyal PPG, tetapi perbedaan sensor, laju sampling, fitur, dan populasi membuat pencampuran langsung dengan SENS-Able berisiko menyebabkan domain shift.

## Kandidat 2: PhysioCGM

Sumber artikel: https://pmc.ncbi.nlm.nih.gov/articles/PMC12630648/

Akses browser langsung terhalang pemeriksaan reCAPTCHA, sehingga detail belum dianggap terverifikasi penuh dari halaman sumber. Hasil pencarian mengindikasikan dataset multimodal dengan ECG, PPG, EDA, dan skin temperature serta rekaman glukosa. Detail akses data, lisensi, jumlah peserta, dan sinkronisasi waktu harus diverifikasi dari repositori/data availability resmi sebelum dipakai.

## Prinsip penggunaan

Dataset online tidak boleh langsung digabung ke 40 sesi SENS-Able lalu divalidasi seolah-olah semuanya berasal dari alat yang sama. Pilihan yang lebih aman adalah: (1) benchmark eksternal, (2) pretraining sinyal tanpa label lalu fine-tuning dengan SENS-Able, atau (3) eksperimen domain adaptation dengan laporan terpisah. Semua evaluasi final tetap harus memakai GroupKFold berdasarkan SubjectID SENS-Able dan tidak boleh memakai GlukosaRef sebagai fitur.

## Kandidat 3: OhioT1DM

Sumber resmi: https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html

OhioT1DM berisi 8 minggu data dari 12 orang dengan diabetes tipe 1: CGM tiap 5 menit, finger-stick berkala, insulin, catatan makan/aktivitas, dan data fitness band. Namun akses dataset memerlukan permintaan melalui email institusional dan persetujuan pemilik data. Halaman resmi tidak menyebut PPG sebagai modalitas utama. Dataset ini lebih cocok untuk riset prediksi/forecasting glukosa berbasis CGM dan konteks, bukan transfer langsung model PPG MAX30102 SENS-Able.

## Kandidat 4: D1NAMO

Sumber resmi: https://zenodo.org/records/5651217

D1NAMO mencakup 20 subjek sehat dan 9 pasien diabetes tipe 1, dengan ECG, pernapasan, akselerometer, pengukuran glukosa, dan foto makanan. Dataset tersedia di Zenodo dengan lisensi CC BY-SA 4.0, tetapi ukurannya sekitar 10,2 GB. Tidak ada PPG atau sensor suhu yang sesuai dengan fitur SENS-Able. Dataset ini dapat menjadi referensi metodologis untuk multimodal diabetes, tetapi tidak cocok sebagai data training langsung untuk model PPG SENS-Able.

## Kandidat 5: STU PPG Blood Glucose Dataset (Zenodo 2026)

Sumber resmi: https://zenodo.org/records/21978226 dan API metadata: https://zenodo.org/api/records/21978226

Dataset ini paling dekat dengan SENS-Able untuk eksperimen PPG: 125 rekaman dari 24 subjek, enam kanal PPG pada 530/655/940 nm, akselerometer, serta referensi glukosa kapiler dari Beurer GL 49 yang diambil segera sebelum rekaman. Data tersedia dalam WFDB, lisensi CC0, dan arsip sinyal hanya sekitar 5,9 MB. Label publik berada dalam mmol/L dan dikonversi ke mg/dL dengan faktor 18.0182 hanya dalam eksperimen; `GlukosaRef` SENS-Able tidak diubah.

Arsip dan file QC berhasil diunduh serta dibaca. Dari 125 rekaman, 105 lolos QC dan dapat diproses, dengan 18 subjek tersisa. Rentang label publik yang dipakai adalah 39.64–304.5076 mg/dL.

Uji augmentasi dilakukan dengan 10 fitur yang tersedia di kedua sumber: demografi, rasio variasi IR/RED, rentang relatif IR/RED, rasio IR/RED, dan HR. Validasi SENS-Able tetap memakai 5-fold GroupKFold berdasarkan `SubjectID`. Model SENS-Able saja menghasilkan MAE 22.1055 mg/dL pada kontrak fitur bersama, sedangkan model yang diberi tambahan data publik menghasilkan MAE 25.8117 mg/dL. Model publik saja menghasilkan MAE 49.6547 mg/dL. Pembobotan data publik juga diuji dengan bobot 0.05, 0.1, 0.25, 0.5, 1, dan 2. Hasil terbaik dari pembobotan adalah MAE 23.1664 mg/dL pada bobot 0.1, tetap lebih buruk daripada model SENS-Able saja dengan MAE 22.1055 mg/dL. Jadi dataset ini valid sebagai pembanding, tetapi pada percobaan ini belum meningkatkan model fisik karena perbedaan perangkat, distribusi data, dan populasi.

## Kandidat 6: Glucdict

Sumber resmi: https://figshare.com/articles/dataset/Glucdict_-_Wearable_Sensors_and_CGM/25939312 dan API metadata: https://api.figshare.com/v2/articles/25939312

Glucdict berisi 12 peserta selama sekitar 10 hari, CGM Dexcom tiap 5 menit, sensor smartwatch/ponsel, heart rate, aktivitas makan/minum, dan suhu? Metadata yang tersedia menjelaskan heart rate, langkah, dan sensor gerak, tetapi tidak menyediakan PPG mentah yang sebanding dengan kanal optik SENS-Able. Arsip berukuran sekitar 4,7 GB dan berlisensi CC BY 4.0. Dataset ini cocok untuk forecasting CGM berbasis konteks/wearable, bukan untuk menambah training model PPG SENS-Able. Karena itu tidak diunduh penuh dan tidak dimasukkan ke eksperimen.
