# SENS-Able Project Memory

**Project:** SENS-Able — Smart Health Monitor Inklusif berbasis AI dengan Audio, Visual, dan Vibrasi
**Team:** AntroOptic Team — Muhammad Daffa Ramadhan dan Aira Cantika Putri
**School:** MAN 2 Kota Bima
**Repository:** `DaffaHeroik/SENS_ABLE_OPSI`
**Active branch:** `data-cleaning-glucometer-validation`
**Repository visibility:** Private
**Last updated:** 26 August 2026

> File ini adalah catatan kesinambungan proyek. Tambahkan entri baru secara kronologis; jangan menghapus keputusan atau hasil lama. Bedakan dengan jelas antara data asli, data processed, hasil terverifikasi, dan rencana.

## 1. Keputusan Inti Proyek

Fokus penelitian yang paling aman untuk OPSI adalah **evaluasi awal prototipe pengumpul data PPG dan suhu untuk estimasi glukosa menggunakan nilai `GlukosaRef` dari glucometer sebagai referensi**. SENS-Able belum boleh disebut sebagai alat diagnosis diabetes, pengganti glucometer, atau perangkat dengan akurasi klinis.

`GlukosaRef` adalah target/referensi dalam satuan mg/dL. Kolom ini tidak boleh digunakan sebagai fitur input pada model estimasi glukosa. Nilainya tidak boleh diimputasi atau diubah hanya agar hasil model terlihat lebih baik.

Data mentah yang berisi identitas dan data kesehatan hanya boleh disimpan di repository private. Laporan, grafik, poster, dan presentasi harus menggunakan `SubjectID` atau agregasi tanpa identitas pribadi.

## 2. Riwayat Progres

### 2.1 Audit Awal Repository

Repository diaudit secara read-only. Ditemukan bahwa klaim klasifikasi diabetes sebelumnya terlalu kuat karena data hanya memiliki satu label positif dan model menghasilkan `TP = 0` serta `F1 = 0,0`. Akurasi 90,9% tidak boleh digunakan sebagai bukti akurasi deteksi diabetes.

Ditemukan pula bahwa pipeline awal belum memiliki validasi yang cukup, dependency belum dipin, dan belum ada bukti deployment TinyML ke ESP32.

### 2.2 Ingestion Dataset Asli

Sebanyak 25 file/sheet dataset digabungkan. Salinan asli disimpan apa adanya di `data/raw/` dan diberi manifest SHA-256. Tidak ada file raw yang diubah.

| Tahap | Jumlah |
|---|---:|
| Baris input gabungan | 237 |
| Baris unik setelah normalisasi/deduplikasi | 46 sesi |
| Dataset processed versi pertama | 33 sesi |
| Dataset processed versi revisi | **40 sesi** |
| SubjectID pseudonim versi revisi | **32** |

### 2.3 Aturan Cleaning Versi Revisi

Aturan awal yang membuang semua suhu nol direvisi agar data yang masih berguna tidak hilang. Sesi dengan `SuhuTubuh = 0` atau `SuhuAmbient = 0` tetap dipertahankan jika fitur optiknya valid dan tidak ada kegagalan sensor penting lainnya.

Nilai suhu nol yang dipulihkan memakai rata-rata observasi positif setelah deduplikasi, dihitung terpisah untuk suhu tubuh dan suhu ambient. Proses ini bukan pembuatan data glucometer atau data PPG baru. Provenance dicatat melalui kolom:

- `SuhuTubuh_Imputed`
- `SuhuAmbient_Imputed`

Hasil cleaning versi revisi:

| Item | Hasil |
|---|---:|
| Sesi diproses | 40 |
| SubjectID unik | 32 |
| Sesi dikeluarkan | 6 |
| Alasan eksklusi | Semua `low_optical_signal_capture` |
| Suhu tubuh diimputasi | 7 |
| Suhu ambient diimputasi | 6 |
| Rata-rata suhu tubuh yang dipakai | 32,626364 °C |
| Rata-rata suhu ambient yang dipakai | 31,631471 °C |
| `GlukosaRef` diubah | Tidak |

