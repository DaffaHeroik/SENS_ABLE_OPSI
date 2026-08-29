# Recheck Proposal OPSI Tahap 1 — OPSI2025.docx

**Tanggal recheck:** 26 Agustus 2026  
**Proyek:** SENS-Able — AntroOptic Team  
**Status:** Proposal tahap 1 berhasil menjadi dasar, tetapi perlu diselaraskan dengan hasil penelitian nyata sebelum dipakai sebagai dasar laporan tahap 2.

## Ringkasan Eksekutif

Proposal yang diunggah memiliki arah inovasi yang kuat: prototipe pemantauan kesehatan dengan ESP32, MAX30102, suhu, dan tujuan aksesibilitas. Namun, proposal menggambarkan target akhir yang lebih luas daripada bukti yang saat ini tersedia. Repository telah membuktikan adanya pipeline pengumpulan data, raw dataset, dataset processed, referensi glucometer, validasi regresi awal, dan firmware collector. Repository belum membuktikan TinyML inference di ESP32, audio/vibrasi yang telah bekerja dan diuji, atau pengujian usability pada kelompok tunanetra, tunarungu, dan non-disabilitas.

Karena itu, proposal tidak perlu dibuang atau ditulis ulang dari nol. Bagian latar belakang, ide alat, komponen utama, dan motivasi aksesibilitas dapat dipertahankan. Bagian tujuan, metode, indikator keberhasilan, hasil yang diharapkan, dan klaim produk harus dipersempit menjadi **evaluasi awal prototipe pengumpulan data PPG dan suhu untuk estimasi glukosa terhadap referensi glucometer**. Proposal tahap 1 tetap menjadi asal-usul ide; laporan tahap 2 harus menceritakan apa yang benar-benar dilaksanakan.

## 1. Perbandingan Klaim Proposal dan Bukti Saat Ini

| Bagian proposal | Isi proposal tahap 1 | Bukti repository saat ini | Keputusan revisi |
|---|---|---|---|
| Judul | Smart Health Monitor inklusif berbasis AI dengan audio, visual, dan vibrasi | Collector dan OLED/web terbukti; audio/vibrasi belum diuji | Pertahankan identitas SENS-Able, tambahkan frasa “evaluasi awal prototipe” bila dipakai untuk laporan |
| Hardware | ESP32, MAX30102, OLED, PAS-0158, MLX90614, motor vibrasi | ESP32 collector dan PPG/suhu terdokumentasi; pengguna mengonfirmasi modul fisik MAX30102 | Tulis MAX30102 secara konsisten; jelaskan library `MAX30100` yang digunakan firmware dan verifikasi kompatibilitasnya |
| Parameter | Gula darah, detak jantung, dan suhu | Dataset memiliki `GlukosaRef`, `HR_est`, suhu, dan fitur IR/RED | Nyatakan gula sebagai estimasi yang dibandingkan dengan glucometer; jangan menyebut pengukuran non-invasif sudah setara glucometer |
| AI/TinyML | Model PPG publik di-deploy ke ESP32 via TensorFlow Lite Micro | Belum ada model embedded atau sketch inference yang terverifikasi | Jadikan TinyML sebagai pekerjaan lanjutan kecuali bukti deployment segera tersedia |
| Audio/vibrasi | Tiga modalitas output dan pola getaran normal/waspada/bahaya | Belum ada bukti implementasi dan uji yang cukup | Jangan masukkan sebagai hasil; boleh ditulis sebagai rancangan atau keterbatasan |
| Responden | 15 responden: 5 tunanetra, 5 tunarungu, 5 non-disabilitas; 30 pengukuran per parameter | 40 sesi processed dan 32 SubjectID; komposisi kelompok belum terbukti | Laporkan angka dataset nyata; jangan mengklaim komposisi kelompok tanpa daftar responden dan bukti pengujian |
| Usability | Observasi dan kuesioner Likert 1–5 | Belum ada dataset kuesioner atau hasil observasi terverifikasi | Jadikan hasil tambahan hanya jika kuesioner dan logbook tersedia; jika tidak, hapus dari hasil |
| Indikator | MAE HR <3 bpm, suhu <0,3°C, glukosa <15 mg/dL; usability ≥4; mandiri ≥80% | Baru ada validasi regresi glukosa; MAE 22,5716 mg/dL pada model comparison | Laporkan target proposal sebagai target awal dan hasil aktual secara terpisah; jangan mengklaim tercapai |
| Pengolahan data | Arduino IDE | Pipeline aktual menggunakan Python/pandas/scikit-learn | Ganti metode analisis laporan menjadi pipeline Python; Arduino IDE digunakan untuk firmware, bukan seluruh analisis statistik |
| Jadwal | Pengumpulan April–Mei dan laporan selesai Juni | Pengembangan dan cleaning berlangsung sampai Agustus | Gunakan jadwal aktual pada laporan tahap 2 dan jelaskan perubahan jadwal bila diperlukan |
| Anggaran | Total Rp444.900 | Dapat dipakai jika sesuai pengeluaran aktual | Ubah menjadi realisasi anggaran, bukan hanya salinan RAB |

