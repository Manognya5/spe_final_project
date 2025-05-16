CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    respiratory_ailments VARCHAR NOT NULL,
    phone_number VARCHAR NOT NULL UNIQUE,
    permanent_location VARCHAR NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS aqi_data_24hr (
    -- station city
    state VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    station VARCHAR NOT NULL,
    last_updated timestamp NOT NULL,
    PM10_max VARCHAR,
    PM10_min VARCHAR,
    PM10_avg VARCHAR,
    PM2_max VARCHAR,
    PM2_min VARCHAR,
    PM2_avg VARCHAR,
    NO2_max VARCHAR,
    NO2_min VARCHAR,
    NO2_avg VARCHAR,
    NH3_min VARCHAR,
    NH3_max VARCHAR,
    NH3_avg VARCHAR,
    SO2_min VARCHAR,
    SO2_max VARCHAR,
    SO2_avg VARCHAR,
    CO_min VARCHAR,
    CO_max VARCHAR,
    CO_avg VARCHAR,
    OZONE_min VARCHAR,
    OZONE_max VARCHAR,
    OZONE_avg VARCHAR,
    PRIMARY KEY(city, last_updated, station)
);

CREATE TABLE IF NOT EXISTS aqi_historical_data (
 -- station city not needed, why?
    state VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    station VARCHAR NOT NULL,
    last_updated_day timestamp NOT NULL,
    PM10 VARCHAR,
    PM2 VARCHAR,
    NO2 VARCHAR,
    NH3 VARCHAR,
    SO2 VARCHAR,
    CO VARCHAR,
    OZONE VARCHAR,
    AQI VARCHAR,
    PRIMARY KEY(city, last_updated_day, station)
);



INSERT INTO admin_users (username, password) VALUES ('admin', 'admin');
INSERT INTO users (username, password, respiratory_ailments, phone_number, permanent_location) VALUES ('user1', 'user1', 'Asthma', '99999999', 'Hyderabad');
INSERT INTO aqi_data_24hr VALUES ('Telangana', 'Hyderabad', 'Central University, Hyderabad - TSPCB', '2025-05-15 20:00:00',
                                    '78', '11', '40',
                                    '44', '10', '26',
                                    '60', '26', '44',
                                    '9', '4', '7',
                                    '8', '4', '6',
                                    '25', '10', '12',
                                    '24', '5', '23');
INSERT INTO aqi_data_24hr VALUES ('Karnataka', 'Bengaluru', 'City Railway Station, Bengaluru - KSPCB', '2025-05-15 20:00:00',
                                    '78', '11', '40',
                                    '44', '10', '26',
                                    '60', '26', '44',
                                    '9', '4', '7',
                                    '8', '4', '6',
                                    '25', '10', '12',
                                    '24', '5', '23');


