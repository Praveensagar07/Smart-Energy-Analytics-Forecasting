# HiveQL Analytical Execution Report

Generated using Apache Spark SQL engine running Hive-compatible SQL on genuine UCI Household Power Consumption records.

## Query 1: Daily Electricity Consumption Time-Series
```sql
SELECT 
                    Date_ISO AS consumption_date,
                    ROUND(Energy_kWh, 4) AS daily_energy_kwh,
                    Reading_count,
                    ROUND(Completeness_ratio * 100, 2) AS completeness_pct
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                ORDER BY consumption_date
```

**Exported File:** `hive\query_results\q1_daily_consumption.csv` (1420 rows)

### Query Output Preview:
| consumption_date   |   daily_energy_kwh |   Reading_count |   completeness_pct |
|:-------------------|-------------------:|----------------:|-------------------:|
| 2006-12-17         |            56.5077 |            1440 |             100    |
| 2006-12-18         |            36.7304 |            1440 |             100    |
| 2006-12-19         |            27.7699 |            1440 |             100    |
| 2006-12-20         |            37.0958 |            1440 |             100    |
| 2006-12-21         |            28.6104 |            1438 |              99.86 |
| 2006-12-22         |            39.0223 |            1440 |             100    |
| 2006-12-23         |            79.5564 |            1440 |             100    |
| 2006-12-24         |            42.5002 |            1440 |             100    |
| 2006-12-25         |            45.7187 |            1440 |             100    |
| 2006-12-26         |            65.5685 |            1440 |             100    |

## Query 2: Monthly Electricity Consumption Aggregations
```sql
SELECT 
                    Year AS year_num,
                    Month AS month_num,
                    Month_name AS month_name,
                    COUNT(*) AS valid_days_in_month,
                    ROUND(SUM(Energy_kWh), 2) AS total_monthly_kwh,
                    ROUND(AVG(Energy_kWh), 2) AS avg_daily_kwh,
                    ROUND(MAX(Energy_kWh), 2) AS max_daily_kwh
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Year, Month, Month_name
                ORDER BY Year, Month
```

**Exported File:** `hive\query_results\q2_monthly_consumption.csv` (48 rows)

### Query Output Preview:
|   year_num |   month_num | month_name   |   valid_days_in_month |   total_monthly_kwh |   avg_daily_kwh |   max_daily_kwh |
|-----------:|------------:|:-------------|----------------------:|--------------------:|----------------:|----------------:|
|       2006 |          12 | December     |                    15 |              676.74 |           45.12 |           79.56 |
|       2007 |           1 | January      |                    31 |             1150.2  |           37.1  |           56.79 |
|       2007 |           2 | February     |                    28 |              941.48 |           33.62 |           67.16 |
|       2007 |           3 | March        |                    31 |              981.04 |           31.65 |           58.49 |
|       2007 |           4 | April        |                    27 |              578.97 |           21.44 |           46.43 |
|       2007 |           5 | May          |                    31 |              733.48 |           23.66 |           35.9  |
|       2007 |           6 | June         |                    30 |              594.71 |           19.82 |           35.8  |
|       2007 |           7 | July         |                    31 |              495.06 |           15.97 |           27.03 |
|       2007 |           8 | August       |                    31 |              568.27 |           18.33 |           27.6  |
|       2007 |           9 | September    |                    30 |              697.88 |           23.26 |           38.28 |

## Query 3: Average Hourly Consumption Profile (Diurnal Cycle)
```sql
SELECT 
                    Hour AS hour_of_day,
                    ROUND(AVG(Energy_kWh), 4) AS avg_hourly_energy_kwh,
                    ROUND(AVG(Avg_power_kW), 4) AS avg_power_kw,
                    ROUND(AVG(Avg_voltage_V), 2) AS avg_voltage_v
                FROM hourly_energy_consumption
                GROUP BY Hour
                ORDER BY Hour
```

**Exported File:** `hive\query_results\q3_avg_hourly_consumption.csv` (24 rows)