Kegagalan optik tidak diimputasi. Enam sesi dengan `IR_Mean` atau `RED_Mean` terlalu rendah tetap dikeluarkan karena kemungkinan sensor tidak menempel atau capture tidak valid.

### 2.4 Validasi Glucometer

Validasi dilakukan oleh `scripts/validate_glucometer.py` dengan `GroupKFold` berdasarkan `SubjectID`. Fitur input tidak mencakup `GlukosaRef`, `SubjectID`, `Diabetes`, maupun flag provenance imputasi.

Hasil versi dataset revisi:

| Metrik | Nilai |
|---|---:|
| MAE | 22,4158 mg/dL |
| RMSE | 27,0395 mg/dL |
| R² | 0,0625 |
| Status | Eksploratif; belum menjadi validasi klinis |

Hasil versi sebelumnya dengan 33 sesi adalah MAE 23,7345 mg/dL, RMSE 28,4437 mg/dL, dan R² -0,0102. Perbandingan ini dicatat untuk transparansi, bukan untuk memilih angka terbaik secara selektif.

## 3. Firmware ESP32

Kode Arduino/ESP32 yang diberikan pengguna disimpan dalam dua salinan:

- `firmware/SENS_ABLE_Data_Collector/SENS_ABLE_Data_Collector_v6_4_original.ino` — salinan byte-identik dari kode yang dikirim.
- `firmware/SENS_ABLE_Data_Collector/SENS_ABLE_Data_Collector_v6_4.ino` — versi supported dengan perbaikan minimal.
- `firmware/SENS_ABLE_Data_Collector/README.md` — pin, library, format CSV, dan aturan pengambilan data.

Perbaikan pada versi supported mencakup validasi input, pembersihan nama untuk CSV, HTML escaping, batas minimum sampling, penolakan capture sensor rusak, pesan kegagalan penyimpanan yang benar, dan `LittleFS.begin(false)` agar kegagalan mount tidak otomatis memformat memori.

`arduino-cli` tidak tersedia di sandbox, sehingga compile penuh firmware belum terverifikasi. Compile final perlu dilakukan di Arduino IDE/PlatformIO dengan library dan board ESP32 yang sesuai. Password AP default `sensable123` harus diganti sebelum penggunaan lapangan.

## 4. OPSI 2026

Proposal Stage 1 yang diunggah pengguna identik dengan `docs/proposal.pdf` di repository berdasarkan SHA-256.

Panduan resmi OPSI SMA 2026 menetapkan batas unggah laporan hasil penelitian pada **31 Agustus 2026**. Laporan maksimal 20 halaman di luar lampiran, disertai logbook dan klirens etik bila diperlukan, dengan ukuran PDF maksimal 8 MB.

Fokus penilaian laporan mencakup metodologi, hasil dan pembahasan, kesimpulan, pustaka, kebaruan, dan kemanfaatan. Untuk final, bobot terbesar berada pada presentasi/wawancara. Penelitian dengan responden manusia harus memperhatikan etika, privasi, keselamatan, izin, dan dokumentasi yang sesuai.

Planning detail tersedia di `docs/opsi_stage2_recheck_plan.md`. Strategi kerja yang disepakati adalah **menyelesaikan bukti penelitian terlebih dahulu**, kemudian memperbaiki proposal berdasarkan data dan hasil yang benar-benar tersedia.

## 5. Bukti Penelitian yang Masih Dibutuhkan

Prioritas berikutnya bukan menambah klaim AI, tetapi memperkuat bukti:

