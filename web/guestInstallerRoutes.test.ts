import express from "express";
import { afterAll, beforeAll, describe, expect, it, vi } from "vitest";

const { getLatestFirmwareRelease, registerGatewayDevice } = vi.hoisted(() => ({
  getLatestFirmwareRelease: vi.fn(),
  registerGatewayDevice: vi.fn(),
}));

vi.mock("./gatewayStore", () => ({ getLatestFirmwareRelease, registerGatewayDevice }));

import { registerGuestInstallerRoutes } from "./guestInstallerRoutes";

let baseUrl = "";
let closeServer: (() => Promise<void>) | undefined;

describe("guest installer routes", () => {
  beforeAll(async () => {
    const app = express();
    app.use(express.json());
    registerGuestInstallerRoutes(app);
    const server = await new Promise<ReturnType<typeof app.listen>>(resolve => {
      const listener = app.listen(0, "127.0.0.1", () => resolve(listener));
    });
    const address = server.address();
    if (!address || typeof address === "string") throw new Error("test server did not start");
    baseUrl = `http://127.0.0.1:${address.port}`;
    closeServer = () => new Promise((resolve, reject) => server.close(error => (error ? reject(error) : resolve())));
  });

  afterAll(async () => { await closeServer?.(); });

  it("publishes only reviewed firmware metadata", async () => {
    getLatestFirmwareRelease.mockResolvedValueOnce({
      id: 11, version: "v0.7.0", board: "ESP32", artifactUrl: "/manus-storage/firmware.bin", artifactKey: "private/storage/key", sha256: "a".repeat(64), sizeBytes: 921600, flashOffset: 0, releaseNotes: "Gateway client", tokenHash: "must-not-leak",
    });
    const response = await fetch(`${baseUrl}/api/public/installer/latest`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.release).toMatchObject({ id: 11, version: "v0.7.0", artifact_url: "/manus-storage/firmware.bin" });
    expect(JSON.stringify(body)).not.toContain("private/storage/key");
    expect(JSON.stringify(body)).not.toContain("must-not-leak");
    expect(JSON.stringify(body)).not.toContain("readings");
  });

  it("issues only the newly created device credential during guest enrollment", async () => {
    registerGatewayDevice.mockResolvedValueOnce({ deviceId: "SENSABLE-TEST", deviceSecret: "one-time-device-secret" });
    const response = await fetch(`${baseUrl}/api/public/installer/enroll`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ device_id: "SENSABLE-TEST" }) });
    expect(response.status).toBe(201);
    const body = await response.json();
    expect(body).toEqual({ accepted: true, device_id: "SENSABLE-TEST", device_token: "one-time-device-secret" });
    expect(JSON.stringify(body)).not.toContain("tokenHash");
    expect(JSON.stringify(body)).not.toContain("readings");
  });
});
