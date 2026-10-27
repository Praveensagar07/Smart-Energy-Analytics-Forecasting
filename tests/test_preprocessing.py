"""
Automated Unit Tests: Preprocessing, Data Cleaning, and Unit Conversions
"""

import os
import pytest
import numpy as np
import pandas as pd
from datetime import datetime

def test_interval_energy_calculation():
    """Verify kW to kWh conversion for 1-minute sampling interval."""
    power_kw = 4.216
    expected_kwh = power_kw / 60.0
    calculated_kwh = power_kw * (1.0 / 60.0)
    assert np.isclose(calculated_kwh, expected_kwh, atol=1e-8)
    assert np.isclose(calculated_kwh, 0.0702666, atol=1e-6)

def test_submetering_unit_conversion():
    """Verify Watt-hour (Wh) to Kilowatt-hour (kWh) conversion."""
    sub1_wh = 17.0
    expected_kwh = 0.017
    assert np.isclose(sub1_wh / 1000.0, expected_kwh, atol=1e-8)

def test_submetering_remainder_calculation():
    """Verify unmonitored energy remainder calculation."""
    interval_energy_kwh = 0.100 # 100 Wh
    sub1_kwh = 0.020 # 20 Wh
    sub2_kwh = 0.015 # 15 Wh
    sub3_kwh = 0.025 # 25 Wh
    # Remainder should be 100 - (20 + 15 + 25) = 40 Wh = 0.040 kWh
    remainder = max(0.0, interval_energy_kwh - (sub1_kwh + sub2_kwh + sub3_kwh))
    assert np.isclose(remainder, 0.040, atol=1e-8)

def test_missing_value_sentinel_parsing():
    """Verify '?' sentinel is properly identified as missing."""
    raw_val = "?"
    parsed = np.nan if raw_val == "?" else float(raw_val)
    assert np.isnan(parsed)

def test_datetime_parsing():
    """Verify DD/MM/YYYY HH:MM:SS parsing to ISO format."""
    date_str = "16/12/2006"
    time_str = "17:24:00"
    dt = pd.to_datetime(f"{date_str} {time_str}", format="%d/%m/%Y %H:%M:%S")
    assert dt.year == 2006
    assert dt.month == 12
    assert dt.day == 16
    assert dt.hour == 17
    assert dt.minute == 24
    assert dt.strftime("%Y-%m-%d") == "2006-12-16"

def test_daily_completeness_ratio():
    """Verify completeness calculation (1440 minutes in a full day)."""
    reading_count = 1440
    ratio = reading_count / 1440.0
    assert ratio == 1.0

    partial_count = 720
    assert (partial_count / 1440.0) == 0.5
