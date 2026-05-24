"""
Export UI component.
"""
from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import streamlit as st

from core.export_run import export_run_to_excel


def render_export(result: dict[str, Any]) -> None:
    """Render export section with detailed report download."""
    st.markdown('<div class="card-style">', unsafe_allow_html=True)
    st.markdown("### Export Results")

    plan_df = result.get("plan_df")
    full_result = result.get("full_result")
    config = result.get("config")

    col1, col2, col3 = st.columns(3)

    with col1:
        if plan_df is not None:
            export_df = plan_df.copy()
            preferred = [c for c in ["date", "weekday", "production_allowed", "day"] if c in export_df.columns]
            remaining = [c for c in export_df.columns if c not in preferred]
            export_df = export_df[preferred + remaining]
            csv = export_df.to_csv(index=False)
            st.download_button(
                "Daily Plan CSV",
                csv,
                "production_plan.csv",
                "text/csv",
                width="stretch",
            )

    with col2:
        if plan_df is not None:
            export_df = plan_df.copy()
            preferred = [c for c in ["date", "weekday", "production_allowed", "day"] if c in export_df.columns]
            remaining = [c for c in export_df.columns if c not in preferred]
            export_df = export_df[preferred + remaining]
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Daily Plan")
            output.seek(0)
            st.download_button(
                "Daily Plan Excel",
                output,
                "production_plan.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )

    with col3:
        if full_result and full_result.success and config:
            buf = export_run_to_excel(
                result=full_result,
                config=config,
                scenario_name="weekly_plan",
            )
            st.download_button(
                "Detailed Report (Excel)",
                buf,
                "detailed_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )

    st.markdown("</div>", unsafe_allow_html=True)
