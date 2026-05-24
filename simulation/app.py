"""
BobaCo Simulation Dashboard

Year-long rolling horizon simulation with interactive visualization.
Separate from the main production planner app.

Run with: streamlit run simulation_app.py
"""
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from io import BytesIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# HiGHS via highspy is required — optimizer will not run without it
try:
    import highspy  # noqa: F401
except ImportError:
    sys.exit("ERROR: highspy is required for the HiGHS solver. Install with: pip install highspy")

from weekly_planner.core.export_run import export_run_to_excel, save_run_to_folder
from simulation import (
    DEFAULT_SCENARIO_DIR,
    SimulationConfig,
    YearSimulation,
    load_year_demand,
)


st.set_page_config(
    page_title="BobaCo Simulation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    css_path = Path(__file__).parent / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    load_css()
    
    # Session state
    if 'sim_results' not in st.session_state:
        st.session_state.sim_results = None
    if 'sim_running' not in st.session_state:
        st.session_state.sim_running = False
    
    # Sidebar
    render_sidebar()
    
    # Main content
    st.markdown("""
    <div class="hero-card">
        <h1>Year-Long Simulation</h1>
        <p>Test the production planner with 48 weekly replanning cycles over a full year.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Results
    if st.session_state.sim_results is not None:
        render_results(st.session_state.sim_results)
    else:
        show_instructions()


def render_sidebar():
    """Render sidebar with simulation controls."""
    with st.sidebar:
        st.markdown("### Simulation Settings")

        # Scenario selection
        data_dir = DEFAULT_SCENARIO_DIR
        scenarios = []
        if data_dir.exists():
            seen = set()
            for f in data_dir.glob("*.xlsx"):
                if f.stem not in seen:
                    scenarios.append(f.stem)
                    seen.add(f.stem)

        if not scenarios:
            st.warning("No scenarios found. Run generate_year_data.py first.")
            return

        scenario = st.selectbox(
            "Demand Scenario",
            scenarios,
            index=scenarios.index("realistic_seasonal") if "realistic_seasonal" in scenarios else 0
        )

        st.markdown("---")
        st.markdown("##### Cost Configuration")

        col1, col2 = st.columns(2)
        with col1:
            holding_cost = st.number_input("Holding Cost", value=1.0, step=0.1)
        with col2:
            backlog_cost = st.number_input("Backlog Cost", value=160.0, step=10.0)
        b12_penalty = st.number_input("B12 Penalty", value=10000.0, step=1000.0)
        
        # Time limit slider with "No limit" option
        time_limit_raw = st.slider("Solver Time Limit", 30, 2000, 300, step=10)
        if time_limit_raw == 2000:
            st.caption("**No limit** (unlimited solve time)")
            time_limit = 9999999  # Very large number for "no limit"
        else:
            st.caption(f"{time_limit_raw} seconds")
            time_limit = time_limit_raw

        st.markdown("---")
        st.markdown("##### Time Horizons")
        col1, col2 = st.columns(2)
        with col1:
            total_days = st.number_input("Total Days", value=288, step=6)
        with col2:
            step_days = st.number_input("Week Length", value=6, step=1)
        lt_block = st.number_input("LT Block (days)", value=24, step=6)

        st.markdown("---")
        st.markdown("##### Initial State")
        lt_warm_start = st.toggle(
            "LT Warm-Start",
            value=False,
            help="Solve LT model at day 0 to automatically determine optimal initial inventory. Overrides manual initial inventory values."
        )
        with st.expander("Inventory & Backlog", expanded=False):
            st.caption("Starting inventory levels (units)")
            ic1, ic2 = st.columns(2)
            with ic1:
                init_inv_1 = st.number_input("P1 Inventory", min_value=0.0, value=10000.0, step=1000.0, key="sim_inv_1")
                init_inv_3 = st.number_input("P3 Inventory", min_value=0.0, value=500000.0, step=10000.0, key="sim_inv_3")
            with ic2:
                init_inv_2 = st.number_input("P2 Inventory", min_value=0.0, value=10000.0, step=1000.0, key="sim_inv_2")
                init_inv_4 = st.number_input("P4 Inventory", min_value=0.0, value=0.0, step=10000.0, key="sim_inv_4")

            st.caption("Starting backlog levels (units)")
            bc1, bc2 = st.columns(2)
            with bc1:
                init_bl_1 = st.number_input("P1 Backlog", min_value=0.0, value=0.0, step=100.0, key="sim_bl_1")
                init_bl_3 = st.number_input("P3 Backlog", min_value=0.0, value=0.0, step=10000.0, key="sim_bl_3")
            with bc2:
                init_bl_2 = st.number_input("P2 Backlog", min_value=0.0, value=0.0, step=100.0, key="sim_bl_2")
                init_bl_4 = st.number_input("P4 Backlog", min_value=0.0, value=0.0, step=10000.0, key="sim_bl_4")

            st.caption("Raw material initial stock")
            base_rm_init = st.number_input("Base RM Stock", min_value=0.0, value=2000000.0, step=100000.0, key="sim_base_rm")
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                rm4_init = st.number_input("RM 4", min_value=0.0, value=6000000.0, step=500000.0, key="sim_rm4")
            with rc2:
                rm7_init = st.number_input("RM 7", min_value=0.0, value=4000000.0, step=500000.0, key="sim_rm7")
            with rc3:
                rm8_init = st.number_input("RM 8", min_value=0.0, value=500000.0, step=100000.0, key="sim_rm8")

        st.markdown("---")
        st.markdown("##### Stochastic LT Model")
        stochastic_lt = st.toggle("Enable Stochastic LT", value=False,
                                   help="Use two-stage stochastic LP for the long-term model")
        if stochastic_lt:
            alpha_base = st.slider("Deviation Range (α)", 0.05, 0.30, 0.15, 0.01,
                                    help="Base perturbation range (e.g. 0.15 = ±15%)")
            n_scenarios = st.number_input("Number of Scenarios", value=10, min_value=3, max_value=50,
                                           help="2 extremes + (N-2) random scenarios")
            fan_out_rate = st.slider("Fan-out Rate", 0.0, 2.0, 0.5, 0.1,
                                     help="Uncertainty growth strength (0=none, 0.5=50%, 1.0=100%)")
        else:
            alpha_base = 0.15
            n_scenarios = 10
            fan_out_rate = 0.5

        st.markdown("---")
        st.markdown("##### Run Output")
        auto_save = st.toggle(
            "Auto-save runs",
            value=True,
            help="Automatically save each run to a 'runs' folder next to this app or a custom path.",
        )
        default_run_dir = str(Path(__file__).resolve().parent / "runs")
        output_dir = st.text_input(
            "Output directory",
            value=default_run_dir,
            help="Folder where timestamped run folders are saved",
            label_visibility="collapsed" if not auto_save else "visible",
            disabled=not auto_save,
        )

        st.markdown("---")

        # Run button
        if st.button("Run Simulation", type="primary", use_container_width=True):
            sim_config = SimulationConfig(
                total_days=total_days,
                step=step_days,
                lt_block=lt_block,
                holding_cost=holding_cost,
                backlog_cost=backlog_cost,
                b12_penalty=b12_penalty,
                time_limit=time_limit,
                initial_inventory={1: init_inv_1, 2: init_inv_2, 3: init_inv_3, 4: init_inv_4},
                initial_backlog={1: init_bl_1, 2: init_bl_2, 3: init_bl_3, 4: init_bl_4},
                base_rm_init=base_rm_init,
                rm4_init=rm4_init,
                rm7_init=rm7_init,
                rm8_init=rm8_init,
                lt_warm_start=lt_warm_start,
                stochastic_lt=stochastic_lt,
                n_scenarios=n_scenarios,
                alpha_base=alpha_base,
                fan_out_rate=fan_out_rate,
            )
            run_simulation(scenario, sim_config,
                           auto_save=auto_save,
                           output_dir=output_dir if auto_save else None)


def run_simulation(scenario, sim_config, auto_save=False, output_dir=None):
    """Run the year-long simulation."""
    data_dir = DEFAULT_SCENARIO_DIR
    filepath = data_dir / f"{scenario}.xlsx"

    if not filepath.exists():
        st.error(f"Scenario file not found: {scenario}.xlsx")
        return

    try:
        daily_demand, monthly_demand = load_year_demand(filepath)
    except ValueError as e:
        st.error(str(e))
        return

    if not monthly_demand:
        st.error("Monthly forecast data is missing from the scenario file. Cannot run simulation.")
        return

    # Progress bar
    progress = st.progress(0, text="Starting simulation...")

    # Run simulation
    sim = YearSimulation(
        full_year_demand=daily_demand,
        monthly_demand=monthly_demand,
        sim_config=sim_config,
    )

    # Set progress callback on optimizer
    total_iters = sim_config.total_iterations
    def update_progress(iteration, total, msg):
        progress.progress(iteration / total, text=f"Step {iteration}/{total}: {msg}")

    sim.optimizer.progress_callback = update_progress

    # Run the full optimization + aggregation
    results_df, full_result = sim.run(verbose=False)

    progress.empty()

    # Auto-save to disk
    saved_folder = None
    if auto_save and full_result and full_result.success:
        try:
            saved_folder = save_run_to_folder(
                result=full_result,
                config=sim_config.optimizer_config,
                scenario_name=scenario,
                weekly_df=results_df,
                base_dir=output_dir,
            )
        except Exception as e:
            st.warning(f"Auto-save failed: {e}")

    # Store results
    st.session_state.sim_results = {
        'scenario': scenario,
        'df': results_df,
        'config': sim_config,
        'full_result': full_result,
        'saved_folder': str(saved_folder) if saved_folder else None,
    }

    msg = "Simulation completed!"
    if saved_folder:
        msg += f" Results saved to `{saved_folder}`"
    st.success(msg)
    st.rerun()


def render_results(results):
    """Render simulation results with charts and tables."""
    df = results['df']
    scenario = results['scenario']
    
    # KPI Cards
    render_kpi_cards(df)
    
    # Execution Log
    full_result = results.get('full_result')
    solver_log = []
    if full_result:
        # full_result is an OptimizationResult object (dataclass)
        solver_log = getattr(full_result, 'solver_log', [])
    with st.expander("Execution Log", expanded=False):
        if solver_log:
            total_duration = sum(l.get('Duration', 0) for l in solver_log)
            # Filter distinct optimization steps (some might be just recording steps)
            optim_steps = [l for l in solver_log if l.get('Status')]
            total_steps = len(optim_steps)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Solve Time", f"{total_duration:.2f}s")
            m2.metric("Optimization Steps", total_steps)
            
            # Convert log to readable DF
            log_data = []
            for entry in solver_log:
                row = {
                    'Day': entry.get('Day'),
                    'Model': entry.get('Model'),
                    'Status': entry.get('Status'),
                    'Obj': entry.get('Objective'),
                    'Time (s)': f"{entry.get('Duration', 0):.2f}",
                    'Gap': f"{entry['Gap']:.2%}" if entry.get('Gap') is not None else "-"
                }
                log_data.append(row)
            
            log_df = pd.DataFrame(log_data)
            st.dataframe(
                log_df.style.format({'Obj': '{:,.2f}'}), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No execution log available. (Try running a new simulation)")

    # LT Decisions viewer
    lt_entries = [e for e in solver_log if e.get('Model', '').startswith('LT')]
    if lt_entries:
        with st.expander("LT Decisions (block-by-block plans)", expanded=False):
            render_lt_decisions(lt_entries, results.get('config'))

    # Charts
    st.markdown("---")
    render_charts(df)
    
    # Data Table
    st.markdown("---")
    render_data_table(df)
    
    # Export
    st.markdown("---")
    render_export(results)


def render_kpi_cards(df):
    """Render key metric cards."""
    total_cost = df['cost'].sum()
    total_demand = df['demand_total'].sum()
    peak_backlog = df['backlog_total'].max()
    total_b10 = df['b10_total'].sum() if 'b10_total' in df.columns else 0
    weeks_with_b10 = (df['b10_total'] > 0).sum() if 'b10_total' in df.columns else 0
    final_backlog = df['backlog_total'].iloc[-1]
    
    # First row - Main KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cost", f"₺{total_cost:,.0f}")
    with col2:
        st.metric("Total Demand", f"{total_demand:,.0f}")
    with col3:
        st.metric("Peak Backlog", f"{peak_backlog:,.0f}")
    with col4:
        st.metric("Final Backlog", f"{final_backlog:,.0f}")
    
    # Second row - B10 focus (critical KPI)
    st.markdown("#### ⚠️ Critical: Backlog > 10 Days")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total B10", f"{total_b10:,.0f}", delta_color="inverse")
    with col2:
        st.metric("Weeks with B10", f"{weeks_with_b10}/48", delta_color="inverse")
    with col3:
        pct_b10 = (total_b10 / total_demand * 100) if total_demand > 0 else 0
        st.metric("B10 % of Demand", f"{pct_b10:.2f}%", delta_color="inverse")
    with col4:
        if weeks_with_b10 > 0:
            st.error(f"⚠️ {weeks_with_b10} weeks with orders delayed >10 days")
        else:
            st.success("✅ No orders delayed >10 days")


def render_charts(df):
    """Render interactive charts."""
    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### Simulation Visualization")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Per Product", "Inventory & Backlog", "Production vs Demand", "Cost Analysis"
    ])
    
    with tab1:
        render_overview_chart(df)
    
    with tab2:
        render_per_product_charts(df)
    
    with tab3:
        render_inv_backlog_chart(df)
    
    with tab4:
        render_prod_demand_chart(df)
    
    with tab5:
        render_cost_chart(df)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_overview_chart(df):
    """Multi-panel overview."""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Inventory", "Backlog", "Weekly Cost"),
        vertical_spacing=0.08
    )
    
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['inv_total'],
        fill='tozeroy', fillcolor='rgba(14, 165, 233, 0.2)',
        line=dict(color='#0ea5e9', width=2),
        name='Inventory'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['backlog_total'],
        fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(color='#ef4444', width=2),
        name='Backlog'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=df['week'], y=df['cost'],
        marker_color='#f59e0b',
        name='Cost'
    ), row=3, col=1)
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#adbac7"),
        height=700,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    
    # Add month annotations
    for month in range(1, 13):
        week_start = (month - 1) * 4 + 1
        fig.add_vline(x=week_start, line_dash="dot", line_color="gray", opacity=0.3)
    
    st.plotly_chart(fig, use_container_width=True)


def render_per_product_charts(df):
    """Render per-product breakdown with product filter."""
    PRODUCT_NAMES = {
        1: "P1 – Plastic Tubs",
        2: "P2 – Semi-Finished Boba",
        3: "P3 – Cup Bubble Tea",
        4: "P4 – Can Bubble Tea",
    }
    PRODUCT_COLORS = {
        1: "#539bf5",  # blue
        2: "#e5534b",  # red
        3: "#57ab5a",  # green
        4: "#daaa3f",  # amber
    }

    # Product filter
    selected = st.multiselect(
        "Select products to display",
        options=[1, 2, 3, 4],
        default=[1, 3, 4],
        format_func=lambda x: PRODUCT_NAMES[x],
        key="per_product_filter",
    )

    if not selected:
        st.info("Select at least one product to display charts.")
        return

    # View mode
    view_mode = st.radio(
        "View", ["Combined", "Individual"],
        horizontal=True,
        key="per_product_view",
        help="Combined overlays all products; Individual shows a subplot per product."
    )

    # --- Production vs Demand ---
    st.markdown("#### Production vs Demand")
    if view_mode == "Combined":
        fig = go.Figure()
        for p in selected:
            prod_col = f'prod_{p}'
            demand_col = f'demand_{p}'
            color = PRODUCT_COLORS[p]
            name = PRODUCT_NAMES[p]

            if prod_col in df.columns:
                fig.add_trace(go.Bar(
                    x=df['week'], y=df[prod_col],
                    name=f"{name} Prod",
                    marker_color=color,
                    opacity=0.7,
                ))
            if demand_col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['week'], y=df[demand_col],
                    name=f"{name} Demand",
                    mode='lines+markers',
                    line=dict(color=color, width=2, dash='dot'),
                    marker=dict(size=4),
                ))

        fig.update_layout(
            xaxis_title="Week", yaxis_title="Units",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#adbac7"),
            height=450, barmode='group',
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        )
        fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = make_subplots(
            rows=len(selected), cols=1,
            subplot_titles=[PRODUCT_NAMES[p] for p in selected],
            vertical_spacing=0.08,
        )
        for idx, p in enumerate(selected, 1):
            prod_col = f'prod_{p}'
            demand_col = f'demand_{p}'
            color = PRODUCT_COLORS[p]
            if prod_col in df.columns:
                fig.add_trace(go.Bar(
                    x=df['week'], y=df[prod_col],
                    name="Production", marker_color=color, opacity=0.7,
                    showlegend=(idx == 1),
                ), row=idx, col=1)
            if demand_col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['week'], y=df[demand_col],
                    name="Demand",
                    mode='lines+markers',
                    line=dict(color='#c9d1d9', width=2, dash='dot'),
                    marker=dict(size=3),
                    showlegend=(idx == 1),
                ), row=idx, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#adbac7"),
            height=250 * len(selected), showlegend=True,
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        )
        fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        for ann in fig['layout']['annotations']:
            ann['font'] = dict(color='#adbac7', size=12)
        st.plotly_chart(fig, use_container_width=True)

    # --- Inventory ---
    st.markdown("#### Inventory Levels")
    fig_inv = go.Figure()
    for p in selected:
        inv_col = f'inv_{p}'
        if inv_col in df.columns:
            fig_inv.add_trace(go.Scatter(
                x=df['week'], y=df[inv_col],
                name=PRODUCT_NAMES[p],
                mode='lines',
                line=dict(color=PRODUCT_COLORS[p], width=2),
                fill='tozeroy',
                fillcolor=f"rgba({','.join(str(int(PRODUCT_COLORS[p].lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))}, 0.08)",
            ))
    fig_inv.update_layout(
        xaxis_title="Week", yaxis_title="Inventory (units)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#adbac7"),
        height=400,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    fig_inv.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    fig_inv.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    st.plotly_chart(fig_inv, use_container_width=True)

    # --- Backlog ---
    st.markdown("#### Backlog Levels")
    fig_bl = go.Figure()
    has_backlog = False
    for p in selected:
        bl_col = f'backlog_{p}'
        if bl_col in df.columns:
            vals = df[bl_col]
            if vals.sum() > 0:
                has_backlog = True
            fig_bl.add_trace(go.Scatter(
                x=df['week'], y=vals,
                name=PRODUCT_NAMES[p],
                mode='lines',
                line=dict(color=PRODUCT_COLORS[p], width=2),
            ))
    if not has_backlog:
        st.success("No backlog for the selected products!")
    else:
        fig_bl.update_layout(
            xaxis_title="Week", yaxis_title="Backlog (units)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#adbac7"),
            height=400,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        )
        fig_bl.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        fig_bl.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
        st.plotly_chart(fig_bl, use_container_width=True)

    # --- Summary metrics per product ---
    st.markdown("#### Product Summary")
    summary_cols = st.columns(len(selected))
    for idx, p in enumerate(selected):
        with summary_cols[idx]:
            name = PRODUCT_NAMES[p].split(" – ")[0]
            prod_col = f'prod_{p}'
            demand_col = f'demand_{p}'
            inv_col = f'inv_{p}'
            bl_col = f'backlog_{p}'

            total_prod = df[prod_col].sum() if prod_col in df.columns else 0
            total_demand = df[demand_col].sum() if demand_col in df.columns else 0
            avg_inv = df[inv_col].mean() if inv_col in df.columns else 0
            peak_bl = df[bl_col].max() if bl_col in df.columns else 0

            st.markdown(f"**{name}**")
            st.caption(f"Total Production: {total_prod:,.0f}")
            st.caption(f"Total Demand: {total_demand:,.0f}")
            st.caption(f"Avg Inventory: {avg_inv:,.0f}")
            st.caption(f"Peak Backlog: {peak_bl:,.0f}")


def render_inv_backlog_chart(df):
    """Inventory and backlog over time."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['inv_total'],
        mode='lines+markers',
        name='Inventory',
        line=dict(color='#0ea5e9', width=2),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['backlog_total'],
        mode='lines+markers',
        name='Backlog',
        line=dict(color='#ef4444', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title="Inventory vs Backlog",
        xaxis_title="Week",
        yaxis_title="Units",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#adbac7"),
        height=450,
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Inventory", f"{df['inv_total'].mean():,.0f}")
    with col2:
        st.metric("Peak Inventory", f"{df['inv_total'].max():,.0f}")
    with col3:
        st.metric("Avg Backlog", f"{df['backlog_total'].mean():,.0f}")


def render_prod_demand_chart(df):
    """Production vs demand comparison."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['week'], y=df['prod_total'],
        name='Production',
        marker_color='#10b981'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['demand_total'],
        mode='lines+markers',
        name='Demand',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Production vs Demand",
        xaxis_title="Week",
        yaxis_title="Units",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#adbac7"),
        height=450,
        barmode='overlay',
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gap analysis
    df['gap'] = df['prod_total'] - df['demand_total']
    weeks_deficit = (df['gap'] < 0).sum()
    weeks_surplus = (df['gap'] > 0).sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Weeks in Deficit", f"{weeks_deficit}")
    with col2:
        st.metric("Weeks in Surplus", f"{weeks_surplus}")
    with col3:
        st.metric("Total Gap", f"{df['gap'].sum():,.0f}")


def render_cost_chart(df):
    """Cost analysis."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['week'], y=df['cost'],
        marker_color=df['cost'].apply(lambda x: '#ef4444' if x > 100000 else '#10b981'),
        name='Weekly Cost'
    ))
    
    # Cumulative cost line
    df['cumulative_cost'] = df['cost'].cumsum()
    fig.add_trace(go.Scatter(
        x=df['week'], y=df['cumulative_cost'],
        mode='lines',
        name='Cumulative',
        line=dict(color='#6366f1', width=2, dash='dash'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Weekly and Cumulative Cost",
        xaxis_title="Week",
        yaxis_title="Weekly Cost (₺)",
        yaxis2=dict(title="Cumulative (₺)", overlaying='y', side='right'),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#adbac7"),
        height=450,
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost breakdown
    high_cost_weeks = df[df['cost'] > 100000]['week'].tolist()
    if high_cost_weeks:
        st.warning(f"High-cost weeks (>₺100k): {', '.join(map(str, high_cost_weeks))}")


def render_data_table(df):
    """Render results table."""
    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### Weekly Results")
    
    # Select columns including B10
    cols = ['week', 'start_day', 'end_day', 'prod_total', 'demand_total', 
            'inv_total', 'backlog_total', 'b10_total', 'cost', 'status']
    # Only include columns that exist
    cols = [c for c in cols if c in df.columns]
    display_df = df[cols].copy()
    
    # Rename columns
    rename_map = {
        'week': 'Week', 'start_day': 'Start', 'end_day': 'End',
        'prod_total': 'Production', 'demand_total': 'Demand',
        'inv_total': 'Inventory', 'backlog_total': 'Backlog',
        'b10_total': 'B10 (>10d)', 'cost': 'Cost', 'status': 'Status'
    }
    display_df.columns = [rename_map.get(c, c) for c in cols]
    
    st.dataframe(display_df, hide_index=True, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)


def render_export(results):
    """Render export options with detailed report."""
    df = results['df']
    scenario = results['scenario']
    full_result = results.get('full_result')
    sim_config = results.get('config')
    saved_folder = results.get('saved_folder')

    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### Export Results")

    if saved_folder:
        st.info(f"Run auto-saved to: `{saved_folder}`")

    col1, col2, col3 = st.columns(3)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "Weekly CSV",
            csv,
            f"{scenario}_simulation.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        output.seek(0)
        st.download_button(
            "Weekly Excel",
            output,
            f"{scenario}_simulation.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col3:
        if full_result and full_result.success and sim_config:
            config = sim_config.optimizer_config if hasattr(sim_config, 'optimizer_config') else sim_config
            buf = export_run_to_excel(
                result=full_result,
                config=config,
                scenario_name=scenario,
                weekly_df=df,
            )
            st.download_button(
                "Detailed Report (Excel)",
                buf,
                f"{scenario}_detailed_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.caption("Run a simulation first to get the detailed report.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_lt_decisions(lt_entries, sim_config):
    """Render LT decisions as block-by-block tables for each LT step."""
    if not lt_entries:
        st.info("No LT decisions to display.")
        return

    config = None
    if sim_config and hasattr(sim_config, 'optimizer_config'):
        config = sim_config.optimizer_config
    elif sim_config:
        config = sim_config

    block_size = getattr(config, 'long_term_block', 24) if config else 24
    total_days = getattr(config, 'total_days', 288) if config else 288

    st.caption(f"{len(lt_entries)} LT solves | Block size = {block_size} days")

    # Step selector
    step_labels = [f"Step {i+1} — Day {e.get('Day', '?')} ({e.get('Model','LT')}, {e.get('Status','?')}, {e.get('Duration',0):.1f}s)"
                   for i, e in enumerate(lt_entries)]
    selected = st.selectbox("Select LT Step", range(len(lt_entries)),
                            format_func=lambda i: step_labels[i],
                            key="lt_step_selector")

    entry = lt_entries[selected]
    production = entry.get('Production', {})
    inventory = entry.get('Inventory', {})
    backlog = entry.get('Backlog', {})
    demand = entry.get('Demand', {})
    targets = entry.get('Targets', {})
    i_state = entry.get('I_state', {})
    b_state = entry.get('B_state', {})
    cur_day = entry.get('Day', 1)

    # State at time of solve
    st.markdown("**State at solve time:**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("P1 Inv", f"{i_state.get(1, 0):,.0f}")
    sc2.metric("P2 Inv", f"{i_state.get(2, 0):,.0f}")
    sc3.metric("P3 Inv", f"{i_state.get(3, 0):,.0f}")
    sc4.metric("P4 Inv", f"{i_state.get(4, 0):,.0f}")

    # Build block table
    blocks = sorted(set(t for (_, t) in production.keys())) if production else list(range(1, 13))
    rows = []
    for t in blocks:
        block_start = cur_day + (t - 1) * block_size
        block_end = min(cur_day + t * block_size - 1, total_days)
        boundary = block_end
        row = {
            "Block": t,
            "Days": f"{block_start}-{block_end}",
            "P1 Prod": round(production.get((1, t), 0), 0),
            "P2 Prod": round(production.get((2, t), 0), 0),
            "P3 Prod": round(production.get((3, t), 0), 0),
            "P4 Prod": round(production.get((4, t), 0), 0),
            "P1 Inv": round(inventory.get((1, t), 0), 0),
            "P2 Inv": round(inventory.get((2, t), 0), 0),
            "P3 Inv": round(inventory.get((3, t), 0), 0),
            "P4 Inv": round(inventory.get((4, t), 0), 0),
            "P1 BL": round(backlog.get((1, t), 0), 0),
            "P3 BL": round(backlog.get((3, t), 0), 0),
            "P4 BL": round(backlog.get((4, t), 0), 0),
            "P1 Dem": round(demand.get((1, t), 0), 0),
            "P3 Dem": round(demand.get((3, t), 0), 0),
            "P4 Dem": round(demand.get((4, t), 0), 0),
        }
        # Add target columns if this block is a boundary
        if (boundary, 1) in targets:
            row["P1 Tgt"] = round(targets[(boundary, 1)], 0)
            row["P2 Tgt"] = round(targets[(boundary, 2)], 0)
            row["P3 Tgt"] = round(targets[(boundary, 3)], 0)
            row["P4 Tgt"] = round(targets[(boundary, 4)], 0)
        else:
            row["P1 Tgt"] = ""
            row["P2 Tgt"] = ""
            row["P3 Tgt"] = ""
            row["P4 Tgt"] = ""
        rows.append(row)

    lt_df = pd.DataFrame(rows)
    st.dataframe(lt_df, hide_index=True, use_container_width=True)

    # Quick objective info
    obj = entry.get('Objective', 0)
    s1 = entry.get('Stage1Cost', 0)
    s2 = entry.get('Stage2Cost', 0)
    info_cols = st.columns(3)
    info_cols[0].metric("LT Objective", f"{obj:,.0f}" if obj else "-")
    if s1 or s2:
        info_cols[1].metric("Stage 1 Cost", f"{s1:,.0f}")
        info_cols[2].metric("Stage 2 Cost", f"{s2:,.0f}")


def show_instructions():
    """Show getting started instructions."""
    st.markdown("""
    <div class="card-style">
        <h3 style="margin-top: 0; margin-bottom: 1.5rem;">How It Works</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;">
            <div class="step-card">
                <div class="step-number">1</div>
                <h4>Select Scenario</h4>
                <p>Choose a demand pattern from the sidebar.</p>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <h4>Configure</h4>
                <p>Set capacities, costs, and initial state.</p>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <h4>Run Simulation</h4>
                <p>48 weekly planning cycles execute.</p>
            </div>
            <div class="step-card">
                <div class="step-number">4</div>
                <h4>Analyze Results</h4>
                <p>View charts, tables, and export data.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 1.5rem;">
        <h3>Simulation Process</h3>
        <p>Each week, the simulation:</p>
        <ol>
            <li>Builds inputs from current state + demand data</li>
            <li>Runs both LT and ST optimization models</li>
            <li>Executes the first 6 days of the ST plan</li>
            <li>Updates inventory/backlog based on actual demand</li>
            <li>Records metrics and moves to next week</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
