# Smart Energy Consumption Analytics & Forecasting
## Academic Project Report — Big Data Analytics (BDA)

**Academic Batch**: 13  
**Project Team**:
- **Praveen Sagar.M** — Register No: 814724104117
- **Naveen.S** — Register No: 814724104104

**Target Sustainable Development Goal**: UN SDG 7 — Affordable and Clean Energy (Level 3)  
**Academic Institution / Subject**: Department of Computer Science & Engineering / Big Data Analytics (BDA)

---

## 1. Abstract
The rapid global deployment of smart electrical grid infrastructure has resulted in massive streams of high-frequency sensor telemetry. Extracting actionable energy conservation insights and generating accurate short-term demand forecasts from these continuous measurement streams is a vital challenge for grid stability and sustainable energy transition. This project presents a complete, distributed Big Data Analytics and Machine Learning framework built upon the UCI Individual Household Electric Power Consumption dataset (comprising 2,075,259 one-minute observations collected over 47 continuous months). The proposed system incorporates distributed storage concepts (HDFS), distributed stream aggregation via Hadoop MapReduce, complex analytical querying via Apache HiveQL, leak-free feature engineering in Apache Spark, and next-day energy forecasting utilizing Apache Spark MLlib. Comparative model evaluation across strict chronological partitions demonstrates that a Random Forest ensemble achieves a Root Mean Squared Error (RMSE) of 5.16 kWh and an $R^2$ of 0.4836 on previously untouched test data, outperforming both Linear Regression (RMSE 5.37 kWh) and a Naive Persistence Baseline (RMSE 6.42 kWh). An end-to-end Star Schema analytical export is created for Microsoft Power BI, enabling multi-dimensional visualization of diurnal curves, sub-metering breakdowns, and demand-side peak-shaving opportunities in alignment with United Nations Sustainable Development Goal 7 (Affordable and Clean Energy).

---

## 2. Introduction
Modern electrical utility networks are transitioning from centralized, unidirectional transmission architectures toward decentralized smart grids. High-frequency smart meters record instantaneous power, current, and voltage parameters at fine temporal resolutions (minute-by-minute or second-by-second). However, high-frequency telemetry presents immense volume, velocity, and variety challenges. Traditional relational database management systems (RDBMS) fail to scale efficiently when processing multi-million-row time-series streams or computing complex historical rolling window statistics. Big Data frameworks such as Apache Hadoop and Apache Spark provide the computational infrastructure necessary to store, transform, and model these data streams reliably.

---

## 3. Problem Statement
Given continuous high-frequency smart meter telemetry:
1. Raw observations exhibit missing readings, sensor dropouts, noise, and mixed physical units (kilowatts vs. Watt-hours) that corrupt analytical validity if processed naively.
2. Large-scale temporal aggregation across multi-year horizons creates computational bottlenecks on single-node compute engines.
3. Conventional machine learning workflows frequently suffer from severe data leakage by applying random shuffling or contemporaneous statistics, resulting in non-generalizable forecasting models.
4. Consumers and utility operators lack unified, interactive business intelligence dashboards that translate raw telemetry into practical, actionable peak-shaving and energy conservation insights.

---

## 4. Objectives
- **Data Ingestion & Physical Cleansing**: Ingest 2,075,259 one-minute raw readings, convert power (kW) to interval energy (kWh), convert sub-metering (Wh) to kWh, derive unmetered energy, and track daily completeness.
- **HDFS Architecture**: Design a multi-tier distributed storage structure (`/smart-energy/raw`, `/cleaned`, `/mapreduce`, `/hive`).
- **Hadoop MapReduce Implementation**: Author and execute genuine Python Streaming Mapper and Reducer jobs to compute daily consumption, verifying mathematical agreement with independent vector calculations.
- **HiveQL Analytical Modeling**: Implement 8 multidimensional queries assessing diurnal patterns, peak demand hours, weekday/weekend variations, seasonal shifts, and sub-metering end-use distributions.
- **Spark Feature Engineering**: Build a leak-free feature matrix using PySpark windowing with lagged and preceding rolling features.
- **Spark MLlib Predictive Modeling**: Train, validate, and evaluate Naive Baseline, Linear Regression, and Random Forest Regressor models on strict chronological partitions.
- **Power BI Decision Support**: Design a 4-page Star Schema Power BI dashboard and publication-quality visualizations for SDG 7 sustainability reporting.

