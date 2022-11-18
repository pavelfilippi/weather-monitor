CREATE DATABASE IF NOT EXISTS weather_monitor;

USE weather_monitor;

CREATE TABLE IF NOT EXISTS meteostations (
	id INTEGER NOT NULL AUTO_INCREMENT,
	battery_percentage FLOAT NOT NULL,
	longitude FLOAT NOT NULL,
	latitude FLOAT NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (longitude, latitude)
);
