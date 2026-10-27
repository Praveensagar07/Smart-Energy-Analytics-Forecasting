#!/usr/bin/env python3
"""
Academic Visualization and Publication Plot Generator
Smart Energy Consumption Analytics & Forecasting

Generates 4 publication-quality visualization charts using actual processed data:
1. screenshots/01_energy_overview.png
2. screenshots/02_consumption_analysis.png
3. screenshots/03_forecasting_results.png
4. screenshots/04_sustainability_insights.png
"""

import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic visual styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

def generate_all_plots():
    os.makedirs("screenshots", exist_ok=True)
    daily_df = pd.read_csv(os.path.join("data", "processed", "daily_energy_consumption.csv"))
    hourly_df = pd.read_csv(os.path.join("data", "processed", "hourly_energy_consumption.csv"))
    test_df = pd.read_csv(os.path.join("forecasting", "test_predictions.csv"))
    with open(os.path.join("forecasting", "evaluation_metrics.json"), "r") as f:
        metrics = json.load(f)

    daily_valid = daily_df[daily_df["Is_valid_day"] == 1].copy()
    daily_valid["Date"] = pd.to_datetime(daily_valid["Date_ISO"])
    daily_valid = daily_valid.sort_values("Date")
    daily_valid["Rolling_30D"] = daily_valid["Energy_kWh"].rolling(30, min_periods=7).mean()

    # =========================================================================
    # PLOT 1: Energy Overview
    # =========================================================================
    print("[*] Generating screenshots/01_energy_overview.png...")
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1.0], hspace=0.3, wspace=0.25)

    # Subplot 1: Daily Trend & Rolling Average
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(daily_valid["Date"], daily_valid["Energy_kWh"], color="#90caf9", alpha=0.5, linewidth=0.8, label="Daily Energy (kWh)")
    ax1.plot(daily_valid["Date"], daily_valid["Rolling_30D"], color="#1565c0", linewidth=2.2, label="30-Day Moving Average")
    ax1.axhline(daily_valid["Energy_kWh"].mean(), color="#d32f2f", linestyle="--", linewidth=1.2, label=f"Mean: {daily_valid['Energy_kWh'].mean():.1f} kWh/day")
    ax1.set_title("Household Electricity Consumption Trend (2006 – 2010)", fontsize=14, fontweight="bold", pad=10)
    ax1.set_ylabel("Energy Consumption (kWh)", fontsize=11)
    ax1.set_xlabel("Date", fontsize=11)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Monthly Energy Totals
    ax2 = fig.add_subplot(gs[1, 0])
    monthly_agg = daily_valid.groupby(["Year", "Month"])["Energy_kWh"].sum().reset_index()
    monthly_agg["YearMonth"] = monthly_agg["Year"].astype(str) + "-" + monthly_agg["Month"].apply(lambda x: f"{x:02d}")
    bars = ax2.bar(range(len(monthly_agg)), monthly_agg["Energy_kWh"], color="#1e88e5", edgecolor="#0d47a1", alpha=0.85)
    ax2.set_title("Total Monthly Electricity Consumption (kWh)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Total Energy (kWh)", fontsize=10)
    ax2.set_xlabel("Year-Month", fontsize=10)
    # Label every 6th tick
    step = 6
    ax2.set_xticks(range(0, len(monthly_agg), step))
    ax2.set_xticklabels(monthly_agg["YearMonth"].iloc[::step], rotation=45, ha="right", fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    # Subplot 3: 24-Hour Diurnal Demand Curve
    ax3 = fig.add_subplot(gs[1, 1])
    diurnal = hourly_df.groupby("Hour")["Energy_kWh"].agg(["mean", "min", "max"]).reset_index()
    ax3.plot(diurnal["Hour"], diurnal["mean"], color="#e65100", linewidth=2.5, marker="o", label="Average Hourly (kWh)")
    ax3.fill_between(diurnal["Hour"], diurnal["min"], diurnal["max"], color="#ffe0b2", alpha=0.5, label="Min-Max Range")
    ax3.set_title("24-Hour Diurnal Electricity Demand Profile", fontsize=12, fontweight="bold")
    ax3.set_ylabel("Hourly Energy (kWh)", fontsize=10)
    ax3.set_xlabel("Hour of Day (0–23)", fontsize=10)
    ax3.set_xticks(range(0, 24, 2))
    ax3.legend(loc="upper left", frameon=True)
    ax3.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Smart Energy Consumption Analytics — Overview Dashboard", fontsize=16, fontweight="bold", y=0.98)
    fig.savefig(os.path.join("screenshots", "01_energy_overview.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # PLOT 2: Consumption Analysis
    # =========================================================================
    print("[*] Generating screenshots/02_consumption_analysis.png...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Subplot 1: Weekday vs Weekend Comparison
    sns.boxplot(
        data=daily_valid,
        x="Is_weekend",
        y="Energy_kWh",
        ax=axes[0],
        palette=["#42a5f5", "#ab47bc"],
        boxprops=dict(alpha=0.8)
    )
    axes[0].set_xticklabels(["Weekday (Mon–Fri)", "Weekend (Sat–Sun)"])
    axes[0].set_title("Weekday vs. Weekend Consumption Distribution", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Daily Energy (kWh)", fontsize=10)
    axes[0].set_xlabel("")
    axes[0].grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Sub-metering Pie Chart
    sub1 = daily_valid["Sub_metering_1_kWh"].sum()
    sub2 = daily_valid["Sub_metering_2_kWh"].sum()
    sub3 = daily_valid["Sub_metering_3_kWh"].sum()
    sub_rem = daily_valid["Sub_metering_remainder_kWh"].sum()
    labels = ["Kitchen (Sub 1)", "Laundry (Sub 2)", "Climate/Water (Sub 3)", "Unmetered Remainder"]
    sizes = [sub1, sub2, sub3, sub_rem]
    colors = ["#ff7043", "#26a69a", "#5c6bc0", "#b0bec5"]
    explode = (0.05, 0.05, 0.05, 0)
    axes[1].pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        explode=explode,
        wedgeprops=dict(edgecolor="w", linewidth=1.5)
    )
    axes[1].set_title("Sub-Metering End-Use Distribution", fontsize=12, fontweight="bold")

    # Subplot 3: Day of Week Hourly Profiles
    hourly_df["Datetime_hour"] = pd.to_datetime(hourly_df["Datetime_hour"])
    hourly_df["Day_of_week"] = hourly_df["Datetime_hour"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_hourly = hourly_df.groupby(["Day_of_week", "Hour"])["Energy_kWh"].mean().reset_index()
    for dow in day_order:
        subset = dow_hourly[dow_hourly["Day_of_week"] == dow]
        is_wknd = dow in ["Saturday", "Sunday"]
        axes[2].plot(
            subset["Hour"],
            subset["Energy_kWh"],
            label=dow,
            linewidth=2.2 if is_wknd else 1.2,
            linestyle="--" if is_wknd else "-"
        )
    axes[2].set_title("Diurnal Demand Curves by Day of Week", fontsize=12, fontweight="bold")
    axes[2].set_ylabel("Average Hourly Energy (kWh)", fontsize=10)
    axes[2].set_xlabel("Hour of Day (0–23)", fontsize=10)
    axes[2].set_xticks(range(0, 24, 3))
    axes[2].legend(loc="upper left", fontsize=8, frameon=True)
    axes[2].grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Smart Energy Consumption Analytics — Deep-Dive Consumption Patterns", fontsize=16, fontweight="bold", y=1.03)
    fig.tight_layout()
    fig.savefig(os.path.join("screenshots", "02_consumption_analysis.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # PLOT 3: Forecasting Results
    # =========================================================================
    print("[*] Generating screenshots/03_forecasting_results.png...")
    fig, axes = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={"height_ratios": [1.4, 1.0], "hspace": 0.3})

    test_dates = pd.to_datetime(test_df["Date"])
    axes[0].plot(test_dates, test_df["Actual_kWh"], color="#212121", linewidth=2.0, label="Actual Consumption (kWh)")
    axes[0].plot(test_dates, test_df["RandomForest_Pred_kWh"], color="#2e7d32", linewidth=1.8, linestyle="-", label="Random Forest MLlib Pred")
    axes[0].plot(test_dates, test_df["LinearRegression_Pred_kWh"], color="#1565c0", linewidth=1.5, linestyle="--", label="Linear Regression Pred")
    axes[0].plot(test_dates, test_df["Baseline_Pred_kWh"], color="#e65100", linewidth=1.0, linestyle=":", alpha=0.7, label="Naive Baseline (Lag-1)")
    axes[0].set_title("Next-Day Household Energy Forecasting on Untouched Test Set (2010)", fontsize=13, fontweight="bold")
    axes[0].set_ylabel("Daily Energy (kWh)", fontsize=11)
    axes[0].set_xlabel("Test Date", fontsize=11)
    axes[0].legend(loc="upper right", frameon=True)
    axes[0].grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Comparative Bar Chart of Evaluation Metrics
    m_df = pd.DataFrame({
        "Model": ["Naive Baseline", "Linear Regression", "Random Forest"],
        "MAE": [metrics["test_metrics"]["Naive_Baseline"]["MAE"], metrics["test_metrics"]["Linear_Regression"]["MAE"], metrics["test_metrics"]["Random_Forest"]["MAE"]],
        "RMSE": [metrics["test_metrics"]["Naive_Baseline"]["RMSE"], metrics["test_metrics"]["Linear_Regression"]["RMSE"], metrics["test_metrics"]["Random_Forest"]["RMSE"]],
        "R2": [metrics["test_metrics"]["Naive_Baseline"]["R2"], metrics["test_metrics"]["Linear_Regression"]["R2"], metrics["test_metrics"]["Random_Forest"]["R2"]]
    })

    x = np.arange(len(m_df))
    width = 0.25
    rects1 = axes[1].bar(x - width, m_df["MAE"], width, label="MAE (kWh)", color="#42a5f5")
    rects2 = axes[1].bar(x, m_df["RMSE"], width, label="RMSE (kWh)", color="#ef5350")
    rects3 = axes[1].bar(x + width, m_df["R2"], width, label="R² Score", color="#66bb6a")

    axes[1].set_title("Test Set Model Evaluation Metrics Comparison (Spark MLlib)", fontsize=12, fontweight="bold")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(m_df["Model"], fontsize=11, fontweight="bold")
    axes[1].legend(loc="upper right", frameon=True)
    axes[1].set_ylabel("Metric Value", fontsize=10)
    axes[1].grid(True, linestyle=":", alpha=0.6)

    # Add data labels
    for rect in [rects1, rects2, rects3]:
        for bar in rect:
            yval = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width() / 2.0, yval + 0.08, f"{yval:.2f}", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Machine Learning Forecasting Performance & Model Comparison", fontsize=16, fontweight="bold", y=0.98)
    fig.savefig(os.path.join("screenshots", "03_forecasting_results.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # PLOT 4: Sustainability & SDG 7 Insights
    # =========================================================================
    print("[*] Generating screenshots/04_sustainability_insights.png...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Anomaly Detection Scatter Plot
    mean_val = daily_valid["Energy_kWh"].mean()
    std_val = daily_valid["Energy_kWh"].std()
    upper_thresh = mean_val + 2 * std_val

    is_anomaly = daily_valid["Energy_kWh"] > upper_thresh
    axes[0].scatter(daily_valid.loc[~is_anomaly, "Date"], daily_valid.loc[~is_anomaly, "Energy_kWh"], color="#4fc3f7", alpha=0.6, s=16, label="Normal Operation")
    axes[0].scatter(daily_valid.loc[is_anomaly, "Date"], daily_valid.loc[is_anomaly, "Energy_kWh"], color="#d32f2f", alpha=0.9, s=36, edgecolor="black", label=f"Anomaly (> Mean+2σ = {upper_thresh:.1f} kWh)")
    axes[0].axhline(upper_thresh, color="#b71c1c", linestyle="--", linewidth=1.2)
    axes[0].axhline(mean_val, color="#37474f", linestyle=":", linewidth=1.0, label=f"Mean: {mean_val:.1f} kWh")
    axes[0].set_title("Statistical Consumption Anomaly Detection (SDG 7 Waste Identification)", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Daily Energy (kWh)", fontsize=10)
    axes[0].set_xlabel("Date", fontsize=10)
    axes[0].legend(loc="upper right", frameon=True)
    axes[0].grid(True, linestyle=":", alpha=0.6)

    # Load-shifting / Peak Shaving Opportunity Window
    hourly_avg = hourly_df.groupby("Hour")["Avg_power_kW"].mean()
    colors_hourly = ["#81c784" if h in [1, 2, 3, 4, 5] else ("#e57373" if h in [18, 19, 20, 21] else "#90caf9") for h in range(24)]
    axes[1].bar(range(24), hourly_avg, color=colors_hourly, edgecolor="#424242", alpha=0.85)
    axes[1].set_title("SDG 7 Actionable Insight: Peak Shaving & Load Shifting Opportunity", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Hour of Day (0–23)", fontsize=10)
    axes[1].set_ylabel("Average Power Demand (kW)", fontsize=10)
    axes[1].set_xticks(range(0, 24, 2))
    axes[1].text(2.5, 0.45, "Optimal Low-Cost Window\n(Off-Peak: 01:00-05:00)", ha="center", fontsize=9, color="#1b5e20", fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#81c784"))
    axes[1].text(19.5, 2.1, "High Grid Stress\n(Peak: 18:00-21:00)", ha="center", fontsize=9, color="#b71c1c", fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#e57373"))
    axes[1].grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Sustainability Insights & Energy Optimization Aligned with SDG 7", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join("screenshots", "04_sustainability_insights.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("[+] All 4 publication figures generated successfully in screenshots/!")

if __name__ == "__main__":
    generate_all_plots()
