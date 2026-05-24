"""
Export module for saving detailed run results to Excel and disk.
"""
from __future__ import annotations

import json
import pandas as pd
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from dataclasses import fields


def _config_to_dict(config: Any) -> dict:
    """Convert OptimizerConfig to a serializable dict."""
    d = {}
    for f in fields(config):
        val = getattr(config, f.name)
        if f.name == "rm_usage" and val is not None and isinstance(val, dict):
            d[f.name] = {f"{i}_{s}": q for (i, s), q in val.items()}
        elif isinstance(val, dict):
            # Convert dicts with int keys to string keys for JSON
            d[f.name] = {str(k): v for k, v in val.items()}
        else:
            d[f.name] = val
    return d


def _build_config_df(config, scenario_name: str, timestamp: str) -> pd.DataFrame:
    """Build a config sheet DataFrame."""
    rows = [
        {"Parameter": "Scenario", "Value": scenario_name},
        {"Parameter": "Timestamp", "Value": timestamp},
        {"Parameter": "Planning Start Date", "Value": str(getattr(config, "planning_start_date", ""))},
        {"Parameter": "Planning Weeks", "Value": getattr(config, "planning_weeks", "")},
        {"Parameter": "Horizon End Date", "Value": str(getattr(config, "horizon_end_date", ""))},
        {"Parameter": "Total Days", "Value": getattr(config, "total_days", "")},
        {"Parameter": "Short Term Step", "Value": getattr(config, "short_term_step", "")},
        {
            "Parameter": "Closed Dates",
            "Value": ", ".join(str(d) for d in (getattr(config, "closed_dates", []) or [])),
        },
        {"Parameter": "---", "Value": "---"},
    ]
    cfg_dict = _config_to_dict(config)
    for k, v in cfg_dict.items():
        rows.append({"Parameter": k, "Value": str(v)})
    return pd.DataFrame(rows)


