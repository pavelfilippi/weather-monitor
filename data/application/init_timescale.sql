\c weather_monitor;

CREATE TABLE IF NOT EXISTS weather_real_time (
  time TIMESTAMPTZ NOT NULL,
  id INT NOT NULL,
  temperature DOUBLE PRECISION NULL,
  humidity DOUBLE PRECISION NULL,
  pressure DOUBLE PRECISION NULL
);

SELECT create_hypertable('weather_real_time','time');

CREATE INDEX ix_station_id_time ON weather_real_time (id, time DESC);

CREATE TABLE IF NOT EXISTS weather_stations (
    station_id serial PRIMARY KEY,
	battery_percentage FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL
);
