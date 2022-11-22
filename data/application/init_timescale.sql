\c weather_monitor;

CREATE TABLE IF NOT EXISTS weather_real_time
(
    time               TIMESTAMP NOT NULL,
    station_id         INT       NOT NULL,
    battery_percentage FLOAT     NULL,
    temperature        FLOAT     NULL,
    humidity           FLOAT     NULL,
    pressure           FLOAT     NULL
);

SELECT create_hypertable('weather_real_time', 'time');

CREATE INDEX ix_station_id_time ON weather_real_time (station_id, time DESC);

CREATE TABLE IF NOT EXISTS weather_stations
(
    station_id serial PRIMARY KEY,
    longitude  FLOAT NOT NULL,
    latitude   FLOAT NOT NULL,
    api_key    TEXT  NOT NULL
);