1. Logbook bertanggal untuk setiap sesi pengukuran.
2. Pasangan jelas antara satu capture ESP32 dan satu nilai glucometer `GlukosaRef`.
3. Foto rangkaian, sensor pada jari, tampilan collector, dan kondisi pengukuran.
4. Verifikasi modul fisik: proposal menyebut MAX30102, sedangkan firmware menggunakan MAX30100; laporan harus mengikuti hardware yang benar-benar digunakan.
5. Bukti audio dan vibrasi jika keduanya tetap diklaim sebagai fitur yang sudah diuji.
6. Bukti usability/accessibility jika klaim ramah tunanetra atau tunarungu tetap digunakan.
7. Dokumen izin, persetujuan, atau klirens etik sesuai arahan pembimbing dan panitia OPSI.
8. Hasil analisis final yang dapat direproduksi dari script dan dataset processed.

## 6. Quality Gates Terakhir

Pada pemeriksaan terakhir, semua enam regression tests lulus. Syntax check Python lulus. `GlukosaRef` tidak masuk ke fitur validasi. Flag imputasi tidak masuk ke fitur model. Dataset processed tidak memiliki nama asli dan tidak memiliki nilai kosong setelah cleaning. File raw tetap dipertahankan.

Perubahan revisi dataset dan dokumentasi berikut **sudah disiapkan secara lokal tetapi belum dipush**:

- `README.md`
- `data/README.md`
- `data/processed/excluded_records.csv`
- `data/processed/quality_report.json`
- `data/processed/sensable_validation.csv`
- `docs/chat_history.md`
- `docs/planning.md`
- `docs/opsi_stage2_recheck_plan.md`
- `reports/glucometer_validation.json`
- `scripts/prepare_dataset.py`
- `scripts/validate_glucometer.py`
- `tests/test_dataset_pipeline.py`

Commit firmware sebelumnya yang sudah dipush adalah `4e7b27d` (`feat: add ESP32 data collector firmware`). Revisi dataset terakhir masih menunggu konfirmasi eksplisit sebelum commit dan push.

## 7. Aturan Pemeliharaan Memory

Setiap progres baru harus menambahkan entri dengan tanggal, file yang berubah, alasan perubahan, hasil quality gate, dan status publikasi. Jangan menghapus data raw. Jangan mengubah `GlukosaRef` tanpa bukti koreksi dari catatan glucometer. Jangan menggunakan nama asli pada laporan atau visualisasi. Jangan menyebut hasil sebagai akurasi klinis sebelum jumlah data, desain validasi, dan bukti kalibrasi benar-benar memadai.

## References

[1]: https://pusatprestasinasional.kemendikdasmen.go.id/uploads/lampiran_pengumuman/Panduan%20OPSI%20SMA%20Sederajat%202026.pdf "Panduan OPSI SMA Sederajat 2026, Pusat Prestasi Nasional"
[2]: https://chatgpt.com/share/6a8e73de-e2d8-83ec-862e-2a66175ed9cc "Shared discussion: Alat SENS-Able"
[3]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/tree/data-cleaning-glucometer-validation "SENS-Able repository branch"

## 8. Date and Pairing Audit (26 Agustus 2026)

A row-level audit was run across all 25 raw CSV/XLSX sources. Every source has a `GlukosaRef` column and all 237 raw rows have a non-null `GlukosaRef`, but none of the uploaded files contains an explicit date/time/timestamp column. Therefore, the dataset proves that a glucose reference value is present for each row, but it does not independently prove that the glucometer reading and ESP32 capture occurred in the same measurement session. The report must not claim date-paired validation unless the researcher supplies the original logbook or another contemporaneous record. If the dates are written in a separate logbook, that logbook should be preserved and linked to the row/SubjectID without exposing identity in public report artifacts.

## 9. File Timestamp Audit (26 Agustus 2026)