---

## 5. Existing Approaches
Traditional energy analytics rely on centralized SQL databases and static univariate statistical models (e.g., classical ARIMA or basic exponential smoothing). While mathematically sound for low-frequency monthly utility bills, existing approaches exhibit significant limitations:
- **Scalability Bottlenecks**: Inability to process high-frequency minute-level data streams without severe down-sampling.
- **Lack of Non-Linear Interactions**: Inability of linear time-series techniques to capture complex non-linear interactions between seasonal calendar cycles and human domestic behavioral patterns.
- **Pervasive Data Leakage**: Widespread reliance on random train/test splits that leak future information into training features.

---

## 6. Proposed System
The proposed system introduces an integrated Big Data pipeline combining distributed Hadoop batch processing with in-memory Apache Spark analytics:
1. **Streaming Data Cleansing**: Memory-conscious chunked ingestion with strict missing-data policies.
2. **Distributed MapReduce**: Parallel map-side unit transformation and reduce-side key aggregation.
3. **Hive SQL Analytical Layer**: Standardized HiveQL queries structured into optimized external and ORC tables.
4. **PySpark Windowing Feature Pipeline**: Causal backwards-looking rolling statistics (`rowsBetween(-W, -1)`).
5. **Spark MLlib Supervised Forecasting**: Chronologically isolated training, validation, and testing.
6. **Dimensional Serving**: Star-schema CSV exports ready for Microsoft Power BI Desktop ingestion.

---

## 7. System Architecture
The system architecture spans 5 modular layers:
```
Raw Ingestion (clean_data.py)
       │
       ▼
HDFS Directory Storage (/smart-energy/...)
       │
       ├───────────────────────────────┐
       ▼                               ▼
Hadoop MapReduce (Streaming)     HiveQL Analytics Engine (8 Queries)
       │                               │
       └───────────────┬───────────────┘
                       ▼
       PySpark Feature Pipeline (Windowing Lags & Rolling Stats)
                       │
                       ▼
       Spark MLlib Predictive Modeling (Baseline, LR, RF)
                       │
                       ▼
       Power BI Star Schema & Publication Figures (screenshots/)
```

---

## 8. Module Descriptions
1. **Module 1: Preprocessing & Unit Normalization (`preprocessing/clean_data.py`)**:
   Enforces physical unit transformations: $\text{Energy (kWh)} = P (\text{kW}) \times \frac{1}{60}$; converts sub-metering from Wh to kWh; derives remainder energy; flags missing records (`?`); and computes daily completeness ratios.
2. **Module 2: Hadoop MapReduce Engine (`hadoop/mapper.py`, `hadoop/reducer.py`)**:
   Streams text records via standard I/O; extracts dates; emits key-value pairs; sorts by date; and accumulates daily energy and valid minute counts.
3. **Module 3: HiveQL Analytical Engine (`hive/schema.hql`, `hive/queries.hql`)**:
   Defines external and ORC table schemas and executes 8 comprehensive queries assessing temporal consumption dynamics.
4. **Module 4: PySpark Feature Engineering (`spark/spark_feature_pipeline.py`)**:
   Uses PySpark Window specifications to generate 15 leak-free lag and rolling features without forward leakage.
5. **Module 5: Machine Learning Forecasting (`forecasting/train_models.py`)**:
   Partitions data chronologically (70% Train, 15% Validation, 15% Test); fits Linear Regression and Random Forest models; and evaluates MAE, RMSE, $R^2$, and MAPE.
6. **Module 6: Business Intelligence & Dashboard (`dashboard/`)**:
   Generates dimensional tables (`dim_calendar`, `fact_daily_energy`, `fact_hourly_energy`, `fact_forecast_comparison`, `dim_model_performance`) and renders 4 publication plots.

---

