import { readFile } from "node:fs/promises";
import crypto from "node:crypto";
import { registerFirmwareArtifact } from "../server/gatewayStore.ts";

const artifactPath = "/home/ubuntu/SENS_ABLE_OPSI/firmware/SENS_ABLE_Gateway_Client/.pio/build/esp32dev/sensable_gateway_v0_7_1_merged.bin";
const binary = new Uint8Array(await readFile(artifactPath));
const sha256 = crypto.createHash("sha256").update(binary).digest("hex");
const release = await registerFirmwareArtifact({
  version: "v0.7.1",
  board: "ESP32",
  sha256,
  flashOffset: 0,
  releaseNotes: "Compiled SENS-Able gateway collector with local serial provisioning. Secure test reporting requires a final certificate-aware release after the public gateway domain is published.",
}, binary);

console.log(JSON.stringify({ id: release?.id, version: release?.version, sha256: release?.sha256, sizeBytes: release?.sizeBytes }));
process.exit(0);
