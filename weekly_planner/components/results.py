"""
Results display components.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

def render_cost_summary(result: dict[str, object]) -> None:
    """Render cost summary metrics (Holding, Backlog, B12, Total) in 4 columns.

    Args:
        result: session_state result dict with 'cost_summary' key.
    """
    costs = result.get('cost_summary', {})
    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### Cost Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Holding Cost", f"₺{costs.get('holding', 0):,.0f}")
    with col2:
        st.metric("Backlog Cost", f"₺{costs.get('backlog', 0):,.0f}")
    with col3:
        st.metric("B12 Penalty", f"₺{costs.get('b12_penalty', 0):,.0f}")
    with col4:
        st.metric("Total Cost", f"₺{costs.get('total', 0):,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_cost_breakdown(cost_summary):
    """Render cost breakdown table and chart."""
    st.markdown("### 💰 Cost Breakdown")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        holding = cost_summary.get('holding', 0)
        backlog = cost_summary.get('backlog', 0)
        total = cost_summary.get('total', 0)
        
        st.markdown(f"""
        <table style="width: 100%;">
            <tr>
                <th style="padding-left: 0;">Cost Type</th>
                <th style="text-align: right; padding-right: 0;">Amount</th>
            </tr>
            <tr>
                <td style="padding-left: 0; padding-top: 1rem;">Holding Cost</td>
                <td style="text-align: right; padding-right: 0; padding-top: 1rem;">₺{holding:,.0f}</td>
            </tr>
            <tr>
                <td style="padding-left: 0;">Backlog Cost</td>
                <td style="text-align: right; padding-right: 0;">₺{backlog:,.0f}</td>
            </tr>
            <tr style="font-weight: 700; font-size: 1.1em;">
                <td style="padding-left: 0; padding-top: 1rem; border-top: 2px solid var(--border-default, #444c56);">Total Cost</td>
                <td style="text-align: right; padding-right: 0; padding-top: 1rem; border-top: 2px solid var(--border-default, #444c56);">₺{total:,.0f}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
    
    with col2:
        if total > 0:
            # Donut chart for modern look
            fig = px.pie(
                values=[holding, backlog],
                names=['Holding', 'Backlog'],
                color_discrete_sequence=['#3b82f6', '#f59e0b'],
                hole=0.6
            )
            fig.update_layout(
                showlegend=True,
                height=220,
                margin=dict(l=20, r=20, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#adbac7"),
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1,
                            font=dict(color="#adbac7"))
            )
            fig.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig, width="stretch")


def render_data_table(df: pd.DataFrame) -> None:
    """Render production plan data table with export."""
    if df is None or df.empty:
        st.info("No data to display")
        return
    
    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### 📋 Production Schedule")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    date_span = ""
    if 'date' in df.columns and not df['date'].isna().all():
        date_span = f" ({df['date'].min()} to {df['date'].max()})"
    with col1:
        st.metric("Planning Horizon", f"{len(df)} Days{date_span}")
    with col2:
        line1_days = ((df['p1'] > 0) | (df['p2'] > 0)).sum()
        st.metric("Line 1 Active", f"{line1_days} Days")
    with col3:
        line2_days = ((df['p3'] > 0) | (df['p4'] > 0)).sum()
        st.metric("Line 2 Active", f"{line2_days} Days")
    
    st.markdown("---")
    
    # Format display
    display_df = df.copy()
    
    # Priority columns for display (calendar-first)
    cols = []
    if 'date' in display_df.columns:
        cols.append('date')
    if 'weekday' in display_df.columns:
        cols.append('weekday')
    if 'production_allowed' in display_df.columns:
        cols.append('production_allowed')
    cols.append('day')
    
    # Append other columns
    other_cols = [c for c in display_df.columns if c not in cols]
    display_df = display_df[cols + other_cols]
    
    display_df.columns = [c.capitalize() for c in display_df.columns]
    
    st.dataframe(display_df, hide_index=True, width="stretch", height=400)
    
    st.markdown("</div>", unsafe_allow_html=True)