## 2. Fokus Penelitian yang Disarankan

### Judul laporan yang lebih aman

**SENS-Able: Evaluasi Awal Fitur Sinyal PPG dan Suhu pada Prototipe Pemantauan Kesehatan untuk Estimasi Glukosa Berbasis Referensi Glucometer**

Judul ini masih mengandung identitas dan kebaruan SENS-Able, tetapi tidak mengklaim bahwa prototipe adalah alat diagnosis atau pengganti glucometer.

### Rumusan masalah yang disarankan

1. Bagaimana pipeline SENS-Able mengumpulkan fitur sinyal PPG, suhu, dan nilai referensi glucometer pada suatu sesi pengukuran?
2. Bagaimana performa model regresi dalam mengestimasi `GlukosaRef` berdasarkan fitur yang dikumpulkan prototipe?
3. Apa keterbatasan prototipe dan pipeline data yang perlu diperbaiki sebelum implementasi TinyML dan pengujian aksesibilitas?

### Tujuan yang dapat dibuktikan

Tujuan penelitian adalah membangun dan mendokumentasikan collector ESP32, membersihkan data secara reproducible, menggunakan `GlukosaRef` glucometer sebagai target, membandingkan model regresi dengan baseline, dan menganalisis keterbatasan prototipe. Tujuan diagnosis, penggantian glucometer, dan validasi klinis harus dikeluarkan.

## 3. Model yang Sesuai dengan Proposal dan Data

Model utama adalah regresi, bukan klasifikasi diabetes. `GlukosaRef` digunakan sebagai `y`, sedangkan fitur sensor dan kondisi pengukuran digunakan sebagai `X`. `SubjectID` dipakai untuk grouping, bukan input model. Flag `SuhuTubuh_Imputed` dan `SuhuAmbient_Imputed` dipakai untuk audit, bukan input model.

Pada dataset revisi terdapat 40 sesi dan 32 SubjectID. Enam sesi dikeluarkan karena sinyal optiknya terlalu rendah. Tujuh nilai suhu tubuh dan enam nilai suhu ambient yang nol dipulihkan menggunakan rata-rata observasi positif, dengan flag provenance. Nilai `GlukosaRef` tidak diubah.

| Model | MAE (mg/dL) | RMSE (mg/dL) | R² | Interpretasi |
|---|---:|---:|---:|---|
| MeanBaseline | 24,2937 | 29,0975 | -0,0856 | Pembanding minimum |
| LinearRegression | 57,8532 | 71,9372 | -5,6353 | Lebih buruk pada data kecil ini |
| RandomForestRegressor | 22,5716 | 27,0552 | 0,0614 | Terbaik pada eksperimen ini, tetapi masih eksploratif |

Angka tersebut tidak memenuhi target awal MAE <15 mg/dL. Hal ini bukan alasan untuk mengubah label atau menghapus hasil; justru menjadi pembahasan keterbatasan dan dasar untuk penambahan data serta kalibrasi.

## 4. Bagian yang Dapat Dipertahankan

Latar belakang tentang kebutuhan pemantauan kesehatan dan aksesibilitas dapat dipertahankan dengan perbaikan sumber dan bahasa. Ide penggunaan ESP32, MAX30102, sensor suhu, penyimpanan lokal, dan antarmuka visual juga dapat dipertahankan jika foto dan bukti rangkaian tersedia.

Kebaruan dapat dirumuskan sebagai integrasi prototipe low-cost, pipeline pengumpulan fitur PPG dan suhu, referensi glucometer, penyimpanan lokal, serta arah aksesibilitas. Kebaruan tidak boleh dirumuskan sebagai “AI on-device yang sudah terbukti” jika model belum berjalan di ESP32.

## 5. Bagian yang Wajib Dikoreksi

### Hardware dan firmware

Proposal menulis MAX30102, sedangkan kode collector menggunakan nama library/objek `MAX30100`. Pengguna telah mengonfirmasi hardware fisik MAX30102. Laporan harus menjelaskan library yang digunakan dan memastikan library tersebut memang kompatibel dengan modul MAX30102. Jangan mengganti nama hardware berdasarkan kode saja.

### Audio dan vibrasi

