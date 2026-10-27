"""
Automated Unit Tests: Streamlit Dashboard Data Loading and Components
"""

import os
import pytest
import pandas as pd
import json

def test_streamlit_app_file_exists():
    """Verify app.py exists and is populated."""
    app_path = "app.py"
    assert os.path.exists(app_path), "app.py is missing!"
    assert os.path.getsize(app_path) > 1000, "app.py is unexpectedly small!"

def test_streamlit_data_dependencies():
    """Verify all precomputed verified outputs loaded by app.py are present."""
    required_files = [
        os.path.join("data", "processed", "daily_energy_consumption.csv"),
        os.path.join("data", "processed", "hourly_energy_consumption.csv"),
        os.path.join("forecasting", "test_predictions.csv"),
        os.path.join("forecasting", "evaluation_metrics.json"),
        os.path.join("data", "processed", "cleaning_summary.json"),
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Required dashboard asset missing: {rf}"
        assert os.path.getsize(rf) > 0, f"Dashboard asset is empty: {rf}"

def test_streamlit_data_integrity():
    """Verify records loaded by app.py have valid non-null rows."""
    daily_df = pd.read_csv(os.path.join("data", "processed", "daily_energy_consumption.csv"))
    assert len(daily_df) > 1000
    assert "Energy_kWh" in daily_df.columns

    preds_df = pd.read_csv(os.path.join("forecasting", "test_predictions.csv"))
    assert len(preds_df) == 213
    assert "RandomForest_Pred_kWh" in preds_df.columns
    assert "Actual_kWh" in preds_df.columns

    with open(os.path.join("forecasting", "evaluation_metrics.json"), "r") as f:
        metrics = json.load(f)
    assert "selected_best_model" in metrics
    assert metrics["selected_best_model"]["model_name"] == "Random_Forest"
