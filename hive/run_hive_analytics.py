#!/usr/bin/env python3
"""
Hive / Spark SQL Analytical Query Engine & Verification Harness
Smart Energy Consumption Analytics & Forecasting

Executes all 8 HiveQL queries specified in hive/queries.hql using Spark's
Hive-compatible SQL engine against real processed datasets:
1. Daily electricity consumption time-series
2. Monthly electricity consumption
3. Average hourly consumption diurnal profile
4. Peak consumption hours
5. Top 10 highest consumption dates
6. Weekday vs Weekend energy usage comparison
7. Seasonal monthly energy trends
8. Sub-metering end-use distribution and percentage breakdown

Saves tabular CSV exports and generates hive/hive_execution_report.md.
"""

import os
import sys
import pandas as pd

# Setup JVM & Hadoop environment for Windows if running locally
os.environ.setdefault("JAVA_HOME", r"C:\Users\PRAVEENRAJ\jdk-17\jdk-17.0.14+7")
os.environ.setdefault("HADOOP_HOME", r"C:\hadoop")
java_bin = os.path.join(os.environ["JAVA_HOME"], "bin")
hadoop_bin = os.path.join(os.environ["HADOOP_HOME"], "bin")
path_sep = ";" if os.name == "nt" else ":"
os.environ["PATH"] = f"{java_bin}{path_sep}{hadoop_bin}{path_sep}{os.environ.get('PATH', '')}"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

