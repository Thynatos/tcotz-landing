"""
LT decision viewer component.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def render_lt_decisions(lt_entries: list[dict[str, Any]], config: Any) -> None:
    """Render LT decisions as block-by-block tables for each LT step."""
    if not lt_entries:
        st.info("No LT decisions to display.")
        return

    st.caption(f"{len(lt_entries)} LT solves")

    step_labels = [
        (
            f"Step {i + 1} -- Day {entry.get('Day', '?')} "
            f"({entry.get('Model', 'LT')}, {entry.get('Status', '?')}, "
            f"{entry.get('Duration', 0):.1f}s)"
        )
        for i, entry in enumerate(lt_entries)
    ]
    selected = st.selectbox(
        "Select LT Step",
        range(len(lt_entries)),
        format_func=lambda index: step_labels[index],
        key="wp_lt_step_selector",
    )

    entry = lt_entries[selected]
    production = entry.get("Production", {})
    inventory = entry.get("Inventory", {})
    backlog = entry.get("Backlog", {})
    demand = entry.get("Demand", {})
    targets = entry.get("Targets", {})
    i_state = entry.get("I_state", {})
    cur_day = entry.get("Day", 1)

    st.markdown("**State at solve time:**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("P1 Inv", f"{i_state.get(1, 0):,.0f}")
    sc2.metric("P2 Inv", f"{i_state.get(2, 0):,.0f}")
    sc3.metric("P3 Inv", f"{i_state.get(3, 0):,.0f}")
    sc4.metric("P4 Inv", f"{i_state.get(4, 0):,.0f}")

    blocks_meta = {b['block_index']: b for b in getattr(config, 'lt_blocks', [])}
    
    rows = []
    for t in sorted(blocks_meta.keys()):
        b = blocks_meta[t]
        block_start_date = b['start_date']
        block_end_date = b['end_date']
        # Map boundary to the last day index in the block for target lookup
        boundary = b['calendar_day_indices'][-1] if b['calendar_day_indices'] else None
        
        row = {
            "Block": t,
            "Period": b.get('period_key', ''),
            "Demand Source": b.get('demand_source', ''),
            "Start Date": block_start_date,
            "End Date": block_end_date,
            "Production Days": b.get('production_days_available', 0),
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
        if boundary and (boundary, 1) in targets:
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
    st.dataframe(lt_df, hide_index=True, width="stretch")

    objective = entry.get("Objective", 0)
    info_cols = st.columns(3)
    info_cols[0].metric("LT Objective", f"{objective:,.0f}" if objective else "-")
