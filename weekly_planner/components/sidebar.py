"""
Sidebar component for settings-only parameters.

Data loading, initial state editing, and BOM editing have moved to
main-area step components (step_data, step_configure, step_review).
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import streamlit as st
import pandas as pd

from core.planning_calendar import next_monday
from components.shared import (
    load_defaults,
    maybe_seed_bom_from_defaults,
)


def render_sidebar() -> dict[str, Any]:
    """Render the settings-only sidebar and return params dict.

    Returns sidebar params: costs, horizons, solver, stochastic, output,
    and run_clicked. Data-loading and configuration params come from the
    main-area step components.
    """
    defaults = load_defaults()
    stoch_defaults = defaults.get('stochastic', {}) or {}
    if "stochastic_lt" not in st.session_state:
        st.session_state["stochastic_lt"] = bool(stoch_defaults.get("enabled", True))
    maybe_seed_bom_from_defaults(defaults)

    logo_path = Path(__file__).parent.parent / "assets" / "logo.jpg"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 12px;"/>'
    else:
        logo_html = '<span>B</span>'

    st.sidebar.markdown(f"""
    <div class="sidebar-brand">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div class="brand-icon">{logo_html}</div>
            <div>
                <div class="brand-name">BobaCo Planner</div>
                <div class="brand-sub">Production Planning</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Costs
    with st.sidebar.expander("Costs", expanded=False):
        cost_defaults = defaults.get('costs', {})

        holding_cost = st.number_input(
            "Holding cost",
            min_value=0.01, max_value=100.0,
            value=float(cost_defaults.get('holding', 1.0)),
            format="%.2f"
        )

        backlog_cost = st.number_input(
            "Backlog cost",
            min_value=1.0, max_value=10000.0,
            value=float(cost_defaults.get('backlog', 160.0)),
            format="%.0f"
        )

        b12_penalty = st.number_input(
            "B12 penalty",
            min_value=100.0, max_value=100000.0,
            value=float(cost_defaults.get('b12_penalty', 10000.0)),
            format="%.0f"
        )

    # Time Horizons
    with st.sidebar.expander("Time Horizons", expanded=False):
        horizon_defaults = defaults.get('horizons', {})

        planning_start_date = st.date_input(
            "Planning start date (Monday)",
            value=next_monday(),
            help="The authoritative planning horizon start. Must be a Monday."
        )
        st.session_state["planning_start_date"] = planning_start_date
        if planning_start_date.weekday() != 0:
            st.error("Planning start date MUST be a Monday.")

        planning_weeks = st.number_input(
            "Total horizon (weeks)",
            min_value=2, max_value=100,
            value=int(horizon_defaults.get('planning_weeks', 8)),
            step=1,
            help="Total simulation horizon in calendar weeks"
        )
        st.session_state["planning_weeks"] = int(planning_weeks)

        closed_dates_raw = st.text_input(
            "Closed dates (YYYY-MM-DD, comma-separated)",
            value="",
            help="Additional dates (e.g. holidays) where no production is allowed."
        )
        closed_dates = []
        if closed_dates_raw.strip():
            for d_str in closed_dates_raw.split(','):
                try:
                    closed_dates.append(pd.to_datetime(d_str.strip()).date())
                except:
                    pass

        sundays_working = st.toggle(
            "Sundays are working days",
            value=bool(st.session_state.get("sundays_working", False)),
            key="sundays_working",
            help="Default: Sundays are closed. Enable to include Sundays in production.",
        )

    # Solver
    with st.sidebar.expander("Solver", expanded=False):
        solver_defaults = defaults.get('solver', {})
        default_time = int(solver_defaults.get('time_limit', 300))

        time_limit_raw = st.slider(
            "Solver time limit (seconds)",
            30,
            2000,
            default_time,
            step=10,
        )

        no_time_limit = st.toggle(
            "No time limit",
            value=False,
            help="If enabled, solver runs without an explicit time cap.",
        )

        if no_time_limit:
            st.caption("**No limit** (unlimited solve time)")
            time_limit = 9999999
        else:
            st.caption(f"{time_limit_raw} seconds")
            time_limit = time_limit_raw

    # Stochastic LT
    with st.sidebar.expander("Stochastic LT Model", expanded=False):
        stochastic_lt = st.toggle(
            "Enable Stochastic LT",
            key="stochastic_lt",
            help="Use two-stage stochastic LP for the long-term model."
        )
        if stochastic_lt:
            alpha_base = st.slider(
                "Deviation range (α)",
                0.05,
                0.30,
                float(stoch_defaults.get('alpha_base', 0.20)),
                0.01,
                help="Base demand perturbation band (e.g. 0.15 = ±15%)."
            )
            n_scenarios = st.number_input(
                "Number of Scenarios",
                value=int(stoch_defaults.get('n_scenarios', 10)),
                min_value=3,
                max_value=50,
                help="2 extremes + (N-2) random scenarios",
            )
            fan_out_rate = st.slider(
                "Fan-out rate",
                0.0,
                2.0,
                float(stoch_defaults.get('fan_out_rate', 0.0)),
                0.1,
                help="Controls uncertainty growth over time (0=none, 0.5=50%, 1.0=100%)."
            )
        else:
            alpha_base = float(stoch_defaults.get('alpha_base', 0.20))
            n_scenarios = int(stoch_defaults.get('n_scenarios', 10))
            fan_out_rate = float(stoch_defaults.get('fan_out_rate', 0.0))

    # Run Output
    st.sidebar.markdown("---")
    default_run_dir = str(Path(__file__).resolve().parent / "runs")
    with st.sidebar.expander("Run Output", expanded=False):
        auto_save = st.toggle(
            "Auto-save runs",
            value=True,
            help="Automatically save each run to a runs folder or custom path.",
        )
        output_dir = st.text_input(
            "Output directory",
            value=default_run_dir,
            help="Folder where timestamped run folders are saved",
            disabled=not auto_save,
        )

    st.sidebar.markdown("---")

    # Run Button
    run_clicked = st.sidebar.button(
        "Generate Schedule",
        type="primary",
        width="stretch"
    )

    params = {
        'holding_cost': holding_cost,
        'backlog_cost': backlog_cost,
        'b12_penalty': b12_penalty,
        'planning_start_date': planning_start_date,
        'planning_weeks': planning_weeks,
        'closed_dates': closed_dates,
        'sundays_working': sundays_working,
        'time_limit': time_limit,
        'stochastic_lt': stochastic_lt,
        'n_scenarios': n_scenarios,
        'alpha_base': alpha_base,
        'fan_out_rate': fan_out_rate,
        'auto_save': auto_save,
        'output_dir': output_dir,
        'run_clicked': run_clicked,
    }

    return params