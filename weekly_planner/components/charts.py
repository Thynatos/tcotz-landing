"""
Chart components for visualization.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots


# ── Slate Dimmed color palette ──────────────────────────────────
C = dict(
    blue='#539bf5', cyan='#39c5cf', green='#57ab5a',
    amber='#c69026', red='#e5534b', purple='#986ee2',
    blue_fill='rgba(83,155,245,0.12)', red_fill='rgba(229,83,75,0.12)',
    green_fill='rgba(87,171,90,0.12)',
)

PRODUCT_COLORS = {
    'p1': C['blue'],  'i1': C['blue'],  'b1': C['blue'],
    'p2': C['green'],  'i2': C['green'],  'b2': C['green'],
    'p3': C['amber'], 'i3': C['amber'], 'b3': C['amber'],
    'p4': C['red'],   'i4': C['red'],   'b4': C['red'],
}


def _get_time_axis(df: pd.DataFrame) -> tuple[str, str]:
    if 'date' in df.columns and not df['date'].isna().all():
        return 'date', 'Date'
    return 'day', 'Day'


def _apply_layout(fig, **kwargs):
    """Apply consistent Slate Dimmed layout to a plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#adbac7", size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        hoverlabel=dict(
            bgcolor="#2d333b", bordercolor="#444c56",
            font=dict(color="#cdd9e5", size=12),
        ),
        **kwargs
    )
    fig.update_xaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56",
                     tickfont=dict(color="#768390"), title_font=dict(color="#adbac7"))
    fig.update_yaxes(gridcolor="rgba(68,76,86,0.4)", zerolinecolor="#444c56",
                     tickfont=dict(color="#768390"), title_font=dict(color="#adbac7"))
    return fig


def render_charts(df: pd.DataFrame):
    """Render interactive charts."""
    if df is None or df.empty:
        st.info("Run optimization to see charts.")
        return
    
    st.markdown('<div class="kpi-section-label">Production Visualization</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Inventory", "Production", "Backlogs", "Per Product", "Overview", "Weekly Schedule"
    ])
    
    with tab1:
        render_inventory_chart(df)
    with tab2:
        render_production_chart(df)
    with tab3:
        render_backlog_chart(df)
    with tab4:
        render_per_product_chart(df)
    with tab5:
        render_overview_chart(df)
    with tab6:
        render_weekly_schedule_chart(df)


def get_inventory_chart(df: pd.DataFrame) -> go.Figure:
    """Get inventory levels over time figure."""
    fig = go.Figure()
    
    names = {
        'i1': 'Product 1 - Plastic Tub',
        'i2': 'Product 2 - Semi-Finished',
        'i3': 'Product 3 - Cup Tea',
        'i4': 'Product 4 - Can Tea'
    }
    
    x_col, xaxis_title = _get_time_axis(df)
    
    for col, name in names.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[col],
                name=name, mode='lines',
                line=dict(color=PRODUCT_COLORS[col], width=2.5),
                customdata=df[['day']] if 'day' in df.columns else None,
                hovertemplate="Date=%{x}<br>Day=%{customdata[0]}<br>Value=%{y}<extra></extra>" if x_col == 'date' and 'day' in df.columns else None,
            ))
    
    _apply_layout(fig,
        title=dict(text="Inventory Levels", font=dict(color="#cdd9e5", size=15)),
        xaxis_title=xaxis_title, yaxis_title="Units",
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7", size=11),
        ),
        height=450,
    )
    return fig


def render_inventory_chart(df: pd.DataFrame):
    """Render inventory levels over time."""
    fig = get_inventory_chart(df)
    st.plotly_chart(fig, width="stretch")


def get_rm_inventory_chart(df: pd.DataFrame) -> go.Figure:
    """Get raw material inventory levels over time figure."""
    fig = go.Figure()
    
    rm_cols = [col for col in df.columns if col.startswith('ir')]
    
    if not rm_cols:
        return None

    x_col, xaxis_title = _get_time_axis(df)

    for col in sorted(rm_cols, key=lambda x: int(x[2:])):
        rm_id = col[2:]
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[col],
            name=f'RM {rm_id}', mode='lines',
            line=dict(width=2)
        ))
        
    _apply_layout(fig,
        title=dict(text="Raw Material Inventory Levels", font=dict(color="#cdd9e5", size=15)),
        xaxis_title=xaxis_title, yaxis_title="Units",
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7", size=11),
        ),
        height=450,
    )
    return fig


