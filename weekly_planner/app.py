"""
BobaCo Production Planner

Runs the rolling horizon optimizer on uploaded demand data.
Uses the latest model with machine-level production decisions.

Input: Excel file with Daily and Monthly sheets. The optimizer internally
handles LT + ST decomposition in single-shot mode (one LT + one ST solve).
"""
from __future__ import annotations

import streamlit as st
from pathlib import Path
import pandas as pd
import sys
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

try:
    import highspy  # noqa: F401
except ImportError:
    sys.exit("ERROR: highspy is required for the HiGHS solver. Install with: pip install highspy")

from core.optimizer import ProductionOptimizer
from core.export_run import save_run_to_folder
from core.config_builder import params_to_config
from components.export import render_export
from components.lt_decisions import render_lt_decisions
from components.sidebar import render_sidebar
from components.results import render_data_table, render_cost_summary
from components.charts import render_charts
from components.step_data import render_step_data
from components.step_configure import render_step_configure
from components.step_review import render_step_review


st.set_page_config(
    page_title="BobaCo Production Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css() -> None:
    css_path = Path(__file__).parent / "styles" / "theme.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        if hasattr(st, "html"):
            st.html(f"<style>{css}</style>")
        else:
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def main() -> None:
    load_css()

    if 'result' not in st.session_state:
        st.session_state.result = None

    # Sidebar returns settings-only params (costs, horizons, solver, stochastic, output)
    sidebar_params = render_sidebar()

    # Title Card
    st.markdown("""
    <div class="hero-card">
        <h1>Production Planner</h1>
        <p>Plan weekly production from demand, inventory, and raw-material inputs in one clean flow.</p>
    </div>
    """, unsafe_allow_html=True)

    # Show results if available, otherwise show the setup steps
    if st.session_state.result is not None and st.session_state.result['success']:
        result = st.session_state.result
        plan_df = result['plan_df']
        solver_log = result.get('solver_log', [])

        # Back to Setup button
        if st.button("New Run", type="secondary", key="new_run_btn"):
            st.session_state.result = None
            st.rerun()

        # Auto-save feedback
        if result.get('saved_folder'):
            st.success(f"Run saved to `{result['saved_folder']}`")

        # Cost summary
        render_cost_summary(result)

        # Execution Log
        with st.expander("Execution Log", expanded=False):
            if solver_log:
                total_duration = sum(l.get('Duration', 0) for l in solver_log)
                total_steps = len(solver_log)

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Solve Time", f"{total_duration:.2f}s")
                m2.metric("Optimization Steps", total_steps)

                log_data = []
                for entry in solver_log:
                    row = {
                        'Day': entry.get('Day'),
                        'Model': entry.get('Model'),
                        'Status': entry.get('Status'),
                        'Obj': entry.get('Objective'),
                        'b12_1': entry.get('b12_1', 0),
                        'b12_2': entry.get('b12_2', 0),
                        'b12_3': entry.get('b12_3', 0),
                        'b12_4': entry.get('b12_4', 0),
                        'Time (s)': f"{entry.get('Duration', 0):.2f}",
                        'Gap': f"{entry['Gap']:.2%}" if entry.get('Gap') is not None else "-"
                    }
                    log_data.append(row)

                log_df = pd.DataFrame(log_data)
                st.dataframe(
                    log_df.style.format({'Obj': '{:,.2f}'}),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.info("No execution log available.")

        # LT Decisions viewer
        lt_entries = [e for e in solver_log if e.get('Model', '').startswith('LT')]
        if lt_entries:
            with st.expander("LT Decisions (block-by-block plans)", expanded=False):
                render_lt_decisions(lt_entries, result.get('config'))

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Visualization", "Data Table", "Export"])
        with tab1:
            render_charts(plan_df)
        with tab2:
            render_data_table(plan_df)
        with tab3:
            render_export(result)

    elif st.session_state.result is not None:
        err = st.session_state.result.get('error_message', 'Optimization failed.')
        st.error(err)
        if 'infeasible' in err.lower() or 'infeasibility' in err.lower():
            st.info("Tip: Try reducing demand, increasing initial inventory, or enabling LT Warm-Start.")
        if st.button("Back to Setup", key="back_to_setup_err_btn"):
            st.session_state.result = None
            st.rerun()

    else:
        # Step 1: Load Data
        data_result = render_step_data()

        # Step 2: Configure
        configure_result = render_step_configure(
            planning_start_date=sidebar_params['planning_start_date'],
            planning_weeks=sidebar_params['planning_weeks'],
            closed_dates=sidebar_params['closed_dates'],
            sundays_working=sidebar_params.get('sundays_working', False),
        )

        # Step 3: Review & Generate
        merged_params = {}
        merged_params.update(sidebar_params)
        merged_params.update(data_result)
        merged_params.update(configure_result)

        # Ensure demand data is attached if available
        if st.session_state.get('demand_data') is not None:
            merged_params['demand_data'] = st.session_state.demand_data
            merged_params['monthly_demand'] = st.session_state.get('monthly_demand')

        # Handle initial state snapshot in merged params
        if merged_params.get('custom_initial_state_applied') and st.session_state.get("applied_initial_state_snapshot"):
            merged_params.update(st.session_state["applied_initial_state_snapshot"])

        # Handle BOM in merged params
        if merged_params.get('custom_rm_usage_applied') and st.session_state.get("applied_rm_usage") is not None:
            merged_params["rm_usage"] = dict(st.session_state["applied_rm_usage"])

        # Handle machine capacity in merged params
        if merged_params.get('custom_capacity_applied') and st.session_state.get("applied_machine_capacity") is not None:
            applied_cap = st.session_state["applied_machine_capacity"]
            merged_params["cap_l1"] = dict(applied_cap.get("cap_l1", {}))
            merged_params["cap_p3"] = dict(applied_cap.get("cap_p3", {}))
            merged_params["cap_p4"] = float(applied_cap.get("cap_p4", 80000.0))

        render_step_review(merged_params)

        # Run optimization (sidebar button or main-area button)
        generate_requested = merged_params.get('run_clicked') or st.session_state.pop('generate_requested', False)
        if generate_requested:
            if st.session_state.get('demand_data') is None:
                st.error("Please load demand data first. Use Step 1 above to upload a file and click **Load Data**.")
            else:
                session_monthly = st.session_state.get('monthly_demand')
                if session_monthly is None or (isinstance(session_monthly, pd.DataFrame) and session_monthly.empty):
                    st.error("Monthly forecast is required. Your demand file must include a 'Monthly' sheet with columns: month, product, demand.")
                    return

                merged_params['demand_data'] = st.session_state.demand_data
                merged_params['monthly_demand'] = session_monthly
                run_optimization(merged_params)


def run_optimization(params: dict) -> None:
    progress_text = "Optimization in progress. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    def progress_callback(iteration, total_iterations, message=""):
        progress_value = float(iteration) / float(total_iterations) if total_iterations > 0 else 0.0
        progress_value = min(1.0, max(0.0, progress_value))
        progress_bar.progress(progress_value, text=f"{progress_text} {message}")

    with st.spinner("Optimizing schedule..."):
        monthly_demand = params.get('monthly_demand')
        if monthly_demand is None or (isinstance(monthly_demand, pd.DataFrame) and monthly_demand.empty):
            st.error("Monthly forecast is missing. Cannot run optimization without LT forecast.")
            return

        config = params_to_config(params)

        for w in config.build_warnings:
            st.warning(w)

        optimizer = ProductionOptimizer(config)
        optimizer.progress_callback = progress_callback

        try:
            result = optimizer.run()
        except Exception as e:
            progress_bar.empty()
            st.session_state.result = {
                'success': False,
                'error_message': str(e),
                'plan_df': None,
                'cost_summary': {},
                'solver_log': [],
            }
            st.rerun()

        saved_folder: Optional[str] = None
        auto_save = params.get('auto_save', False)
        output_dir = params.get('output_dir')
        if auto_save and result.success and result.plan_df is not None:
            try:
                folder = save_run_to_folder(
                    result=result,
                    config=config,
                    scenario_name="weekly_plan",
                    weekly_df=None,
                    base_dir=output_dir or None,
                )
                saved_folder = str(folder)
            except Exception as e:
                st.warning(f"Failed to auto-save run: {e}")

        progress_bar.empty()
        st.session_state.result = {
            'success': result.success,
            'status': result.status,
            'plan_df': result.plan_df,
            'cost_summary': result.cost_summary,
            'solver_log': result.solver_log,
            'error_message': result.error_message,
            'full_result': result,
            'config': config,
            'saved_folder': saved_folder,
        }
        st.rerun()


if __name__ == "__main__":
    main()