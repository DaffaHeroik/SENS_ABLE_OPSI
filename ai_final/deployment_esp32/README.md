# ESP32 Deployment — SENS-Able AI V0.1

Folder ini menyiapkan kontrak input untuk alat fisik SENS-Able. **Inference glukosa belum aktif di ESP32.** Model Python `joblib` tidak dapat langsung dijalankan oleh Arduino.

## Yang sudah tersedia

- `model_contract_v0_1.h` berisi jumlah dan urutan 22 fitur input.
- Kontrak tidak memasukkan `GlukosaRef`, `SubjectID`, `Nama`, `Diabetes`, atau flag imputasi.
- Kontrak mengikuti data yang dihasilkan collector MAX30102 dan sensor suhu.

## Syarat sebelum deployment

1. Pilih format embedded yang kompatibel dengan ESP32. Model scikit-learn joblib tidak dapat disalin langsung ke sketch Arduino.
2. Konversi model atau implementasikan estimator embedded yang ekuivalen.
3. Implementasikan preprocessing yang sama persis dengan pipeline Python.
4. Uji input feature order menggunakan data contoh yang sudah diketahui.
5. Ukur ukuran flash, penggunaan RAM, dan waktu inferensi.
6. Uji pada sesi baru yang tidak dipakai untuk fitting artifact.
7. Bandingkan prediksi embedded dengan prediksi Python.
8. Dokumentasikan hasil dan kegagalan sebelum menyebut TinyML telah berhasil.

## Urutan input

```text
Usia, Berat_kg, Tinggi_cm, BMI, TerakhirMakan_jam,
SuhuTubuh, SuhuAmbient, HR_est, SpO2_est,
IR_Mean, IR_Min, IR_Max, IR_Std, IR_RMS,
RED_Mean, RED_Min, RED_Max, RED_Std, RED_RMS,
Ratio_AC, Ratio_DC, Samples
```

## Status laporan OPSI

Untuk laporan saat ini, tuliskan bahwa model V0.1 telah dibuat dan diuji secara offline dengan Python. TinyML ESP32 adalah pengembangan lanjutan sampai semua syarat deployment di atas selesai. Jangan menampilkan fungsi prediksi palsu hanya untuk membuat demo terlihat selesai.
