import crypto from "node:crypto";
import { z } from "zod";

export const DEVICE_ID_PATTERN = /^[A-Z0-9][A-Z0-9_-]{2,47}$/;

export const deviceIdSchema = z
  .string()
  .trim()
  .regex(DEVICE_ID_PATTERN, "device_id must use A-Z, 0-9, _ or - and be 3-48 characters.");

/**
 * This schema intentionally accepts sensor test signals only. Health identities,
 * SubjectID values, names, and glucometer reference values are rejected because
 * the schema is strict and these properties are not present.
 */
export const sensorTestReadingSchema = z
  .object({
    device_id: deviceIdSchema,
    firmware_version: z.string().trim().min(1).max(48).optional(),
    ir_mean: z.number().finite().min(0).max(262143),
    red_mean: z.number().finite().min(0).max(262143),
    heart_rate_bpm: z.number().finite().min(20).max(240).optional(),
    spo2_pct: z.number().finite().min(50).max(100).optional(),
    temperature_c: z.number().finite().min(-20).max(100).optional(),
    uptime_ms: z.number().int().min(0).max(4_294_967_295).optional(),
  })
  .strict();

export type SensorTestReading = z.infer<typeof sensorTestReadingSchema>;

export const firmwareReleaseMetadataSchema = z
  .object({
    version: z.string().trim().regex(/^v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$/, "Use a semantic firmware version such as v0.6.5."),
    board: z.string().trim().regex(/^[A-Z0-9_ -]{3,48}$/, "board must be a concise hardware identifier."),
    sha256: z.string().trim().regex(/^[a-f0-9]{64}$/i, "sha256 must be a 64-character hexadecimal checksum."),
    flashOffset: z.number().int().min(0).max(0x100000),
    releaseNotes: z.string().trim().max(2000).optional(),
  })
  .strict();

export type FirmwareReleaseMetadata = z.infer<typeof firmwareReleaseMetadataSchema>;

export const deploymentEventSchema = z
  .object({
    deviceId: deviceIdSchema,
    firmwareReleaseId: z.number().int().positive(),
    method: z.enum(["web_serial", "ota"]),
    status: z.enum(["started", "completed", "failed"]),
    detail: z.string().trim().max(512).optional(),
  })
  .strict();

export function hashFirmwareBinary(binary: Uint8Array): string {
  return crypto.createHash("sha256").update(binary).digest("hex");
}

export function createDeviceSecret(): string {
  return crypto.randomBytes(32).toString("base64url");
}

export function hashDeviceSecret(secret: string): string {
  return crypto.createHash("sha256").update(secret, "utf8").digest("hex");
}

export function verifyDeviceSecret(secret: string, expectedHash: string): boolean {
  const receivedHash = hashDeviceSecret(secret);
  const received = Buffer.from(receivedHash, "hex");
  const expected = Buffer.from(expectedHash, "hex");
  return received.length === expected.length && crypto.timingSafeEqual(received, expected);
}

export class DeviceRateLimiter {
  private readonly windows = new Map<string, number[]>();

  constructor(
    private readonly limit = 30,
    private readonly windowMs = 60_000
  ) {}

  allow(deviceId: string, now = Date.now()): boolean {
    const active = (this.windows.get(deviceId) ?? []).filter(timestamp => now - timestamp < this.windowMs);
    if (active.length >= this.limit) {
      this.windows.set(deviceId, active);
      return false;
    }
    active.push(now);
    this.windows.set(deviceId, active);
    return true;
  }
}
