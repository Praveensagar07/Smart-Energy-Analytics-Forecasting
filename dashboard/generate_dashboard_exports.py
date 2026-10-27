#!/usr/bin/env python3
"""
Power BI Dashboard Export Generator
Smart Energy Consumption Analytics & Forecasting

Generates clean, star-schema structured CSV exports for Power BI Desktop ingestion:
1. dim_calendar.csv               - Date dimension with temporal hierarchies
2. fact_daily_energy.csv           - Daily consumption facts with estimated cost
3. fact_hourly_energy.csv          - Hourly diurnal facts for load curve analysis
4. fact_forecast_comparison.csv    - Test period actuals vs forecasts
5. dim_model_performance.csv       - Comparative model metrics (MAE, RMSE, R2, MAPE)
"""

import os
import json
import pandas as pd
import numpy as np

def generate_power_bi_exports():
    export_dir = os.path.join("dashboard", "power_bi_exports")
    os.makedirs(export_dir, exist_ok=True)
    print(f"[*] Preparing Power BI Star-Schema exports in: {export_dir}")

    # Load source processed data
    daily_path = os.path.join("data", "processed", "daily_energy_consumption.csv")
    hourly_path = os.path.join("data", "processed", "hourly_energy_consumption.csv")
    preds_path = os.path.join("forecasting", "test_predictions.csv")
    metrics_path = os.path.join("forecasting", "evaluation_metrics.json")

    daily_df = pd.read_csv(daily_path)
    hourly_df = pd.read_csv(hourly_path)
    preds_df = pd.read_csv(preds_path)
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    # 1. Dimension: Calendar Table
    dates = pd.to_datetime(daily_df["Date_ISO"])
    dim_calendar = pd.DataFrame({
        "Date": daily_df["Date_ISO"],
        "Year": dates.dt.year,
        "Quarter": "Q" + dates.dt.quarter.astype(str),
        "Month_Num": dates.dt.month,
        "Month_Name": dates.dt.month_name(),
        "Day": dates.dt.day,
        "Day_of_Week_Num": dates.dt.dayofweek, # 0=Mon, 6=Sun
        "Day_of_Week": dates.dt.day_name(),
        "Is_Weekend": dates.dt.dayofweek.isin([5, 6]).astype(int),
        "Day_Category": np.where(dates.dt.dayofweek.isin([5, 6]), "Weekend", "Weekday")
    })
    dim_calendar.to_csv(os.path.join(export_dir, "dim_calendar.csv"), index=False)
    print(f"  -> Generated dim_calendar.csv ({len(dim_calendar)} rows)")

    # 2. Fact: Daily Energy Consumption (with Configurable Tariff Estimation)
    # Standard European residential tariff estimate ~0.20 EUR / kWh
    TARIFF_EUR_PER_KWH = 0.20
    fact_daily = daily_df.copy()
    fact_daily["Estimated_Cost_EUR"] = fact_daily["Energy_kWh"] * TARIFF_EUR_PER_KWH
    
    # Statistical Anomaly Detection: Days > (Mean + 2 * Std) of energy consumption
    valid_mask = fact_daily["Is_valid_day"] == 1
    mean_e = fact_daily.loc[valid_mask, "Energy_kWh"].mean()
    std_e = fact_daily.loc[valid_mask, "Energy_kWh"].std()
    upper_threshold = mean_e + 2.0 * std_e
    fact_daily["Anomaly_Upper_Threshold_kWh"] = round(upper_threshold, 2)
    fact_daily["Is_Consumption_Anomaly"] = (
        (fact_daily["Is_valid_day"] == 1) & (fact_daily["Energy_kWh"] > upper_threshold)
    ).astype(int)

    fact_daily = fact_daily.rename(columns={"Date_ISO": "Date"})
    fact_daily.to_csv(os.path.join(export_dir, "fact_daily_energy.csv"), index=False)
    print(f"  -> Generated fact_daily_energy.csv ({len(fact_daily)} rows, {fact_daily['Is_Consumption_Anomaly'].sum()} anomaly days)")

    # 3. Fact: Hourly Energy Profile
    fact_hourly = hourly_df.rename(columns={"Date_ISO": "Date"}).copy()
    fact_hourly.to_csv(os.path.join(export_dir, "fact_hourly_energy.csv"), index=False)
    print(f"  -> Generated fact_hourly_energy.csv ({len(fact_hourly)} rows)")

    # 4. Fact: Forecast Comparison (Test Period)
    fact_forecast = preds_df.copy()
    fact_forecast["RF_Abs_Error"] = (fact_forecast["Actual_kWh"] - fact_forecast["RandomForest_Pred_kWh"]).abs()
    fact_forecast["RF_Sq_Error"] = (fact_forecast["Actual_kWh"] - fact_forecast["RandomForest_Pred_kWh"]) ** 2
    fact_forecast["LR_Abs_Error"] = (fact_forecast["Actual_kWh"] - fact_forecast["LinearRegression_Pred_kWh"]).abs()
    fact_forecast.to_csv(os.path.join(export_dir, "fact_forecast_comparison.csv"), index=False)
    print(f"  -> Generated fact_forecast_comparison.csv ({len(fact_forecast)} rows)")

    # 5. Dimension: Model Performance
    val_m = metrics_data["validation_metrics"]
    test_m = metrics_data["test_metrics"]
    models_summary = []
    for model_name in ["Naive_Baseline", "Linear_Regression", "Random_Forest"]:
        models_summary.append({
            "Model_Name": model_name.replace("_", " "),
            "Validation_MAE": val_m[model_name]["MAE"],
            "Validation_RMSE": val_m[model_name]["RMSE"],
            "Validation_R2": val_m[model_name]["R2"],
            "Test_MAE": test_m[model_name]["MAE"],
            "Test_RMSE": test_m[model_name]["RMSE"],
            "Test_R2": test_m[model_name]["R2"],
            "Test_MAPE_pct": test_m[model_name].get("MAPE_pct", 0.0),
            "Is_Selected_Best": 1 if model_name == metrics_data["selected_best_model"]["model_name"] else 0
        })
    dim_models = pd.DataFrame(models_summary)
    dim_models.to_csv(os.path.join(export_dir, "dim_model_performance.csv"), index=False)
    print(f"  -> Generated dim_model_performance.csv ({len(dim_models)} rows)")

    print("[+] All Power BI exports successfully generated!")

if __name__ == "__main__":
    generate_power_bi_exports()
