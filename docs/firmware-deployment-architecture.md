# SENS-Able Firmware Delivery Architecture

## Decision

The gateway will support a safe two-stage deployment workflow. First, an owner uploads a **pre-built ESP32 firmware artifact** with a version, SHA-256 checksum, target board, and release notes. Second, a user explicitly selects a serial port in a compatible Chromium browser to flash that artifact with Web Serial. The browser cannot silently access USB hardware; a physical user gesture and port-selection dialog are required.

The web application will not claim to compile Arduino code inside the managed gateway runtime. The ESP32 Arduino/MAX30102 build needs its own toolchain and board libraries. Firmware compilation therefore belongs in a reproducible external build step, such as a checked-in Arduino CLI or PlatformIO workflow. The gateway records and distributes the resulting binary after its checksum is recorded.

## Automatic connection after deployment

The production firmware must contain a provisioning and reporting client. The device stores a gateway HTTPS origin, device identifier, and per-device token in its own local configuration. It posts only bounded sensor-test fields to `/api/ingest/v1/readings`. The guest installer creates a one-time token only after the visitor starts installation and writes it directly to the selected ESP32 serial port; it does not render, retain, or list that token. The device token must never be committed in source code or included in a research report.

OTA is a second-stage capability. A device first needs a firmware build with an OTA partition layout and verified HTTPS certificate handling. ESP-IDF's HTTPS OTA mechanism uses an HTTPS endpoint and can verify the server certificate; it should not be implemented by disabling TLS validation. Firmware signing and rollback testing are also required before OTA is called production-ready. The current v0.7.1 binary supports USB flashing and serial provisioning but intentionally refuses HTTPS reporting until a release is built with the reviewed root CA for the final published domain.

## Reporting boundary

Dashboard reports will show firmware version, artifact checksum, device connection status, accepted test-reading count, and server timestamps. The system will not store names, SubjectID values, glucometer-reference values, or clinical claims. USB flash success means only that the browser finished writing the selected firmware artifact; it is not evidence that the sensor or glucose-estimation model is clinically valid.

## References

[1] https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API
[2] https://github.com/espressif/esptool-js
[3] https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/esp_https_ota.html
