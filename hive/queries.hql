-- =============================================================================
-- HiveQL Analytical Queries
-- Project: Smart Energy Consumption Analytics & Forecasting
-- Subject: Big Data Analytics (BDA)
-- =============================================================================

USE smart_energy_db;

-- -----------------------------------------------------------------------------
-- Query 1: Daily Electricity Consumption Time-Series
-- Objective: Track day-by-day aggregate electricity usage across valid days
-- -----------------------------------------------------------------------------
SELECT 
    consumption_date,
    ROUND(total_energy_kwh, 4) AS daily_energy_kwh,
    reading_count,
    ROUND(completeness_ratio * 100, 2) AS completeness_pct
FROM daily_energy_consumption
WHERE is_valid_day = 1
ORDER BY consumption_date;

-- -----------------------------------------------------------------------------
-- Query 2: Monthly Electricity Consumption Aggregations
-- Objective: Assess calendar month totals, average daily demand, and active days
-- -----------------------------------------------------------------------------
SELECT 
    year_num,
    month_num,
    month_name,
    COUNT(*) AS valid_days_in_month,
    ROUND(SUM(total_energy_kwh), 2) AS total_monthly_kwh,
    ROUND(AVG(total_energy_kwh), 2) AS avg_daily_kwh,
    ROUND(MAX(total_energy_kwh), 2) AS max_daily_kwh
FROM daily_energy_consumption
WHERE is_valid_day = 1
GROUP BY year_num, month_num, month_name
ORDER BY year_num, month_num;

-- -----------------------------------------------------------------------------
-- Query 3: Average Hourly Consumption Profile (24-Hour Diurnal Cycle)
-- Objective: Understand intra-day demand curve for load-shifting and peak shaving
-- -----------------------------------------------------------------------------
SELECT 
    hour_of_day,
    ROUND(AVG(total_energy_kwh), 4) AS avg_hourly_energy_kwh,
    ROUND(AVG(avg_power_kw), 4) AS avg_power_kw,
    ROUND(AVG(avg_voltage_v), 2) AS avg_voltage_v
FROM hourly_energy_consumption
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- -----------------------------------------------------------------------------
-- Query 4: Peak Consumption Hours Identification
-- Objective: Pinpoint top 5 highest electricity demand hours in the day
-- -----------------------------------------------------------------------------
SELECT 
    hour_of_day,
    ROUND(AVG(total_energy_kwh), 4) AS avg_hourly_energy_kwh,
    ROUND(MAX(total_energy_kwh), 4) AS peak_recorded_hourly_kwh,
    ROUND(AVG(avg_power_kw), 4) AS avg_power_demand_kw
FROM hourly_energy_consumption
GROUP BY hour_of_day
ORDER BY avg_hourly_energy_kwh DESC
LIMIT 5;

-- -----------------------------------------------------------------------------
-- Query 5: Top 10 Highest Consumption Dates (Historical Peaks)
-- Objective: Identify extreme consumption events for grid stress analysis
-- -----------------------------------------------------------------------------
SELECT 
    consumption_date,
    day_of_week,
    month_name,
    year_num,
    ROUND(total_energy_kwh, 2) AS total_energy_kwh,
    ROUND(max_power_kw, 2) AS peak_power_kw
FROM daily_energy_consumption
WHERE is_valid_day = 1
ORDER BY total_energy_kwh DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 6: Weekday versus Weekend Energy Usage Patterns
-- Objective: Contrast behavioral patterns between working days and weekends
-- -----------------------------------------------------------------------------
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_category,
    COUNT(*) AS total_days,
    ROUND(AVG(total_energy_kwh), 2) AS avg_daily_energy_kwh,
    ROUND(MIN(total_energy_kwh), 2) AS min_daily_energy_kwh,
    ROUND(MAX(total_energy_kwh), 2) AS max_daily_energy_kwh,
    ROUND(STDDEV(total_energy_kwh), 2) AS std_dev_energy_kwh
FROM daily_energy_consumption
WHERE is_valid_day = 1
GROUP BY is_weekend;

-- -----------------------------------------------------------------------------
-- Query 7: Seasonal Monthly Energy Trends
-- Objective: Measure seasonal variations across the 12 calendar months
-- -----------------------------------------------------------------------------
SELECT 
    month_num,
    month_name,
    ROUND(AVG(total_energy_kwh), 2) AS seasonal_avg_daily_kwh,
    ROUND(SUM(total_energy_kwh), 2) AS cumulative_energy_kwh,
    ROUND(AVG(avg_voltage_v), 2) AS seasonal_avg_voltage
FROM daily_energy_consumption
WHERE is_valid_day = 1
GROUP BY month_num, month_name
ORDER BY month_num;

-- -----------------------------------------------------------------------------
-- Query 8: Sub-Metering End-Use Distribution & Breakdown
-- Objective: Disaggregate household energy into Kitchen, Laundry, Climate, Remainder
-- -----------------------------------------------------------------------------
SELECT 
    ROUND(SUM(total_energy_kwh), 2) AS total_household_kwh,
    ROUND(SUM(sub_metering_1_kwh), 2) AS sub1_kitchen_kwh,
    ROUND(SUM(sub_metering_2_kwh), 2) AS sub2_laundry_kwh,
    ROUND(SUM(sub_metering_3_kwh), 2) AS sub3_climate_water_kwh,
    ROUND(SUM(sub_remainder_kwh), 2) AS unmetered_remainder_kwh,
    ROUND(SUM(sub_metering_1_kwh) / SUM(total_energy_kwh) * 100, 2) AS kitchen_percentage,
    ROUND(SUM(sub_metering_2_kwh) / SUM(total_energy_kwh) * 100, 2) AS laundry_percentage,
    ROUND(SUM(sub_metering_3_kwh) / SUM(total_energy_kwh) * 100, 2) AS climate_water_percentage,
    ROUND(SUM(sub_remainder_kwh) / SUM(total_energy_kwh) * 100, 2) AS remainder_percentage
FROM daily_energy_consumption
WHERE is_valid_day = 1;
