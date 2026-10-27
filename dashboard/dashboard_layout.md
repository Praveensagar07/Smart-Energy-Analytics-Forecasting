# Power BI Dashboard Architecture & Layout Specification

## Project: Smart Energy Consumption Analytics & Forecasting
**Target Application**: Microsoft Power BI Desktop  
**Data Sources**: Pre-aggregated Star Schema CSV exports in `dashboard/power_bi_exports/`

---

## 1. Data Model Architecture (Star Schema)

The dashboard is structured around an industry-standard dimensional star schema:

```
                  +-------------------------+
                  |      dim_calendar       |
                  |-------------------------|
                  | Date (PK)               |
                  | Year, Quarter, Month    |
                  | Day, Day_of_Week        |
                  | Is_Weekend, Day_Category|
                  +-------------------------+
                               |
            +------------------+------------------+
            | 1:*                                 | 1:*
            v                                     v
+-------------------------+           +--------------------------+
|    fact_daily_energy    |           |   fact_hourly_energy     |
|-------------------------|           |--------------------------|
| Date (FK)               |           | Date (FK), Hour          |
| Energy_kWh, Avg_Power_kW|           | Total_energy_kwh         |
| Peak_Power_kW, Voltage  |           | Avg_power_kW, Voltage    |
| Sub1, Sub2, Sub3, Rem   |           | Sub1, Sub2, Sub3, Rem    |
| Estimated_Cost_EUR      |           +--------------------------+
| Is_Consumption_Anomaly  |
+-------------------------+
            | 1:*
            v
+-------------------------------+
|   fact_forecast_comparison   |
|-------------------------------|
| Date (FK)                     |
| Actual_kWh, Baseline_Pred_kWh |
| LinearRegression_Pred_kWh     |
| RandomForest_Pred_kWh         |
| RF_Abs_Error, RF_Sq_Error     |
+-------------------------------+

+--------------------------------+
|     dim_model_performance      |  (Standalone Evaluation Dimension)
|--------------------------------|
| Model_Name, Val_RMSE, Val_MAE  |
| Test_RMSE, Test_MAE, Test_R2   |
+--------------------------------+
```

---

## 2. Four-Page Dashboard Structure

### Page 1: Energy Overview
* **Header**: Title, Batch 13, Student Names (Praveen Sagar.M & Naveen.S), Date Range Slicer (2006–2010).
* **KPI Card Row**:
  1. `Total Energy (kWh)`: **37,283.75 kWh**
  2. `Average Daily Consumption`: **26.18 kWh/day**
  3. `Peak Recorded Demand`: **11.12 kW**
  4. `Estimated Total Cost`: **€7,434.53** (at €0.20/kWh)
* **Main Visual (Top 60%)**: Line & Area Chart — Daily Electricity Consumption (kWh) over time with a 30-day moving average overlay.
* **Bottom Left (20%)**: Clustered Column Chart — Monthly Energy Totals across monitored years.
* **Bottom Right (20%)**: Area Chart — 24-Hour Diurnal Demand Profile showing intra-day peak periods.

---

### Page 2: Consumption Analysis
* **Visual 1 (Top Left)**: Box and Whisker / Violin Chart — Weekday vs Weekend energy variance. Shows higher mean usage and variance on Saturdays and Sundays.
* **Visual 2 (Top Right)**: Donut Chart — Sub-Metering End-Use Distribution:
  - Climate Control & Water Heater (Sub 3): ~31.8%
  - Kitchen Dishwasher / Microwave (Sub 1): ~5.2%
  - Laundry Washing Machine (Sub 2): ~4.9%
  - Unmetered Household Remainder: ~58.1%
* **Visual 3 (Bottom)**: Multi-line Line Chart — 24-Hour Diurnal curves broken down by Day of the Week (Monday to Sunday) highlighting afternoon and evening lifestyle peaks.

---

### Page 3: Energy Forecasting (Machine Learning)
* **KPI Card Row**:
  1. `Best Model Selected`: **Random Forest Regressor (Spark MLlib)**
  2. `Test RMSE`: **5.16 kWh** (vs Baseline 6.42 kWh — 19.5% improvement)
  3. `Test MAE`: **3.83 kWh** (vs Baseline 4.50 kWh)
  4. `Test R²`: **0.4836** (vs Baseline 0.2024)
* **Main Visual**: Line Chart — Test Period (April 2010 – November 2010) showing **Actual Energy Consumption** (solid black) vs **Random Forest Prediction** (green) vs **Linear Regression** (blue dashed) vs **Baseline** (orange dotted).
* **Secondary Visual**: Clustered Column Chart — Side-by-side metric comparison (MAE, RMSE, R²) across all three evaluated algorithms.

---

### Page 4: Sustainability Insights (SDG 7 Alignment)
* **KPI Card Row**:
  1. `High-Consumption Anomaly Days`: **49 days** identified ($> \mu + 2\sigma$)
  2. `Peak Grid Stress Window`: **18:00 – 21:00** (Average power: 2.12 kW)
  3. `Optimal Load-Shifting Window`: **01:00 – 05:00** (Average power: 0.48 kW)
  4. `Est. Annual Saving Potential`: **€280 – €420** via off-peak shifting
* **Visual 1**: Scatter Plot — Date vs Daily Consumption, with anomaly events highlighted in crimson.
* **Visual 2**: Stacked Column Chart — Hourly Power Demand color-coded by tariff tier (Off-Peak green, Mid-Peak blue, On-Peak red).
* **Narrative Card**: Concrete energy conservation guidelines supporting UN Sustainable Development Goal 7:
  - Shifting high-consumption appliances (dishwashers, tumble dryers) to nocturnal off-peak hours.
  - Mitigating thermal load through smart thermostat scheduling.

---

## 3. Step-by-Step Power BI Desktop Import Procedure

1. Launch **Microsoft Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV**.
3. Navigate to `dashboard/power_bi_exports/` and import:
   - `dim_calendar.csv`
   - `fact_daily_energy.csv`
   - `fact_hourly_energy.csv`
   - `fact_forecast_comparison.csv`
   - `dim_model_performance.csv`
4. In the **Model View**, verify relationships:
   - `dim_calendar[Date]` $1 \rightarrow *$ `fact_daily_energy[Date]`
   - `dim_calendar[Date]` $1 \rightarrow *$ `fact_hourly_energy[Date]`
   - `dim_calendar[Date]` $1 \rightarrow *$ `fact_forecast_comparison[Date]`
5. In the **Report View**, create a **New Measure Table** and paste the DAX measures from `dashboard/dax_measures.md`.
6. Add 4 report pages corresponding to the layouts documented above.
7. Save the report file as `dashboard/Smart_Energy_Analytics.pbix`.
