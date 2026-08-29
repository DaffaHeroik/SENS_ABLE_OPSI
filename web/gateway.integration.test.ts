import express from "express";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { eq } from "drizzle-orm";
import { gatewayDevices, sensorTestReadings } from "../drizzle/schema";
import { getDb } from "./db";
import { registerGatewayRoutes } from "./gatewayRoutes";
import { getGatewayOverview, registerGatewayDevice } from "./gatewayStore";

const runDatabaseTest = process.env.RUN_GATEWAY_DB_TEST === "1";
const deviceId = `TST-${Date.now().toString().slice(-10)}`;
let baseUrl = "";
let stopServer: (() => Promise<void>) | undefined;

describe.skipIf(!runDatabaseTest)("public ESP32 ingestion persistence", () => {
  beforeAll(async () => {
    const app = express();
    app.use(express.json({ limit: "16kb" }));
    registerGatewayRoutes(app);
    const server = await new Promise<ReturnType<typeof app.listen>>(resolve => {
      const listener = app.listen(0, "127.0.0.1", () => resolve(listener));
    });
    const address = server.address();
    if (!address || typeof address === "string") throw new Error("test server did not expose a TCP address");
    baseUrl = `http://127.0.0.1:${address.port}`;
    stopServer = () => new Promise((resolve, reject) => server.close(error => (error ? reject(error) : resolve())));
  });

  afterAll(async () => {
    const db = await getDb();
    if (db) {
      await db.delete(sensorTestReadings).where(eq(sensorTestReadings.deviceId, deviceId));
      await db.delete(gatewayDevices).where(eq(gatewayDevices.deviceId, deviceId));
    }
    await stopServer?.();
  });

  it("accepts a token-authenticated test reading and persists no prohibited data", async () => {
    const registered = await registerGatewayDevice(deviceId);
    const response = await fetch(`${baseUrl}/api/ingest/v1/readings`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-device-token": registered.deviceSecret },
      body: JSON.stringify({
        device_id: deviceId,
        firmware_version: "v0.6.4",
        ir_mean: 12345,
        red_mean: 11200,
        heart_rate_bpm: 78,
        spo2_pct: 98,
        temperature_c: 36.5,
        uptime_ms: 4567,
      }),
    });

    expect(response.status).toBe(202);
    const overview = await getGatewayOverview();
    expect(overview.readings.some(reading => reading.deviceId === deviceId && reading.irMean === 12345)).toBe(true);
  });

  it("rejects a payload containing a glucometer-reference field", async () => {
    const response = await fetch(`${baseUrl}/api/ingest/v1/readings`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-device-token": "incorrect-test-token-abcdefghijklmnopqrstuvwxyz" },
      body: JSON.stringify({ device_id: deviceId, ir_mean: 12345, red_mean: 11200, GlukosaRef: 105 }),
    });
    expect(response.status).toBe(422);
  });

  it("rejects an unknown device token", async () => {
    const response = await fetch(`${baseUrl}/api/ingest/v1/readings`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-device-token": "incorrect-test-token-abcdefghijklmnopqrstuvwxyz" },
      body: JSON.stringify({ device_id: deviceId, ir_mean: 12345, red_mean: 11200 }),
    });
    expect(response.status).toBe(401);
  });
});