def _build_summary_df(
    cost_summary: dict, plan_df: pd.DataFrame, weekly_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Build a summary KPI sheet."""
    rows = [
        {"Metric": "Total Cost", "Value": cost_summary.get("total", 0)},
        {"Metric": "Holding Cost", "Value": cost_summary.get("holding", 0)},
        {"Metric": "Backlog Cost", "Value": cost_summary.get("backlog", 0)},
        {"Metric": "B12 Penalty", "Value": cost_summary.get("b12_penalty", 0)},
        {"Metric": "---", "Value": "---"},
        {"Metric": "Total Days", "Value": len(plan_df) if plan_df is not None else 0},
    ]

    if weekly_df is not None and not weekly_df.empty:
        rows.extend([
            {"Metric": "Total Weeks", "Value": len(weekly_df)},
            {"Metric": "Weeks with Backlog", "Value": int((weekly_df["backlog_total"] > 0).sum()) if "backlog_total" in weekly_df.columns else 0},
            {"Metric": "Total Demand", "Value": weekly_df["demand_total"].sum() if "demand_total" in weekly_df.columns else 0},
            {"Metric": "Total Production", "Value": weekly_df["prod_total"].sum() if "prod_total" in weekly_df.columns else 0},
            {"Metric": "Final Backlog", "Value": weekly_df["backlog_total"].iloc[-1] if "backlog_total" in weekly_df.columns else 0},
            {"Metric": "Avg Weekly Cost", "Value": weekly_df["cost"].mean() if "cost" in weekly_df.columns else 0},
        ])

    return pd.DataFrame(rows)


def _build_solver_log_df(solver_log: list[dict]) -> pd.DataFrame:
    """Build a clean solver log DataFrame (without nested dicts)."""
    rows = []
    for entry in solver_log:
        rows.append({
            "Day": entry.get("Day"),
            "Model": entry.get("Model"),
            "Status": entry.get("Status"),
            "Objective": entry.get("Objective"),
            "Stage1Cost": entry.get("Stage1Cost", ""),
            "Stage2Cost": entry.get("Stage2Cost", ""),
            "Duration_s": round(entry.get("Duration", 0), 3),
            "Gap": entry.get("Gap", ""),
        })
    return pd.DataFrame(rows)


def _build_lt_step_df(lt_entry: dict, config: Any) -> pd.DataFrame:
    """Build a block-by-block table for one LT solve step.

    Columns: Block, Period, Start/End Date, Demand Source, P1..P4 Prod, P1..P4 Inv, P1/P3/P4 Backlog,
              P1/P3/P4 Demand, Inv Targets (if boundary).
    """
    production = lt_entry.get("Production", {})
    inventory = lt_entry.get("Inventory", {})
    backlog = lt_entry.get("Backlog", {})
    demand = lt_entry.get("Demand", {})
    targets = lt_entry.get("Targets", {})
    i_state = lt_entry.get("I_state", {})
    b_state = lt_entry.get("B_state", {})
    blocks_meta = {b['block_index']: b for b in getattr(config, 'lt_blocks', [])}

    # Determine how many blocks we have data for
    blocks = sorted(blocks_meta.keys()) if blocks_meta else (sorted(set(t for (_, t) in production.keys())) if production else list(range(1, 13)))

    rows = []

    # State snapshot row
    rows.append({
        "Block": "Init",
        "Period": "",
        "Demand Source": "",
        "Start Date": "",
        "End Date": "",
        "Production Days": "",
        "P1 Prod": "",
        "P2 Prod": "",
        "P3 Prod": "",
        "P4 Prod": "",
        "P1 Inv": i_state.get(1, 0),
        "P2 Inv": i_state.get(2, 0),
        "P3 Inv": i_state.get(3, 0),
        "P4 Inv": i_state.get(4, 0),
        "P1 Backlog": b_state.get(1, 0),
        "P3 Backlog": b_state.get(3, 0),
        "P4 Backlog": b_state.get(4, 0),
        "P1 Demand": "",
        "P3 Demand": "",
        "P4 Demand": "",
        "P1 Target": "",
        "P2 Target": "",
        "P3 Target": "",
        "P4 Target": "",
    })

    for t in blocks:
        meta = blocks_meta.get(t, {})
        calendar_days = meta.get('calendar_day_indices') or []
        boundary_day = calendar_days[-1] if calendar_days else None

        row = {
            "Block": t,
            "Period": meta.get('period_key', ''),
            "Demand Source": meta.get('demand_source', ''),
            "Start Date": meta.get('start_date', ''),
            "End Date": meta.get('end_date', ''),
            "Production Days": meta.get('production_days_available', ''),
            "P1 Prod": round(production.get((1, t), 0), 1),
            "P2 Prod": round(production.get((2, t), 0), 1),
            "P3 Prod": round(production.get((3, t), 0), 1),
            "P4 Prod": round(production.get((4, t), 0), 1),
            "P1 Inv": round(inventory.get((1, t), 0), 1),
            "P2 Inv": round(inventory.get((2, t), 0), 1),
            "P3 Inv": round(inventory.get((3, t), 0), 1),
            "P4 Inv": round(inventory.get((4, t), 0), 1),
            "P1 Backlog": round(backlog.get((1, t), 0), 1),
            "P3 Backlog": round(backlog.get((3, t), 0), 1),
            "P4 Backlog": round(backlog.get((4, t), 0), 1),
            "P1 Demand": round(demand.get((1, t), 0), 1),
            "P3 Demand": round(demand.get((3, t), 0), 1),
            "P4 Demand": round(demand.get((4, t), 0), 1),
            "P1 Target": round(targets.get((boundary_day, 1), 0), 1) if (boundary_day, 1) in targets else "",
            "P2 Target": round(targets.get((boundary_day, 2), 0), 1) if (boundary_day, 2) in targets else "",
            "P3 Target": round(targets.get((boundary_day, 3), 0), 1) if (boundary_day, 3) in targets else "",
            "P4 Target": round(targets.get((boundary_day, 4), 0), 1) if (boundary_day, 4) in targets else "",
        }
        rows.append(row)

    return pd.DataFrame(rows)


def _build_week_definitions_df(config: Any) -> pd.DataFrame:
    rows = []
    for w in getattr(config, 'week_definitions', []) or []:
        rows.append(
            {
                'Week': w.get('week_index'),
                'Start Date': w.get('start_date'),
                'End Date': w.get('end_date'),
                'Calendar Day Count': len(w.get('day_indices', [])),
                'Production Day Count': len(w.get('production_day_indices', [])),
                'Contains Closed Dates': w.get('contains_closed_dates', False),
            }
        )
    return pd.DataFrame(rows)


def _build_lt_blocks_df(config: Any) -> pd.DataFrame:
    rows = []
    for b in getattr(config, 'lt_blocks', []) or []:
        rows.append(
            {
                'Block': b.get('block_index'),
                'Period': b.get('period_key'),
                'Demand Source': b.get('demand_source'),
                'Start Date': b.get('start_date'),
                'End Date': b.get('end_date'),
                'Calendar Days': b.get('calendar_days_in_block'),
                'Production Days': b.get('production_days_available'),
            }
        )
    return pd.DataFrame(rows)


def export_run_to_excel(
    result: Any,
    config: Any,
    scenario_name: str = "unknown",
    weekly_df: Optional[pd.DataFrame] = None,
    output_path: Optional[Path] = None,
) -> BytesIO:
    """
    Write a comprehensive multi-sheet Excel workbook for a run.

    Args:
        result: OptimizationResult from the optimizer
        config: OptimizerConfig used for the run
        scenario_name: Name of the demand scenario
        weekly_df: Optional aggregated weekly results DataFrame
        output_path: If provided, also write to this file path

    Returns:
        BytesIO buffer with the Excel workbook (for download buttons)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # 1. Config sheet
        config_df = _build_config_df(config, scenario_name, timestamp)
        config_df.to_excel(writer, sheet_name="Config", index=False)

        # 2. Summary sheet
        summary_df = _build_summary_df(result.cost_summary, result.plan_df, weekly_df)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # 3. Solver log sheet
        solver_log = getattr(result, "solver_log", []) or []
        log_df = _build_solver_log_df(solver_log)
        log_df.to_excel(writer, sheet_name="Solver Log", index=False)

        # 4. LT Step sheets
        lt_entries = [e for e in solver_log if e.get("Model", "").startswith("LT")]
        for idx, lt_entry in enumerate(lt_entries, 1):
            lt_df = _build_lt_step_df(lt_entry, config)
            sheet_name = f"LT Step {idx} (d{lt_entry.get('Day', '?')})"
            # Excel sheet names max 31 chars
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            lt_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # 5. Daily Plan sheet
        if result.plan_df is not None and not result.plan_df.empty:
            result.plan_df.to_excel(writer, sheet_name="Daily Plan", index=False)

        # 6. Weekly Summary sheet
        if weekly_df is not None and not weekly_df.empty:
            weekly_df.to_excel(writer, sheet_name="Weekly Summary", index=False)

        # 7. Calendar week definitions
        week_df = _build_week_definitions_df(config)
        if not week_df.empty:
            week_df.to_excel(writer, sheet_name="Week Definitions", index=False)

        # 8. LT blocks metadata
        lt_blocks_df = _build_lt_blocks_df(config)
        if not lt_blocks_df.empty:
            lt_blocks_df.to_excel(writer, sheet_name="LT Blocks", index=False)

        # Apply formatting
        _apply_formatting(writer)

    buf.seek(0)

    # Also write to disk if path given
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())
        buf.seek(0)

    return buf


