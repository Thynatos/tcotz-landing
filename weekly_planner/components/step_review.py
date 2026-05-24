"""
Step 3: Review & Generate — parameter summary, consolidated warnings, and generate button.
"""
from __future__ import annotations

from typing import Any

import streamlit as st


def render_step_review(params: dict[str, Any]) -> None:
    demand_loaded = st.session_state.get('demand_data') is not None
    tag_text = "✅ Ready" if demand_loaded else "⏳ Waiting"
    tag_color = "background:rgba(87,171,90,0.15);color:#8ddb8c;border:1px solid rgba(87,171,90,0.3);" if demand_loaded else "background:rgba(83,155,245,0.15);color:#a2cdff;border:1px solid rgba(83,155,245,0.3);"

    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">'
            f'<span style="font-size:1.15rem;font-weight:700;color:#cdd9e5;">📋 Review & Generate</span>'
            f'<span style="font-size:0.78rem;font-weight:600;padding:4px 12px;border-radius:999px;{tag_color}">{tag_text}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.subheader("Configuration Summary", divider=False)

        col1, col2 = st.columns(2)

        with col1:
            start_date = params.get('planning_start_date', '—')
            weeks = params.get('planning_weeks', '—')
            closed = params.get('closed_dates', [])
            closed_str = ', '.join(str(d) for d in closed) if closed else 'None'
            sundays = "Working" if params.get('sundays_working') else "Closed"
            st.markdown(
                f'<div style="background:#2d333b;border:1px solid #373e47;border-radius:10px;padding:1.1rem 1.3rem;">'
                f'<div style="font-size:0.9rem;font-weight:600;color:#cdd9e5;margin-bottom:0.5rem;">📅 Planning Horizon</div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Start Date</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{start_date}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Weeks</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{weeks}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Sundays</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{sundays}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;">'
                f'<span style="color:#768390;font-size:0.85rem;">Closed</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{closed_str}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            holding = params.get('holding_cost', '—')
            backlog = params.get('backlog_cost', '—')
            b12 = params.get('b12_penalty', '—')
            time_limit = params.get('time_limit', '—')
            st.markdown(
                f'<div style="background:#2d333b;border:1px solid #373e47;border-radius:10px;padding:1.1rem 1.3rem;">'
                f'<div style="font-size:0.9rem;font-weight:600;color:#cdd9e5;margin-bottom:0.5rem;">⚙️ Costs & Solver</div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Holding</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{holding}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Backlog</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{backlog}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">B12 Penalty</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{b12}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;">'
                f'<span style="color:#768390;font-size:0.85rem;">Time Limit</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{time_limit}s</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        if params.get('stochastic_lt'):
            scenarios = params.get('n_scenarios', '—')
            alpha = params.get('alpha_base', '—')
            fanout = params.get('fan_out_rate', '—')
            st.markdown(
                f'<div style="background:#2d333b;border:1px solid #373e47;border-radius:10px;padding:1.1rem 1.3rem;">'
                f'<div style="font-size:0.9rem;font-weight:600;color:#cdd9e5;margin-bottom:0.5rem;">🎲 Stochastic LT Enabled</div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Scenarios</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{scenarios}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Alpha</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{alpha}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;">'
                f'<span style="color:#768390;font-size:0.85rem;">Fan-out</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{fanout}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Machine capacity summary (if customized)
        if params.get("custom_capacity_applied"):
            cap_l1 = params.get("cap_l1", {}) or {}
            cap_p3 = params.get("cap_p3", {}) or {}
            cap_p4 = params.get("cap_p4", '—')
            l1_str = ', '.join(f"M{k}={int(v)}" for k, v in sorted(cap_l1.items()))
            p3_str = ', '.join(f"M{k}={int(v)}" for k, v in sorted(cap_p3.items()))
            st.markdown(
                f'<div style="background:#2d333b;border:1px solid #373e47;border-radius:10px;padding:1.1rem 1.3rem;">'
                f'<div style="font-size:0.9rem;font-weight:600;color:#cdd9e5;margin-bottom:0.5rem;">🏭 Custom Machine Capacities</div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Line 1 (P1/P2)</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{l1_str}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #373e47;">'
                f'<span style="color:#768390;font-size:0.85rem;">Line 2 (P3)</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{p3_str}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;">'
                f'<span style="color:#768390;font-size:0.85rem;">P4 Line</span><span style="color:#adbac7;font-weight:600;font-size:0.9rem;">{int(cap_p4) if isinstance(cap_p4, (int, float)) else cap_p4}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Consolidated warnings
        if params.get('custom_initial_state_enabled') and not params.get('custom_initial_state_applied'):
            st.warning("Initial State edits are enabled, but not applied. This run will use default stock/start values.")
        elif params.get('custom_initial_state_dirty'):
            st.info("Initial State has draft changes. This run will use the last applied stock/start values.")

        if params.get("custom_rm_usage_enabled") and not params.get("custom_rm_usage_applied"):
            st.warning("BOM edits are enabled, but not applied. This run uses legacy default consumption coefficients.")
        elif params.get("custom_rm_usage_dirty"):
            st.info("BOM has draft changes. This run uses the last applied BOM.")

        if params.get("custom_capacity_enabled") and not params.get("custom_capacity_applied"):
            st.warning("Machine capacity edits are enabled, but not applied. This run uses default capacities.")
        elif params.get("custom_capacity_dirty"):
            st.info("Machine capacities have draft changes. This run uses the last applied values.")

        # Generate button
        if demand_loaded:
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Generate Schedule", type="primary", width="stretch", key="main_generate_btn"):
                st.session_state.generate_requested = True
                st.rerun()
        else:
            st.info("Upload demand data in Step 1 and click **Load Data** to get started.")