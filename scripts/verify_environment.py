#!/usr/bin/env python3
"""
Environment Diagnostic & Verification Tool
Smart Energy Consumption Analytics & Forecasting
"""

import os
import sys
import shutil
import platform
import subprocess

def check_env():
    print("=" * 65)
    print("ENVIRONMENT & TOOLING DIAGNOSTIC REPORT")
    print("=" * 65)

    print(f"OS Platform:          {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python Executable:    {sys.executable}")
    print(f"Python Version:       {sys.version.split()[0]}")

    # Java check
    java_home = os.environ.get("JAVA_HOME", r"C:\Users\PRAVEENRAJ\jdk-17\jdk-17.0.14+7")
    print(f"JAVA_HOME:            {java_home}")
    java_exe = os.path.join(java_home, "bin", "java.exe" if os.name == "nt" else "java")
    if os.path.exists(java_exe):
        try:
            j_ver = subprocess.check_output([java_exe, "-version"], stderr=subprocess.STDOUT, text=True)
            first_line = j_ver.strip().split("\n")[0]
            print(f"Java Version:         {first_line} [FOUND]")
        except Exception as e:
            print(f"Java Version:         Error querying java: {e}")
    else:
        print(f"Java Executable:      [NOT FOUND at {java_exe}]")

    # Hadoop check
    hadoop_home = os.environ.get("HADOOP_HOME", r"C:\hadoop")
    print(f"HADOOP_HOME:          {hadoop_home}")
    winutils_exe = os.path.join(hadoop_home, "bin", "winutils.exe")
    if os.path.exists(winutils_exe):
        print(f"Winutils Binary:      {winutils_exe} [FOUND]")
    else:
        print(f"Winutils Binary:      [NOT FOUND at {winutils_exe}]")

    # Git check
    git_bin = shutil.which("git")
    print(f"Git Binary:           {git_bin or '[NOT FOUND]'}")

    # PySpark check
    try:
        import pyspark
        print(f"PySpark Library:      v{pyspark.__version__} [INSTALLED]")
    except ImportError:
        print(f"PySpark Library:      [NOT INSTALLED]")

    # Check Dataset Files
    raw_file = os.path.join("data", "raw", "household_power_consumption.txt")
    sample_file = os.path.join("data", "raw", "sample_household_power_consumption.txt")
    processed_daily = os.path.join("data", "processed", "daily_energy_consumption.csv")
    features_file = os.path.join("data", "features", "daily_energy_features.csv")
    predictions_file = os.path.join("forecasting", "test_predictions.csv")

    print("\nDataset Artifacts Status:")
    print(f"  Raw Full Dataset:   {'[PRESENT]' if os.path.exists(raw_file) else '[ABSENT]'} ({raw_file})")
    print(f"  Sample Dataset:     {'[PRESENT]' if os.path.exists(sample_file) else '[ABSENT]'} ({sample_file})")
    print(f"  Processed Daily:    {'[PRESENT]' if os.path.exists(processed_daily) else '[ABSENT]'} ({processed_daily})")
    print(f"  Engineered Features:{'[PRESENT]' if os.path.exists(features_file) else '[ABSENT]'} ({features_file})")
    print(f"  Forecast Models:    {'[PRESENT]' if os.path.exists(predictions_file) else '[ABSENT]'} ({predictions_file})")

    print("=" * 65)

if __name__ == "__main__":
    check_env()