Proposal menyebut PAS-0158 dan motor vibrasi, tetapi status saat ini adalah alat pengukuran dengan output yang belum diuji untuk audio/vibrasi. Jika sampai laporan ditulis belum ada bukti kerja dan pengujian, tulis keduanya sebagai rancangan pengembangan berikutnya, bukan hasil penelitian.

### TinyML

Proposal menyebut deployment TensorFlow Lite Micro. Saat ini belum ada artefak `model.tflite`, `model.h`, sketch inference, waktu inferensi, pemakaian RAM/flash, atau hasil prediksi langsung di ESP32. Klaim tersebut harus dipindahkan ke “rencana lanjutan” atau dibuktikan melalui eksperimen tersendiri.

### Metode responden

Proposal menyebut 15 responden dengan komposisi tertentu, tetapi dataset sekarang hanya dapat menyatakan 40 sesi dan 32 SubjectID pseudonim. Komposisi disabilitas, jumlah bantuan, dan jumlah pengukuran per responden harus bersumber dari logbook atau kuesioner, bukan disimpulkan dari nama file.

### Waktu pengukuran

Tidak ada kolom tanggal/waktu di dataset. Tanggal file dan tanggal commit hanya menunjukkan proses upload/pengolahan, bukan waktu pengukuran. `TerakhirMakan_jam` adalah durasi sejak makan terakhir dan dapat menjadi fitur kondisi, tetapi bukan timestamp sesi.

## 6. Struktur Laporan Hasil yang Disarankan

Laporan hasil tahap 2 sebaiknya tidak menyalin proposal secara utuh. Gunakan proposal sebagai dasar, kemudian tulis hasil aktual:

1. Pendahuluan yang mempersempit masalah menjadi evaluasi awal prototipe.
2. Landasan teori tentang PPG, glucometer sebagai reference measurement, regresi, dan keterbatasan pengukuran non-invasif.
3. Metode dengan hardware MAX30102 yang benar, collector ESP32, aturan cleaning, target/fitur, GroupKFold, dan etika.
4. Hasil dan pembahasan yang memuat 40 sesi, 32 SubjectID, enam eksklusi optical signal, 13 nilai suhu yang diimputasi, perbandingan model, grafik, dan keterbatasan.
5. Anggaran serta kegiatan aktual.
6. Kesimpulan yang menyatakan status sebagai studi pendahuluan, bukan validasi klinis.
7. Lampiran berisi logbook, foto alat, tabel processed anonymized, exclusion log, kode inti, dan dokumen izin.

## 7. Prioritas Kerja Setelah Recheck

| Prioritas | Tindakan | Kriteria selesai |
|---|---|---|
| 1 | Bekukan scope | Judul dan tujuan memakai istilah evaluasi awal; tidak ada klaim diagnosis |
| 2 | Cocokkan hardware | MAX30102 pada alat, laporan, foto, dan dokumentasi konsisten |
| 3 | Bekukan data | `sensable_validation.csv`, `quality_report.json`, dan `model_comparison.json` tersimpan dengan versi |
| 4 | Lengkapi bukti | Foto alat, logbook, prosedur glucometer, dan bukti sesi tersedia |
| 5 | Putuskan audio/vibrasi | Jika belum diuji, pindahkan ke pekerjaan lanjutan |
| 6 | Tulis Bab 3–4 | Semua angka dapat dihasilkan dari script dan tidak ada data sintetis |
| 7 | Review pembimbing | Periksa etika, privasi, sumber, dan ketepatan klaim |
| 8 | Revisi proposal | Dilakukan setelah hasil penelitian dan laporan terkunci |

## Kesimpulan Recheck

Proposal tahap 1 **layak dipertahankan sebagai dasar ide**, tetapi tidak boleh disalin mentah menjadi laporan hasil. Jalur paling kuat adalah mempertahankan identitas SENS-Able dan masalah aksesibilitas, sambil mengubah klaim utama menjadi evaluasi awal pipeline PPG/suhu terhadap glucometer. Dengan cara ini, keterbatasan dataset kecil, hasil model yang belum mencapai target, belum adanya TinyML embedded, dan belum terujinya audio/vibrasi dapat disampaikan sebagai temuan ilmiah, bukan disembunyikan.

**Status:** PASS WITH LIMITATIONS — proposal dapat diperbaiki setelah penelitian dan bukti aktual dikunci.

## Referensi

[1]: https://pusatprestasinasional.kemendikdasmen.go.id/uploads/lampiran_pengumuman/Panduan%20OPSI%20SMA%20Sederajat%202026.pdf "Panduan OPSI SMA Sederajat 2026"
[2]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/tree/data-cleaning-glucometer-validation "SENS-Able repository branch"
