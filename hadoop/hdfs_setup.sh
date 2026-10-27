#!/bin/bash
# ==============================================================================
# HDFS Directory Setup and Dataset Ingestion Script
# Project: Smart Energy Consumption Analytics & Forecasting
# Subject: Big Data Analytics (BDA)
# ==============================================================================

set -e

echo "=== 1. Checking HDFS Service Availability ==="
if ! command -v hdfs &> /dev/null; then
    echo "[ERROR] 'hdfs' command not found. Please ensure Hadoop is installed and added to PATH."
    echo "        See docs/installation.md for Hadoop single-node cluster setup on WSL2/Linux."
    exit 1
fi

# Verify NameNode is active by querying root directory
hdfs dfs -ls / &> /dev/null || {
    echo "[ERROR] Cannot connect to HDFS NameNode. Is the HDFS daemon running? (start-dfs.sh)"
    exit 1
}

echo "[+] HDFS NameNode is active and responsive."

echo "=== 2. Creating Project Directory Hierarchy in HDFS ==="
hdfs dfs -mkdir -p /smart-energy/raw
hdfs dfs -mkdir -p /smart-energy/cleaned
hdfs dfs -mkdir -p /smart-energy/mapreduce
hdfs dfs -mkdir -p /smart-energy/hive/warehouse

echo "[+] Directories created successfully:"
hdfs dfs -ls /smart-energy

echo "=== 3. Ingesting Raw Dataset to HDFS ==="
LOCAL_SAMPLE="data/raw/sample_household_power_consumption.txt"
LOCAL_FULL="data/raw/household_power_consumption.txt"

if [ -f "$LOCAL_FULL" ]; then
    echo "Uploading full dataset to /smart-energy/raw..."
    hdfs dfs -put -f "$LOCAL_FULL" /smart-energy/raw/
elif [ -f "$LOCAL_SAMPLE" ]; then
    echo "Uploading sample dataset to /smart-energy/raw..."
    hdfs dfs -put -f "$LOCAL_SAMPLE" /smart-energy/raw/
else
    echo "[ERROR] No dataset found in data/raw/"
    exit 1
fi

echo "=== 4. Verifying Uploaded Files in HDFS ==="
hdfs dfs -ls -h /smart-energy/raw

echo "=== 5. Reading Sample Records from HDFS ==="
hdfs dfs -cat /smart-energy/raw/*.txt | head -n 5

echo "=== HDFS Ingestion Completed Successfully ==="