A pemeriksaan terhadap nama file, kolom dataset, metadata file, dan Git history tidak menemukan tanggal pengukuran yang dapat dipercaya di dalam dataset. Semua file sumber memiliki `GlukosaRef` dan tidak memiliki kolom `Tanggal`, `Date`, `Waktu`, `Time`, atau `Timestamp`. Waktu modifikasi file yang terlihat adalah waktu file diunggah/disalin ke workspace pada 26 Agustus 2026, bukan waktu pengambilan data oleh ESP32. Tanggal pada `docs/chat_history.md` dan commit Git hanya menunjukkan waktu dokumentasi/pemrosesan, bukan waktu pengukuran.

Kesimpulan metodologis: tanggal kalender tidak diperlukan sebagai fitur model dan `TerakhirMakan_jam` tetap dapat dipakai sebagai fitur kondisi sebelum pengukuran. Namun, tanggal/waktu sesi hanya boleh disebut dalam laporan jika peneliti memiliki logbook atau catatan pengukuran terpisah. Tanpa logbook tersebut, laporan harus menyebut dataset sebagai data retrospektif dengan nilai referensi glucometer yang dicatat oleh pemilik data, bukan mengklaim bahwa pairing waktu sensor–glucometer dapat diverifikasi dari CSV.

## 10. Model-Building Workflow (26 Agustus 2026)

Model utama untuk penelitian adalah regresi terhadap `GlukosaRef` dari glucometer. Fitur input berasal dari demografi, `TerakhirMakan_jam`, suhu, detak/SpO2, serta fitur IR/RED/ratio dari MAX30102. `GlukosaRef`, `SubjectID`, `Diabetes`, dan flag imputasi suhu tidak digunakan sebagai fitur.

Ditambahkan `scripts/compare_glucose_models.py` untuk membandingkan baseline rata-rata yang dihitung per fold, Linear Regression, dan Random Forest dengan `GroupKFold` berdasarkan `SubjectID`. Hasil pada 40 sesi dan 32 SubjectID:

| Model | MAE (mg/dL) | RMSE (mg/dL) | R² |
|---|---:|---:|---:|
| MeanBaseline | 24,2937 | 29,0975 | -0,0856 |
| LinearRegression | 57,8532 | 71,9372 | -5,6353 |
| RandomForestRegressor | 22,5716 | 27,0552 | 0,0614 |

Random Forest sedikit mengungguli baseline pada eksperimen ini, tetapi hasil masih eksploratif dan belum menjadi bukti akurasi klinis. Panduan penggunaan model tersedia di `docs/model_building_guide.md`.

## 11. Proposal Stage 1 Recheck — OPSI2025.docx (26 Agustus 2026)

The uploaded `OPSI2025.docx` is a Stage 1 proposal for SENS-Able and remains a valid foundation for the project idea. It describes ESP32, MAX30102, MLX90614, OLED, audio, vibration, TinyML, 15 respondents, usability testing, and targets including MAE glucose <15 mg/dL.

The proposal should not be copied directly into the Stage 2 result report. Current evidence supports the ESP32 data collector, MAX30102 hardware according to the user's confirmation, processed sensor data, and exploratory glucometer-reference regression. Current evidence does not yet support completed TinyML inference on ESP32, tested audio/vibration, or completed usability/accessibility claims.

The recommended report focus is: **early evaluation of PPG and temperature features from the SENS-Able prototype for glucose estimation against a glucometer reference**. The proposal's accessibility motivation and system identity can be retained, while diagnosis claims, clinical accuracy claims, unverified TinyML deployment, and untested audio/vibration outcomes must be removed or moved to future work.

The recheck report is stored at `docs/proposal_recheck_OPSI2025.md`. Proposal revision is intentionally postponed until the research results and supporting evidence are locked.

## 12. Complete Machine-Learning Modeling Plan (26 Agustus 2026)

Tahap pemodelan akan memakai regresi dengan `GlukosaRef` dari glucometer sebagai target `y`. Fitur `X` berasal dari demografi, `TerakhirMakan_jam`, suhu, HR/SpO2, serta fitur IR/RED/ratio. `GlukosaRef`, SubjectID, Diabetes, dan flag imputasi suhu tidak boleh masuk sebagai fitur.

