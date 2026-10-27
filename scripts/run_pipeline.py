#!/usr/bin/env python3
"""
Master Pipeline Orchestration Script
Smart Energy Consumption Analytics & Forecasting

Sequentially executes the end-to-end Big Data & Analytics pipeline:
1. Ingestion & Preprocessing (data/raw -> data/processed)
2. Hadoop MapReduce Execution & Mathematical Validation
3. HiveQL Analytical Query Execution (8 queries)
4. PySpark Feature Engineering (data/features)
5. Machine Learning Forecasting Models (Spark MLlib)
6. Power BI Star-Schema Export Generation
7. Publication Figure Rendering (screenshots/)
8. Automated Unit Test Verification (pytest)
"""

import os
import sys
import time
import subprocess

def run_step(step_num: int, title: str, cmd_args: list):
    print(f"\n{'='*75}")
    print(f"STEP {step_num}: {title.upper()}")
    print(f"{'='*75}")
    start = time.time()
    
    result = subprocess.run([sys.executable] + cmd_args, check=False)
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"[-] Step {step_num} FAILED in {elapsed:.2f}s with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"[+] Step {step_num} COMPLETED SUCCESSFULLY in {elapsed:.2f}s")

def main():
    print("===========================================================================")
    print("SMART ENERGY CONSUMPTION ANALYTICS & FORECASTING")
    print("Batch 13 | Academic Mini Project Pipeline Runner")
    print("Praveen Sagar.M (814724104117) & Naveen.S (814724104104)")
    print("===========================================================================")

    t0 = time.time()

    # Step 1: Preprocessing
    run_step(1, "Data Cleaning and Preprocessing", ["preprocessing/clean_data.py"])

    # Step 2: MapReduce
    run_step(2, "Hadoop MapReduce Daily Energy Aggregation & Validation", ["hadoop/run_mapreduce.py"])

    # Step 3: Hive Analytics
    run_step(3, "HiveQL Analytical Queries Execution", ["hive/run_hive_analytics.py"])

    # Step 4: Spark Feature Pipeline
    run_step(4, "PySpark Time-Series Feature Engineering", ["spark/spark_feature_pipeline.py"])

    # Step 5: Machine Learning Forecasting
    run_step(5, "Spark MLlib Model Training & Evaluation", ["forecasting/train_models.py"])

    # Step 6: Power BI Exports
    run_step(6, "Power BI Star-Schema CSV Export Generation", ["dashboard/generate_dashboard_exports.py"])

    # Step 7: Plot Generation
    run_step(7, "Publication Figures and Visualizations Rendering", ["dashboard/generate_plots.py"])

    # Step 8: Pytest Verification
    print(f"\n{'='*75}")
    print("STEP 8: AUTOMATED UNIT TEST SUITE (PYTEST)")
    print(f"{'='*75}")
    res_test = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=False)
    if res_test.returncode != 0:
        print("[-] Unit tests failed!")
        sys.exit(res_test.returncode)

    total_time = time.time() - t0
    print("\n" + "="*75)
    print(f"[SUCCESS] COMPLETE PIPELINE EXECUTED AND VERIFIED IN {total_time:.2f}s!")
    print("="*75)

if __name__ == "__main__":
    main()
