# Experimental Results & Performance Analysis

## Smart Energy Consumption Analytics & Forecasting
**Academic Batch**: 13  
**Authors**: Praveen Sagar.M & Naveen.S

---

## 1. Dataset Processing & Validation Summary

| Metric | Measured Value | Unit / Note |
|---|---|---|
| Total Raw Minute Readings | **2,075,259** | 100.0% |
| Valid Power Readings | **2,049,280** | 98.7482% |
| Missing Power Readings (`?`) | **25,979** | 1.2518% |
| Duplicate Timestamps Detected | **0** | Perfect sequential sampling |
| Monitored Calendar Period | **Dec 16, 2006 – Nov 26, 2010** | 47 continuous months (1,433 days) |
| Valid Calendar Days ($\ge 85\%$ complete) | **1,420** | 99.09% of days |
| Total Recorded Energy | **37,283.75** | kWh |
| Mean Daily Consumption | **26.18** | kWh/day |
| Maximum Daily Consumption | **69.83** | kWh/day (Recorded 2007-06-04) |
| Minimum Valid Daily Consumption | **3.85** | kWh/day |

---

## 2. Hadoop MapReduce Execution Evidence

The MapReduce streaming pipeline was executed and validated against an independent Pandas vector aggregation across identical input records:

| Parameter | MapReduce Result | Independent Reference | Absolute Difference |
|---|---|---|---|
| Sample Lines Processed | 5,000 | 5,000 | 0 |
| Valid Emitted Key-Value Pairs | 5,000 | 5,000 | 0 |
| Dates Verified | 5 | 5 | 0 |
| Maximum Energy Discrepancy | — | — | **0.000033 kWh** ($< 10^{-4}$) |
| Discrepancy Count | **0** | **0** | **0 (VERIFIED EQUIVALENT)** |

---

## 3. HiveQL Analytical Findings

### A. Sub-Metering Disaggregation (Query 8)
- **Total Monitored Energy**: 37,172.66 kWh (across 1,420 valid days)
- **Sub-Metering 3 (Water Heater & Air Conditioner)**: 11,812.54 kWh (**31.78%**) — Primary household thermal load.
- **Sub-Metering 1 (Kitchen Dishwasher/Microwave)**: 1,938.83 kWh (**5.22%**)
- **Sub-Metering 2 (Laundry Washing Machine)**: 1,819.53 kWh (**4.89%**)
- **Unmetered Household Remainder**: 21,601.76 kWh (**58.11%**) — Lighting, electronics, small appliances, refrigeration.

### B. Weekday versus Weekend Patterns (Query 6)
- **Weekday Consumption (Mon–Fri)**: Mean = **25.04 kWh/day** ($N = 1019$ days)
- **Weekend Consumption (Sat–Sun)**: Mean = **29.17 kWh/day** ($N = 401$ days)
- **Weekend Premium**: Weekend consumption is **+16.49% higher** than weekdays, reflecting continuous household occupancy and intensive domestic chores.

### C. Diurnal Peak Demand Hours (Query 4)
The top 5 peak electricity demand hours of the day:
1. **Hour 20 (20:00 – 21:00)**: Average demand = **1.94 kWh/hr** (Avg power = 1.94 kW)
2. **Hour 21 (21:00 – 22:00)**: Average demand = **1.86 kWh/hr**
3. **Hour 19 (19:00 – 20:00)**: Average demand = **1.78 kWh/hr**
4. **Hour 13 (13:00 – 14:00)**: Average demand = **1.52 kWh/hr**
5. **Hour 12 (12:00 – 13:00)**: Average demand = **1.48 kWh/hr**
*Base-load Nocturnal Valley*: **Hour 03 (03:00 – 04:00)**: Average demand = **0.46 kWh/hr** (a 4.2x ratio between peak and trough).

---

## 4. Machine Learning Forecasting Model Comparison

Forecasting Next-Day Household Electricity Consumption ($E_t$) on the strict chronological test period ($N = 213$ days, April 2010 – November 2010):

| Model | Algorithm / Type | Validation RMSE | Test MAE (kWh) | Test RMSE (kWh) | Test $R^2$ | Test MAPE (%) |
|---|---|---|---|---|---|---|
| **Naive Baseline** | Persistence ($y_{t-1}$) | 8.4182 | 4.4998 | 6.4155 | 0.2024 | 19.20% |
| **Linear Regression** | Spark MLlib ElasticNet | 6.2883 | 3.9607 | 5.3711 | 0.4409 | 18.21% |
| **Random Forest** | Spark MLlib (40 trees, depth 5) | **6.0823** | **3.8297** | **5.1623** | **0.4836** | **18.13%** |

### Performance Discussion & Key Takeaways:
1. **Baseline Outperformance**: Both MLlib models substantially outperformed the Naive Persistence baseline. The Random Forest model achieved an RMSE reduction of **19.53%** (5.16 kWh vs. 6.42 kWh) and more than doubled the explained variance ($R^2 = 0.4836$ vs. $0.2024$).
2. **Non-Linear Dynamics**: Random Forest surpassed Linear Regression across all metrics (Test RMSE 5.16 vs 5.37 kWh), demonstrating that non-linear interaction terms between seasonal month, day of week, and multi-day rolling standard deviations are essential for modeling stochastic household electricity behavior.
3. **Model Selection**: Random Forest Regressor was objectively selected as the best model based on having the lowest Validation RMSE (6.0823).
