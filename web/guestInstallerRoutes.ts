import type { Express, Request, Response } from "express";
import { z } from "zod";
import { DeviceRateLimiter, deviceIdSchema } from "./gateway";
import { getLatestFirmwareRelease, registerGatewayDevice } from "./gatewayStore";

const enrollLimiter = new DeviceRateLimiter(5, 60_000);

function reject(response: Response, status: number, code: string) {
  return response.status(status).json({ accepted: false, code });
}

function requesterKey(request: Request) {
  return request.ip || request.socket.remoteAddress || "unknown";
}

export function registerGuestInstallerRoutes(app: Express) {
  app.get("/api/public/installer/latest", async (_request, response) => {
    try {
      const release = await getLatestFirmwareRelease();
      if (!release) return response.status(404).json({ available: false, code: "no_ready_firmware" });
      return response.status(200).json({
        available: true,
        release: {
          id: release.id,
          version: release.version,
          board: release.board,
          artifact_url: release.artifactUrl,
          sha256: release.sha256,
          size_bytes: release.sizeBytes,
          flash_offset: release.flashOffset,
          release_notes: release.releaseNotes,
        },
      });
    } catch {
      return reject(response, 503, "installer_unavailable");
    }
  });

  app.post("/api/public/installer/enroll", async (request, response) => {
    const parsed = z.object({ device_id: deviceIdSchema }).strict().safeParse(request.body);
    if (!parsed.success) return reject(response, 422, "invalid_device_id");
    if (!enrollLimiter.allow(requesterKey(request))) {
      response.setHeader("Retry-After", "60");
      return reject(response, 429, "enrollment_rate_limited");
    }
    try {
      const enrolled = await registerGatewayDevice(parsed.data.device_id);
      // The token is intentionally returned only in this response so the browser can
      // immediately write it to the ESP32. It is never listed in guest endpoints.
      return response.status(201).json({ accepted: true, device_id: enrolled.deviceId, device_token: enrolled.deviceSecret });
    } catch (error) {
      if (error instanceof Error && error.message === "device_exists") return reject(response, 409, "device_id_exists");
      return reject(response, 503, "installer_unavailable");
    }
  });
}
