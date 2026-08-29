CREATE TABLE `gateway_devices` (
	`id` int AUTO_INCREMENT NOT NULL,
	`deviceId` varchar(48) NOT NULL,
	`tokenHash` varchar(64) NOT NULL,
	`active` enum('active','revoked') NOT NULL DEFAULT 'active',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`lastSeenAt` timestamp,
	CONSTRAINT `gateway_devices_id` PRIMARY KEY(`id`),
	CONSTRAINT `gateway_devices_deviceId_unique` UNIQUE(`deviceId`)
);
--> statement-breakpoint
CREATE TABLE `sensor_test_readings` (
	`id` int AUTO_INCREMENT NOT NULL,
	`deviceId` varchar(48) NOT NULL,
	`firmwareVersion` varchar(48),
	`irMean` double NOT NULL,
	`redMean` double NOT NULL,
	`heartRateBpm` double,
	`spo2Pct` double,
	`temperatureC` double,
	`uptimeMs` int unsigned,
	`receivedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `sensor_test_readings_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `name` varchar(255);--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `role` enum('admin','user') NOT NULL DEFAULT 'user';