"""
Generate Full-Year Demand Data for Simulation

Creates 240-day (12-month) demand scenarios for use with simulation.py.
Extends the existing 40-day patterns to a full year.

Usage:
    python generate_year_data.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(2025)

# CONFIG
OUTPUT_DIR = Path(__file__).parent / "templates" / "simulation_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LINE1_CAP = 3000
LINE2_CAP = 900
DAYS_PER_MONTH = 20
TOTAL_DAYS = 240  # 12 months


def get_base_demand(prod):
    """Return base daily demand."""
    if prod == 1:
        return 2400  # ~80% of Line 1
    elif prod == 3:
        return 360   # ~40% of Line 2
    elif prod == 4:
        return 360   # ~40% of Line 2
    return 0


def generate_scenario(filename, description, daily_func):
    """Generate a full-year demand scenario."""
    
    rows = []
    for day in range(1, TOTAL_DAYS + 1):
        month = (day - 1) // DAYS_PER_MONTH + 1
        for prod in [1, 3, 4]:
            base = get_base_demand(prod)
            qty = daily_func(day, month, prod, base)
            rows.append({
                'day': day,
                'month': month,
                'product': prod,
                'demand': int(max(0, qty))
            })
    
    df = pd.DataFrame(rows)
    
    # Save
    path = OUTPUT_DIR / f"{filename}.xlsx"
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Daily', index=False)
        pd.DataFrame({'Description': [description]}).to_excel(writer, sheet_name='Info', index=False)
    
    print(f"Generated: {filename} ({len(df)} records)")


# --- SCENARIO FUNCTIONS ---

def steady(day, month, prod, base):
    """Steady 80% utilization."""
    return base * np.random.normal(1.0, 0.05)


def low_utilization(day, month, prod, base):
    """Low 40% utilization."""
    return base * 0.5 * np.random.normal(1.0, 0.05)


def high_stress(day, month, prod, base):
    """High 110% utilization."""
    return base * 1.1 * np.random.normal(1.0, 0.05)


def summer_peak(day, month, prod, base):
    """Summer peak (months 5-8)."""
    if 5 <= month <= 8:
        mult = 1.5
    elif month in [4, 9]:
        mult = 1.2
    else:
        mult = 0.7
    return base * mult * np.random.normal(1.0, 0.05)


def end_year_rush(day, month, prod, base):
    """End-of-year rush (months 11-12)."""
    if month >= 11:
        mult = 1.8
    elif month == 10:
        mult = 1.3
    else:
        mult = 0.7
    return base * mult * np.random.normal(1.0, 0.05)


def ramp_up(day, month, prod, base):
    """Linear ramp from 50% to 150% over the year."""
    progress = day / TOTAL_DAYS
    mult = 0.5 + (1.0 * progress)
    return base * mult * np.random.normal(1.0, 0.05)


def volatility(day, month, prod, base):
    """High variance (+/- 40%)."""
    return base * np.random.normal(1.0, 0.4)


def product_imbalance(day, month, prod, base):
    """High P3, low P4."""
    if prod == 3:
        return base * 2.0 * np.random.normal(1.0, 0.05)
    elif prod == 4:
        return base * 0.1 * np.random.normal(1.0, 0.05)
    return base * np.random.normal(1.0, 0.05)


def weekly_spikes(day, month, prod, base):
    """Spikes every Monday (every 5th day)."""
    day_of_week = (day - 1) % 5
    if day_of_week == 0:  # Monday
        return base * 2.0
    return base * 0.75


def stepwise_growth(day, month, prod, base):
    """Quarterly step increases."""
    quarter = (month - 1) // 3 + 1
    mult = 0.5 + (quarter * 0.25)  # 0.75, 1.0, 1.25, 1.5
    return base * mult * np.random.normal(1.0, 0.05)


def main():
    scenarios = [
        ("01_steady_optimal", "Steady 80% utilization year-round", steady),
        ("02_low_utilization", "Low 40% utilization", low_utilization),
        ("03_high_stress", "High 110% utilization (backlogs expected)", high_stress),
        ("04_summer_peak", "Seasonal: peak in months 5-8", summer_peak),
        ("05_end_year_rush", "Seasonal: holiday rush months 11-12", end_year_rush),
        ("06_ramp_up", "Linear growth from 50% to 150%", ramp_up),
        ("07_volatility", "High daily variance (+/- 40%)", volatility),
        ("08_product_imbalance", "High P3, very low P4", product_imbalance),
        ("09_weekly_spikes", "Demand spikes every Monday", weekly_spikes),
        ("10_stepwise_growth", "Quarterly step increases", stepwise_growth),
    ]
    
    print("Generating 10 full-year (240-day) simulation scenarios...\n")
    for args in scenarios:
        generate_scenario(*args)
    
    print(f"\n✅ Done! Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
