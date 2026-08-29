import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { adminProcedure, publicProcedure, router } from "./_core/trpc";
import { deploymentEventSchema, deviceIdSchema } from "./gateway";
import { getGatewayOverview, recordFirmwareDeploymentEvent, registerGatewayDevice } from "./gatewayStore";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  gateway: router({
    overview: adminProcedure.query(async () => getGatewayOverview()),
    registerDevice: adminProcedure
      .input(z.object({ deviceId: deviceIdSchema }).strict())
      .mutation(async ({ input }) => {
        try {
          return await registerGatewayDevice(input.deviceId);
        } catch (error) {
          if (error instanceof Error && error.message === "device_exists") {
            throw new TRPCError({ code: "CONFLICT", message: "This device identifier already exists." });
          }
          throw new TRPCError({ code: "SERVICE_UNAVAILABLE", message: "The gateway database is unavailable." });
        }
      }),
    recordDeployment: adminProcedure.input(deploymentEventSchema).mutation(async ({ input }) => {
      try {
        await recordFirmwareDeploymentEvent(input);
        return { success: true } as const;
      } catch {
        throw new TRPCError({ code: "SERVICE_UNAVAILABLE", message: "Deployment event could not be stored." });
      }
    }),
  }),
});

export type AppRouter = typeof appRouter;
