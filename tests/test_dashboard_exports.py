"""
Automated Unit Tests: Dashboard Exports, Star-Schema Integrity & Visualizations
"""

import os
import pytest
import pandas as pd

def test_power_bi_export_files_exist():
    """Verify all 5 required Power BI Star-Schema CSV exports exist."""
    base_dir = os.path.join("dashboard", "power_bi_exports")
    expected_files = [
        "dim_calendar.csv",
        "fact_daily_energy.csv",
        "fact_hourly_energy.csv",
        "fact_forecast_comparison.csv",
        "dim_model_performance.csv"
    ]
    for fname in expected_files:
        fpath = os.path.join(base_dir, fname)
        assert os.path.exists(fpath), f"Missing required Power BI export: {fpath}"
        assert os.path.getsize(fpath) > 50, f"Export file is empty: {fpath}"

def test_foreign_key_referential_integrity():
    """Verify referential integrity between fact tables and dim_calendar."""
    base_dir = os.path.join("dashboard", "power_bi_exports")
    cal_df = pd.read_csv(os.path.join(base_dir, "dim_calendar.csv"))
    daily_df = pd.read_csv(os.path.join(base_dir, "fact_daily_energy.csv"))

    cal_dates = set(cal_df["Date"])
    daily_dates = set(daily_df["Date"])

    unmatched = daily_dates - cal_dates
    assert len(unmatched) == 0, f"Foreign key violation: {len(unmatched)} dates not in dim_calendar!"

def test_anomaly_flag_column_validity():
    """Verify anomaly detection flags are binary (0 or 1) and positive count."""
    daily_path = os.path.join("dashboard", "power_bi_exports", "fact_daily_energy.csv")
    df = pd.read_csv(daily_path)
    assert "Is_Consumption_Anomaly" in df.columns
    unique_vals = set(df["Is_Consumption_Anomaly"].unique())
    assert unique_vals.issubset({0, 1}), f"Unexpected anomaly flag values: {unique_vals}"
    assert df["Is_Consumption_Anomaly"].sum() > 0, "No anomalies identified in dataset!"

def test_screenshot_visualizations_exist():
    """Verify all 4 academic publication plots were rendered and saved."""
    expected_screenshots = [
        "01_energy_overview.png",
        "02_consumption_analysis.png",
        "03_forecasting_results.png",
        "04_sustainability_insights.png"
    ]
    for sname in expected_screenshots:
        spath = os.path.join("screenshots", sname)
        assert os.path.exists(spath), f"Missing figure: {spath}"
        assert os.path.getsize(spath) > 50000, f"Figure file size too small: {spath}"
