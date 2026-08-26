# SENS-Able ESP32 Data Collector

Folder ini berisi kode Arduino yang digunakan untuk menangkap fitur sensor SENS-Able dan menyimpan hasilnya ke `dataset.csv` pada LittleFS.

| File | Keterangan |
|---|---|
| `SENS_ABLE_Data_Collector_v6_4_original.ino` | Salinan persis kode yang dikirimkan pemilik proyek; tidak diubah |
| `SENS_ABLE_Data_Collector_v6_4.ino` | Salinan supported dengan perbaikan validasi input, escaping output, batas sampling, laporan kegagalan penyimpanan, dan mount LittleFS non-destruktif |

## Hardware dan Pin

| Komponen | Bus/pin |
|---|---|
| OLED SSD1306 dan MLX90614 | `BusOLED`, SDA 21, SCL 22 |
| MAX30100 | `BusSensor`, SDA 18, SCL 19 |
| MLX90614 | I²C address `0x5A` |
| OLED SSD1306 | I²C address `0x3C` |

Sketch menggunakan Wi-Fi Access Point `SENS-Able`, web server port 80, dan LittleFS untuk mempertahankan dataset setelah reset normal atau listrik mati. Sebelum penggunaan lapangan, ganti password AP default dan jangan membagikan hasil CSV yang masih memiliki nama responden.

## Library Arduino

Install library yang sesuai sebelum compile:

- ESP32 Arduino core, termasuk `WiFi.h`, `WebServer.h`, dan `LittleFS.h`.
- Adafruit GFX Library.
- Adafruit SSD1306.
- MAX30100lib atau library MAX30100 yang menyediakan API `MAX30100`, `getRawValues`, dan konfigurasi sampling yang digunakan sketch.

## Kontrak Data

Saat formulir web dikirim, `glukosa` harus diisi dari **pengukuran glucometer asli** dalam mg/dL. Nilai tersebut ditulis ke kolom `GlukosaRef` sebagai target/referensi validasi. Nilai sensor MAX30100 dan MLX90614 ditulis ke kolom fitur lain. `GlukosaRef` tidak boleh diisi dari hasil prediksi SENS-Able dan tidak boleh digunakan sebagai input saat menguji model estimasi gula darah.

Header CSV yang dihasilkan sketch harus tetap sinkron dengan dataset processed:

```text
Nama,Usia,Gender,Berat_kg,Tinggi_cm,BMI,Diabetes,GlukosaRef,TerakhirMakan_jam,SuhuTubuh,SuhuAmbient,HR_est,SpO2_est,IR_Mean,IR_Min,IR_Max,IR_Std,IR_RMS,RED_Mean,RED_Min,RED_Max,RED_Std,RED_RMS,Ratio_AC,Ratio_DC,Samples
```

## Perbaikan pada Supported Copy

Supported copy tidak mengubah formula fitur utama. Perubahannya berfokus pada kualitas data dan keselamatan operasional. Nama responden dibatasi dan dibersihkan sebelum ditulis ke CSV; tampilan HTML melakukan escaping; nilai formulir diperiksa; sampel kurang dari batas minimum atau sinyal/suhu tidak valid tidak disimpan; pesan sukses hanya dikirim setelah LittleFS berhasil menulis; dan LittleFS tidak lagi diformat otomatis ketika proses mount gagal.

Kestabilan fisik sensor, ketepatan nilai `GlukosaRef`, dan akurasi estimasi gula darah tetap harus diuji dengan prosedur kalibrasi terhadap glucometer. Sketch ini adalah data collector penelitian, bukan alat diagnosis.
