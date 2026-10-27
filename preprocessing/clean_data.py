"""
Data Cleaning and Preprocessing Pipeline
Smart Energy Consumption Analytics & Forecasting

Processes raw UCI Household Power Consumption dataset:
- Ingestion with missing-value handling ('?')
- Temporal datetime parsing and chronological ordering
- Unit conversions: kW to kWh (power * 1/60), Wh to kWh (/1000)
- Hourly and daily consumption aggregation
- Data quality, completeness tracking, and summary reporting
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Clean and aggregate household power consumption dataset.")
    parser.add_argument(
        "--input-file",
        type=str,
        default=os.path.join("data", "raw", "household_power_consumption.txt"),
        help="Path to raw dataset file."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join("data", "processed"),
        help="Directory to save cleaned and aggregated outputs."
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=250000,
        help="Chunk size for memory-conscious streaming ingestion."
    )
    return parser.parse_args()

def clean_and_process(input_path: str, output_dir: str, chunksize: int = 250000):
    if not os.path.exists(input_path):
        sample_path = os.path.join("data", "raw", "sample_household_power_consumption.txt")
        if os.path.exists(sample_path):
            print(f"[WARN] Main file {input_path} not found. Falling back to sample file {sample_path}")
            input_path = sample_path
        else:
            raise FileNotFoundError(f"Input file not found at {input_path} or {sample_path}")

    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Commencing data processing on: {input_path}")
    print(f"[*] Memory-conscious processing chunk size: {chunksize}")

    numeric_cols = [
        "Global_active_power",
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]

    total_records = 0
    missing_records = 0
    hourly_records_list = []
    daily_records_list = []

    # Stream through dataset in chunks to respect 8GB RAM constraints
    chunk_index = 0
    for chunk in pd.read_csv(
        input_path,
        sep=";",
        na_values=["?", ""],
        dtype={col: "float32" for col in numeric_cols},
        chunksize=chunksize,
        low_memory=False
    ):
        chunk_index += 1
        total_records += len(chunk)
        
        # Count missing active power
        chunk_missing = chunk["Global_active_power"].isna().sum()
        missing_records += int(chunk_missing)
        
        # Filter valid readings for power
        valid_chunk = chunk.dropna(subset=["Global_active_power"]).copy()
        if len(valid_chunk) == 0:
            continue

        # Datetime construction
        valid_chunk["Datetime"] = pd.to_datetime(
            valid_chunk["Date"] + " " + valid_chunk["Time"],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce"
        )
        valid_chunk = valid_chunk.dropna(subset=["Datetime"])
        
        # Unit Conversions
        # 1-minute interval energy in kWh: kW * (1/60 hr)
        valid_chunk["Energy_kWh"] = valid_chunk["Global_active_power"] / 60.0
        
        # Sub-metering in kWh: Wh / 1000
        valid_chunk["Sub_metering_1_kWh"] = valid_chunk["Sub_metering_1"] / 1000.0
        valid_chunk["Sub_metering_2_kWh"] = valid_chunk["Sub_metering_2"] / 1000.0
        valid_chunk["Sub_metering_3_kWh"] = valid_chunk["Sub_metering_3"] / 1000.0
        
        # Remainder energy (active energy not metered by sub-meters 1, 2, 3)
        metered_sum = (
            valid_chunk["Sub_metering_1_kWh"] + 
            valid_chunk["Sub_metering_2_kWh"] + 
            valid_chunk["Sub_metering_3_kWh"]
        )
        valid_chunk["Sub_metering_remainder_kWh"] = (valid_chunk["Energy_kWh"] - metered_sum).clip(lower=0.0)

        # Temporal dimensions
        valid_chunk["Date_ISO"] = valid_chunk["Datetime"].dt.strftime("%Y-%m-%d")
        valid_chunk["Hour"] = valid_chunk["Datetime"].dt.hour

        # Hourly pre-aggregation for this chunk
        chunk_hourly = valid_chunk.groupby(["Date_ISO", "Hour"]).agg(
            Energy_kWh=("Energy_kWh", "sum"),
            Sub_metering_1_kWh=("Sub_metering_1_kWh", "sum"),
            Sub_metering_2_kWh=("Sub_metering_2_kWh", "sum"),
            Sub_metering_3_kWh=("Sub_metering_3_kWh", "sum"),
            Sub_metering_remainder_kWh=("Sub_metering_remainder_kWh", "sum"),
            Avg_power_kW=("Global_active_power", "mean"),
            Avg_voltage_V=("Voltage", "mean"),
            Reading_count=("Energy_kWh", "count")
        ).reset_index()
        hourly_records_list.append(chunk_hourly)

        # Daily pre-aggregation for this chunk
        chunk_daily = valid_chunk.groupby("Date_ISO").agg(
            Energy_kWh=("Energy_kWh", "sum"),
            Sub_metering_1_kWh=("Sub_metering_1_kWh", "sum"),
            Sub_metering_2_kWh=("Sub_metering_2_kWh", "sum"),
            Sub_metering_3_kWh=("Sub_metering_3_kWh", "sum"),
            Sub_metering_remainder_kWh=("Sub_metering_remainder_kWh", "sum"),
            Avg_power_kW=("Global_active_power", "mean"),
            Max_power_kW=("Global_active_power", "max"),
            Min_power_kW=("Global_active_power", "min"),
            Avg_voltage_V=("Voltage", "mean"),
            Reading_count=("Energy_kWh", "count")
        ).reset_index()
        daily_records_list.append(chunk_daily)

        print(f"  Processed chunk {chunk_index} ({total_records:,} records inspected)")

    print("[*] Consolidating and sorting aggregated tables...")

    # Merge Hourly tables across chunks
    all_hourly = pd.concat(hourly_records_list, ignore_index=True)
    hourly_df = all_hourly.groupby(["Date_ISO", "Hour"]).agg(
        Energy_kWh=("Energy_kWh", "sum"),
        Sub_metering_1_kWh=("Sub_metering_1_kWh", "sum"),
        Sub_metering_2_kWh=("Sub_metering_2_kWh", "sum"),
        Sub_metering_3_kWh=("Sub_metering_3_kWh", "sum"),
        Sub_metering_remainder_kWh=("Sub_metering_remainder_kWh", "sum"),
        Avg_power_kW=("Avg_power_kW", "mean"),
        Avg_voltage_V=("Avg_voltage_V", "mean"),
        Reading_count=("Reading_count", "sum")
    ).reset_index()
    hourly_df["Datetime_hour"] = pd.to_datetime(hourly_df["Date_ISO"] + " " + hourly_df["Hour"].astype(str) + ":00:00")
    hourly_df = hourly_df.sort_values("Datetime_hour").reset_index(drop=True)

    # Merge Daily tables across chunks
    all_daily = pd.concat(daily_records_list, ignore_index=True)
    daily_df = all_daily.groupby("Date_ISO").agg(
        Energy_kWh=("Energy_kWh", "sum"),
        Sub_metering_1_kWh=("Sub_metering_1_kWh", "sum"),
        Sub_metering_2_kWh=("Sub_metering_2_kWh", "sum"),
        Sub_metering_3_kWh=("Sub_metering_3_kWh", "sum"),
        Sub_metering_remainder_kWh=("Sub_metering_remainder_kWh", "sum"),
        Avg_power_kW=("Avg_power_kW", "mean"),
        Max_power_kW=("Max_power_kW", "max"),
        Min_power_kW=("Min_power_kW", "min"),
        Avg_voltage_V=("Avg_voltage_V", "mean"),
        Reading_count=("Reading_count", "sum")
    ).reset_index()

    daily_df["Date"] = pd.to_datetime(daily_df["Date_ISO"])
    daily_df = daily_df.sort_values("Date").reset_index(drop=True)

    # 1440 minutes in a full day
    daily_df["Completeness_ratio"] = daily_df["Reading_count"] / 1440.0
    daily_df["Is_valid_day"] = (daily_df["Completeness_ratio"] >= 0.85).astype(int)

    # Add Calendar Features
    daily_df["Day_of_week"] = daily_df["Date"].dt.day_name()
    daily_df["Day_of_week_num"] = daily_df["Date"].dt.dayofweek # 0=Mon, 6=Sun
    daily_df["Is_weekend"] = daily_df["Day_of_week_num"].isin([5, 6]).astype(int)
    daily_df["Month"] = daily_df["Date"].dt.month
    daily_df["Month_name"] = daily_df["Date"].dt.month_name()
    daily_df["Year"] = daily_df["Date"].dt.year

    # Export cleaned outputs
    hourly_out_path = os.path.join(output_dir, "hourly_energy_consumption.csv")
    daily_out_path = os.path.join(output_dir, "daily_energy_consumption.csv")
    summary_out_path = os.path.join(output_dir, "cleaning_summary.json")

    print(f"[*] Saving hourly aggregated data to {hourly_out_path} ({len(hourly_df):,} rows)...")
    hourly_df.to_csv(hourly_out_path, index=False)

    print(f"[*] Saving daily aggregated data to {daily_out_path} ({len(daily_df):,} rows)...")
    daily_df.to_csv(daily_out_path, index=False)

    valid_days = int(daily_df["Is_valid_day"].sum())
    total_days = len(daily_df)
    total_energy_kwh = float(daily_df["Energy_kWh"].sum())
    avg_daily_energy_kwh = float(daily_df.loc[daily_df["Is_valid_day"] == 1, "Energy_kWh"].mean())

    summary_stats = {
        "dataset_name": "UCI Individual Household Electric Power Consumption",
        "input_file": input_path,
        "processed_timestamp": datetime.now().isoformat(),
        "total_raw_records": total_records,
        "missing_power_records": missing_records,
        "valid_power_records": total_records - missing_records,
        "missing_percentage": round((missing_records / total_records) * 100, 4) if total_records > 0 else 0,
        "total_calendar_days": total_days,
        "valid_calendar_days": valid_days,
        "incomplete_calendar_days": total_days - valid_days,
        "total_energy_kwh": round(total_energy_kwh, 2),
        "mean_daily_energy_kwh": round(avg_daily_energy_kwh, 2),
        "max_daily_energy_kwh": round(float(daily_df["Energy_kWh"].max()), 2),
        "min_daily_energy_kwh": round(float(daily_df.loc[daily_df["Is_valid_day"] == 1, "Energy_kWh"].min()), 2),
        "date_start": daily_df["Date_ISO"].iloc[0] if len(daily_df) > 0 else None,
        "date_end": daily_df["Date_ISO"].iloc[-1] if len(daily_df) > 0 else None,
    }

    with open(summary_out_path, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=4)

    print("[+] Preprocessing successfully completed!")
    print(f"    - Total records: {total_records:,}")
    print(f"    - Missing records: {missing_records:,} ({summary_stats['missing_percentage']}%)")
    print(f"    - Daily span: {summary_stats['date_start']} to {summary_stats['date_end']} ({total_days} days)")
    print(f"    - Valid days (completeness >= 85%): {valid_days}")
    print(f"    - Total Energy Recorded: {total_energy_kwh:,.2f} kWh")
    print(f"    - Mean Daily Energy: {avg_daily_energy_kwh:.2f} kWh/day")

    return summary_stats

if __name__ == "__main__":
    args = parse_args()
    clean_and_process(args.input_file, args.output_dir, args.chunksize)