### Query Output Preview:
|   hour_of_day |   avg_hourly_energy_kwh |   avg_power_kw |   avg_voltage_v |
|--------------:|------------------------:|---------------:|----------------:|
|             0 |                  0.6589 |         0.6596 |          242.4  |
|             1 |                  0.5393 |         0.5393 |          241.72 |
|             2 |                  0.4806 |         0.4806 |          242.59 |
|             3 |                  0.4448 |         0.4448 |          242.68 |
|             4 |                  0.4438 |         0.4438 |          242.43 |
|             5 |                  0.4537 |         0.4537 |          242.09 |
|             6 |                  0.7916 |         0.7916 |          241.94 |
|             7 |                  1.5016 |         1.5024 |          239.92 |
|             8 |                  1.4606 |         1.461  |          239.5  |
|             9 |                  1.3316 |         1.3316 |          239.42 |

## Query 4: Peak Consumption Hours Identification (Top 5)
```sql
SELECT 
                    Hour AS hour_of_day,
                    ROUND(AVG(Energy_kWh), 4) AS avg_hourly_energy_kwh,
                    ROUND(MAX(Energy_kWh), 4) AS peak_recorded_hourly_kwh,
                    ROUND(AVG(Avg_power_kW), 4) AS avg_power_demand_kw
                FROM hourly_energy_consumption
                GROUP BY Hour
                ORDER BY avg_hourly_energy_kwh DESC
                LIMIT 5
```

**Exported File:** `hive\query_results\q4_peak_consumption_hours.csv` (5 rows)

### Query Output Preview:
|   hour_of_day |   avg_hourly_energy_kwh |   peak_recorded_hourly_kwh |   avg_power_demand_kw |
|--------------:|------------------------:|---------------------------:|----------------------:|
|            20 |                  1.899  |                     6.5196 |                1.8991 |
|            21 |                  1.8744 |                     6.3639 |                1.8761 |
|            19 |                  1.7318 |                     6.496  |                1.7334 |
|             7 |                  1.5016 |                     4.4166 |                1.5024 |
|             8 |                  1.4606 |                     4.4189 |                1.461  |

## Query 5: Top 10 Highest Consumption Dates (Historical Extremes)
```sql
SELECT 
                    Date_ISO AS consumption_date,
                    Day_of_week,
                    Month_name,
                    Year,
                    ROUND(Energy_kWh, 2) AS total_energy_kwh,
                    ROUND(Max_power_kW, 2) AS peak_power_kw
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                ORDER BY total_energy_kwh DESC
                LIMIT 10
```

**Exported File:** `hive\query_results\q5_top_consumption_dates.csv` (10 rows)

### Query Output Preview:
| consumption_date   | Day_of_week   | Month_name   |   Year |   total_energy_kwh |   peak_power_kw |
|:-------------------|:--------------|:-------------|-------:|-------------------:|----------------:|
| 2006-12-23         | Saturday      | December     |   2006 |              79.56 |            8.7  |
| 2007-02-03         | Saturday      | February     |   2007 |              67.16 |            7.9  |
| 2006-12-26         | Tuesday       | December     |   2006 |              65.57 |            6.5  |
| 2007-02-18         | Sunday        | February     |   2007 |              63.83 |            7.16 |
| 2007-02-04         | Sunday        | February     |   2007 |              59.93 |            7.7  |
| 2007-02-11         | Sunday        | February     |   2007 |              59.52 |            7.43 |
| 2007-03-31         | Saturday      | March        |   2007 |              58.49 |            7.1  |
| 2006-12-31         | Sunday        | December     |   2006 |              58.24 |            6.72 |
| 2007-03-11         | Sunday        | March        |   2007 |              58.01 |            7.14 |
| 2007-01-21         | Sunday        | January      |   2007 |              56.79 |            8.02 |

## Query 6: Weekday versus Weekend Energy Usage Comparison
```sql
SELECT 
                    CASE WHEN Is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_category,
                    COUNT(*) AS total_days,
                    ROUND(AVG(Energy_kWh), 2) AS avg_daily_energy_kwh,
                    ROUND(MIN(Energy_kWh), 2) AS min_daily_energy_kwh,
                    ROUND(MAX(Energy_kWh), 2) AS max_daily_energy_kwh,
                    ROUND(STDDEV(Energy_kWh), 2) AS std_dev_energy_kwh
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Is_weekend
```

