# Power BI DAX Measures Reference Guide

## Project: Smart Energy Consumption Analytics & Forecasting
**Target Dataset**: UCI Individual Household Electric Power Consumption  
**Data Model**: Star Schema (`dim_calendar` $\rightarrow$ `fact_daily_energy`, `fact_hourly_energy`, `fact_forecast_comparison`)

---

### 1. Key Performance Indicators (KPIs)

#### Total Electricity Consumed (kWh)
```dax
Total Energy (kWh) = 
SUM('fact_daily_energy'[Energy_kWh])
```

#### Total Electricity Consumed (MWh)
```dax
Total Energy (MWh) = 
DIVIDE([Total Energy (kWh)], 1000, 0)
```

#### Average Daily Energy Consumption (kWh/day)
```dax
Avg Daily Energy (kWh) = 
AVERAGEX(
    FILTER('fact_daily_energy', 'fact_daily_energy'[Is_valid_day] = 1),
    'fact_daily_energy'[Energy_kWh]
)
```

#### Peak Power Demand (kW)
```dax
Peak Demand (kW) = 
MAX('fact_daily_energy'[Max_power_kW])
```

#### Total Active Days Monitored
```dax
Monitored Days = 
CALCULATE(
    COUNTROWS('fact_daily_energy'),
    'fact_daily_energy'[Is_valid_day] = 1
)
```

---

### 2. Financial & Cost Estimations (Tariff = 0.20 EUR / kWh)

#### Total Estimated Energy Cost (€)
```dax
Total Energy Cost (€) = 
SUM('fact_daily_energy'[Estimated_Cost_EUR])
```

#### Average Daily Cost (€/day)
```dax
Avg Daily Cost (€) = 
[Avg Daily Energy (kWh)] * 0.20
```

---

### 3. Time Intelligence & Moving Averages

#### 7-Day Rolling Average Energy (kWh)
```dax
Energy 7D Rolling Avg (kWh) = 
CALCULATE(
    AVERAGE('fact_daily_energy'[Energy_kWh]),
    DATESINPERIOD('dim_calendar'[Date], LASTDATE('dim_calendar'[Date]), -7, DAY),
    'fact_daily_energy'[Is_valid_day] = 1
)
```

#### 30-Day Rolling Average Energy (kWh)
```dax
Energy 30D Rolling Avg (kWh) = 
CALCULATE(
    AVERAGE('fact_daily_energy'[Energy_kWh]),
    DATESINPERIOD('dim_calendar'[Date], LASTDATE('dim_calendar'[Date]), -30, DAY),
    'fact_daily_energy'[Is_valid_day] = 1
)
```

#### Month-over-Month (MoM) Consumption Growth %
```dax
MoM Consumption Growth % = 
VAR CurrentMonth = [Total Energy (kWh)]
VAR PreviousMonth = CALCULATE([Total Energy (kWh)], DATEADD('dim_calendar'[Date], -1, MONTH))
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0)
```

---

### 4. Sub-Metering Breakdown Measures

#### Kitchen Active Energy (kWh & %)
```dax
Kitchen Energy (kWh) = SUM('fact_daily_energy'[Sub_metering_1_kWh])

Kitchen Energy % = DIVIDE([Kitchen Energy (kWh)], [Total Energy (kWh)], 0)
```

#### Laundry Room Active Energy (kWh & %)
```dax
Laundry Energy (kWh) = SUM('fact_daily_energy'[Sub_metering_2_kWh])

Laundry Energy % = DIVIDE([Laundry Energy (kWh)], [Total Energy (kWh)], 0)
```

#### Climate Control & Water Heater Energy (kWh & %)
```dax
Climate & Water Energy (kWh) = SUM('fact_daily_energy'[Sub_metering_3_kWh])

Climate & Water Energy % = DIVIDE([Climate & Water Energy (kWh)], [Total Energy (kWh)], 0)
```

#### Unmonitored Remainder Energy (kWh & %)
```dax
Unmetered Remainder Energy (kWh) = SUM('fact_daily_energy'[Sub_metering_remainder_kWh])

Unmetered Remainder % = DIVIDE([Unmetered Remainder Energy (kWh)], [Total Energy (kWh)], 0)
```

---

### 5. Forecasting & Machine Learning Evaluation

#### Forecast Mean Absolute Error (MAE) - Test Set
```dax
RF Forecast MAE = 
AVERAGEX('fact_forecast_comparison', 'fact_forecast_comparison'[RF_Abs_Error])
```

#### Forecast Root Mean Squared Error (RMSE) - Test Set
```dax
RF Forecast RMSE = 
SQRT(AVERAGEX('fact_forecast_comparison', 'fact_forecast_comparison'[RF_Sq_Error]))
```

#### Forecast Accuracy % (100 - MAPE)
```dax
RF Forecast Accuracy % = 
VAR MeanMAPE = AVERAGEX(
    FILTER('fact_forecast_comparison', 'fact_forecast_comparison'[Actual_kWh] > 0.5),
    DIVIDE('fact_forecast_comparison'[RF_Abs_Error], 'fact_forecast_comparison'[Actual_kWh])
)
RETURN
    1 - MeanMAPE
```

---

### 6. Sustainability & Anomaly Identification (SDG 7)

#### High Consumption Anomaly Flag (Count of Days)
```dax
Consumption Anomaly Days Count = 
CALCULATE(
    COUNTROWS('fact_daily_energy'),
    'fact_daily_energy'[Is_Consumption_Anomaly] = 1
)
```

#### Potential Energy Saving from Off-Peak Load Shifting (kWh)
```dax
Peak Shaving Potential (kWh) = 
CALCULATE(
    SUM('fact_hourly_energy'[Total_energy_kwh]),
    'fact_hourly_energy'[Hour] >= 18 && 'fact_hourly_energy'[Hour] <= 21
) * 0.15
```
*(Estimates a realistic 15% discretionary load transfer from peak 18:00–21:00 to low-cost nocturnal hours 01:00–05:00).*
