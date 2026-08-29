CREATE TABLE `firmware_deployment_events` (
	`id` int AUTO_INCREMENT NOT NULL,
	`deviceId` varchar(48) NOT NULL,
	`firmwareReleaseId` int NOT NULL,
	`method` enum('web_serial','ota') NOT NULL,
	`status` enum('started','completed','failed') NOT NULL,
	`detail` varchar(512),
	`recordedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `firmware_deployment_events_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `firmware_releases` (
	`id` int AUTO_INCREMENT NOT NULL,
	`version` varchar(48) NOT NULL,
	`board` varchar(48) NOT NULL,
	`artifactKey` varchar(512) NOT NULL,
	`artifactUrl` varchar(768) NOT NULL,
	`sha256` varchar(64) NOT NULL,
	`sizeBytes` int unsigned NOT NULL,
	`flashOffset` int unsigned NOT NULL DEFAULT 0,
	`releaseNotes` text,
	`status` enum('ready','retracted') NOT NULL DEFAULT 'ready',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `firmware_releases_id` PRIMARY KEY(`id`),
	CONSTRAINT `firmware_releases_version_unique` UNIQUE(`version`)
);