def render_rm_inventory_chart(df: pd.DataFrame):
    """Render raw material inventory levels over time."""
    fig = get_rm_inventory_chart(df)
    if fig is None:
        st.info("No raw material data available.")
        return
    st.plotly_chart(fig, width="stretch")


def get_production_charts(df: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    """Get Line 1 and Line 2 production charts."""
    x_col, _ = _get_time_axis(df)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=df[x_col], y=df['p1'], name='P1', marker_color=C['blue']))
    fig1.add_trace(go.Bar(x=df[x_col], y=df['p2'], name='P2', marker_color=C['green']))
    _apply_layout(fig1,
        title=dict(text="Line 1 Production (P1 & P2)", font=dict(color="#cdd9e5", size=14)),
        height=320, barmode='stack',
        showlegend=True,
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
    )
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df[x_col], y=df['p3'], name='P3', marker_color=C['amber']))
    fig2.add_trace(go.Bar(x=df[x_col], y=df['p4'], name='P4', marker_color=C['red']))
    _apply_layout(fig2,
        title=dict(text="Line 2 Production (P3 & P4)", font=dict(color="#cdd9e5", size=14)),
        height=320, barmode='stack',
        showlegend=True,
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
    )
    return fig1, fig2


def render_production_chart(df: pd.DataFrame):
    """Render production schedule."""
    fig1, fig2 = get_production_charts(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, width="stretch")
    with col2:
        st.plotly_chart(fig2, width="stretch")


def get_backlog_chart(df: pd.DataFrame) -> go.Figure:
    """Get backlog analysis figure."""
    fig = go.Figure()
    
    x_col, xaxis_title = _get_time_axis(df)
    
    for col, name, color in [
        ('b1', 'Product 1', C['blue']),
        ('b3', 'Product 3', C['amber']),
        ('b4', 'Product 4', C['red'])
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[col],
                name=name, mode='lines+markers',
                line=dict(color=color, width=2),
                marker=dict(size=4, color=color)
            ))
    
    _apply_layout(fig,
        title=dict(text="Backlog Levels", font=dict(color="#cdd9e5", size=15)),
        xaxis_title=xaxis_title, yaxis_title="Units",
        hovermode="x unified", height=400,
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
    )
    return fig


