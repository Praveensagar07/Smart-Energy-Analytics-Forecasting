# Missing Data & Data Quality Policy

## 1. Overview
The UCI Individual Household Electric Power Consumption dataset contains 2,075,259 one-minute sampling records collected over a 47-month period between December 16, 2006 and November 26, 2010.

During ingestion, each record was evaluated for schema adherence, data type fidelity, and temporal integrity.

## 2. Identified Data Anomalies
- **Missing Value Sentinel**: Missing readings are encoded as `?` strings in numerical fields.
- **Affected Columns**: Exactly 25,979 rows contain `?` across `Global_active_power`, `Global_reactive_power`, `Voltage`, `Global_intensity`, `Sub_metering_1`, and `Sub_metering_2`.
- **Proportion**: Missing rows account for 25,979 / 2,075,259 = **1.2518%** of total observations.
- **Sub_metering_3**: Encoded as numeric or NaN when preceding values are missing.
- **Duplicate Timestamps**: 0 duplicate timestamps were detected in the raw input file. All rows follow a strict 1-minute sequential sampling interval.

## 3. Policy Decisions and Scientific Rationale

### A. No Silent Interpolation of Extended Missing Periods
- As specified by Big Data Analytics best practices and academic standards, arbitrary numerical interpolation (e.g., mean/median filling or linear splines) across hours or days of missing sensor data is prohibited. Silent interpolation distorts peak demand curves, introduces artificial variance, and biases energy forecasting models.

### B. Cleaning and Filtering Rules
1. **Minute-Level Record Cleaning**:
   - Rows where `Global_active_power` or other primary power attributes are missing (`?`) are omitted from cumulative energy summations.
   - Timestamps are strictly parsed using `Date` (`DD/MM/YYYY`) and `Time` (`HH:MM:SS`) into unified ISO-8601 timestamps (`YYYY-MM-DD HH:MM:SS`).
2. **Unit Conversion & Calculation**:
   - `Global_active_power` is provided in kilowatts (kW).
   - Energy consumption in kilowatt-hours (kWh) for a 1-minute interval is calculated as:
     $$\text{Energy}_{\text{interval}} (\text{kWh}) = \text{Global\_active\_power} (\text{kW}) \times \left(\frac{1}{60} \text{ hour}\right)$$
   - Sub-metering values ($S_1, S_2, S_3$) are provided in watt-hours (Wh). They are converted to kWh via division by 1,000:
     $$S_{i} (\text{kWh}) = \frac{S_i (\text{Wh})}{1000}$$
   - Unmetered remainder energy is derived as:
     $$S_{\text{remainder}} (\text{kWh}) = \text{Energy}_{\text{interval}} - (S_1 + S_2 + S_3) / 1000$$
3. **Daily Aggregation and Completeness Tracking**:
   - A complete 24-hour day contains 1,440 minutes.
   - For each calendar date, both `reading_count` and `completeness_ratio` ($N / 1440$) are calculated.
   - Days with completeness $\ge 90\%$ (at least 1,296 readings) are classified as fully representative for machine learning training and daily energy forecasting.
   - Partial days at the boundary (e.g. December 16, 2006 starting at 17:24 and November 26, 2010 ending at 21:02) are flagged as boundary periods.
