# Simulation Codebase Review

## 1. Purpose

The `simulation` app runs the production planner across a long horizon and aggregates the optimizer's day-level output into weekly KPIs.

- `simulation/app.py` provides the Streamlit dashboard for scenario selection, parameter input, visualization, and export.
- `simulation/simulation.py` is the simulation driver and CLI entrypoint.
- Shared planning logic is imported from `weekly_planner.core`, so the long-horizon simulation uses the same optimizer, loader, and export formats as the weekly planner app.

## 2. Architecture Overview

### Shared code

The simulation now reuses these `weekly_planner` modules directly:

- `weekly_planner.core.optimizer` for `ProductionOptimizer`, `OptimizerConfig`, and `OptimizationResult`
- `weekly_planner.core.data_loader` for `DemandLoader` and shared validation/error handling
- `weekly_planner.core.export_run` for Excel export and run-folder saving
- `weekly_planner.config/defaults.yaml` as the default source for costs, solver limits, and initial-state values

### Simulation-specific code

`simulation/simulation.py` adds the pieces that are unique to long-horizon evaluation:

- `SimulationConfig` for simulation-facing parameters such as `total_days`, `step`, and `lt_block`
- `build_optimizer_config()` to translate shared defaults plus simulation overrides into an `OptimizerConfig`
- `YearSimulation` to call the shared optimizer once and aggregate the resulting `plan_df` into weekly summaries
- CLI helpers for scenario resolution, output path handling, and non-zero exit codes on failure

## 3. Execution Flow

### Streamlit app flow

1. `app.py` loads scenarios from `templates/simulation_data/`
2. The sidebar builds a `SimulationConfig` from user inputs
3. `load_year_demand()` loads `Daily` and `Monthly` sheets using the shared demand loader
4. `YearSimulation.run()` executes the shared optimizer and aggregates daily rows into weekly results
5. The dashboard renders KPIs, charts, solver logs, LT decisions, and exports

### CLI flow

Run from the project root:

```bash
python -m simulation.simulation --scenario 01_steady_optimal
```

Important CLI options:

- `--input` to supply an explicit scenario workbook path
- `--output-dir`, `--output`, and `--plan-output` to control exports
- `--total-days`, `--step`, `--short-term-horizon`, and `--lt-block` for horizon tuning
- `--holding-cost`, `--backlog-cost`, `--b12-penalty`, `--time-limit`
- `--lt-warm-start`, `--stochastic-lt`, `--n-scenarios`, `--alpha-base`, `--fan-out-rate`

The CLI exits with status code `1` when input loading or optimization fails.

## 4. Input and Output Contracts

### Inputs

Simulation scenario files are Excel workbooks that must contain:

- `Daily`: realized daily demand with columns `day`, `product`, `demand`
- `Monthly`: forecast demand with columns `month`, `product`, `demand`

Validation and normalization come from `weekly_planner.core.data_loader.DemandLoader`.

### Outputs

`YearSimulation.run()` returns:

- a weekly aggregated `DataFrame` with totals such as `prod_total`, `demand_total`, `backlog_total`, `b10_total`, and `cost`
- the full `OptimizationResult`, including the day-level `plan_df`, `cost_summary`, and `solver_log`

The dashboard and CLI both export:

- weekly aggregated CSV results
- day-by-day plan Excel output
- optional timestamped run folders via `weekly_planner.core.export_run.save_run_to_folder()`