Pipeline modeling yang disepakati: prepare dataset → MeanBaseline per fold → Linear Regression → Random Forest Regressor → GroupKFold berdasarkan SubjectID → MAE/RMSE/median absolute error/R² → analisis fold dan residual → pembekuan model. Model kandidat saat ini adalah Random Forest karena sedikit mengungguli baseline pada 40 sesi, tetapi statusnya masih eksperimen dan belum siap deployment ke ESP32/TinyML.

Panduan lengkap tersimpan di `docs/ml_modeling_plan_summary.md`. Script perbandingan model tersimpan di `scripts/compare_glucose_models.py`, dengan output di `reports/model_comparison.json`.

## 13. Model V0.1 Built and Organized (26 Agustus 2026)

Tahap modeling V0.1 sudah dibangun secara configuration-driven. Kontrak fitur dan parameter tersimpan di `configs/glucose_model_v0_1.json`. Pipeline utama ada di `scripts/compare_glucose_models.py`, visualisasi ada di `scripts/plot_model_results.py`, artifact model tersimpan di `models/glucose_model_v0_1.joblib`, dan metadata artifact di `models/glucose_model_v0_1_metadata.json`.

Model yang dipilih untuk artifact eksploratif adalah `RandomForestRegressor` karena memiliki MAE terendah pada perbandingan GroupKFold yang sama. Hasilnya: MeanBaseline MAE 24.2937 mg/dL, LinearRegression MAE 57.8532 mg/dL, dan RandomForestRegressor MAE 22.5716 mg/dL. R² Random Forest 0.0614. Artifact dilatih pada seluruh 40 sesi processed untuk inspeksi/offline use, bukan untuk klaim klinis dan bukan untuk eksekusi langsung di Arduino.

Enam figure dibuat di `reports/figures/`: actual-vs-predicted dan residual untuk baseline, Linear Regression, dan Random Forest. Visual QA menunjukkan label dan unit terbaca, garis prediksi ideal terlihat, dan penyebaran error ditampilkan tanpa menyembunyikan outlier.

Quality gate terakhir: syntax check PASS, seluruh **9 regression tests PASS**, target leakage check PASS, `GlukosaRef` tidak menjadi fitur, flag imputasi tidak menjadi fitur, artifact dan metadata cocok, serta `git diff --check` PASS. Perubahan modeling masih lokal dan belum dipush.

## 14. OPSI Stage 2 Package Preparation (26 Agustus 2026)

Dataset diperlakukan sebagai final pada tahap ini: 40 sesi processed dan 32 SubjectID; tidak ada target penambahan data. Model V0.1 dan artifact Random Forest sudah tersedia untuk menjadi sumber angka laporan.

Disiapkan dokumen pendukung:

- `docs/proposal_recheck_OPSI2025.md` — perbandingan proposal Stage 1 dengan bukti aktual.
- `docs/proposal_revision_draft.md` — draf perubahan judul, rumusan masalah, tujuan, metode, batasan, dan indikator.
- `reports/opsi_stage2_report_framework.md` — kerangka laporan Stage 2 dengan tabel hasil, struktur bab, lampiran, dan checklist.
- `reports/modeling_v0_1_summary.md` — ringkasan faktual hasil model.
- `reports/MANIFEST_v0_1.sha256` — hash dataset/config/model/laporan.

Arah laporan yang dikunci: evaluasi awal fitur PPG dan suhu untuk estimasi glukosa berbasis referensi glucometer. Audio, vibrasi, TinyML embedded, diagnosis, dan validasi klinis tidak boleh diklaim selesai tanpa bukti tersendiri. Perubahan dokumen dan pipeline ini masih lokal dan belum dipush.

## 15. Remote Publication and Fresh-Clone Verification (26 Agustus 2026)

