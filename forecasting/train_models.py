#!/usr/bin/env python3
"""
Machine Learning Forecasting & Model Evaluation Module
Smart Energy Consumption Analytics & Forecasting

Trains and evaluates next-day energy forecasting models using Apache Spark MLlib:
1. Naive Persistence Baseline Model (y_hat = lag_1)
2. Spark MLlib Linear Regression (with regularization)
3. Spark MLlib Random Forest Regressor (ensemble regression)

Strict Chronological Partitioning (70% Train, 15% Validation, 15% Test) - Zero Shuffling.
Uses Spark MLlib RegressionEvaluator (RMSE, MAE, R2).
Saves actual vs predicted values to CSV and evaluation metrics to JSON.
"""

import os
import sys
import json
import numpy as np
import pandas as pd

# JVM & Hadoop setup for Windows
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
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

def train_and_evaluate():
    features_csv = os.path.join("data", "features", "daily_energy_features.csv")
    if not os.path.exists(features_csv):
        raise FileNotFoundError(f"Feature dataset not found at {features_csv}. Run spark_feature_pipeline.py first.")

    print(f"[*] Initializing Spark MLlib modeling pipeline...")
    spark = SparkSession.builder \
        .appName("SmartEnergyForecastingML") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Load dataset directly into Spark DataFrame
    df = spark.read.csv(features_csv, header=True, inferSchema=True)
    df = df.sort("Date_ISO")
    total_samples = df.count()
    print(f"[*] Total dataset records available for modeling: {total_samples}")

    # Chronological Split Boundaries:
    # 70% Train, 15% Validation, 15% Test
    # Determine exact cutoff dates from data
    all_dates = [row["Date_ISO"] for row in df.select("Date_ISO").collect()]
    n_train = int(total_samples * 0.70)
    n_val = int(total_samples * 0.15)
    
    val_start_date = all_dates[n_train]
    test_start_date = all_dates[n_train + n_val]
    
    print(f"[*] Chronological splits:")
    print(f"    - Train set:      {n_train} samples ({all_dates[0]} to {all_dates[n_train - 1]})")
    print(f"    - Validation set: {n_val} samples ({val_start_date} to {all_dates[n_train + n_val - 1]})")
    print(f"    - Test set:       {total_samples - n_train - n_val} samples ({test_start_date} to {all_dates[-1]})")

    train_df = df.filter(F.col("Date_ISO") < val_start_date)
    val_df = df.filter((F.col("Date_ISO") >= val_start_date) & (F.col("Date_ISO") < test_start_date))
    test_df = df.filter(F.col("Date_ISO") >= test_start_date)

    # Feature definitions
    feature_cols = [
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
        "Month"
    ]

    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    train_assembled = assembler.transform(train_df)
    val_assembled = assembler.transform(val_df)
    test_assembled = assembler.transform(test_df)

    eval_rmse = RegressionEvaluator(labelCol="Energy_kWh", predictionCol="prediction", metricName="rmse")
    eval_mae = RegressionEvaluator(labelCol="Energy_kWh", predictionCol="prediction", metricName="mae")
    eval_r2 = RegressionEvaluator(labelCol="Energy_kWh", predictionCol="prediction", metricName="r2")

    # Helper function for metrics
    def evaluate_predictions(preds_df, pred_col="prediction"):
        rmse = eval_rmse.setPredictionCol(pred_col).evaluate(preds_df)
        mae = eval_mae.setPredictionCol(pred_col).evaluate(preds_df)
        r2 = eval_r2.setPredictionCol(pred_col).evaluate(preds_df)
        return {
            "MAE": round(float(mae), 4),
            "RMSE": round(float(rmse), 4),
            "R2": round(float(r2), 4)
        }

    # 1. Baseline Model: Naive Persistence (Tomorrow = lag_1_energy_kwh)
    print("\n--- 1. Evaluating Naive Persistence Baseline Model ---")
    val_baseline_metrics = evaluate_predictions(val_assembled, pred_col="lag_1_energy_kwh")
    test_baseline_metrics = evaluate_predictions(test_assembled, pred_col="lag_1_energy_kwh")
    print(f"  Validation Metrics: {val_baseline_metrics}")
    print(f"  Test Metrics:       {test_baseline_metrics}")

    # 2. Spark MLlib Linear Regression
    print("\n--- 2. Training Spark MLlib Linear Regression Model ---")
    lr = LinearRegression(
        featuresCol="features",
        labelCol="Energy_kWh",
        maxIter=50,
        regParam=0.1,
        elasticNetParam=0.1
    )
    lr_model = lr.fit(train_assembled)
    val_lr_preds = lr_model.transform(val_assembled)
    test_lr_preds = lr_model.transform(test_assembled)

    val_lr_metrics = evaluate_predictions(val_lr_preds)
    test_lr_metrics = evaluate_predictions(test_lr_preds)
    print(f"  Validation Metrics: {val_lr_metrics}")
    print(f"  Test Metrics:       {test_lr_metrics}")

    # 3. Spark MLlib Random Forest Regressor
    print("\n--- 3. Training Spark MLlib Random Forest Regressor ---")
    rf = RandomForestRegressor(
        featuresCol="features",
        labelCol="Energy_kWh",
        numTrees=40,
        maxDepth=5,
        seed=42
    )
    rf_model = rf.fit(train_assembled)
    val_rf_preds = rf_model.transform(val_assembled)
    test_rf_preds = rf_model.transform(test_assembled)

    val_rf_metrics = evaluate_predictions(val_rf_preds)
    test_rf_metrics = evaluate_predictions(test_rf_preds)
    print(f"  Validation Metrics: {val_rf_metrics}")
    print(f"  Test Metrics:       {test_rf_metrics}")

    # Model selection based on validation RMSE
    models_val_rmse = {
        "Naive_Baseline": val_baseline_metrics["RMSE"],
        "Linear_Regression": val_lr_metrics["RMSE"],
        "Random_Forest": val_rf_metrics["RMSE"]
    }
    best_model_name = min(models_val_rmse, key=models_val_rmse.get)
    print(f"\n[+] Model Selection Result: Selected Best Model is '{best_model_name}' (Val RMSE = {models_val_rmse[best_model_name]})")

    # Combine test predictions for export
    print("[*] Consolidating test predictions...")
    test_lr_p = test_lr_preds.select("Date_ISO", "Energy_kWh", "lag_1_energy_kwh", F.col("prediction").alias("LinearRegression_Pred_kWh"))
    test_rf_p = test_rf_preds.select("Date_ISO", F.col("prediction").alias("RandomForest_Pred_kWh"))
    
    test_combined = test_lr_p.join(test_rf_p, on="Date_ISO").sort("Date_ISO")
    
    # Export predictions CSV
    preds_pdf = test_combined.toPandas()
    preds_pdf = preds_pdf.rename(columns={
        "Date_ISO": "Date",
        "Energy_kWh": "Actual_kWh",
        "lag_1_energy_kwh": "Baseline_Pred_kWh"
    })
    
    preds_out_path = os.path.join("forecasting", "test_predictions.csv")
    preds_pdf.to_csv(preds_out_path, index=False)
    print(f"[+] Test predictions saved to: {preds_out_path} ({len(preds_pdf)} rows)")

    # Compute MAPE on test set
    def get_mape(y_true, y_pred):
        mask = y_true > 0.5
        return round(float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100), 2)

    test_baseline_metrics["MAPE_pct"] = get_mape(preds_pdf["Actual_kWh"], preds_pdf["Baseline_Pred_kWh"])
    test_lr_metrics["MAPE_pct"] = get_mape(preds_pdf["Actual_kWh"], preds_pdf["LinearRegression_Pred_kWh"])
    test_rf_metrics["MAPE_pct"] = get_mape(preds_pdf["Actual_kWh"], preds_pdf["RandomForest_Pred_kWh"])

    # Export Evaluation Metrics JSON
    all_metrics = {
        "training_configuration": {
            "dataset_total_samples": total_samples,
            "train_samples": n_train,
            "validation_samples": n_val,
            "test_samples": total_samples - n_train - n_val,
            "split_ratios": "70% Train / 15% Validation / 15% Test",
            "splitting_method": "Chronological Sequential (No Shuffling)",
            "target_variable": "Energy_kWh (Next-day household electricity consumption in kWh)",
            "feature_count": len(feature_cols),
            "features_list": feature_cols
        },
        "validation_metrics": {
            "Naive_Baseline": val_baseline_metrics,
            "Linear_Regression": val_lr_metrics,
            "Random_Forest": val_rf_metrics
        },
        "test_metrics": {
            "Naive_Baseline": test_baseline_metrics,
            "Linear_Regression": test_lr_metrics,
            "Random_Forest": test_rf_metrics
        },
        "selected_best_model": {
            "model_name": best_model_name,
            "selection_criterion": "Lowest Validation RMSE",
            "test_mae": test_rf_metrics["MAE"] if best_model_name == "Random_Forest" else test_lr_metrics["MAE"],
            "test_rmse": test_rf_metrics["RMSE"] if best_model_name == "Random_Forest" else test_lr_metrics["RMSE"],
            "test_r2": test_rf_metrics["R2"] if best_model_name == "Random_Forest" else test_lr_metrics["R2"],
            "test_mape_pct": test_rf_metrics["MAPE_pct"] if best_model_name == "Random_Forest" else test_lr_metrics["MAPE_pct"]
        }
    }

    metrics_out_path = os.path.join("forecasting", "evaluation_metrics.json")
    with open(metrics_out_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=4)
    print(f"[+] Evaluation metrics saved to: {metrics_out_path}")

    spark.stop()
    return all_metrics

if __name__ == "__main__":
    train_and_evaluate()
