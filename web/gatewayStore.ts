import { count, desc, eq } from "drizzle-orm";
import { firmwareDeploymentEvents, firmwareReleases, gatewayDevices, sensorTestReadings } from "../drizzle/schema";
import { FirmwareReleaseMetadata, SensorTestReading, createDeviceSecret, hashDeviceSecret, hashFirmwareBinary } from "./gateway";
import { getDb } from "./db";
import { storagePut } from "./storage";

function requireDatabase<T>(database: T | null): T {
  if (!database) throw new Error("database_unavailable");
  return database;
}

export async function registerGatewayDevice(deviceId: string) {
  const db = requireDatabase(await getDb());
  const existing = await db.select({ deviceId: gatewayDevices.deviceId }).from(gatewayDevices).where(eq(gatewayDevices.deviceId, deviceId)).limit(1);
  if (existing.length > 0) throw new Error("device_exists");

  const deviceSecret = createDeviceSecret();
  await db.insert(gatewayDevices).values({ deviceId, tokenHash: hashDeviceSecret(deviceSecret), active: "active" });
  return { deviceId, deviceSecret };
}

export async function findActiveGatewayDevice(deviceId: string) {
  const db = requireDatabase(await getDb());
  const devices = await db.select({ deviceId: gatewayDevices.deviceId, tokenHash: gatewayDevices.tokenHash, active: gatewayDevices.active }).from(gatewayDevices).where(eq(gatewayDevices.deviceId, deviceId)).limit(1);
  const device = devices[0];
  return device?.active === "active" ? device : undefined;
}

export async function saveAcceptedReading(reading: SensorTestReading) {
  const db = requireDatabase(await getDb());
  await db.insert(sensorTestReadings).values({
    deviceId: reading.device_id,
    firmwareVersion: reading.firmware_version ?? null,
    irMean: reading.ir_mean,
    redMean: reading.red_mean,
    heartRateBpm: reading.heart_rate_bpm ?? null,
    spo2Pct: reading.spo2_pct ?? null,
    temperatureC: reading.temperature_c ?? null,
    uptimeMs: reading.uptime_ms ?? null,
  });
  await db.update(gatewayDevices).set({ lastSeenAt: new Date() }).where(eq(gatewayDevices.deviceId, reading.device_id));
}

export async function registerFirmwareArtifact(metadata: FirmwareReleaseMetadata, binary: Uint8Array) {
  const db = requireDatabase(await getDb());
  const existing = await db.select({ id: firmwareReleases.id }).from(firmwareReleases).where(eq(firmwareReleases.version, metadata.version)).limit(1);
  if (existing.length > 0) throw new Error("firmware_version_exists");
  if (binary.byteLength < 1024 || binary.byteLength > 4 * 1024 * 1024) throw new Error("firmware_size_invalid");
  if (hashFirmwareBinary(binary).toLowerCase() !== metadata.sha256.toLowerCase()) throw new Error("firmware_checksum_invalid");

  const safeVersion = metadata.version.replace(/[^A-Za-z0-9._-]/g, "_");
  const uploaded = await storagePut(`firmware/${metadata.board}/${safeVersion}/merged-flash.bin`, binary, "application/octet-stream");
  await db.insert(firmwareReleases).values({
    version: metadata.version,
    board: metadata.board,
    artifactKey: uploaded.key,
    artifactUrl: uploaded.url,
    sha256: metadata.sha256.toLowerCase(),
    sizeBytes: binary.byteLength,
    flashOffset: metadata.flashOffset,
    releaseNotes: metadata.releaseNotes ?? null,
    status: "ready",
  });
  const release = await db.select().from(firmwareReleases).where(eq(firmwareReleases.version, metadata.version)).limit(1);
  return release[0];
}

export async function getLatestFirmwareRelease() {
  const db = requireDatabase(await getDb());
  const releases = await db.select().from(firmwareReleases).where(eq(firmwareReleases.status, "ready")).orderBy(desc(firmwareReleases.createdAt)).limit(1);
  return releases[0];
}

export async function getFirmwareReleaseById(releaseId: number) {
  const db = requireDatabase(await getDb());
  const releases = await db.select().from(firmwareReleases).where(eq(firmwareReleases.id, releaseId)).limit(1);
  return releases[0];
}

export async function recordFirmwareDeploymentEvent(input: { deviceId: string; firmwareReleaseId: number; method: "web_serial" | "ota"; status: "started" | "completed" | "failed"; detail?: string }) {
  const db = requireDatabase(await getDb());
  await db.insert(firmwareDeploymentEvents).values({
    deviceId: input.deviceId,
    firmwareReleaseId: input.firmwareReleaseId,
    method: input.method,
    status: input.status,
    detail: input.detail ?? null,
  });
}

export async function getGatewayOverview() {
  const db = requireDatabase(await getDb());
  const [devices, readings, readingCountRows, releases, deploymentEvents] = await Promise.all([
    db.select({ deviceId: gatewayDevices.deviceId, active: gatewayDevices.active, createdAt: gatewayDevices.createdAt, lastSeenAt: gatewayDevices.lastSeenAt }).from(gatewayDevices).orderBy(desc(gatewayDevices.createdAt)),
    db.select({ id: sensorTestReadings.id, deviceId: sensorTestReadings.deviceId, firmwareVersion: sensorTestReadings.firmwareVersion, irMean: sensorTestReadings.irMean, redMean: sensorTestReadings.redMean, heartRateBpm: sensorTestReadings.heartRateBpm, spo2Pct: sensorTestReadings.spo2Pct, temperatureC: sensorTestReadings.temperatureC, uptimeMs: sensorTestReadings.uptimeMs, receivedAt: sensorTestReadings.receivedAt }).from(sensorTestReadings).orderBy(desc(sensorTestReadings.receivedAt)).limit(25),
    db.select({ value: count() }).from(sensorTestReadings),
    db.select({ id: firmwareReleases.id, version: firmwareReleases.version, board: firmwareReleases.board, artifactUrl: firmwareReleases.artifactUrl, sha256: firmwareReleases.sha256, sizeBytes: firmwareReleases.sizeBytes, flashOffset: firmwareReleases.flashOffset, releaseNotes: firmwareReleases.releaseNotes, status: firmwareReleases.status, createdAt: firmwareReleases.createdAt }).from(firmwareReleases).orderBy(desc(firmwareReleases.createdAt)).limit(10),
    db.select({ id: firmwareDeploymentEvents.id, deviceId: firmwareDeploymentEvents.deviceId, firmwareReleaseId: firmwareDeploymentEvents.firmwareReleaseId, method: firmwareDeploymentEvents.method, status: firmwareDeploymentEvents.status, detail: firmwareDeploymentEvents.detail, recordedAt: firmwareDeploymentEvents.recordedAt }).from(firmwareDeploymentEvents).orderBy(desc(firmwareDeploymentEvents.recordedAt)).limit(20),
  ]);

  return {
    generatedAt: new Date(),
    stats: {
      activeDevices: devices.filter(device => device.active === "active").length,
      totalDevices: devices.length,
      totalAcceptedReadings: Number(readingCountRows[0]?.value ?? 0),
      firmwareReleases: releases.length,
    },
    devices,
    readings,
    firmwareReleases: releases,
    deploymentEvents,
  };
}