def render_backlog_chart(df: pd.DataFrame):
    """Render backlog analysis."""
    fig = get_backlog_chart(df)
    st.plotly_chart(fig, width="stretch")
    
    # Summary Metrics
    b1 = df['b1'] if 'b1' in df.columns else 0
    b3 = df['b3'] if 'b3' in df.columns else 0
    b4 = df['b4'] if 'b4' in df.columns else 0
    
    total_days = ((b1 + b3 + b4) > 0).sum() if isinstance(b1, pd.Series) else 0
    max_val = max(
        b1.max() if isinstance(b1, pd.Series) else 0,
        b3.max() if isinstance(b3, pd.Series) else 0,
        b4.max() if isinstance(b4, pd.Series) else 0
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Days with Backlog", f"{total_days}")
    with col2:
        st.metric("Peak Backlog Quantity", f"{max_val:,.0f}")


def render_per_product_chart(df: pd.DataFrame):
    """Render per-product breakdown with product filter."""
    PRODUCT_NAMES = {
        1: "P1 – Plastic Tubs",
        2: "P2 – Semi-Finished Boba",
        3: "P3 – Cup Bubble Tea",
        4: "P4 – Can Bubble Tea",
    }
    PCOLORS = {1: C['blue'], 2: C['green'], 3: C['amber'], 4: C['red']}

    selected = st.multiselect(
        "Select products to display",
        options=[1, 2, 3, 4],
        default=[1, 3, 4],
        format_func=lambda x: PRODUCT_NAMES[x],
        key="wp_per_product_filter",
    )

    if not selected:
        st.info("Select at least one product to display charts.")
        return

    view_mode = st.radio(
        "View", ["Combined", "Individual"],
        horizontal=True, key="wp_per_product_view",
        help="Combined overlays all products; Individual shows a subplot per product."
    )

    st.markdown("#### Production")
    
    x_col, xaxis_title = _get_time_axis(df)

    if view_mode == "Combined":
        fig = go.Figure()
        for p in selected:
            col_name = f'p{p}'
            if col_name in df.columns:
                fig.add_trace(go.Bar(
                    x=df[x_col], y=df[col_name],
                    name=PRODUCT_NAMES[p], marker_color=PCOLORS[p], opacity=0.7,
                ))
        _apply_layout(fig,
            xaxis_title=xaxis_title, yaxis_title="Units",
            height=400, barmode='group',
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        fig = make_subplots(
            rows=len(selected), cols=1,
            subplot_titles=[PRODUCT_NAMES[p] for p in selected],
            vertical_spacing=0.08,
        )
        for idx, p in enumerate(selected, 1):
            col_name = f'p{p}'
            if col_name in df.columns:
                fig.add_trace(go.Bar(
                    x=df[x_col], y=df[col_name],
                    name=PRODUCT_NAMES[p], marker_color=PCOLORS[p], opacity=0.7,
                    showlegend=False,
                ), row=idx, col=1)
        _apply_layout(fig, height=250 * len(selected))
        for ann in fig['layout']['annotations']:
            ann['font'] = dict(color='#adbac7', size=12)
        st.plotly_chart(fig, width="stretch")

    # --- Inventory ---
    st.markdown("#### Inventory Levels")
    fig_inv = go.Figure()
    for p in selected:
        col_name = f'i{p}'
        if col_name in df.columns:
            color = PCOLORS[p]
            fig_inv.add_trace(go.Scatter(
                x=df[x_col], y=df[col_name],
                name=PRODUCT_NAMES[p], mode='lines',
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=f"rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))}, 0.08)",
            ))
    _apply_layout(fig_inv,
        xaxis_title=xaxis_title, yaxis_title="Inventory (units)",
        height=400,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
    )
    st.plotly_chart(fig_inv, width="stretch")

    # --- Backlog ---
    st.markdown("#### Backlog Levels")
    fig_bl = go.Figure()
    has_backlog = False
    for p in selected:
        col_name = f'b{p}'
        if col_name in df.columns:
            vals = df[col_name]
            if vals.sum() > 0:
                has_backlog = True
            fig_bl.add_trace(go.Scatter(
                x=df[x_col], y=vals,
                name=PRODUCT_NAMES[p], mode='lines',
                line=dict(color=PCOLORS[p], width=2),
            ))
    if not has_backlog:
        st.success("No backlog for the selected products!")
    else:
        _apply_layout(fig_bl,
            xaxis_title=xaxis_title, yaxis_title="Backlog (units)",
            height=400,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(color="#adbac7")),
        )
        st.plotly_chart(fig_bl, width="stretch")

    # --- Summary metrics ---
    st.markdown("#### Product Summary")
    summary_cols = st.columns(len(selected))
    for idx, p in enumerate(selected):
        with summary_cols[idx]:
            name = PRODUCT_NAMES[p].split(" – ")[0]
            total_prod = df[f'p{p}'].sum() if f'p{p}' in df.columns else 0
            avg_inv = df[f'i{p}'].mean() if f'i{p}' in df.columns else 0
            peak_bl = df[f'b{p}'].max() if f'b{p}' in df.columns else 0
            st.markdown(f"**{name}**")
            st.caption(f"Total Prod: {total_prod:,.0f}")
            st.caption(f"Avg Inventory: {avg_inv:,.0f}")
            st.caption(f"Peak Backlog: {peak_bl:,.0f}")


def get_overview_chart(df: pd.DataFrame) -> go.Figure:
    """Get overview dashboard figure."""
    df_sum = df.copy()
    df_sum['total_inventory'] = df.get('i1', 0) + df.get('i2', 0) + df.get('i3', 0) + df.get('i4', 0)
    df_sum['total_production'] = df.get('p1', 0) + df.get('p2', 0) + df.get('p3', 0) + df.get('p4', 0)
    
    b1 = df['b1'] if 'b1' in df.columns else 0
    b3 = df['b3'] if 'b3' in df.columns else 0
    b4 = df['b4'] if 'b4' in df.columns else 0
    df_sum['total_backlog'] = b1 + b3 + b4
    
    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=("Total Inventory", "Total Production", "Total Backlog"),
                        vertical_spacing=0.1)
    
    x_col, _ = _get_time_axis(df)
    
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df_sum['total_inventory'],
        fill='tozeroy', fillcolor=C['blue_fill'],
        line=dict(color=C['blue'], width=2),
        name='Inventory'
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=df[x_col], y=df_sum['total_production'],
        marker_color=C['green'],
        name='Production'
    ), row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df_sum['total_backlog'],
        fill='tozeroy', fillcolor=C['red_fill'],
        line=dict(color=C['red'], width=2),
        name='Backlog'
    ), row=3, col=1)
    
    _apply_layout(fig, height=700, showlegend=False)
    
    # Style subplot titles
    for ann in fig['layout']['annotations']:
        ann['font'] = dict(color='#adbac7', size=12)
        
    return fig


