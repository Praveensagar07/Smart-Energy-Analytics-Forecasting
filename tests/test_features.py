"""
Automated Unit Tests: Feature Engineering & Data Leakage Prevention
"""

import os
import pytest
import numpy as np
import pandas as pd

def test_features_file_exists():
    """Verify generated feature dataset exists."""
    path = os.path.join("data", "features", "daily_energy_features.csv")
    assert os.path.exists(path), f"Features CSV missing at {path}"

def test_feature_data_leakage_prevention():
    """Verify lag and rolling features do not contain current or future information."""
    path = os.path.join("data", "features", "daily_energy_features.csv")
    df = pd.read_csv(path)

    # Check lag 1 alignment: lag_1_energy_kwh at index i MUST equal Energy_kWh at index i-1
    for i in range(1, min(50, len(df))):
        expected_lag1 = df.loc[i - 1, "Energy_kWh"]
        actual_lag1 = df.loc[i, "lag_1_energy_kwh"]
        assert np.isclose(expected_lag1, actual_lag1, atol=1e-4), (
            f"Leakage detected! Row {i} lag_1={actual_lag1} does not match row {i-1} actual={expected_lag1}"
        )

def test_rolling_mean_no_future_leakage():
    """Verify rolling mean is calculated strictly over preceding historical window."""
    path = os.path.join("data", "features", "daily_energy_features.csv")
    df = pd.read_csv(path)

    # In our Spark feature pipeline, rolling_mean_7_kwh is computed over rowsBetween(-7, -1)
    # So for row i, rolling_mean should equal the mean of rows [i-7 ... i-1]
    for i in range(10, min(30, len(df))):
        preceding_7 = df.loc[i-7:i-1, "Energy_kWh"]
        expected_mean = preceding_7.mean()
        actual_mean = df.loc[i, "rolling_mean_7_kwh"]
        assert np.isclose(expected_mean, actual_mean, atol=1e-3), (
            f"Rolling mean mismatch at row {i}: expected {expected_mean}, got {actual_mean}"
        )

def test_no_null_values_in_features():
    """Verify feature dataset has no NaN or Null values."""
    path = os.path.join("data", "features", "daily_energy_features.csv")
    df = pd.read_csv(path)
    assert not df.isnull().values.any(), "Feature dataset contains unexpected nulls!"

def test_chronological_ordering():
    """Verify feature dataset is monotonically sorted by date."""
    path = os.path.join("data", "features", "daily_energy_features.csv")
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Date_ISO"])
    assert dates.is_monotonic_increasing, "Feature dataset dates are not chronologically sorted!"
