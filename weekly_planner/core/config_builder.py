"""
Helpers for mapping UI params into optimizer config.
"""
from __future__ import annotations

import datetime

import pandas as pd

from core.optimizer import OptimizerConfig
from core.planning_calendar import (
    build_planning_calendar, build_lt_blocks, normalize_daily_demand_records,
    normalize_monthly_forecast_records, normalize_pipeline_records,
    zero_fill_daily_demand, next_monday, check_demand_date_coverage,
)

def params_to_config(params: dict) -> OptimizerConfig:
    """Convert sidebar params into an OptimizerConfig."""
    planning_start_date = params.get("planning_start_date")
    if planning_start_date is None:
        planning_start_date = next_monday()
    planning_weeks = params.get("planning_weeks", 8)
    closed_dates = params.get("closed_dates", [])
    sundays_working = bool(params.get("sundays_working", False))

    cal = build_planning_calendar(
        planning_start_date, planning_weeks, closed_dates, sundays_working=sundays_working
    )
    total_days = planning_weeks * 7
    
    demand_df = params.get("demand_data")
    if demand_df is None:
        demand_df = pd.DataFrame(columns=["day", "product", "demand"])

    monthly_df = params.get("monthly_demand")
    if monthly_df is None:
        monthly_df = pd.DataFrame(columns=["month", "product", "demand"])
    pipeline_input = params.get("initial_pipeline", {})
    
    if isinstance(pipeline_input, dict):
        pipe_rows = [{'material': m, 'arrival_day': d, 'qty': q} for (m,d), q in pipeline_input.items()]
        pipeline_df = pd.DataFrame(pipe_rows)
    else:
        pipeline_df = pipeline_input

    if pipeline_df is None:
        pipeline_df = pd.DataFrame(columns=["material", "arrival_day", "qty"])

    pipe_by_date, pipe_by_day = normalize_pipeline_records(pipeline_df, cal)
    
    build_warnings = check_demand_date_coverage(demand_df, cal)
    daily_by_date, daily_by_day = normalize_daily_demand_records(demand_df, cal)
    daily_by_day = zero_fill_daily_demand(daily_by_day, cal)
    
    monthly_by_period = normalize_monthly_forecast_records(monthly_df, cal)
    
    lt_blocks = build_lt_blocks(cal, total_blocks=12)

    week_stride = 7
    if cal["week_definitions"]:
        week_stride = len(cal["week_definitions"][0].get("day_indices", [])) or 7

    return OptimizerConfig(
        planning_start_date=planning_start_date,
        planning_weeks=planning_weeks,
        closed_dates=cal['closed_dates_in_horizon'],
        total_days=total_days,
        calendar_dates=cal['calendar_dates'],
        day_to_date=cal['day_to_date'],
        date_to_day=cal['date_to_day'],
        weekday_by_day=cal['weekday_by_day'],
        production_allowed_by_day=cal['production_allowed_by_day'],
        production_allowed_day_indices=cal['production_allowed_day_indices'],
        closed_day_indices=cal['closed_day_indices'],
        week_definitions=cal['week_definitions'],
        horizon_end_date=cal['horizon_end_date'],
        lt_blocks=lt_blocks,
        daily_demand_by_date=daily_by_date,
        daily_demand_by_day=daily_by_day,
        monthly_forecast_by_period=monthly_by_period,
        pipeline_by_date=pipe_by_date,
        pipeline_by_day=pipe_by_day,
        short_term_horizon=total_days,
        short_term_step=week_stride,
        long_term_block=params.get("lt_block", 24),
        holding_cost=params["holding_cost"],
        backlog_cost=params["backlog_cost"],
        b12_penalty=params["b12_penalty"],
        time_limit=params["time_limit"],
        initial_inventory=params.get(
            "initial_inventory",
            {1: 10000.0, 2: 20000.0, 3: 250000.0, 4: 0.0},
        ),
        initial_backlog=params.get(
            "initial_backlog",
            {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
        ),
        base_rm_init=params.get("base_rm_init", 2000000.0),
        rm4_init=params.get("rm4_init", 6000000.0),
        rm7_init=params.get("rm7_init", 4000000.0),
        rm8_init=params.get("rm8_init", 1000000.0),
        initial_pipeline=params.get("initial_pipeline", {}),
        lt_warm_start=params.get("lt_warm_start", False),
        stochastic_lt=params.get("stochastic_lt", True),
        n_scenarios=params.get("n_scenarios", 10),
        alpha_base=params.get("alpha_base", 0.20),
        fan_out_rate=params.get("fan_out_rate", 0.0),
        scenario_seed=42,
        rm_usage=params.get("rm_usage"),
        cap_l1=params.get("cap_l1", {1: 1000.0, 2: 500.0, 3: 2000.0}),
        cap_p3=params.get("cap_p3", {1: 10000.0, 2: 25000.0}),
        cap_p4=params.get("cap_p4", 80000.0),
        build_warnings=build_warnings,
    )