def _apply_formatting(writer: Any) -> None:
    """Apply basic formatting to all sheets: bold headers, freeze panes, column widths."""
    from openpyxl.styles import Font, Alignment, numbers

    wb = writer.book
    header_font = Font(bold=True)
    num_fmt = "#,##0.0"

    for ws in wb.worksheets:
        # Bold headers
        for cell in ws[1]:
            cell.font = header_font

        # Freeze top row
        ws.freeze_panes = "A2"

        # Auto-width columns (approximate)
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    val = str(cell.value) if cell.value is not None else ""
                    max_len = max(max_len, len(val))
                except:
                    pass
            ws.column_dimensions[col_letter].width = min(max_len + 3, 25)

        # Number format for numeric cells (skip header row)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = num_fmt


def save_run_to_folder(
    result: Any,
    config: Any,
    scenario_name: str,
    weekly_df: Optional[pd.DataFrame] = None,
    base_dir: Optional[str] = None,
) -> Path:
    """
    Save a complete run to a timestamped folder.

    Creates:
      <base_dir>/YYYY-MM-DD_HHMMSS_<scenario>/
        - detailed_report.xlsx  (multi-sheet workbook)
        - solver_log.csv        (flat solver log)
        - config.json           (all config parameters)
        - plots/                (directory with HTML charts)

    Returns:
        Path to the created folder
    """
    if base_dir is None:
        # Default: Data/runs relative to the workspace root (477/)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "Data" / "runs"
    else:
        base_dir = Path(base_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_name = scenario_name.replace(" ", "_").replace("/", "_")
    folder = base_dir / f"{timestamp}_{safe_name}"
    folder.mkdir(parents=True, exist_ok=True)

    # 1. Multi-sheet Excel
    excel_path = folder / "detailed_report.xlsx"
    export_run_to_excel(
        result=result,
        config=config,
        scenario_name=scenario_name,
        weekly_df=weekly_df,
        output_path=excel_path,
    )

    # 2. Solver log CSV
    solver_log = getattr(result, "solver_log", []) or []
    log_df = _build_solver_log_df(solver_log)
    log_df.to_csv(folder / "solver_log.csv", index=False)

    # 3. Config JSON
    cfg_dict = _config_to_dict(config)
    cfg_dict["_scenario"] = scenario_name
    cfg_dict["_timestamp"] = timestamp
    with open(folder / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg_dict, f, indent=2, default=str)

    # 4. Plots (as interactive HTML)
    if result.plan_df is not None and not result.plan_df.empty:
        try:
            import plotly.io as pio
            # Support both package imports and running app.py from inside weekly_planner/.
            try:
                from weekly_planner.components.charts import (
                    get_inventory_chart, get_rm_inventory_chart,
                    get_production_charts, get_backlog_chart,
                    get_overview_chart, get_weekly_schedule_chart
                )
            except ImportError:
                from components.charts import (
                    get_inventory_chart, get_rm_inventory_chart,
                    get_production_charts, get_backlog_chart,
                    get_overview_chart, get_weekly_schedule_chart
                )

            plots_dir = folder / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # Save Inventory
            pio.write_html(get_inventory_chart(result.plan_df), plots_dir / "inventory.html")
            
            # Save RM Inventory
            rm_fig = get_rm_inventory_chart(result.plan_df)
            if rm_fig:
                pio.write_html(rm_fig, plots_dir / "rm_inventory.html")
                
            # Save Production
            p1_fig, p2_fig = get_production_charts(result.plan_df)
            pio.write_html(p1_fig, plots_dir / "production_line1.html")
            pio.write_html(p2_fig, plots_dir / "production_line2.html")
            
            # Save Backlog
            pio.write_html(get_backlog_chart(result.plan_df), plots_dir / "backlog.html")
            
            # Save Overview
            pio.write_html(get_overview_chart(result.plan_df), plots_dir / "overview.html")
            
            # Save Weekly Schedule
            pio.write_html(get_weekly_schedule_chart(result.plan_df), plots_dir / "weekly_schedule.html")
        except Exception as e:
            print(f"Warning: Failed to save plots to folder: {e}")

    return folder

