# BobaCo Year-Long Simulation

Test the production planner with 48 weekly replanning cycles over a full simulated year.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate demand scenarios
python generate_year_data.py
python generate_realistic_seasonal.py

# Run the simulation dashboard
streamlit run app.py
```

## Features

- Select from 10+ pre-built demand scenarios
- Configure capacities, costs, and initial state
- Watch 48 weeks of simulation execute
- View KPIs, charts, and detailed results
- Export results to CSV/Excel

## Scenarios

| Scenario | Description |
|----------|-------------|
| steady_optimal | 80% utilization year-round |
| summer_peak | Seasonal peak May-August |
| realistic_seasonal | Bubble tea seasonal pattern |
| high_stress | 110% capacity (backlogs expected) |
| volatility | ±40% daily variance |
| ... | See `templates/simulation_data/` |

## How It Works

Each simulated week:
1. Builds inputs from current state + demand data
2. Runs LT + ST optimization (same as weekly planner)
3. Executes the first 5 days of the plan
4. Updates inventory/backlog based on actual demand
5. Records metrics and advances to next week
