-- =============================================================================
-- Hive DDL Schema Definitions
-- Project: Smart Energy Consumption Analytics & Forecasting
-- Academic Subject: Big Data Analytics (BDA)
-- =============================================================================

-- Database Creation
CREATE DATABASE IF NOT EXISTS smart_energy_db
COMMENT 'Database for Household Electricity Consumption Analytics'
LOCATION '/smart-energy/hive/warehouse';

USE smart_energy_db;

-- 1. External Raw Staging Table backed by HDFS storage
-- Delimited by semicolon ';', handling header and NULL representation
DROP TABLE IF EXISTS raw_household_power;
CREATE EXTERNAL TABLE IF NOT EXISTS raw_household_power (
    record_date STRING COMMENT 'Measurement Date (DD/MM/YYYY)',
    record_time STRING COMMENT 'Measurement Time (HH:MM:SS)',
    global_active_power FLOAT COMMENT 'Minute-averaged active power in kW',
    global_reactive_power FLOAT COMMENT 'Minute-averaged reactive power in kW',
    voltage FLOAT COMMENT 'Minute-averaged voltage in Volts',
    global_intensity FLOAT COMMENT 'Minute-averaged current intensity in Amperes',
    sub_metering_1 FLOAT COMMENT 'Active energy in Watt-hour (Kitchen)',
    sub_metering_2 FLOAT COMMENT 'Active energy in Watt-hour (Laundry room)',
    sub_metering_3 FLOAT COMMENT 'Active energy in Watt-hour (Climate / Water heater)'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ';'
STORED AS TEXTFILE
LOCATION '/smart-energy/raw'
TBLPROPERTIES (
    "skip.header.line.count"="1",
    "serialization.null.format"="?"
);

-- 2. Daily Energy Consumption Analytics Table (ORC format for high-efficiency querying)
DROP TABLE IF EXISTS daily_energy_consumption;
CREATE TABLE IF NOT EXISTS daily_energy_consumption (
    consumption_date STRING COMMENT 'ISO Date YYYY-MM-DD',
    total_energy_kwh DOUBLE COMMENT 'Daily energy consumption in kilowatt-hours (kWh)',
    avg_power_kw DOUBLE COMMENT 'Average power demand in kW',
    max_power_kw DOUBLE COMMENT 'Peak power demand in kW',
    min_power_kw DOUBLE COMMENT 'Base load power demand in kW',
    avg_voltage_v DOUBLE COMMENT 'Average voltage in Volts',
    sub_metering_1_kwh DOUBLE COMMENT 'Kitchen active energy in kWh',
    sub_metering_2_kwh DOUBLE COMMENT 'Laundry active energy in kWh',
    sub_metering_3_kwh DOUBLE COMMENT 'Water/AC active energy in kWh',
    sub_remainder_kwh DOUBLE COMMENT 'Unmonitored household active energy in kWh',
    reading_count INT COMMENT 'Count of valid minute records',
    completeness_ratio DOUBLE COMMENT 'Reading count / 1440',
    is_valid_day INT COMMENT '1 if completeness >= 0.85, else 0',
    day_of_week STRING COMMENT 'Day name (Monday..Sunday)',
    is_weekend INT COMMENT '1 for Saturday/Sunday, else 0',
    month_num INT COMMENT 'Month number (1..12)',
    month_name STRING COMMENT 'Month name (January..December)'
)
PARTITIONED BY (year_num INT)
STORED AS ORC
TBLPROPERTIES ("orc.compress"="SNAPPY");

-- 3. Hourly Energy Consumption Analytics Table
DROP TABLE IF EXISTS hourly_energy_consumption;
CREATE TABLE IF NOT EXISTS hourly_energy_consumption (
    consumption_date STRING COMMENT 'ISO Date YYYY-MM-DD',
    hour_of_day INT COMMENT 'Hour of the day (0..23)',
    total_energy_kwh DOUBLE COMMENT 'Hourly energy in kWh',
    avg_power_kw DOUBLE COMMENT 'Average power demand in kW',
    avg_voltage_v DOUBLE COMMENT 'Average voltage in Volts',
    sub_metering_1_kwh DOUBLE COMMENT 'Kitchen energy in kWh',
    sub_metering_2_kwh DOUBLE COMMENT 'Laundry energy in kWh',
    sub_metering_3_kwh DOUBLE COMMENT 'Water/AC energy in kWh',
    sub_remainder_kwh DOUBLE COMMENT 'Unmonitored energy in kWh',
    reading_count INT COMMENT 'Valid minute records in hour'
)
STORED AS PARQUET;