**Exported File:** `hive\query_results\q6_weekday_vs_weekend.csv` (2 rows)

### Query Output Preview:
| day_category   |   total_days |   avg_daily_energy_kwh |   min_daily_energy_kwh |   max_daily_energy_kwh |   std_dev_energy_kwh |
|:---------------|-------------:|-----------------------:|-----------------------:|-----------------------:|---------------------:|
| Weekend        |          401 |                  29.59 |                   4.24 |                  79.56 |                12    |
| Weekday        |         1019 |                  24.84 |                   4.17 |                  65.57 |                 8.74 |

## Query 7: Seasonal Monthly Energy Trends
```sql
SELECT 
                    Month AS month_num,
                    Month_name,
                    ROUND(AVG(Energy_kWh), 2) AS seasonal_avg_daily_kwh,
                    ROUND(SUM(Energy_kWh), 2) AS cumulative_energy_kwh,
                    ROUND(AVG(Avg_voltage_V), 2) AS seasonal_avg_voltage
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Month, Month_name
                ORDER BY Month
```

**Exported File:** `hive\query_results\q7_seasonal_monthly_trends.csv` (12 rows)

### Query Output Preview:
|   month_num | Month_name   |   seasonal_avg_daily_kwh |   cumulative_energy_kwh |   seasonal_avg_voltage |
|------------:|:-------------|-------------------------:|------------------------:|-----------------------:|
|           1 | January      |                    35.07 |                 4243.5  |                 242.16 |
|           2 | February     |                    31.2  |                 3525.23 |                 241.46 |
|           3 | March        |                    29.55 |                 3605.31 |                 241.53 |
|           4 | April        |                    25.16 |                 2943.36 |                 241.07 |
|           5 | May          |                    24.71 |                 3063.88 |                 239.01 |
|           6 | June         |                    21.83 |                 2554.47 |                 239.91 |
|           7 | July         |                    16.8  |                 2082.66 |                 240    |
|           8 | August       |                    13.69 |                 1615.3  |                 240.17 |
|           9 | September    |                    23.41 |                 2715.03 |                 240.45 |
|          10 | October      |                    27.28 |                 3383.24 |                 240.78 |

## Query 8: Sub-Metering End-Use Distribution & Breakdown
```sql
SELECT 
                    ROUND(SUM(Energy_kWh), 2) AS total_household_kwh,
                    ROUND(SUM(Sub_metering_1_kWh), 2) AS kitchen_kwh,
                    ROUND(SUM(Sub_metering_2_kWh), 2) AS laundry_kwh,
                    ROUND(SUM(Sub_metering_3_kWh), 2) AS climate_water_kwh,
                    ROUND(SUM(Sub_metering_remainder_kWh), 2) AS unmetered_remainder_kwh,
                    ROUND(SUM(Sub_metering_1_kWh) / SUM(Energy_kWh) * 100, 2) AS kitchen_pct,
                    ROUND(SUM(Sub_metering_2_kWh) / SUM(Energy_kWh) * 100, 2) AS laundry_pct,
                    ROUND(SUM(Sub_metering_3_kWh) / SUM(Energy_kWh) * 100, 2) AS climate_water_pct,
                    ROUND(SUM(Sub_metering_remainder_kWh) / SUM(Energy_kWh) * 100, 2) AS remainder_pct
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
```

**Exported File:** `hive\query_results\q8_submetering_breakdown.csv` (1 rows)

### Query Output Preview:
|   total_household_kwh |   kitchen_kwh |   laundry_kwh |   climate_water_kwh |   unmetered_remainder_kwh |   kitchen_pct |   laundry_pct |   climate_water_pct |   remainder_pct |
|----------------------:|--------------:|--------------:|--------------------:|--------------------------:|--------------:|--------------:|--------------------:|----------------:|
|               37172.7 |       2290.73 |       2649.12 |             13203.5 |                   19029.7 |          6.16 |          7.13 |               35.52 |           51.19 |