## 9. Dataset Overview
- **Dataset**: UCI Individual Household Electric Power Consumption.
- **Source**: UCI Machine Learning Repository / EDF R&D (France).
- **Temporal Span**: December 16, 2006 (17:24) to November 26, 2010 (21:02) — 47 continuous months.
- **Total Records**: 2,075,259 one-minute observations.
- **Attributes**: Date, Time, Global_active_power (kW), Global_reactive_power (kW), Voltage (V), Global_intensity (A), Sub_metering_1 (Kitchen Wh), Sub_metering_2 (Laundry Wh), Sub_metering_3 (Climate/Water Wh).

---

## 10. Data Preprocessing & Validation
- **Missing Data Policy**: 25,979 rows (1.2518%) contain `?` across active power and voltage. In accordance with physical standards, missing periods are excluded from energy summations and flagged; no synthetic interpolation is performed.
- **Completeness Tracking**: Days with $\ge 85\%$ completeness (at least 1,224 valid minutes) are designated as valid for modeling ($N_{\text{valid}} = 1,420$ days).
- **Energy Conservation Validation**: Monitored sub-meters account for 41.89% of active energy, with the remaining 58.11% attributed to lighting, consumer electronics, and general plug loads.

---

## 11. Hadoop MapReduce Implementation
The MapReduce pipeline was tested and mathematically verified using `hadoop/run_mapreduce.py`:
- **Mapper Execution**: Emitted 5,000 key-value pairs from test input.
- **Shuffle & Sort**: Grouped and ordered intermediate keys alphabetically by date.
- **Reducer Aggregation**: Summed interval kWh and counted records per date.
- **Mathematical Equivalence**: Compared against an independent Pandas reference on identical data; maximum energy discrepancy was **0.000033 kWh**, verifying 100% equivalence down to floating-point rounding.

---

## 12. HiveQL Analytical Query Execution
All 8 queries were executed on actual processed data:
- **Query 1 (Daily Series)**: Tracked 1,420 valid daily consumption totals.
- **Query 2 (Monthly Aggregates)**: Discovered peak monthly consumption during winter (December/January, averaging 32–36 kWh/day) and lowest in summer (August, averaging 14–18 kWh/day).
- **Query 3 & 4 (Diurnal Profile & Peaks)**: Pinpointed maximum peak demand at 20:00 (1.94 kWh/hr) and minimum nocturnal baseload at 03:00 (0.46 kWh/hr).
- **Query 5 (Extreme Dates)**: Identified highest single-day historical consumption on June 4, 2007 (69.83 kWh).
- **Query 6 (Weekday vs. Weekend)**: Weekends average 29.17 kWh/day vs. weekdays 25.04 kWh/day (+16.49% weekend surge).
- **Query 7 (Seasonality)**: Confirmed strong winter-peaking thermal characteristics.
- **Query 8 (Sub-Metering Distribution)**: Sub 3 (Water/Climate) represents 31.78% of household energy, Sub 1 (Kitchen) 5.22%, Sub 2 (Laundry) 4.89%, and Remainder 58.11%.

---

## 13. PySpark Feature Engineering
- Windowing: Configured with `Window.orderBy("Date_ISO").rowsBetween(-W, -1)` to strictly prevent current-day or future leakage.
- Features Constructed: Lags 1, 2, 7 days; 7-day rolling mean and standard deviation; 14-day rolling mean; lag 1 voltage and power; sub-metering lags; and calendar indicators (Day of week, Weekend flag, Month).
- Final Feature Dataset: 1,413 complete chronological records with zero null values.

---

## 14. Machine Learning Methodology
- **Partitioning Strategy**:
  - Train Set: 989 days (70%, 2006-12-24 to 2009-09-14)
  - Validation Set: 211 days (15%, 2009-09-15 to 2010-04-18)
  - Held-out Test Set: 213 days (15%, 2010-04-19 to 2010-11-26)
- **Algorithms Evaluated**:
  1. Naive Persistence Baseline ($\hat{y}_{t+1} = y_t$)
  2. Spark MLlib Linear Regression (ElasticNet penalty)
  3. Spark MLlib Random Forest Regressor (40 trees, max depth 5)

---

## 15. Model Evaluation & Comparative Discussion

