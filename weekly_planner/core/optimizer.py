"""
ProductionOptimizer: single-shot facade (1 LT solve + 1 ST solve for the full horizon).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional
import datetime

import pandas as pd

from .optimizer_helpers import (
    build_result_row,
    build_usage_matrix,
    complete_rm_usage_matrix,
    compute_costs,
    compute_w_global,
    policy_order_qty,
    shift_arrival_to_monday,
    week_first_day_local,
)
from .optimizer_lt import compute_warm_start_initial_state, solve_long_term
from .optimizer_st import solve_short_term


@dataclass
class OptimizerConfig:
    """Configuration for the production optimizer."""

    total_days: int = 56
    short_term_horizon: int = 56
    short_term_step: int = 7
    long_term_block: int = 24
    planning_start_date: Optional[datetime.date] = None
    planning_weeks: int = 8
    closed_dates: list = field(default_factory=list)
    calendar_dates: list = field(default_factory=list)
    day_to_date: dict = field(default_factory=dict)
    date_to_day: dict = field(default_factory=dict)
    weekday_by_day: dict = field(default_factory=dict)
    production_allowed_by_day: dict = field(default_factory=dict)
    production_allowed_day_indices: list = field(default_factory=list)
    closed_day_indices: list = field(default_factory=list)
    week_definitions: list = field(default_factory=list)
    horizon_end_date: Optional[datetime.date] = None
    lt_blocks: list = field(default_factory=list)
    daily_demand_by_date: dict = field(default_factory=dict)
    daily_demand_by_day: dict = field(default_factory=dict)
    monthly_forecast_by_period: dict = field(default_factory=dict)
    pipeline_by_date: dict = field(default_factory=dict)
    pipeline_by_day: dict = field(default_factory=dict)

    holding_cost: float = 1.0
    backlog_cost: float = 160.0
    b12_penalty: float = 10000.0
    rm_holding_cost: float = 0.1

    max_product_inventory: float = 3000000.0
    max_rm_inventory: float = 10**15

    time_limit: int = 300
    gap_tolerance: float = 0.0

    base_rm_init: float = 2000000.0
    rm4_init: float = 6000000.0
    rm7_init: float = 4000000.0
    rm8_init: float = 500000.0

    initial_inventory: dict = field(default_factory=lambda: {1: 10000.0, 2: 10000.0, 3: 500000.0, 4: 0.0})
    initial_backlog: dict = field(default_factory=lambda: {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0})
    initial_pipeline: dict = field(default_factory=dict)

    lt_warm_start: bool = False

    stochastic_lt: bool = True
    n_scenarios: int = 10
    alpha_base: float = 0.20
    fan_out_rate: float = 0.0
    scenario_seed: int = None

    rm_usage: Optional[dict[tuple[int, int], float]] = None

    cap_l1: dict = field(default_factory=lambda: {1: 1000.0, 2: 500.0, 3: 2000.0})
    cap_p3: dict = field(default_factory=lambda: {1: 10000.0, 2: 25000.0})
    cap_p4: float = 80000.0

    build_warnings: list = field(default_factory=list)


@dataclass
class OptimizationResult:
    """Result from an optimization run."""

    success: bool
    status: str
    objective_value: float
    plan_df: Optional[pd.DataFrame]
    cost_summary: dict
    solver_log: list
    error_message: str = ""
    warnings: list = field(default_factory=list)


class ProductionOptimizer:
    """Production planning optimizer — single-shot mode: 1 LT solve + 1 ST solve for 56 days."""

    LINE1_M = [1, 2, 3]
    LINE2_M3 = [1, 2]

    U23 = 60 / 3400
    U24 = 60 / 3400

    POLICY_MATS = {4, 7, 8}

    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.I_prod = [1, 2, 3, 4]
        self.S_rm = list(range(1, 11))

        self.CAP_L1 = {int(k): float(v) for k, v in (config.cap_l1 or {}).items()}
        if not self.CAP_L1:
            self.CAP_L1 = {1: 1000.0, 2: 500.0, 3: 2000.0}
        self.CAP_P3 = {int(k): float(v) for k, v in (config.cap_p3 or {}).items()}
        if not self.CAP_P3:
            self.CAP_P3 = {1: 10000.0, 2: 25000.0}
        self.CAP_P4 = float(config.cap_p4) if config.cap_p4 is not None else 80000.0

        self.ui = {1: 2, 2: 2, 3: 1, 4: 1}
        self.Rui = {s: 1 for s in self.S_rm}

        self.LT_rm = {
            1: 6, 2: 12, 3: 12, 4: 78, 5: 12,
            6: 18, 7: 48, 8: 30, 9: 18, 10: 6,
        }
        self.MOQ_rm = {
            1: 1000, 2: 10000, 3: 2200, 4: 1000, 5: 15000,
            6: 20000, 7: 1000, 8: 25, 9: 50000, 10: 1000,
        }

        if self.config.rm_usage is not None:
            self.nis = complete_rm_usage_matrix(self.config.rm_usage, self.I_prod, self.S_rm)
        else:
            self.nis = build_usage_matrix(self.I_prod, self.S_rm)

        self.h_lt = {i: 1 for i in self.I_prod}
        self.b_lt = {i: 160 for i in self.I_prod}
        self.u_lt = {3: self.U23, 4: self.U24}
        self.r_lt = {1: 2, 2: 2, 3: 1, 4: 1}

        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

    def _compute_w_global(self) -> dict:
        return compute_w_global(self.config.daily_demand_by_day, self.I_prod, self.config.total_days)

    @staticmethod
    def _week_first_day_local(w: int, step: int = 7) -> int:
        return week_first_day_local(w, step)

    @staticmethod
    def _shift_arrival_to_monday(cur_day: int, arrival_day: int, step: int = 7) -> int | None:
        return shift_arrival_to_monday(cur_day, arrival_day, step)

    def _policy_order_qty(self, s: int, current_day: int, rm_onhand: float, pipeline: dict) -> float:
        return policy_order_qty(
            s=s,
            current_day=current_day,
            rm_onhand=rm_onhand,
            pipeline=pipeline,
            config=self.config,
            lt_rm=self.LT_rm,
            moq_rm=self.MOQ_rm,
            nis=self.nis,
            line1_m=self.LINE1_M,
            cap_l1=self.CAP_L1,
            cap_p3=self.CAP_P3,
            cap_p4=self.CAP_P4,
        )

    def _compute_warm_start_initial_state(self) -> dict[int, float]:
        return compute_warm_start_initial_state(
            config=self.config,
            i_prod=self.I_prod,
            h_lt=self.h_lt,
            b_lt=self.b_lt,
            u_lt=self.u_lt,
            r_lt=self.r_lt,
            u23=self.U23,
            u24=self.U24,
        )

    def _solve_long_term(self, cur_day, i_init, b_init, scenarios=None):
        return solve_long_term(
            cur_day=cur_day,
            i_init=i_init,
            b_init=b_init,
            config=self.config,
            i_prod=self.I_prod,
            h_lt=self.h_lt,
            b_lt=self.b_lt,
            u_lt=self.u_lt,
            r_lt=self.r_lt,
            scenarios=scenarios,
        )

    def _solve_short_term(self, demand, w_global, cur_day, i_init, b_init, rm_init, pipeline, i_target_map):
        return solve_short_term(
            demand=demand,
            w_global=w_global,
            cur_day=cur_day,
            i_init=i_init,
            b_init=b_init,
            rm_init=rm_init,
            pipeline=pipeline,
            i_target_map=i_target_map,
            config=self.config,
            i_prod=self.I_prod,
            s_rm=self.S_rm,
            nis=self.nis,
            policy_mats=self.POLICY_MATS,
            line1_m=self.LINE1_M,
            cap_l1=self.CAP_L1,
            line2_m3=self.LINE2_M3,
            cap_p3=self.CAP_P3,
            cap_p4=self.CAP_P4,
            lt_rm=self.LT_rm,
            moq_rm=self.MOQ_rm,
            ui=self.ui,
            rui=self.Rui,
            u23=self.U23,
            u24=self.U24,
            week_first_day_local_fn=self._week_first_day_local,
            shift_arrival_to_monday_fn=self._shift_arrival_to_monday,
        )

    def _build_result_row(self, gday, t_local, result, policy_orders=None):
        row = build_result_row(gday, t_local, result, self.S_rm, self.POLICY_MATS, policy_orders)
        row["date"] = self.config.day_to_date.get(gday)
        row["weekday"] = row["date"].strftime("%A") if row["date"] else None
        row["production_allowed"] = self.config.production_allowed_by_day.get(gday, False)
        return row

    def _apply_block_control(self, rows, last_day, i_state, b_state):
        return apply_block_control(rows, last_day, i_state, b_state, self.I_prod)

    def _compute_costs(self, df: pd.DataFrame) -> dict:
        return compute_costs(df, self.config)

    def run(self) -> OptimizationResult:
        """Run the complete single-shot optimization (1 LT + 1 ST solve)."""
        if not self.config.monthly_forecast_by_period:
            return OptimizationResult(
                success=False,
                status="Error",
                objective_value=0.0,
                plan_df=None,
                cost_summary={},
                solver_log=[],
                error_message=(
                    "Monthly forecast data is required for the LT model. "
                    "Upload an Excel file with a 'Monthly' sheet containing columns: month, product, demand."
                ),
            )

        if self.config.lt_warm_start:
            warm_start_inv = self._compute_warm_start_initial_state()
            for i in self.I_prod:
                if i in warm_start_inv:
                    self.config.initial_inventory[i] = warm_start_inv[i]

        try:
            return self._run_single_shot()
        except Exception as exc:
            return OptimizationResult(
                success=False,
                status="Error",
                objective_value=0.0,
                plan_df=None,
                cost_summary={},
                solver_log=[],
                error_message=str(exc),
            )

    def _run_single_shot(self) -> OptimizationResult:
        """Execute single-shot optimization: 1 LT solve + 1 ST solve for the full 56-day horizon."""
        cfg = self.config
        i_state = {i: float(cfg.initial_inventory.get(i, 0.0)) for i in self.I_prod}
        b_state = {i: float(cfg.initial_backlog.get(i, 0.0)) for i in self.I_prod}

        rm_state = {s: float(cfg.base_rm_init) for s in self.S_rm}
        rm_state[4] = float(cfg.rm4_init)
        rm_state[7] = float(cfg.rm7_init)
        rm_state[8] = float(cfg.rm8_init)

        w_global = self._compute_w_global()
        pipeline = dict(cfg.initial_pipeline) if cfg.initial_pipeline else {}
        i_target_map = {}
        solver_log = []

        # ── Step 1: LT solve (once, at day 1) ──────────────────────────────
        if self.progress_callback:
            self.progress_callback(1, 2, "Solving long-term model...")

        lt_result = self._solve_long_term(1, i_state, b_state)
        i_target_map.update(lt_result["targets"])
        solver_log.append(
            {
                "Day": 1,
                "Model": "LT",
                "Status": lt_result["status"],
                "Objective": lt_result["objective"],
                "Stage1Cost": lt_result.get("stage1_cost", 0.0),
                "Stage2Cost": lt_result.get("stage2_cost", 0.0),
                "Targets": lt_result["targets"],
                "Duration": lt_result.get("duration", 0.0),
                "Gap": lt_result.get("gap", None),
                "Production": lt_result.get("production", {}),
                "Inventory": lt_result.get("inventory", {}),
                "Backlog": lt_result.get("backlog", {}),
                "Demand": lt_result.get("demand", {}),
                "I_state": dict(i_state),
                "B_state": dict(b_state),
            }
        )

        # ── Step 2: Policy orders computed once at day 1 ───────────────────
        policy_orders = {}
        for s in self.POLICY_MATS:
            q_pol = self._policy_order_qty(s, 1, rm_state[s], pipeline)
            policy_orders[s] = q_pol
            if q_pol > 1e-6:
                arr_day = 1 + self.LT_rm[s]
                if arr_day <= cfg.total_days:
                    pipeline[(s, arr_day)] = pipeline.get((s, arr_day), 0.0) + q_pol

        # ── Step 3: ST solve once for the full horizon ─────────────────────
        if self.progress_callback:
            self.progress_callback(2, 2, "Solving short-term model (56 days)...")

        st_result = self._solve_short_term(
            cfg.daily_demand_by_day,
            w_global,
            1,
            i_state,
            b_state,
            rm_state,
            pipeline,
            i_target_map,
        )
        solver_log.append(
            {
                "Day": 1,
                "Model": "ST",
                "Status": st_result["status"],
                "Objective": st_result["objective"],
                "Duration": st_result.get("duration", 0.0),
                "Gap": st_result.get("gap", None),
            }
        )

        # ── Step 4: Collect all 56 days from the single ST result ──────────
        rows = []
        for t_local in range(1, cfg.total_days + 1):
            rows.append(self._build_result_row(t_local, t_local, st_result, policy_orders))

        df = pd.DataFrame(rows).sort_values("day").round(2)
        cost_summary = self._compute_costs(df)

        return OptimizationResult(
            success=True,
            status="Optimal",
            objective_value=cost_summary["total"],
            plan_df=df,
            cost_summary=cost_summary,
            solver_log=solver_log,
        )
