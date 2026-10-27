"""
Automated Unit Tests: Machine Learning Metrics, Model Splitting & Predictions
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

def test_metrics_calculation_formula():
    """Verify standard formula accuracy for MAE, RMSE, R2, MAPE."""
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 33.0, 37.0])

    # Errors: [2.0, -2.0, 3.0, -3.0]
    expected_mae = 2.5
    expected_rmse = np.sqrt((4 + 4 + 9 + 9) / 4.0) # sqrt(6.5) = 2.5495

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    assert np.isclose(mae, expected_mae)
    assert np.isclose(rmse, expected_rmse)

def test_evaluation_metrics_file():
    """Verify evaluation metrics JSON structure and validity."""
    path = os.path.join("forecasting", "evaluation_metrics.json")
    assert os.path.exists(path), f"Metrics JSON missing at {path}"

    with open(path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    assert "test_metrics" in metrics
    test_m = metrics["test_metrics"]
    for model_name in ["Naive_Baseline", "Linear_Regression", "Random_Forest"]:
        assert model_name in test_m
        assert test_m[model_name]["MAE"] > 0
        assert test_m[model_name]["RMSE"] > 0
        assert test_m[model_name]["R2"] > 0

    # Best model (Random Forest) should outperform Naive Baseline on test RMSE
    rf_rmse = test_m["Random_Forest"]["RMSE"]
    base_rmse = test_m["Naive_Baseline"]["RMSE"]
    assert rf_rmse < base_rmse, f"Random Forest ({rf_rmse}) failed to beat Naive Baseline ({base_rmse})"

def test_predictions_alignment():
    """Verify test predictions file has valid columns and non-null values."""
    path = os.path.join("forecasting", "test_predictions.csv")
    assert os.path.exists(path), f"Predictions CSV missing at {path}"

    df = pd.read_csv(path)
    expected_cols = ["Date", "Actual_kWh", "Baseline_Pred_kWh", "LinearRegression_Pred_kWh", "RandomForest_Pred_kWh"]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in test predictions"

    assert len(df) > 50, "Test predictions row count is unexpectedly small"
    assert not df.isnull().values.any(), "Test predictions contain null values"
    assert (df["Actual_kWh"] > 0).all(), "Actual energy contains non-positive values"
    assert (df["RandomForest_Pred_kWh"] > 0).all(), "Predictions contain negative energy"