### Quantitative Results on Held-Out Test Data:
| Model Name | Test MAE (kWh) | Test RMSE (kWh) | Test $R^2$ | Test MAPE (%) | Validation RMSE |
|---|---|---|---|---|---|
| **Naive Baseline** | 4.4998 | 6.4155 | 0.2024 | 19.20% | 8.4182 |
| **Linear Regression** | 3.9607 | 5.3711 | 0.4409 | 18.21% | 6.2883 |
| **Random Forest Regressor** | **3.8297** | **5.1623** | **0.4836** | **18.13%** | **6.0823** |

### Evaluation Discussion:
- **Accuracy Improvement**: Random Forest reduced Test RMSE by 19.53% and MAE by 14.89% relative to the persistence baseline.
- **Explained Variance**: The $R^2$ metric improved from 0.2024 (baseline) to 0.4836 (Random Forest), demonstrating that historical lags and preceding rolling statistics capture nearly half of the day-to-day variance in household electricity demand.
- **Model Selection Justification**: Random Forest achieved the lowest validation RMSE (6.0823), justifying its selection as the primary deployment model.

---

## 16. Power BI Dashboard Architecture
- **Data Model**: Star Schema with `dim_calendar` joined to `fact_daily_energy`, `fact_hourly_energy`, and `fact_forecast_comparison`.
- **Pages Designed**:
  1. *Energy Overview*: High-level consumption KPIs, 4-year trend with 30-day moving average, monthly totals.
  2. *Consumption Analysis*: Weekday vs. weekend boxplots, diurnal demand curves by day of week, sub-metering breakdown.
  3. *Energy Forecasting*: Actual vs. predicted next-day energy, comparative metric bar charts.
  4. *Sustainability Insights (SDG 7)*: Statistical anomaly scatter plots, peak-shaving windows, and bill savings estimates.

---

## 17. Automated Testing Suite
A 24-test unit test suite was implemented in `pytest`:
- Preprocessing unit conversions (kW to kWh, Wh to kWh, remainder): 6 tests passed.
- MapReduce mapper/reducer streaming logic and edge cases: 6 tests passed.
- Feature engineering, leakage prevention, and ordering: 5 tests passed.
- Model evaluation metrics and prediction validity: 3 tests passed.
- Dashboard export schemas and foreign key referential integrity: 4 tests passed.
- **Result**: 24 passed in 1.17 seconds (100% pass rate).

---

## 18. Limitations
1. Single household context restricts direct extrapolation to commercial buildings without transfer learning.
2. Absence of localized weather data (temperature, solar irradiance) limits modeling of climate-driven HVAC loads.
3. Sub-metering is limited to 3 aggregate circuits; individual appliance non-intrusive load monitoring (NILM) is not possible.

---

## 19. Conclusion
This project successfully designed, implemented, tested, and validated an end-to-end Big Data Analytics and Machine Learning system for household energy consumption. By integrating Hadoop MapReduce, HiveQL, PySpark, and Spark MLlib, the system effectively processes multi-million-row smart meter streams, validates mathematical equivalence across distributed execution boundaries, prevents temporal data leakage, and provides actionable demand-side energy conservation insights aligned with UN Sustainable Development Goal 7.

---

## 20. Future Scope
1. **Multivariate Weather Integration**: Ingest real-time meteorological API data (ambient temperature, humidity, wind speed) to enhance HVAC forecasting.
2. **Deep Learning Sequence Models**: Explore Long Short-Term Memory (LSTM) networks and Temporal Fusion Transformers (TFT) for multi-step horizon forecasting ($t+7, t+30$).
3. **Edge Streaming Architecture**: Deploy Apache Kafka and Spark Structured Streaming for real-time sub-minute anomaly alerts.

---

## 21. References
1. **UCI Machine Learning Repository**: Individual Household Electric Power Consumption Dataset. Georges Hébrail, Alice Bérard. EDF R&D, 2012. https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
2. **Apache Hadoop Documentation**: Hadoop Streaming, HDFS Architecture, and MapReduce Tutorial. Apache Software Foundation. https://hadoop.apache.org/docs/stable/
3. **Apache Spark Documentation**: Spark SQL, DataFrames and MLlib Guide (Regression, VectorAssembler). Apache Software Foundation. https://spark.apache.org/docs/latest/
4. **United Nations Sustainable Development Goals**: Goal 7: Ensure access to affordable, reliable, sustainable and modern energy for all. https://sdgs.un.org/goals/goal7
