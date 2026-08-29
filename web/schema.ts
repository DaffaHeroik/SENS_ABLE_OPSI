import { double, int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

/** Stores only anonymous device identifiers and secret hashes. */
export const gatewayDevices = mysqlTable("gateway_devices", {
  id: int("id").autoincrement().primaryKey(),
  deviceId: varchar("deviceId", { length: 48 }).notNull().unique(),
  tokenHash: varchar("tokenHash", { length: 64 }).notNull(),
  active: mysqlEnum("active", ["active", "revoked"]).default("active").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  lastSeenAt: timestamp("lastSeenAt"),
});

/** Stores test signal values only; no names, SubjectID, or glucose-reference records are allowed. */
export const sensorTestReadings = mysqlTable("sensor_test_readings", {
  id: int("id").autoincrement().primaryKey(),
  deviceId: varchar("deviceId", { length: 48 }).notNull(),
  firmwareVersion: varchar("firmwareVersion", { length: 48 }),
  irMean: double("irMean").notNull(),
  redMean: double("redMean").notNull(),
  heartRateBpm: double("heartRateBpm"),
  spo2Pct: double("spo2Pct"),
  temperatureC: double("temperatureC"),
  uptimeMs: int("uptimeMs", { unsigned: true }),
  receivedAt: timestamp("receivedAt").defaultNow().notNull(),
});

/** A reviewed pre-built binary; source compilation intentionally occurs outside the managed gateway runtime. */
export const firmwareReleases = mysqlTable("firmware_releases", {
  id: int("id").autoincrement().primaryKey(),
  version: varchar("version", { length: 48 }).notNull().unique(),
  board: varchar("board", { length: 48 }).notNull(),
  artifactKey: varchar("artifactKey", { length: 512 }).notNull(),
  artifactUrl: varchar("artifactUrl", { length: 768 }).notNull(),
  sha256: varchar("sha256", { length: 64 }).notNull(),
  sizeBytes: int("sizeBytes", { unsigned: true }).notNull(),
  flashOffset: int("flashOffset", { unsigned: true }).notNull().default(0),
  releaseNotes: text("releaseNotes"),
  status: mysqlEnum("status", ["ready", "retracted"]).default("ready").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

/** Owner-reported USB/OTA deployment evidence; this records deployment workflow state, not clinical outcomes. */
export const firmwareDeploymentEvents = mysqlTable("firmware_deployment_events", {
  id: int("id").autoincrement().primaryKey(),
  deviceId: varchar("deviceId", { length: 48 }).notNull(),
  firmwareReleaseId: int("firmwareReleaseId").notNull(),
  method: mysqlEnum("method", ["web_serial", "ota"]).notNull(),
  status: mysqlEnum("status", ["started", "completed", "failed"]).notNull(),
  detail: varchar("detail", { length: 512 }),
  recordedAt: timestamp("recordedAt").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