Commit `00cd3a0` berhasil dipush ke branch private `data-cleaning-glucometer-validation`. Fresh clone dari remote menunjukkan commit dan branch yang sama. Pipeline berhasil dijalankan ulang dari fresh clone: syntax check PASS, seluruh 9 regression tests PASS, artifact model tersedia, 6 figure tersedia, dan metrik sama dengan hasil lokal. Repository terkonfirmasi berstatus PRIVATE.

Pemeriksaan klaim laporan juga PASS: dokumen memakai bahasa eksploratif dan secara eksplisit melarang klaim diagnosis, pengganti glucometer, akurasi klinis, TinyML selesai, atau audio/vibrasi teruji tanpa bukti. Identitas tim hanya muncul pada dokumen kerja yang memang memerlukan informasi penulis; report artifacts dan hasil model tidak memuat identitas responden.

## 16. Canonical Validator Alignment and Full Pipeline Run (26 Agustus 2026)

A metric mismatch between `validate_glucometer.py` and `compare_glucose_models.py` was found and corrected. The dedicated validator now reads `configs/glucose_model_v0_1.json` and uses the same explicit feature list and Random Forest parameters (`n_estimators=200`, `max_depth=6`, `min_samples_leaf=2`, `random_state=42`) as the canonical comparison pipeline. The canonical V0.1 result is therefore MAE 22.5716 mg/dL, RMSE 27.0552 mg/dL, median absolute error 20.5580 mg/dL, and R² 0.0614. The earlier 22.4158 result remains only as historical output and is not the current canonical result.

The full published branch was cloned into a clean workspace and run end-to-end: preparation produced 40 processed sessions, 32 SubjectID, 6 exclusions, 7 body-temperature imputations, 6 ambient-temperature imputations, and 40 non-null `GlukosaRef` values; validation, model comparison, artifact generation, and six figures completed; syntax checks and all 9 regression tests passed; the clean worktree and target-leakage checks passed. The latest remote branch is `e413ff2`.

## 17. Dedicated AI Folder for the Physical SENS-Able Device (26 Agustus 2026)

Dibuat folder `ai_final/` sebagai pusat coding AI untuk alat fisik SENS-Able. Struktur ini memisahkan kontrak model, training, improvement, evaluation, artifact, dan deployment ESP32:

- `ai_final/config/` — `model_contract_v0_1.json`, salinan kontrak fitur yang hash-nya sama dengan konfigurasi canonical.
- `ai_final/training/` — `train_final_model.py` untuk melatih artifact offline.
- `ai_final/improvement/` — runner nested tuning dan feature ablation.
- `ai_final/evaluation/` — evaluator V0.1, prediksi out-of-fold, dan runner grafik.
- `ai_final/artifacts/` — artifact serta manifest V0.1.
- `ai_final/deployment_esp32/` — header urutan 22 fitur dan scaffold inference yang sengaja belum mengaktifkan prediksi palsu.

Eksperimen improvement nested GroupKFold menghasilkan kandidat terbaik `TunedRandomForestWithFeatureSelection` dengan MAE 21.4932 mg/dL, RMSE 26.3387 mg/dL, dan R² 0.1105. Namun nilai `k` fitur terpilih berubah antar-fold (8, 12, 5, 12, 5), sehingga kandidat belum stabil dan tidak dipromosikan menggantikan model fisik V0.1. Feature ablation juga menunjukkan `context_only` memiliki MAE 18.7840 mg/dL, tetapi kelompok ini tidak memakai PPG sehingga tidak boleh dianggap bukti sensor lebih akurat; hasilnya disimpan sebagai analisis confounding.

Quality gate setelah folder AI ditambahkan: syntax check PASS, **13 regression tests PASS**, target leakage check PASS, artifact/evaluation contract PASS, improvement runners PASS, dan `git diff --check` PASS. Perubahan AI folder dan eksperimen improvement belum dipush.
