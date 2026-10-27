#!/usr/bin/env python3
"""
Hadoop Streaming Reducer: Daily Household Electricity Consumption Aggregator
Aggregates interval energy across each date emitted by the mapper.

Input from stdin (sorted by key: Date):
Date \t Interval_Energy_kWh \t 1

Output to stdout:
Date \t Total_Energy_kWh \t Reading_Count
"""

import sys

def main():
    current_date = None
    accumulated_energy = 0.0
    accumulated_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        date_key = parts[0]
        try:
            energy_val = float(parts[1])
            count_val = int(parts[2]) if len(parts) > 2 else 1
        except ValueError:
            continue

        if current_date == date_key:
            accumulated_energy += energy_val
            accumulated_count += count_val
        else:
            if current_date is not None:
                print(f"{current_date}\t{accumulated_energy:.4f}\t{accumulated_count}")
            current_date = date_key
            accumulated_energy = energy_val
            accumulated_count = count_val

    # Flush the last date group
    if current_date is not None:
        print(f"{current_date}\t{accumulated_energy:.4f}\t{accumulated_count}")

if __name__ == "__main__":
    main()
