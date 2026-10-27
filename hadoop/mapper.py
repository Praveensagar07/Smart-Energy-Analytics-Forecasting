#!/usr/bin/env python3
"""
Hadoop Streaming Mapper: Daily Household Electricity Consumption
Calculates 1-minute interval energy in kilowatt-hours (kWh).

Input format (UCI Household Power Consumption):
Date;Time;Global_active_power;Global_reactive_power;Voltage;Global_intensity;Sub_metering_1;Sub_metering_2;Sub_metering_3

Output emitted to stdout:
Date \t Interval_Energy_kWh \t 1
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Check for header
        if line.startswith("Date;") or line.startswith("Date,"):
            continue

        # Support semicolon (UCI raw format) or comma
        delimiter = ";" if ";" in line else ","
        parts = line.split(delimiter)

        if len(parts) < 3:
            continue

        date_str = parts[0].strip()
        time_str = parts[1].strip()
        active_power_str = parts[2].strip()

        # Handle missing or invalid readings represented by '?' or empty
        if active_power_str in ("?", "", "NA", "null", "NaN"):
            continue

        try:
            active_power_kw = float(active_power_str)
            # Energy in kWh for a 1-minute sampling interval: kW * (1/60 hours)
            interval_energy_kwh = active_power_kw / 60.0
            
            # Emit key: Date, value: interval_energy_kwh, reading_count (1)
            print(f"{date_str}\t{interval_energy_kwh:.6f}\t1")
        except ValueError:
            # Skip malformed numeric records safely
            continue

if __name__ == "__main__":
    main()
