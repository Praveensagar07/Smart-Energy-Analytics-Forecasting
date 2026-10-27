"""
Automated Unit Tests: Hadoop Streaming Mapper and Reducer Logic
"""

import sys
import subprocess
import pytest
import numpy as np

def run_script(script_path, input_text):
    proc = subprocess.Popen(
        [sys.executable, script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=input_text)
    return proc.returncode, stdout, stderr

def test_mapper_valid_row():
    """Verify mapper properly extracts date and computes interval kWh."""
    line = "16/12/2006;17:24:00;4.216;0.418;234.840;18.400;0.000;1.000;17.000\n"
    code, stdout, stderr = run_script("hadoop/mapper.py", line)
    assert code == 0
    parts = stdout.strip().split("\t")
    assert len(parts) == 3
    assert parts[0] == "16/12/2006"
    assert np.isclose(float(parts[1]), 4.216 / 60.0, atol=1e-5)
    assert parts[2] == "1"

def test_mapper_header_skipping():
    """Verify mapper silently skips header line."""
    header = "Date;Time;Global_active_power;Global_reactive_power;Voltage;Global_intensity\n"
    code, stdout, stderr = run_script("hadoop/mapper.py", header)
    assert code == 0
    assert stdout.strip() == ""

def test_mapper_missing_data_skipping():
    """Verify mapper ignores rows with '?' sentinel in active power."""
    line = "17/12/2006;10:00:00;?;?;?;?;?;?;?\n"
    code, stdout, stderr = run_script("hadoop/mapper.py", line)
    assert code == 0
    assert stdout.strip() == ""

def test_reducer_single_date_aggregation():
    """Verify reducer correctly accumulates energy and count for a single date."""
    input_text = "16/12/2006\t0.070267\t1\n16/12/2006\t0.089333\t1\n16/12/2006\t0.089567\t1\n"
    code, stdout, stderr = run_script("hadoop/reducer.py", input_text)
    assert code == 0
    parts = stdout.strip().split("\t")
    assert parts[0] == "16/12/2006"
    total_energy = float(parts[1])
    count = int(parts[2])
    assert np.isclose(total_energy, 0.070267 + 0.089333 + 0.089567, atol=1e-4)
    assert count == 3

def test_reducer_multi_date_aggregation():
    """Verify reducer partitions and flushes on date key transitions."""
    input_text = (
        "16/12/2006\t10.0\t100\n"
        "17/12/2006\t20.0\t200\n"
        "17/12/2006\t5.0\t50\n"
    )
    code, stdout, stderr = run_script("hadoop/reducer.py", input_text)
    assert code == 0
    lines = stdout.strip().split("\n")
    assert len(lines) == 2
    row1 = lines[0].split("\t")
    row2 = lines[1].split("\t")
    assert row1[0] == "16/12/2006" and float(row1[1]) == 10.0 and int(row1[2]) == 100
    assert row2[0] == "17/12/2006" and float(row2[1]) == 25.0 and int(row2[2]) == 250

def test_end_to_end_mapreduce_pipeline():
    """Verify end-to-end mapper | sort | reducer pipeline."""
    sample_data = (
        "Date;Time;Global_active_power\n"
        "16/12/2006;17:24:00;6.0\n" # 6.0 / 60 = 0.1 kWh
        "16/12/2006;17:25:00;6.0\n" # 6.0 / 60 = 0.1 kWh
        "17/12/2006;08:00:00;12.0\n" # 12.0 / 60 = 0.2 kWh
    )
    code_m, out_m, _ = run_script("hadoop/mapper.py", sample_data)
    assert code_m == 0

    lines = sorted(out_m.strip().split("\n"))
    code_r, out_r, _ = run_script("hadoop/reducer.py", "\n".join(lines) + "\n")
    assert code_r == 0

    results = {l.split("\t")[0]: float(l.split("\t")[1]) for l in out_r.strip().split("\n")}
    assert np.isclose(results["16/12/2006"], 0.20, atol=1e-3)
    assert np.isclose(results["17/12/2006"], 0.20, atol=1e-3)
