import { describe, expect, it } from "vitest";
import { DeviceRateLimiter, firmwareReleaseMetadataSchema, hashDeviceSecret, sensorTestReadingSchema, verifyDeviceSecret } from "./gateway";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

const validPayload = {
  device_id: "SENSABLE-01",
  firmware_version: "v0.6.4",
  ir_mean: 12345,
  red_mean: 11200,
  heart_rate_bpm: 78,
  spo2_pct: 98,
  temperature_c: 36.5,
  uptime_ms: 123456,
};

describe("ESP32 gateway contract", () => {
  it("accepts a bounded, non-identifying test payload", () => {
    expect(sensorTestReadingSchema.safeParse(validPayload).success).toBe(true);
  });

  it("rejects private health and identity fields", () => {
    expect(sensorTestReadingSchema.safeParse({ ...validPayload, name: "person" }).success).toBe(false);
    expect(sensorTestReadingSchema.safeParse({ ...validPayload, SubjectID: "S-01" }).success).toBe(false);
    expect(sensorTestReadingSchema.safeParse({ ...validPayload, GlukosaRef: 105 }).success).toBe(false);
  });

  it("rejects unsafe sensor values", () => {
    expect(sensorTestReadingSchema.safeParse({ ...validPayload, spo2_pct: 101 }).success).toBe(false);
    expect(sensorTestReadingSchema.safeParse({ ...validPayload, ir_mean: -1 }).success).toBe(false);
  });

  it("verifies device secrets using a hash", () => {
    const hash = hashDeviceSecret("a-strong-device-test-token-1234567890");
    expect(verifyDeviceSecret("a-strong-device-test-token-1234567890", hash)).toBe(true);
    expect(verifyDeviceSecret("incorrect-device-test-token-123456", hash)).toBe(false);
  });

  it("enforces a per-device request ceiling", () => {
    const limiter = new DeviceRateLimiter(2, 60_000);
    expect(limiter.allow("SENSABLE-01", 1)).toBe(true);
    expect(limiter.allow("SENSABLE-01", 2)).toBe(true);
    expect(limiter.allow("SENSABLE-01", 3)).toBe(false);
    expect(limiter.allow("SENSABLE-02", 3)).toBe(true);
  });

  it("accepts only integrity-complete firmware release metadata", () => {
    const validRelease = { version: "v0.7.1", board: "ESP32", sha256: "a".repeat(64), flashOffset: 0, releaseNotes: "Verified build" };
    expect(firmwareReleaseMetadataSchema.safeParse(validRelease).success).toBe(true);
    expect(firmwareReleaseMetadataSchema.safeParse({ ...validRelease, sha256: "not-a-checksum" }).success).toBe(false);
    expect(firmwareReleaseMetadataSchema.safeParse({ ...validRelease, artifactUrl: "https://not-accepted.example" }).success).toBe(false);
  });

  it("keeps dashboard gateway procedures restricted to the owner role", async () => {
    const context = {
      user: {
        id: 2,
        openId: "standard-user",
        email: "user@example.com",
        name: "Standard user",
        loginMethod: "manus",
        role: "user",
        createdAt: new Date(),
        updatedAt: new Date(),
        lastSignedIn: new Date(),
      },
      req: {} as TrpcContext["req"],
      res: {} as TrpcContext["res"],
    } as TrpcContext;
    await expect(appRouter.createCaller(context).gateway.overview()).rejects.toMatchObject({ code: "FORBIDDEN" });
  });
});
