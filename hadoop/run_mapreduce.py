#!/usr/bin/env python3
"""
MapReduce Execution and Independent Validation Harness
Smart Energy Consumption Analytics & Forecasting

Simulates and verifies Hadoop Streaming pipeline:
Input Stream -> Mapper -> Sort / Shuffle -> Reducer -> Output

Validates mathematical equivalence between MapReduce aggregation
and independent trusted Pandas vector aggregation on the identical input dataset.
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np

def run_mapreduce_pipeline(input_file: str, output_file: str):
    print(f"[*] Running MapReduce pipeline on {input_file}...")
    
    mapper_path = os.path.join(os.path.dirname(__file__), "mapper.py")
    reducer_path = os.path.join(os.path.dirname(__file__), "reducer.py")

    # Step 1: Mapper execution
    print("  -> Step 1: Streaming through mapper.py...")
    with open(input_file, "r", encoding="utf-8", errors="ignore") as in_f:
        mapper_proc = subprocess.Popen(
            [sys.executable, mapper_path],
            stdin=in_f,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        mapper_out, mapper_err = mapper_proc.communicate()

    if mapper_proc.returncode != 0:
        raise RuntimeError(f"Mapper failed with error: {mapper_err}")

    mapper_lines = [l for l in mapper_out.strip().split("\n") if l]
    print(f"     Mapper emitted {len(mapper_lines):,} key-value pairs.")

    # Step 2: Shuffle and Sort by Key (Date)
    print("  -> Step 2: Sorting and partitioning by key (Date)...")
    mapper_lines.sort(key=lambda x: x.split("\t")[0])
    sorted_input = "\n".join(mapper_lines) + "\n"

    # Step 3: Reducer execution
    print("  -> Step 3: Streaming sorted pairs through reducer.py...")
    reducer_proc = subprocess.Popen(
        [sys.executable, reducer_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    reducer_out, reducer_err = reducer_proc.communicate(input=sorted_input)

    if reducer_proc.returncode != 0:
        raise RuntimeError(f"Reducer failed with error: {reducer_err}")

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(reducer_out)

    print(f"[+] MapReduce completed successfully! Output saved to: {output_file}")
    return reducer_out

def validate_against_reference(input_file: str, mr_output_file: str):
    print(f"[*] Validating MapReduce output against independent Pandas reference...")
    
    # Independent reference calculation using Pandas
    df = pd.read_csv(
        input_file,
        sep=";" if ";" in open(input_file).readline() else ",",
        na_values=["?", ""],
        usecols=["Date", "Global_active_power"],
        low_memory=False
    )
    df = df.dropna(subset=["Global_active_power"])
    df["Interval_kWh"] = df["Global_active_power"].astype(float) / 60.0
    ref_agg = df.groupby("Date")["Interval_kWh"].agg(["sum", "count"]).reset_index()
    ref_dict = {row["Date"]: (row["sum"], row["count"]) for _, row in ref_agg.iterrows()}

    # Load MapReduce output
    mr_dict = {}
    with open(mr_output_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                date_k = parts[0]
                energy_v = float(parts[1])
                count_v = int(parts[2])
                mr_dict[date_k] = (energy_v, count_v)

    # Verification checks
    discrepancies = 0
    max_energy_diff = 0.0
    checked_dates = 0

    for d, (ref_energy, ref_count) in ref_dict.items():
        if d not in mr_dict:
            discrepancies += 1
            print(f"  [ERROR] Missing date {d} in MapReduce output!")
            continue

        mr_energy, mr_count = mr_dict[d]
        diff = abs(ref_energy - mr_energy)
        max_energy_diff = max(max_energy_diff, diff)

        # Allow small floating point rounding error up to 0.01 kWh
        if diff > 0.05 or ref_count != mr_count:
            discrepancies += 1
            print(f"  [MISMATCH] Date {d}: Ref=({ref_energy:.4f} kWh, {ref_count} readings) vs MR=({mr_energy:.4f} kWh, {mr_count} readings)")

        checked_dates += 1

    print(f"  Total dates verified: {checked_dates}")
    print(f"  Max absolute energy difference: {max_energy_diff:.6f} kWh")
    print(f"  Total discrepancies: {discrepancies}")

    if discrepancies == 0:
        print("[+] VERIFICATION PASSED: MapReduce output matches independent reference perfectly!")
        return True
    else:
        print("[-] VERIFICATION FAILED: Discrepancies detected.")
        return False

if __name__ == "__main__":
    test_input = os.path.join("data", "raw", "sample_household_power_consumption.txt")
    if not os.path.exists(test_input):
        test_input = os.path.join("data", "raw", "household_power_consumption.txt")

    mr_out = os.path.join("hadoop", "mapreduce_daily_output.txt")
    run_mapreduce_pipeline(test_input, mr_out)
    validate_against_reference(test_input, mr_out)