def init_spark_sql():
    print("[*] Initializing Hive-compatible SparkSession...")
    spark = SparkSession.builder \
        .appName("HiveAnalyticsEngine") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def run_queries():
    daily_csv = os.path.join("data", "processed", "daily_energy_consumption.csv")
    hourly_csv = os.path.join("data", "processed", "hourly_energy_consumption.csv")

    if not os.path.exists(daily_csv) or not os.path.exists(hourly_csv):
        raise FileNotFoundError("Processed datasets missing. Run preprocessing/clean_data.py first.")

    spark = init_spark_sql()
    results_dir = os.path.join("hive", "query_results")
    os.makedirs(results_dir, exist_ok=True)

    print(f"[*] Registering Daily and Hourly tables in Hive Metastore view...")
    # Load daily
    df_daily = spark.read.csv(daily_csv, header=True, inferSchema=True)
    df_daily.createOrReplaceTempView("daily_energy_consumption")

    # Load hourly
    df_hourly = spark.read.csv(hourly_csv, header=True, inferSchema=True)
    df_hourly.createOrReplaceTempView("hourly_energy_consumption")

    queries = {
        "q1_daily_consumption": {
            "title": "Query 1: Daily Electricity Consumption Time-Series",
            "sql": """
                SELECT 
                    Date_ISO AS consumption_date,
                    ROUND(Energy_kWh, 4) AS daily_energy_kwh,
                    Reading_count,
                    ROUND(Completeness_ratio * 100, 2) AS completeness_pct
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                ORDER BY consumption_date
            """
        },
        "q2_monthly_consumption": {
            "title": "Query 2: Monthly Electricity Consumption Aggregations",
            "sql": """
                SELECT 
                    Year AS year_num,
                    Month AS month_num,
                    Month_name AS month_name,
                    COUNT(*) AS valid_days_in_month,
                    ROUND(SUM(Energy_kWh), 2) AS total_monthly_kwh,
                    ROUND(AVG(Energy_kWh), 2) AS avg_daily_kwh,
                    ROUND(MAX(Energy_kWh), 2) AS max_daily_kwh
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Year, Month, Month_name
                ORDER BY Year, Month
            """
        },
        "q3_avg_hourly_consumption": {
            "title": "Query 3: Average Hourly Consumption Profile (Diurnal Cycle)",
            "sql": """
                SELECT 
                    Hour AS hour_of_day,
                    ROUND(AVG(Energy_kWh), 4) AS avg_hourly_energy_kwh,
                    ROUND(AVG(Avg_power_kW), 4) AS avg_power_kw,
                    ROUND(AVG(Avg_voltage_V), 2) AS avg_voltage_v
                FROM hourly_energy_consumption
                GROUP BY Hour
                ORDER BY Hour
            """
        },
        "q4_peak_consumption_hours": {
            "title": "Query 4: Peak Consumption Hours Identification (Top 5)",
            "sql": """
                SELECT 
                    Hour AS hour_of_day,
                    ROUND(AVG(Energy_kWh), 4) AS avg_hourly_energy_kwh,
                    ROUND(MAX(Energy_kWh), 4) AS peak_recorded_hourly_kwh,
                    ROUND(AVG(Avg_power_kW), 4) AS avg_power_demand_kw
                FROM hourly_energy_consumption
                GROUP BY Hour
                ORDER BY avg_hourly_energy_kwh DESC
                LIMIT 5
            """
        },
        "q5_top_consumption_dates": {
            "title": "Query 5: Top 10 Highest Consumption Dates (Historical Extremes)",
            "sql": """
                SELECT 
                    Date_ISO AS consumption_date,
                    Day_of_week,
                    Month_name,
                    Year,
                    ROUND(Energy_kWh, 2) AS total_energy_kwh,
                    ROUND(Max_power_kW, 2) AS peak_power_kw
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                ORDER BY total_energy_kwh DESC
                LIMIT 10
            """
        },
        "q6_weekday_vs_weekend": {
            "title": "Query 6: Weekday versus Weekend Energy Usage Comparison",
            "sql": """
                SELECT 
                    CASE WHEN Is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_category,
                    COUNT(*) AS total_days,
                    ROUND(AVG(Energy_kWh), 2) AS avg_daily_energy_kwh,
                    ROUND(MIN(Energy_kWh), 2) AS min_daily_energy_kwh,
                    ROUND(MAX(Energy_kWh), 2) AS max_daily_energy_kwh,
                    ROUND(STDDEV(Energy_kWh), 2) AS std_dev_energy_kwh
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Is_weekend
            """
        },
        "q7_seasonal_monthly_trends": {
            "title": "Query 7: Seasonal Monthly Energy Trends",
            "sql": """
                SELECT 
                    Month AS month_num,
                    Month_name,
                    ROUND(AVG(Energy_kWh), 2) AS seasonal_avg_daily_kwh,
                    ROUND(SUM(Energy_kWh), 2) AS cumulative_energy_kwh,
                    ROUND(AVG(Avg_voltage_V), 2) AS seasonal_avg_voltage
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
                GROUP BY Month, Month_name
                ORDER BY Month
            """
        },
        "q8_submetering_breakdown": {
            "title": "Query 8: Sub-Metering End-Use Distribution & Breakdown",
            "sql": """
                SELECT 
                    ROUND(SUM(Energy_kWh), 2) AS total_household_kwh,
                    ROUND(SUM(Sub_metering_1_kWh), 2) AS kitchen_kwh,
                    ROUND(SUM(Sub_metering_2_kWh), 2) AS laundry_kwh,
                    ROUND(SUM(Sub_metering_3_kWh), 2) AS climate_water_kwh,
                    ROUND(SUM(Sub_metering_remainder_kWh), 2) AS unmetered_remainder_kwh,
                    ROUND(SUM(Sub_metering_1_kWh) / SUM(Energy_kWh) * 100, 2) AS kitchen_pct,
                    ROUND(SUM(Sub_metering_2_kWh) / SUM(Energy_kWh) * 100, 2) AS laundry_pct,
                    ROUND(SUM(Sub_metering_3_kWh) / SUM(Energy_kWh) * 100, 2) AS climate_water_pct,
                    ROUND(SUM(Sub_metering_remainder_kWh) / SUM(Energy_kWh) * 100, 2) AS remainder_pct
                FROM daily_energy_consumption
                WHERE Is_valid_day = 1
            """
        }
    }

    report_md = ["# HiveQL Analytical Execution Report", "", "Generated using Apache Spark SQL engine running Hive-compatible SQL on genuine UCI Household Power Consumption records.", ""]

    print("[*] Executing all 8 analytical queries...")
    for q_id, q_info in queries.items():
        print(f"  -> Executing {q_info['title']}...")
        df_res = spark.sql(q_info["sql"])
        
        # Save CSV export for Power BI & verification
        csv_out = os.path.join(results_dir, f"{q_id}.csv")
        pdf = df_res.toPandas()
        pdf.to_csv(csv_out, index=False)

        # Append to report
        report_md.append(f"## {q_info['title']}")
        report_md.append("```sql")
        report_md.append(q_info["sql"].strip())
        report_md.append("```")
        report_md.append("")
        report_md.append(f"**Exported File:** `{csv_out}` ({len(pdf)} rows)")
        report_md.append("")
        report_md.append("### Query Output Preview:")
        report_md.append(pdf.head(10).to_markdown(index=False))
        report_md.append("")

    report_path = os.path.join("hive", "hive_execution_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_md))

    print(f"[+] All 8 queries executed successfully! Report saved to: {report_path}")

    # Step: Mathematical Verification of Selected Queries against Pandas
    print("[*] Validating query outputs against independent Pandas references...")
    df_p = pd.read_csv(daily_csv)
    df_p_valid = df_p[df_p["Is_valid_day"] == 1]
    
    # Verify Sub-metering total
    total_energy_ref = df_p_valid["Energy_kWh"].sum()
    q8_pdf = pd.read_csv(os.path.join(results_dir, "q8_submetering_breakdown.csv"))
    q8_total = q8_pdf["total_household_kwh"].iloc[0]
    diff_total = abs(total_energy_ref - q8_total)
    print(f"  Query 8 Total Energy: Hive/Spark={q8_total} vs Ref={total_energy_ref:.2f} (diff={diff_total:.4f} kWh)")
    assert diff_total < 0.1, "Query 8 total mismatch!"

    # Verify Weekday vs Weekend
    q6_pdf = pd.read_csv(os.path.join(results_dir, "q6_weekday_vs_weekend.csv"))
    weekend_days = int(q6_pdf.loc[q6_pdf["day_category"] == "Weekend", "total_days"].iloc[0])
    weekday_days = int(q6_pdf.loc[q6_pdf["day_category"] == "Weekday", "total_days"].iloc[0])
    ref_weekend = int(df_p_valid["Is_weekend"].sum())
    ref_weekday = len(df_p_valid) - ref_weekend
    print(f"  Query 6 Day Counts: Weekend={weekend_days} (Ref={ref_weekend}), Weekday={weekday_days} (Ref={ref_weekday})")
    assert weekend_days == ref_weekend and weekday_days == ref_weekday, "Day count mismatch!"

    print("[+] All verification checks PASSED successfully!")
    spark.stop()

if __name__ == "__main__":
    run_queries()