def render_overview_chart(df: pd.DataFrame):
    """Render overview dashboard."""
    fig = get_overview_chart(df)
    st.plotly_chart(fig, width="stretch")


def get_weekly_schedule_chart(df: pd.DataFrame) -> go.Figure:
    """Get the weekly production schedule heatmap."""
    if 'day' not in df.columns:
        return go.Figure()

    first_day = int(df['day'].min())
    df_week = df[(df['day'] >= first_day) & (df['day'] <= first_day + 6)].copy()
    if df_week.empty:
        return go.Figure()

    if 'date' in df_week.columns and 'weekday' in df_week.columns:
        days = [f"{wd[:3]}\n{str(dt)}" for wd, dt in zip(df_week['weekday'], df_week['date'])]
    elif 'date' in df_week.columns:
        days = [str(dt) for dt in df_week['date']]
    else:
        days = [f"Day {d}" for d in df_week['day'].tolist()]
    
    machines = [
        "Line 1 - M1 (1000u)",
        "Line 1 - M2 (500u)",
        "Line 1 - M3 (2000u)",
        "Line 2 - P3 M1 (10000u)",
        "Line 2 - P3 M2 (25000u)",
        "Line 2 - P4 (80000u)"
    ]
    
    z_vals = []
    text_vals = []
    
    def get_state(row, m_idx):
        if m_idx == 0: # L1 M1
            return (1, 'P1') if row.get('x1_1_1', 0) == 1 else (2, 'P2') if row.get('x1_2_1', 0) == 1 else (0, 'Idle')
        elif m_idx == 1: # L1 M2
            return (1, 'P1') if row.get('x1_1_2', 0) == 1 else (2, 'P2') if row.get('x1_2_2', 0) == 1 else (0, 'Idle')
        elif m_idx == 2: # L1 M3
            return (1, 'P1') if row.get('x1_1_3', 0) == 1 else (2, 'P2') if row.get('x1_2_3', 0) == 1 else (0, 'Idle')
        elif m_idx == 3: # L2 P3 M1
            return (3, 'P3') if row.get('x2_3_1', 0) == 1 else (0, 'Idle')
        elif m_idx == 4: # L2 P3 M2
            return (3, 'P3') if row.get('x2_3_2', 0) == 1 else (0, 'Idle')
        elif m_idx == 5: # L2 P4
            return (4, 'P4') if row.get('x2_4_1', 0) == 1 else (0, 'Idle')
        return (0, 'Idle')

    for m_idx in range(6):
        m_z = []
        m_text = []
        for _, row in df_week.iterrows():
            zv, tv = get_state(row, m_idx)
            m_z.append(zv)
            m_text.append(tv)
        z_vals.append(m_z)
        text_vals.append(m_text)
        
    colorscale = [
        [0.0, 'rgba(68,76,86,0.3)'], [0.125, 'rgba(68,76,86,0.3)'], 
        [0.125, C['blue']],          [0.375, C['blue']],          
        [0.375, C['green']],         [0.625, C['green']],         
        [0.625, C['amber']],         [0.875, C['amber']],         
        [0.875, C['red']],           [1.0, C['red']]              
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_vals,
        x=days,
        y=machines,
        text=text_vals,
        texttemplate="%{text}",
        textfont={"color": "white", "size": 13},
        hoverinfo="x+y+text",
        colorscale=colorscale,
        zmin=0, zmax=4,
        showscale=False,
        xgap=2, ygap=2
    ))
    
    _apply_layout(fig,
        title=dict(text="Next Calendar Week Schedule", font=dict(color="#cdd9e5", size=15)),
        xaxis_title="Week Timeline",
        yaxis_autorange="reversed",
        height=350,
    )
    fig.update_layout(margin=dict(l=150, r=20, t=50, b=20))
    
    fig.update_xaxes(tickmode="array", tickvals=days)
    return fig


def render_weekly_schedule_chart(df: pd.DataFrame):
    """Render the weekly schedule heatmap."""
    fig = get_weekly_schedule_chart(df)
    st.plotly_chart(fig, width="stretch")
