# OTA Readiness Boundary

The current guest installer is intentionally **USB-first**. It flashes a merged ESP32 image at offset `0x0` through a browser-authorized serial port. That merged file is not suitable for `HTTPUpdate`, which requires an application-only OTA image and an OTA partition layout.

The repository includes `partitions_ota.csv` and `gateway_ota_template.h` so the next firmware release can be prepared correctly. OTA remains disabled by `SENSABLE_ENABLE_OTA=0` until the following evidence exists:

1. The gateway is published under its final HTTPS domain.
2. A reviewed root CA is compiled into `gateway_certificate.h`.
3. A separate application-only OTA artifact has a recorded SHA-256 checksum and signature policy.
4. Update interruption, reboot, and rollback have been tested on a non-research ESP32.

Until then, use the guest USB installer. This avoids silently deploying an unverified update to the research device.
