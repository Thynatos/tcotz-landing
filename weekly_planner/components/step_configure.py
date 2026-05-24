"""
Step 2: Configure — initial state editing, in-transit RM, and BOM editing
with draft/apply patterns and status cards.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import pandas as pd

from core.data_loader import load_in_transit_config, save_in_transit_config
from core.bom_classification import RM_LABELS, RM_BUCKET_LABELS, rm_label
from core.optimizer_helpers import (
    build_usage_matrix,
    complete_rm_usage_matrix,
    dataframe_to_rm_usage_dict,
    usage_matrix_to_dataframe,
)
from core.planning_calendar import build_planning_calendar
from components.shared import (
    _I_PROD_BOM,
    _S_RM_BOM,
    get_initial_state_defaults,
    set_initial_state_widget_values,
    clear_initial_state_widget_values,
    build_initial_state_snapshot,
    pipeline_rows_to_dict,
    save_rm_usage_defaults_yaml,
    load_defaults,
)


def render_step_configure(
    planning_start_date,
    planning_weeks,
    closed_dates,
    sundays_working: bool = False,
) -> dict[str, Any]:
    demand_loaded = st.session_state.get('demand_data') is not None
    tag_text = "✅ Optional" if demand_loaded else "⚙ Optional"
    tag_color = "background:rgba(87,171,90,0.15);color:#8ddb8c;border:1px solid rgba(87,171,90,0.3);" if demand_loaded else "background:rgba(255,255,255,0.06);color:#768390;border:1px solid rgba(255,255,255,0.1);"

    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">'
            f'<span style="font-size:1.15rem;font-weight:700;color:#cdd9e5;">🛠 Configure</span>'
            f'<span style="font-size:0.78rem;font-weight:600;padding:4px 12px;border-radius:999px;{tag_color}">{tag_text}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        init_result = _render_initial_state_section(
            planning_start_date, planning_weeks, closed_dates, sundays_working=sundays_working
        )
        st.divider()
        bom_result = _render_bom_section()
        st.divider()
        cap_result = _render_capacity_section()

    result = {}
    result.update(init_result)
    result.update(bom_result)
    result.update(cap_result)
    return result


def _render_initial_state_section(
    planning_start_date, planning_weeks, closed_dates, sundays_working: bool = False,
) -> dict[str, Any]:
    config_init = load_defaults().get('initial_state', {}) or {}
    _loaded_init_raw = (
        st.session_state.get("initial_state_from_file")
        if "initial_state_from_file" in st.session_state
        else None
    )
    init_defaults = get_initial_state_defaults(
        config_init, _loaded_init_raw if _loaded_init_raw else None
    )

    st.subheader("Initial State", divider=False)

    manual_initial_state_enabled = st.toggle(
        "Customize initial state manually",
        value=bool(st.session_state.get("use_custom_initial_state", False)),
        key="use_custom_initial_state",
        help="Reveal manual inventory, backlog, raw material, and in-transit editing controls.",
    )

    lt_warm_start = False
    init_inv_1 = float(init_defaults.get('p1_inv', 10000))
    init_inv_2 = float(init_defaults.get('p2_inv', 20000))
    init_inv_3 = float(init_defaults.get('p3_inv', 250000))
    init_inv_4 = float(init_defaults.get('p4_inv', 0))
    init_bl_1 = float(init_defaults.get('p1_bl', 0))
    init_bl_2 = float(init_defaults.get('p2_bl', 0))
    init_bl_3 = float(init_defaults.get('p3_bl', 0))
    init_bl_4 = float(init_defaults.get('p4_bl', 0))
    base_rm_init = float(init_defaults.get('base_rm', 2000000))
    rm4_init = float(init_defaults.get('rm4', 6000000))
    rm7_init = float(init_defaults.get('rm7', 4000000))
    rm8_init = float(init_defaults.get('rm8', 1000000))
    manual_pipeline: dict[tuple[int, int], float] = {}
    applied_initial_state_snapshot = st.session_state.get("applied_initial_state_snapshot")
    custom_initial_state_dirty = False
    combined_pipeline: dict[tuple[int, int], float] = {}

    if manual_initial_state_enabled:
        with st.expander("Initial State", expanded=True):
            lt_warm_start = st.toggle(
                "LT Warm-Start",
                value=False,
                help="Solve LT model at day 0 to automatically determine optimal initial inventory. Overrides manual initial inventory values."
            )

            st.caption("Starting inventory levels (units)")
            ic1, ic2 = st.columns(2)
            with ic1:
                init_inv_1 = st.number_input("P1 Inventory", min_value=0.0, value=float(init_defaults.get('p1_inv', 10000)), step=1000.0, key="init_inv_1")
                init_inv_3 = st.number_input("P3 Inventory", min_value=0.0, value=float(init_defaults.get('p3_inv', 250000)), step=10000.0, key="init_inv_3")
            with ic2:
                init_inv_2 = st.number_input("P2 Inventory", min_value=0.0, value=float(init_defaults.get('p2_inv', 20000)), step=1000.0, key="init_inv_2")
                init_inv_4 = st.number_input("P4 Inventory", min_value=0.0, value=float(init_defaults.get('p4_inv', 0)), step=10000.0, key="init_inv_4")

            st.caption("Starting backlog levels (units)")
            bc1, bc2 = st.columns(2)
            with bc1:
                init_bl_1 = st.number_input("P1 Backlog", min_value=0.0, value=float(init_defaults.get('p1_bl', 0)), step=100.0, key="init_bl_1")
                init_bl_3 = st.number_input("P3 Backlog", min_value=0.0, value=float(init_defaults.get('p3_bl', 0)), step=10000.0, key="init_bl_3")
            with bc2:
                init_bl_2 = st.number_input("P2 Backlog", min_value=0.0, value=float(init_defaults.get('p2_bl', 0)), step=100.0, key="init_bl_2")
                init_bl_4 = st.number_input("P4 Backlog", min_value=0.0, value=float(init_defaults.get('p4_bl', 0)), step=10000.0, key="init_bl_4")

            st.caption("Raw material initial stock")
            st.markdown(
                "Stock is tracked in four ERP-aligned buckets. Hover each field for details."
            )
            base_rm_init = st.number_input(
                RM_BUCKET_LABELS['base_rm']['title'],
                min_value=0.0,
                value=float(init_defaults.get('base_rm', 2000000)),
                step=100000.0,
                key="base_rm",
                help=RM_BUCKET_LABELS['base_rm']['description'],
            )
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                rm4_init = st.number_input(
                    RM_BUCKET_LABELS['rm4']['title'],
                    min_value=0.0,
                    value=float(init_defaults.get('rm4', 6000000)),
                    step=500000.0,
                    key="rm4",
                    help=RM_BUCKET_LABELS['rm4']['description'],
                )
            with rc2:
                rm7_init = st.number_input(
                    RM_BUCKET_LABELS['rm7']['title'],
                    min_value=0.0,
                    value=float(init_defaults.get('rm7', 4000000)),
                    step=500000.0,
                    key="rm7",
                    help=RM_BUCKET_LABELS['rm7']['description'],
                )
            with rc3:
                rm8_init = st.number_input(
                    RM_BUCKET_LABELS['rm8']['title'],
                    min_value=0.0,
                    value=float(init_defaults.get('rm8', 1000000)),
                    step=100000.0,
                    key="rm8",
                    help=RM_BUCKET_LABELS['rm8']['description'],
                )

        with st.expander("In-Transit RM", expanded=False):
            in_transit_path = Path(__file__).resolve().parent.parent / "config" / "in_transit.json"
            saved_orders = load_in_transit_config(in_transit_path)
            df_orders = pd.DataFrame(saved_orders, columns=["material", "arrival_day", "qty"])
            if df_orders.empty:
                df_orders = pd.DataFrame(columns=["material", "arrival_day", "qty"])

            st.caption("Add raw material shipments currently in transit. See the RM legend below for what each ID means.")
            _render_rm_legend(compact=True)
            edited_df = st.data_editor(
                df_orders,
                num_rows="dynamic",
                key="in_transit_editor",
                width="stretch",
                column_config={
                    "material": st.column_config.NumberColumn(
                        "RM ID (1-10)",
                        min_value=1,
                        max_value=10,
                        step=1,
                        help="Raw material ID (1-10). See legend above for the meaning of each ID.",
                    ),
                    "arrival_day": st.column_config.NumberColumn("Arrival Day", min_value=1, step=1),
                    "qty": st.column_config.NumberColumn("Quantity", min_value=1.0, format="%.1f")
                }
            )

            if st.button("Save Orders", key="save_transit_btn", width="stretch"):
                validated_orders = []
                for _, row in edited_df.iterrows():
                    if pd.notna(row.get('material')) and pd.notna(row.get('arrival_day')) and pd.notna(row.get('qty')):
                        validated_orders.append({
                            "material": int(row['material']),
                            "arrival_day": int(row['arrival_day']),
                            "qty": float(row['qty'])
                        })
                save_in_transit_config(validated_orders, in_transit_path)
                st.success("Orders saved!")

            for _, row in edited_df.iterrows():
                if pd.notna(row.get('material')) and pd.notna(row.get('arrival_day')) and pd.notna(row.get('qty')):
                    m = int(row['material'])
                    d = int(row['arrival_day'])
                    q = float(row['qty'])
                    if 1 <= m <= 10 and d > 0 and q > 0:
                        manual_pipeline[(m, d)] = manual_pipeline.get((m, d), 0.0) + q

    cal_for_pipeline = build_planning_calendar(
        planning_start_date, planning_weeks, closed_dates, sundays_working=sundays_working
    )
    base_pipeline = pipeline_rows_to_dict(
        st.session_state.get('initial_pipeline_from_file'),
        date_to_legacy_day=cal_for_pipeline.get('date_to_legacy_working_day', {}),
    )
    combined_pipeline = dict(base_pipeline)
    for (m, d), q in manual_pipeline.items():
        combined_pipeline[(m, d)] = combined_pipeline.get((m, d), 0.0) + q

    draft_initial_state_available = (
        "initial_state_from_file" in st.session_state
    ) or manual_initial_state_enabled

    if draft_initial_state_available:
        draft_snapshot = build_initial_state_snapshot(
            init_inv_1=init_inv_1, init_inv_2=init_inv_2, init_inv_3=init_inv_3, init_inv_4=init_inv_4,
            init_bl_1=init_bl_1, init_bl_2=init_bl_2, init_bl_3=init_bl_3, init_bl_4=init_bl_4,
            base_rm_init=base_rm_init, rm4_init=rm4_init, rm7_init=rm7_init, rm8_init=rm8_init,
            lt_warm_start=lt_warm_start, initial_pipeline=combined_pipeline,
        )
        custom_initial_state_dirty = bool(applied_initial_state_snapshot and applied_initial_state_snapshot != draft_snapshot)

        if applied_initial_state_snapshot and not custom_initial_state_dirty:
            st.success("Initial state is applied and ready.", icon="✅")
        elif applied_initial_state_snapshot and custom_initial_state_dirty:
            st.warning("Draft changes not applied. Next run uses last applied state.", icon="⚠️")
        else:
            st.info("Draft values ready. Click Apply to use for next run.", icon="ℹ️")

        if st.button("Apply Initial State", key="apply_init_btn", type="primary", width="stretch"):
            st.session_state["applied_initial_state_snapshot"] = draft_snapshot
            st.rerun()

    if not manual_initial_state_enabled and "initial_state_from_file" not in st.session_state:
        st.session_state.pop("applied_initial_state_snapshot", None)
        st.caption("Defaults are active. Upload a file or enable manual customization only when needed.")

    custom_initial_state_enabled = bool(
        manual_initial_state_enabled
        or ("initial_state_from_file" in st.session_state)
        or applied_initial_state_snapshot
    )
    custom_initial_state_applied = bool(custom_initial_state_enabled and applied_initial_state_snapshot)

    return {
        'custom_initial_state_enabled': custom_initial_state_enabled,
        'custom_initial_state_applied': custom_initial_state_applied,
        'custom_initial_state_dirty': custom_initial_state_dirty,
        'custom_initial_state_loaded': "initial_state_from_file" in st.session_state,
        'lt_warm_start': lt_warm_start,
        'init_inv_1': init_inv_1, 'init_inv_2': init_inv_2, 'init_inv_3': init_inv_3, 'init_inv_4': init_inv_4,
        'init_bl_1': init_bl_1, 'init_bl_2': init_bl_2, 'init_bl_3': init_bl_3, 'init_bl_4': init_bl_4,
        'base_rm_init': base_rm_init, 'rm4_init': rm4_init, 'rm7_init': rm7_init, 'rm8_init': rm8_init,
        'combined_pipeline': combined_pipeline,
    }


def _render_bom_section() -> dict[str, Any]:
    st.subheader("Raw Material Consumption (BOM)", divider=False)

    use_custom_rm_usage = st.toggle(
        "Use custom RM usage (BOM)",
        value=bool(st.session_state.get("use_custom_rm_usage", False)),
        key="use_custom_rm_usage",
        help="Override per-unit raw material consumption (products P1-P4 x RM1-RM10).",
    )
    applied_bom = st.session_state.get("applied_rm_usage")
    custom_rm_usage_dirty = False
    legacy_nis = build_usage_matrix(_I_PROD_BOM, _S_RM_BOM)
    bom_app_nis = applied_bom if applied_bom is not None else legacy_nis

    if use_custom_rm_usage:
        with st.expander("Raw material usage (BOM)", expanded=True):
            st.caption("Coefficients: units of each RM consumed per unit of product produced.")

            _render_rm_legend()

            if "bom_df" not in st.session_state:
                st.session_state["bom_df"] = usage_matrix_to_dataframe(
                    bom_app_nis, _I_PROD_BOM, _S_RM_BOM
                )
            if st.button("Reset grid to app defaults", key="bom_reset_defaults", width="stretch"):
                st.session_state["bom_df"] = usage_matrix_to_dataframe(
                    bom_app_nis, _I_PROD_BOM, _S_RM_BOM
                )
                st.rerun()
            bom_df = st.data_editor(
                st.session_state["bom_df"],
                key="bom_data_editor",
                width="stretch",
                num_rows="fixed",
                column_config={
                    c: st.column_config.NumberColumn(
                        c,
                        help=_column_help_for(c),
                        min_value=0.0,
                        format="%.6g",
                    )
                    for c in st.session_state["bom_df"].columns
                },
            )
            st.session_state["bom_df"] = bom_df
            draft_usage = dataframe_to_rm_usage_dict(bom_df, _I_PROD_BOM, _S_RM_BOM)
            if applied_bom is not None and draft_usage != applied_bom:
                custom_rm_usage_dirty = True

            if applied_bom is not None and not custom_rm_usage_dirty:
                st.success("BOM coefficients applied for next run.", icon="✅")
            elif applied_bom is not None and custom_rm_usage_dirty:
                st.warning("BOM has unapplied edits. Next run uses last applied BOM.", icon="⚠️")
            else:
                st.info("Edit the grid, then Apply BOM Coefficients to use for next run.", icon="ℹ️")

            if st.button("Apply BOM Coefficients", key="apply_bom_btn", type="primary", width="stretch"):
                try:
                    validated_usage = complete_rm_usage_matrix(draft_usage, _I_PROD_BOM, _S_RM_BOM)
                except ValueError as e:
                    st.error(f"Cannot apply BOM: {e}")
                else:
                    st.session_state["applied_rm_usage"] = validated_usage
                    st.session_state["bom_df"] = usage_matrix_to_dataframe(
                        validated_usage, _I_PROD_BOM, _S_RM_BOM
                    )
                    save_rm_usage_defaults_yaml(validated_usage)
                    st.rerun()
    else:
        if st.session_state.get("applied_rm_usage") is not None:
            st.caption("BOM settings are preserved while disabled.")

    custom_rm_usage_applied = bool(use_custom_rm_usage and st.session_state.get("applied_rm_usage"))

    return {
        'custom_rm_usage_enabled': use_custom_rm_usage,
        'custom_rm_usage_applied': custom_rm_usage_applied,
        'custom_rm_usage_dirty': custom_rm_usage_dirty,
    }


def _render_rm_legend(compact: bool = False) -> None:
    """Show a reference table explaining what each RM1..RM10 represents.

    When ``compact`` is True the legend is collapsed inside an expander so it
    does not dominate smaller sections (e.g. the In-Transit editor).
    """
    bucket_title = {k: v['title'].split(' — ')[0] for k, v in RM_BUCKET_LABELS.items()}
    rows = []
    for s in sorted(RM_LABELS):
        meta = RM_LABELS[s]
        rows.append({
            'RM': f"RM{s}",
            'Description': meta['description'],
            'ERP stock bucket': bucket_title.get(meta['bucket'], meta['bucket']),
        })
    legend_df = pd.DataFrame(rows)

    def _render_table() -> None:
        st.dataframe(legend_df, hide_index=True, width="stretch")
        st.caption(
            "ERP stock buckets map to initial-state keys: **base_rm** (bulk ingredients + misc. packaging), "
            "**rm4** (bubble packaging), **rm7** (drink film), **rm8** (drink cartons)."
        )

    if compact:
        with st.expander("RM legend (click to expand)", expanded=False):
            _render_table()
    else:
        _render_table()


def _column_help_for(col: str) -> str:
    """Tooltip text for a BOM grid column ('RM1'..'RM10') — description + bucket."""
    if not isinstance(col, str) or not col.startswith("RM"):
        return col
    try:
        s = int(col[2:])
    except ValueError:
        return col
    meta = RM_LABELS.get(s)
    if not meta:
        return col
    return f"{meta['description']} — ERP bucket: {meta['bucket']}"


_CAP_L1_DEFAULT = {1: 1000.0, 2: 500.0, 3: 2000.0}
_CAP_P3_DEFAULT = {1: 10000.0, 2: 25000.0}
_CAP_P4_DEFAULT = 80000.0


def _capacity_defaults() -> dict[str, Any]:
    """Read machine capacity defaults from config/defaults.yaml (falling back to legacy constants)."""
    cfg = load_defaults().get("machine_capacity", {}) or {}
    raw_l1 = cfg.get("line1", {}) or {}
    raw_p3 = cfg.get("line2_p3", {}) or {}

    def _coerce_machine_dict(raw: dict, fallback: dict) -> dict[int, float]:
        out: dict[int, float] = {}
        for k, v in raw.items():
            try:
                out[int(k)] = float(v)
            except (TypeError, ValueError):
                continue
        for k, v in fallback.items():
            out.setdefault(k, v)
        return out

    return {
        "cap_l1": _coerce_machine_dict(raw_l1, _CAP_L1_DEFAULT),
        "cap_p3": _coerce_machine_dict(raw_p3, _CAP_P3_DEFAULT),
        "cap_p4": float(cfg.get("line_p4", _CAP_P4_DEFAULT)),
    }


def _render_capacity_section() -> dict[str, Any]:
    st.subheader("Machine Capacities", divider=False)

    defaults = _capacity_defaults()
    applied = st.session_state.get("applied_machine_capacity")

    use_custom_capacity = st.toggle(
        "Customize machine capacities",
        value=bool(st.session_state.get("use_custom_capacity", False)),
        key="use_custom_capacity",
        help="Override per-machine daily production capacity (units/day).",
    )

    base = applied if applied is not None else defaults
    base_l1 = base.get("cap_l1", defaults["cap_l1"])
    base_p3 = base.get("cap_p3", defaults["cap_p3"])
    base_p4 = float(base.get("cap_p4", defaults["cap_p4"]))

    draft_l1 = dict(base_l1)
    draft_p3 = dict(base_p3)
    draft_p4 = base_p4
    custom_capacity_dirty = False

    if use_custom_capacity:
        with st.expander("Machine capacities (units/day)", expanded=True):
            st.caption("Line 1 (P1 / P2) — 3 machines")
            l1a, l1b, l1c = st.columns(3)
            with l1a:
                draft_l1[1] = float(st.number_input(
                    "L1 Machine 1", min_value=0.0,
                    value=float(base_l1.get(1, _CAP_L1_DEFAULT[1])),
                    step=100.0, format="%.2f", key="cap_l1_1",
                ))
            with l1b:
                draft_l1[2] = float(st.number_input(
                    "L1 Machine 2", min_value=0.0,
                    value=float(base_l1.get(2, _CAP_L1_DEFAULT[2])),
                    step=100.0, format="%.2f", key="cap_l1_2",
                ))
            with l1c:
                draft_l1[3] = float(st.number_input(
                    "L1 Machine 3", min_value=0.0,
                    value=float(base_l1.get(3, _CAP_L1_DEFAULT[3])),
                    step=100.0, format="%.2f", key="cap_l1_3",
                ))

            st.caption("Line 2 (P3) — 2 machines")
            p3a, p3b = st.columns(2)
            with p3a:
                draft_p3[1] = float(st.number_input(
                    "P3 Machine 1", min_value=0.0,
                    value=float(base_p3.get(1, _CAP_P3_DEFAULT[1])),
                    step=1000.0, format="%.2f", key="cap_p3_1",
                ))
            with p3b:
                draft_p3[2] = float(st.number_input(
                    "P3 Machine 2", min_value=0.0,
                    value=float(base_p3.get(2, _CAP_P3_DEFAULT[2])),
                    step=1000.0, format="%.2f", key="cap_p3_2",
                ))

            st.caption("P4 line — 1 machine")
            draft_p4 = float(st.number_input(
                "P4 Machine", min_value=0.0,
                value=base_p4,
                step=1000.0, format="%.2f", key="cap_p4",
            ))

            draft_snapshot = {
                "cap_l1": draft_l1,
                "cap_p3": draft_p3,
                "cap_p4": draft_p4,
            }
            if applied is not None and applied != draft_snapshot:
                custom_capacity_dirty = True

            if applied is not None and not custom_capacity_dirty:
                st.success("Machine capacities applied for next run.", icon="✅")
            elif applied is not None and custom_capacity_dirty:
                st.warning("Capacity edits not applied. Next run uses last applied values.", icon="⚠️")
            else:
                st.info("Edit values, then Apply Capacities to use for next run.", icon="ℹ️")

            if st.button("Apply Capacities", key="apply_capacity_btn", type="primary", width="stretch"):
                st.session_state["applied_machine_capacity"] = draft_snapshot
                st.rerun()
    else:
        if st.session_state.get("applied_machine_capacity") is not None:
            st.caption("Custom capacities are preserved while disabled.")

    custom_capacity_applied = bool(
        use_custom_capacity and st.session_state.get("applied_machine_capacity")
    )

    return {
        "custom_capacity_enabled": use_custom_capacity,
        "custom_capacity_applied": custom_capacity_applied,
        "custom_capacity_dirty": custom_capacity_dirty,
    }