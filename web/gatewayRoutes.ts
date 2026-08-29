import type { Express, Request, Response } from "express";
import { DeviceRateLimiter, sensorTestReadingSchema, verifyDeviceSecret } from "./gateway";
import { findActiveGatewayDevice, saveAcceptedReading } from "./gatewayStore";

const rateLimiter = new DeviceRateLimiter();

function reject(response: Response, status: number, code: string) {
  return response.status(status).json({ accepted: false, code });
}

export function registerGatewayRoutes(app: Express) {
  app.get("/api/health", (_request, response) => {
    response.status(200).json({ status: "ok", service: "sensable-esp32-gateway", timestamp: new Date().toISOString() });
  });

  app.post("/api/ingest/v1/readings", async (request: Request, response: Response) => {
    const parsed = sensorTestReadingSchema.safeParse(request.body);
    if (!parsed.success) {
      return reject(response, 422, "invalid_test_payload");
    }

    const tokenHeader = request.header("x-device-token");
    if (!tokenHeader || tokenHeader.length < 32 || tokenHeader.length > 128) {
      return reject(response, 401, "unauthorized_device");
    }

    try {
      const device = await findActiveGatewayDevice(parsed.data.device_id);
      if (!device || !verifyDeviceSecret(tokenHeader, device.tokenHash)) {
        return reject(response, 401, "unauthorized_device");
      }

      if (!rateLimiter.allow(parsed.data.device_id)) {
        response.setHeader("Retry-After", "60");
        return reject(response, 429, "rate_limited");
      }

      await saveAcceptedReading(parsed.data);
      return response.status(202).json({
        accepted: true,
        device_id: parsed.data.device_id,
        received_at: new Date().toISOString(),
      });
    } catch (error) {
      console.error("Gateway ingestion failed", error instanceof Error ? error.message : "unknown_error");
      return reject(response, 503, "gateway_unavailable");
    }
  });
}
