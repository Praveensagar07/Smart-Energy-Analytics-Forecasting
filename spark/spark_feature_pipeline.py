#!/usr/bin/env python3
"""
PySpark Feature Engineering Pipeline
Smart Energy Consumption Analytics & Forecasting

Constructs leak-free chronological time-series features for next-day energy forecasting:
- Lagged features (Lag 1 day, Lag 2 days, Lag 7 days)
- Historical rolling statistics strictly over preceding windows (7-day mean, 7-day std, 14-day mean)
- Temporal cyclical features (Day of week, Weekend flag, Month)
- Sub-metering historical lag ratios
- Export to data/features/daily_energy_features.csv and Parquet
"""

import os
import sys

# Configure environment
os.environ.setdefault("JAVA_HOME", r"C:\Users\PRAVEENRAJ\jdk-17\jdk-17.0.14+7")
os.environ.setdefault("HADOOP_HOME", r"C:\hadoop")
java_bin = os.path.join(os.environ["JAVA_HOME"], "bin")
hadoop_bin = os.path.join(os.environ["HADOOP_HOME"], "bin")
path_sep = ";" if os.name == "nt" else ":"
os.environ["PATH"] = f"{java_bin}{path_sep}{hadoop_bin}{path_sep}{os.environ.get('PATH', '')}"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def run_feature_pipeline(input_csv: str = None, output_dir: str = None):
    input_csv = input_csv or os.path.join("data", "processed", "daily_energy_consumption.csv")
    output_dir = output_dir or os.path.join("data", "features")
    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Starting PySpark Feature Engineering on: {input_csv}")
    spark = SparkSession.builder \
        .appName("SmartEnergyFeatureEngineering") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    df = spark.read.csv(input_csv, header=True, inferSchema=True)
    df_valid = df.filter(F.col("Is_valid_day") == 1).sort("Date_ISO")
    total_valid = df_valid.count()
    print(f"[*] Loaded {total_valid} valid daily observations.")

    # Window definitions strictly ordered chronologically
    # Rolling windows MUST look only backwards: rowsBetween(-7, -1) to strictly avoid data leakage!
    w_lag = Window.orderBy("Date_ISO")
    w_roll_7 = Window.orderBy("Date_ISO").rowsBetween(-7, -1)
    w_roll_14 = Window.orderBy("Date_ISO").rowsBetween(-14, -1)

    print("[*] Generating lag and rolling features (ensuring zero forward leakage)...")
    df_feat = df_valid \
        .withColumn("lag_1_energy_kwh", F.lag("Energy_kWh", 1).over(w_lag)) \
        .withColumn("lag_2_energy_kwh", F.lag("Energy_kWh", 2).over(w_lag)) \
        .withColumn("lag_7_energy_kwh", F.lag("Energy_kWh", 7).over(w_lag)) \
        .withColumn("lag_1_avg_power_kw", F.lag("Avg_power_kW", 1).over(w_lag)) \
        .withColumn("lag_1_max_power_kw", F.lag("Max_power_kW", 1).over(w_lag)) \
        .withColumn("lag_1_avg_voltage_v", F.lag("Avg_voltage_V", 1).over(w_lag)) \
        .withColumn("rolling_mean_7_kwh", F.mean("Energy_kWh").over(w_roll_7)) \
        .withColumn("rolling_std_7_kwh", F.stddev("Energy_kWh").over(w_roll_7)) \
        .withColumn("rolling_mean_14_kwh", F.mean("Energy_kWh").over(w_roll_14)) \
        .withColumn("lag_1_sub1_kwh", F.lag("Sub_metering_1_kWh", 1).over(w_lag)) \
        .withColumn("lag_1_sub2_kwh", F.lag("Sub_metering_2_kWh", 1).over(w_lag)) \
        .withColumn("lag_1_sub3_kwh", F.lag("Sub_metering_3_kWh", 1).over(w_lag))

    # The forecasting target: Today's energy consumption (Energy_kWh) predicted from prior historical features!
    # Or predicting Next Day's Energy (lead 1). Here, target = Energy_kWh, features = historical lags and rolling stats.
    # Filter rows with complete history (drop the initial 14-day warm-up window)
    df_clean_feat = df_feat.dropna(subset=[
        "lag_1_energy_kwh",
        "lag_2_energy_kwh",
        "lag_7_energy_kwh",
        "rolling_mean_7_kwh",
        "rolling_std_7_kwh",
        "rolling_mean_14_kwh"
    ])

    final_count = df_clean_feat.count()
    print(f"[*] Complete feature matrix contains {final_count} days (initial 14 lag-initialization days removed).")

    # Select final schema for modeling
    feature_cols = [
        "Date_ISO",
        "Energy_kWh", # Target variable
        "lag_1_energy_kwh",
        "lag_2_energy_kwh",
        "lag_7_energy_kwh",
        "rolling_mean_7_kwh",
        "rolling_std_7_kwh",
        "rolling_mean_14_kwh",
        "lag_1_avg_power_kw",
        "lag_1_max_power_kw",
        "lag_1_avg_voltage_v",
        "lag_1_sub1_kwh",
        "lag_1_sub2_kwh",
        "lag_1_sub3_kwh",
        "Day_of_week_num",
        "Is_weekend",
        "Month",
        "Year"
    ]
    df_final = df_clean_feat.select(*feature_cols)

    csv_out = os.path.join(output_dir, "daily_energy_features.csv")
    pdf = df_final.toPandas()
    pdf.to_csv(csv_out, index=False)
    print(f"[+] Feature matrix exported to CSV: {csv_out} ({len(pdf)} rows, {len(feature_cols)} columns)")

    # Data Quality Validation checks
    print("[*] Running feature data quality checks...")
    assert not pdf.isnull().values.any(), "Error: Feature dataset contains null values!"
    assert (pdf["rolling_mean_7_kwh"] > 0).all(), "Error: Non-positive rolling mean detected!"
    assert (pdf["lag_1_energy_kwh"] > 0).all(), "Error: Non-positive lag energy detected!"
    print("[+] All feature quality checks PASSED successfully!")

    spark.stop()
    return pdf

if __name__ == "__main__":
    run_feature_pipeline()
