import express, { type Express, type Request, type Response } from "express";
import { firmwareReleaseMetadataSchema, verifyDeviceSecret } from "./gateway";
import { findActiveGatewayDevice, getLatestFirmwareRelease, registerFirmwareArtifact } from "./gatewayStore";
import { sdk } from "./_core/sdk";

function reject(response: Response, status: number, code: string) {
  return response.status(status).json({ accepted: false, code });
}

async function requireOwner(request: Request, response: Response) {
  try {
    const user = await sdk.authenticateRequest(request);
    if (user?.role === "admin") return user;
  } catch {
    // Return the same compact response for missing and invalid sessions.
  }
  reject(response, 403, "owner_access_required");
  return undefined;
}

async function requireDeviceToken(request: Request, response: Response) {
  const deviceId = typeof request.query.device_id === "string" ? request.query.device_id : "";
  const token = request.header("x-device-token");
  if (!deviceId || !token || token.length < 32 || token.length > 128) {
    reject(response, 401, "unauthorized_device");
    return undefined;
  }
  try {
    const device = await findActiveGatewayDevice(deviceId);
    if (!device || !verifyDeviceSecret(token, device.tokenHash)) {
      reject(response, 401, "unauthorized_device");
      return undefined;
    }
    return device;
  } catch {
    reject(response, 503, "gateway_unavailable");
    return undefined;
  }
}

export function registerFirmwareRoutes(app: Express) {
  app.post("/api/admin/firmware/upload", express.raw({ type: "application/octet-stream", limit: "4mb" }), async (request, response) => {
    if (!(await requireOwner(request, response))) return;

    const parsed = firmwareReleaseMetadataSchema.safeParse({
      version: request.header("x-firmware-version"),
      board: request.header("x-firmware-board"),
      sha256: request.header("x-firmware-sha256"),
      flashOffset: Number(request.header("x-firmware-flash-offset") ?? "0"),
      releaseNotes: request.header("x-firmware-notes") || undefined,
    });
    if (!parsed.success || !Buffer.isBuffer(request.body)) {
      return reject(response, 422, "invalid_firmware_release");
    }

    try {
      const release = await registerFirmwareArtifact(parsed.data, request.body);
      return response.status(201).json({
        accepted: true,
        release: { id: release?.id, version: release?.version, board: release?.board, sha256: release?.sha256 },
      });
    } catch (error) {
      const code = error instanceof Error ? error.message : "firmware_upload_failed";
      const status = code === "firmware_version_exists" ? 409 : code === "firmware_size_invalid" || code === "firmware_checksum_invalid" ? 422 : 503;
      console.error("Firmware upload failed", code);
      return reject(response, status, code);
    }
  });

  app.get("/api/firmware/v1/latest", async (request, response) => {
    if (!(await requireDeviceToken(request, response))) return;
    try {
      const release = await getLatestFirmwareRelease();
      if (!release) return response.status(404).json({ available: false, code: "no_ready_firmware" });
      const origin = `${request.protocol}://${request.get("host")}`;
      return response.status(200).json({
        available: true,
        version: release.version,
        board: release.board,
        sha256: release.sha256,
        size_bytes: release.sizeBytes,
        flash_offset: release.flashOffset,
        artifact_url: `${origin}${release.artifactUrl}`,
        ota_status: "prepared_not_enabled",
      });
    } catch (error) {
      console.error("Firmware manifest request failed", error instanceof Error ? error.message : "unknown_error");
      return reject(response, 503, "gateway_unavailable");
    }
  });
}
