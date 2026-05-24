"""Year-long rolling-horizon simulation built on weekly_planner core."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = Path(__file__).resolve().parent
DEFAULT_SCENARIO_DIR = SIMULATION_DIR / "templates" / "simulation_data"
DEFAULTS_PATH = PROJECT_ROOT / "weekly_planner" / "config" / "defaults.yaml"
DEFAULT_SCENARIO_NAME = "01_steady_optimal"
DEFAULT_SCENARIO_SEED = 42

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from weekly_planner.core.data_loader import DemandLoader, load_config
from weekly_planner.core.optimizer import OptimizationResult, OptimizerConfig, ProductionOptimizer


@lru_cache(maxsize=1)
def _shared_default_params() -> dict[str, Any]:
    """Load the shared weekly_planner defaults once."""
    config = load_config(DEFAULTS_PATH)

    costs = config.get("costs", {})
    horizons = config.get("horizons", {})
    solver = config.get("solver", {})
    initial_state = config.get("initial_state", {})
    stochastic = config.get("stochastic", {})

    return {
        "holding_cost": float(costs.get("holding", 1.0)),
        "backlog_cost": float(costs.get("backlog", 160.0)),
        "b12_penalty": float(costs.get("b12_penalty", 10000.0)),
        "short_term_horizon": int(horizons.get("total_days", 48)),
        "time_limit": int(solver.get("time_limit", 300)),
        "initial_inventory": {
            1: float(initial_state.get("p1_inv", 10000.0)),
            2: float(initial_state.get("p2_inv", 10000.0)),
            3: float(initial_state.get("p3_inv", 500000.0)),
            4: float(initial_state.get("p4_inv", 0.0)),
        },
        "initial_backlog": {
            1: float(initial_state.get("p1_bl", 0.0)),
            2: float(initial_state.get("p2_bl", 0.0)),
            3: float(initial_state.get("p3_bl", 0.0)),
            4: float(initial_state.get("p4_bl", 0.0)),
        },
        "base_rm_init": float(initial_state.get("base_rm", 2000000.0)),
        "rm4_init": float(initial_state.get("rm4", 6000000.0)),
        "rm7_init": float(initial_state.get("rm7", 4000000.0)),
        "rm8_init": float(initial_state.get("rm8", 500000.0)),
        "lt_warm_start": False,
        "stochastic_lt": False,
        "n_scenarios": int(stochastic.get("n_scenarios", 10)),
        "alpha_base": float(stochastic.get("alpha_base", 0.15)),
        "fan_out_rate": float(stochastic.get("fan_out_rate", 0.5)),
        "scenario_seed": DEFAULT_SCENARIO_SEED,
    }


def _default_inventory() -> dict[int, float]:
    return dict(_shared_default_params()["initial_inventory"])


def _default_backlog() -> dict[int, float]:
    return dict(_shared_default_params()["initial_backlog"])


def build_optimizer_config(
    *,
    total_days: int = 288,
    step: int = 6,
    lt_block: int = 24,
    short_term_horizon: Optional[int] = None,
    holding_cost: Optional[float] = None,
    backlog_cost: Optional[float] = None,
    b12_penalty: Optional[float] = None,
    time_limit: Optional[int] = None,
    initial_inventory: Optional[dict[int, float]] = None,
    initial_backlog: Optional[dict[int, float]] = None,
    base_rm_init: Optional[float] = None,
    rm4_init: Optional[float] = None,
    rm7_init: Optional[float] = None,
    rm8_init: Optional[float] = None,
    initial_pipeline: Optional[dict] = None,
    lt_warm_start: Optional[bool] = None,
    stochastic_lt: Optional[bool] = None,
    n_scenarios: Optional[int] = None,
    alpha_base: Optional[float] = None,
    fan_out_rate: Optional[float] = None,
    scenario_seed: Optional[int] = None,
) -> OptimizerConfig:
    """Build an OptimizerConfig using shared weekly_planner defaults."""
    defaults = _shared_default_params()

    return OptimizerConfig(
        total_days=total_days,
        short_term_horizon=short_term_horizon or defaults["short_term_horizon"],
        short_term_step=step,
        long_term_block=lt_block,
        holding_cost=holding_cost if holding_cost is not None else defaults["holding_cost"],
        backlog_cost=backlog_cost if backlog_cost is not None else defaults["backlog_cost"],
        b12_penalty=b12_penalty if b12_penalty is not None else defaults["b12_penalty"],
        time_limit=time_limit if time_limit is not None else defaults["time_limit"],
        initial_inventory=dict(initial_inventory or defaults["initial_inventory"]),
        initial_backlog=dict(initial_backlog or defaults["initial_backlog"]),
        base_rm_init=base_rm_init if base_rm_init is not None else defaults["base_rm_init"],
        rm4_init=rm4_init if rm4_init is not None else defaults["rm4_init"],
        rm7_init=rm7_init if rm7_init is not None else defaults["rm7_init"],
        rm8_init=rm8_init if rm8_init is not None else defaults["rm8_init"],
        initial_pipeline=dict(initial_pipeline or {}),
        lt_warm_start=lt_warm_start if lt_warm_start is not None else defaults["lt_warm_start"],
        stochastic_lt=stochastic_lt if stochastic_lt is not None else defaults["stochastic_lt"],
        n_scenarios=n_scenarios if n_scenarios is not None else defaults["n_scenarios"],
        alpha_base=alpha_base if alpha_base is not None else defaults["alpha_base"],
        fan_out_rate=fan_out_rate if fan_out_rate is not None else defaults["fan_out_rate"],
        scenario_seed=scenario_seed if scenario_seed is not None else defaults["scenario_seed"],
    )


@dataclass
class SimulationConfig:
    """Configuration for the year simulation."""
    total_days: int = 288
    step: int = 6
    lt_block: int = 24
    short_term_horizon: int = field(default_factory=lambda: _shared_default_params()["short_term_horizon"])
    holding_cost: float = field(default_factory=lambda: _shared_default_params()["holding_cost"])
    backlog_cost: float = field(default_factory=lambda: _shared_default_params()["backlog_cost"])
    b12_penalty: float = field(default_factory=lambda: _shared_default_params()["b12_penalty"])
    time_limit: int = field(default_factory=lambda: _shared_default_params()["time_limit"])
    initial_inventory: dict[int, float] = field(default_factory=_default_inventory)
    initial_backlog: dict[int, float] = field(default_factory=_default_backlog)
    base_rm_init: float = field(default_factory=lambda: _shared_default_params()["base_rm_init"])
    rm4_init: float = field(default_factory=lambda: _shared_default_params()["rm4_init"])
    rm7_init: float = field(default_factory=lambda: _shared_default_params()["rm7_init"])
    rm8_init: float = field(default_factory=lambda: _shared_default_params()["rm8_init"])
    initial_pipeline: dict = field(default_factory=dict)
    lt_warm_start: bool = field(default_factory=lambda: _shared_default_params()["lt_warm_start"])
    stochastic_lt: bool = field(default_factory=lambda: _shared_default_params()["stochastic_lt"])
    n_scenarios: int = field(default_factory=lambda: _shared_default_params()["n_scenarios"])
    alpha_base: float = field(default_factory=lambda: _shared_default_params()["alpha_base"])
    fan_out_rate: float = field(default_factory=lambda: _shared_default_params()["fan_out_rate"])
    scenario_seed: int = field(default_factory=lambda: _shared_default_params()["scenario_seed"])
    optimizer_config: Optional[OptimizerConfig] = None

    @property
    def total_iterations(self) -> int:
        return self.total_days // self.step

    def to_optimizer_config(self) -> OptimizerConfig:
        """Build the optimizer config used by the shared core."""
        if self.optimizer_config is not None:
            return self.optimizer_config
        return build_optimizer_config(
            total_days=self.total_days,
            step=self.step,
            lt_block=self.lt_block,
            short_term_horizon=self.short_term_horizon,
            holding_cost=self.holding_cost,
            backlog_cost=self.backlog_cost,
            b12_penalty=self.b12_penalty,
            time_limit=self.time_limit,
            initial_inventory=self.initial_inventory,
            initial_backlog=self.initial_backlog,
            base_rm_init=self.base_rm_init,
            rm4_init=self.rm4_init,
            rm7_init=self.rm7_init,
            rm8_init=self.rm8_init,
            initial_pipeline=self.initial_pipeline,
            lt_warm_start=self.lt_warm_start,
            stochastic_lt=self.stochastic_lt,
            n_scenarios=self.n_scenarios,
            alpha_base=self.alpha_base,
            fan_out_rate=self.fan_out_rate,
            scenario_seed=self.scenario_seed,
        )


@dataclass
class WeekResult:
    """Results from one week of simulation."""
    week: int
    start_day: int
    end_day: int
    planned_production: Dict[int, float]
    actual_demand: Dict[int, float]
    ending_inventory: Dict[int, float]
    ending_backlog: Dict[int, float]
    b10_total: float
    week_cost: float
    planner_status: str


class YearSimulation:
    """
    Simulates a full year of production planning with weekly replanning.

    Uses the ProductionOptimizer directly, which implements the full rolling
    horizon heuristic internally. The simulation feeds in demand data and
    collects results.
    """

    PRODUCTS = [1, 2, 3, 4]
    DEMAND_PRODUCTS = [1, 3, 4]

    def __init__(self,
                 full_year_demand: Dict,
                 monthly_demand: Dict = None,
                 sim_config: SimulationConfig = None,
                 initial_inventory: Dict = None,
                 initial_backlog: Dict = None):
        self.sim_config = sim_config or SimulationConfig()
        self.demand = full_year_demand
        self.monthly_demand = monthly_demand

        if initial_inventory:
            self.sim_config.initial_inventory = dict(initial_inventory)
        if initial_backlog:
            self.sim_config.initial_backlog = dict(initial_backlog)

        opt_config = self.sim_config.to_optimizer_config()
        self.sim_config.optimizer_config = opt_config
        self.optimizer = ProductionOptimizer(opt_config)
        self.results: List[WeekResult] = []
        self.progress_callback = None

    def run(self, verbose: bool = True) -> tuple[pd.DataFrame, OptimizationResult]:
        """Run the full-year simulation and return weekly and daily outputs."""
        self.results = []

        if verbose:
            total_iters = self.sim_config.total_iterations
            print(f"Starting Year Simulation: {total_iters} iterations, "
                  f"{self.sim_config.total_days} days")
            print("-" * 60)

        if self.progress_callback:
            self.optimizer.progress_callback = self.progress_callback

        result = self.optimizer.run(self.demand, self.monthly_demand)

        if not result.success:
            if verbose:
                print(f"Optimizer failed: {result.error_message}")
            return pd.DataFrame(), result

        if result.plan_df is not None and not result.plan_df.empty:
            self._aggregate_results(result.plan_df, verbose)

        if verbose:
            print("-" * 60)
            self._print_summary()

        return self._build_results_df(), result

    def _aggregate_results(self, plan_df: pd.DataFrame, verbose: bool) -> None:
        """Aggregate the optimizer's day-by-day results into weekly summaries."""
        cfg = self.sim_config
        step = cfg.step

        for iteration in range(cfg.total_iterations):
            start_day = iteration * step + 1
            end_day = min(start_day + step - 1, cfg.total_days)

            # Get this week's rows from plan
            week_df = plan_df[(plan_df['day'] >= start_day) & (plan_df['day'] <= end_day)]

            if week_df.empty:
                continue

            # Sum production
            planned_prod = {
                1: week_df['p1'].sum(),
                2: week_df['p2'].sum(),
                3: week_df['p3'].sum(),
                4: week_df['p4'].sum(),
            }

            # Get actual demand for this week
            actual_demand = {i: 0 for i in self.DEMAND_PRODUCTS}
            for day in range(start_day, end_day + 1):
                for prod in self.DEMAND_PRODUCTS:
                    actual_demand[prod] += self.demand.get((prod, day), 0)

            # Get ending state from last day of week
            last_row = week_df.iloc[-1]
            ending_inv = {
                1: last_row.get('i1', 0),
                2: last_row.get('i2', 0),
                3: last_row.get('i3', 0),
                4: last_row.get('i4', 0),
            }
            ending_backlog = {
                1: last_row.get('b1', 0),
                2: last_row.get('b2', 0),
                3: last_row.get('b3', 0),
                4: last_row.get('b4', 0),
            }

            b10_total = 0.0
            if 'b10_1' in week_df.columns:
                b10_total = (week_df['b10_1'].sum() +
                            week_df['b10_3'].sum() +
                            week_df['b10_4'].sum())

            holding = (week_df['i1'].sum() + week_df['i2'].sum() +
                      week_df['i3'].sum() + week_df['i4'].sum())
            backlog = (week_df['b1'].sum() + week_df['b2'].sum() +
                      week_df['b3'].sum() + week_df['b4'].sum())
            b10_cost = b10_total * self.optimizer.config.b12_penalty
            week_cost = (
                holding * self.optimizer.config.holding_cost
                + backlog * self.optimizer.config.backlog_cost
                + b10_cost
            )

            week_num = iteration + 1

            if verbose:
                total_prod = sum(planned_prod.values())
                total_demand = sum(actual_demand.values())
                total_backlog = sum(ending_backlog.values())
                print(f"Week {week_num:2d} | Days {start_day:3d}-{end_day:3d} | "
                      f"Prod: {total_prod:8.0f} | Demand: {total_demand:8.0f} | "
                      f"Backlog: {total_backlog:8.0f} | B10: {b10_total:,.0f} | "
                      f"Cost: ₺{week_cost:,.0f}")

            self.results.append(WeekResult(
                week=week_num,
                start_day=start_day,
                end_day=end_day,
                planned_production=planned_prod,
                actual_demand=actual_demand,
                ending_inventory=ending_inv,
                ending_backlog=ending_backlog,
                b10_total=b10_total,
                week_cost=week_cost,
                planner_status="Optimal",
            ))

    def _build_results_df(self) -> pd.DataFrame:
        """Build DataFrame from results."""
        rows = []
        for r in self.results:
            rows.append({
                'week': r.week,
                'start_day': r.start_day,
                'end_day': r.end_day,
                'prod_total': sum(r.planned_production.values()),
                'demand_total': sum(r.actual_demand.values()),
                'inv_total': sum(r.ending_inventory.values()),
                'backlog_total': sum(r.ending_backlog.values()),
                'b10_total': r.b10_total,
                'cost': r.week_cost,
                'status': r.planner_status,
                **{f'prod_{i}': r.planned_production.get(i, 0) for i in self.PRODUCTS},
                **{f'demand_{i}': r.actual_demand.get(i, 0) for i in self.PRODUCTS},
                **{f'inv_{i}': r.ending_inventory.get(i, 0) for i in self.PRODUCTS},
                **{f'backlog_{i}': r.ending_backlog.get(i, 0) for i in self.PRODUCTS},
            })
        return pd.DataFrame(rows)

    def _print_summary(self) -> None:
        """Print simulation summary."""
        df = self._build_results_df()

        if df.empty:
            print("No results to summarize.")
            return

        total_cost = df['cost'].sum()
        total_demand = df['demand_total'].sum()
        total_backlog = df['backlog_total'].sum()
        weeks_with_backlog = (df['backlog_total'] > 0).sum()

        print("\nSIMULATION SUMMARY")
        print(f"  Total Cost:        ₺{total_cost:,.0f}")
        print(f"  Total Demand:      {total_demand:,.0f} units")
        print(f"  Final Backlog:     {df['backlog_total'].iloc[-1]:,.0f} units")
        print(f"  Weeks w/ Backlog:  {weeks_with_backlog} / {len(df)}")
        print(f"  Avg Weekly Cost:   ₺{df['cost'].mean():,.0f}")


def _load_year_demand_data(filepath: Path) -> tuple[Dict, Dict, list[str]]:
    """Load demand data using the shared weekly_planner loader."""
    filepath = Path(filepath)

    if filepath.suffix.lower() == '.csv':
        raise ValueError(
            "CSV files are no longer supported for simulation input. "
            "Use an Excel file with both 'Daily' and 'Monthly' sheets."
        )

    loader = DemandLoader(DEFAULTS_PATH)
    daily_demand, monthly_demand, errors, warnings = loader.load_demand_from_file(filepath)

    if errors:
        raise ValueError("\n".join(errors))
    if daily_demand is None or monthly_demand is None:
        raise ValueError("Failed to load demand data from scenario file.")

    return daily_demand, monthly_demand, warnings


def load_year_demand(filepath: Path) -> tuple[Dict, Dict]:
    """Load full-year demand from an Excel file."""
    daily_demand, monthly_demand, _warnings = _load_year_demand_data(filepath)
    return daily_demand, monthly_demand


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the simulation runner."""
    parser = argparse.ArgumentParser(description="Run year-long rolling horizon simulation")
    parser.add_argument(
        "--scenario",
        type=str,
        default=DEFAULT_SCENARIO_NAME,
        help="Scenario name from templates/simulation_data/ (without .xlsx)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional explicit path to an Excel scenario file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for weekly CSV and daily plan exports",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Explicit path for the weekly aggregated CSV output",
    )
    parser.add_argument("--plan-output", type=Path, default=None, help="Explicit path for the daily plan Excel export")
    parser.add_argument("--quiet", action="store_true", help="Reduce console logging")
    parser.add_argument("--total-days", type=int, default=288, help="Total simulation horizon in days")
    parser.add_argument("--step", type=int, default=6, help="Execution step size in days")
    parser.add_argument("--short-term-horizon", type=int, default=None, help="Short-term lookahead horizon in days")
    parser.add_argument("--lt-block", type=int, default=24, help="Long-term block size in days")
    parser.add_argument("--holding-cost", type=float, default=None, help="Per-unit holding cost")
    parser.add_argument("--backlog-cost", type=float, default=None, help="Per-unit backlog cost")
    parser.add_argument("--b12-penalty", type=float, default=None, help="Penalty for backlog over 12 days")
    parser.add_argument("--time-limit", type=int, default=None, help="Solver time limit in seconds")
    parser.add_argument("--lt-warm-start", action="store_true", help="Enable LT warm start for initial inventory")
    parser.add_argument("--stochastic-lt", action="store_true", help="Enable stochastic long-term planning")
    parser.add_argument("--n-scenarios", type=int, default=None, help="Number of stochastic scenarios")
    parser.add_argument("--alpha-base", type=float, default=None, help="Base demand perturbation size")
    parser.add_argument("--fan-out-rate", type=float, default=None, help="Growth rate of scenario uncertainty")
    return parser.parse_args()


def _resolve_input_path(args: argparse.Namespace) -> Path:
    """Resolve the scenario file path from CLI args."""
    if args.input is not None:
        return args.input.resolve()
    return DEFAULT_SCENARIO_DIR / f"{args.scenario}.xlsx"


def _resolve_output_paths(args: argparse.Namespace, scenario_name: str) -> tuple[Path, Path]:
    """Resolve weekly CSV and daily plan export paths."""
    if args.output is not None:
        weekly_output = args.output
    else:
        output_dir = args.output_dir or DEFAULT_SCENARIO_DIR
        weekly_output = output_dir / f"{scenario_name}_results.csv"

    if args.plan_output is not None:
        plan_output = args.plan_output
    else:
        output_dir = args.output_dir or DEFAULT_SCENARIO_DIR
        plan_output = output_dir / f"{scenario_name}_dayplan.xlsx"

    return weekly_output, plan_output


def main() -> int:
    """Run the simulation CLI."""
    args = _parse_args()
    filepath = _resolve_input_path(args)

    if not filepath.exists():
        print(f"Error: scenario file not found: {filepath}", file=sys.stderr)
        return 1

    try:
        demand, monthly_demand, warnings = _load_year_demand_data(filepath)
    except ValueError as exc:
        print(f"Error loading demand: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(
            f"Loaded {len(demand)} daily demand points and {len(monthly_demand)} "
            f"monthly forecast records from {filepath.stem}"
        )
        for warning in warnings:
            print(f"Warning: {warning}")

    sim_config = SimulationConfig(
        total_days=args.total_days,
        step=args.step,
        lt_block=args.lt_block,
        short_term_horizon=args.short_term_horizon or _shared_default_params()["short_term_horizon"],
        holding_cost=args.holding_cost if args.holding_cost is not None else _shared_default_params()["holding_cost"],
        backlog_cost=args.backlog_cost if args.backlog_cost is not None else _shared_default_params()["backlog_cost"],
        b12_penalty=args.b12_penalty if args.b12_penalty is not None else _shared_default_params()["b12_penalty"],
        time_limit=args.time_limit if args.time_limit is not None else _shared_default_params()["time_limit"],
        lt_warm_start=args.lt_warm_start,
        stochastic_lt=args.stochastic_lt,
        n_scenarios=args.n_scenarios if args.n_scenarios is not None else _shared_default_params()["n_scenarios"],
        alpha_base=args.alpha_base if args.alpha_base is not None else _shared_default_params()["alpha_base"],
        fan_out_rate=args.fan_out_rate if args.fan_out_rate is not None else _shared_default_params()["fan_out_rate"],
    )

    sim = YearSimulation(demand, monthly_demand, sim_config=sim_config)
    results_df, full_result = sim.run(verbose=not args.quiet)

    if not full_result.success:
        print(f"Simulation failed: {full_result.error_message}", file=sys.stderr)
        return 1

    weekly_output, plan_output = _resolve_output_paths(args, filepath.stem)
    weekly_output.parent.mkdir(parents=True, exist_ok=True)
    plan_output.parent.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(weekly_output, index=False)
    if not args.quiet:
        print(f"\nWeekly results saved to {weekly_output}")

    if full_result.plan_df is not None:
        full_result.plan_df.to_excel(plan_output, index=False)
        if not args.quiet:
            print(f"Day-by-day plan saved to {plan_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
