"""
Shared helpers and constants used by sidebar and step components.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import yaml

from core.data_loader import merge_initial_state, load_in_transit_config, save_in_transit_config
from core.optimizer_helpers import (
    build_usage_matrix,
    complete_rm_usage_matrix,
    dataframe_to_rm_usage_dict,
    usage_matrix_to_dataframe,
)
from core.planning_calendar import coerce_date

import pandas as pd


_I_PROD_BOM = [1, 2, 3, 4]
_S_RM_BOM = list(range(1, 11))

INITIAL_STATE_FALLBACKS = {
    'p1_inv': 10000.0,
    'p2_inv': 20000.0,
    'p3_inv': 250000.0,
    'p4_inv': 0.0,
    'p1_bl': 0.0,
    'p2_bl': 0.0,
    'p3_bl': 0.0,
    'p4_bl': 0.0,
    'base_rm': 2000000.0,
    'rm4': 6000000.0,
    'rm7': 4000000.0,
    'rm8': 1000000.0,
}

INITIAL_STATE_WIDGET_KEYS = {
    'p1_inv': "init_inv_1",
    'p2_inv': "init_inv_2",
    'p3_inv': "init_inv_3",
    'p4_inv': "init_inv_4",
    'p1_bl': "init_bl_1",
    'p2_bl': "init_bl_2",
    'p3_bl': "init_bl_3",
    'p4_bl': "init_bl_4",
    'base_rm': "base_rm",
    'rm4': "rm4",
    'rm7': "rm7",
    'rm8': "rm8",
}


def load_defaults() -> dict[str, Any]:
    base_path = Path(__file__).parent.parent / "config" / "defaults.yaml"
    out: dict[str, Any] = {}
    if base_path.exists():
        with open(base_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                out = loaded
    rm_path = Path(__file__).parent.parent / "config" / "rm_usage_defaults.yaml"
    if rm_path.exists():
        try:
            with open(rm_path, 'r', encoding='utf-8') as f:
                rm_doc = yaml.safe_load(f)
            if isinstance(rm_doc, dict) and isinstance(rm_doc.get("rm_usage"), dict):
                out["rm_usage"] = dict(rm_doc["rm_usage"])
        except (OSError, yaml.YAMLError, TypeError):
            pass
    return out


def get_initial_state_defaults(config_init: dict[str, Any] | None, loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    defaults = dict(INITIAL_STATE_FALLBACKS)
    if config_init:
        defaults.update(config_init)
    return merge_initial_state(defaults, loaded if loaded else None)


def set_initial_state_widget_values(values: dict[str, Any]) -> None:
    for param_key, widget_key in INITIAL_STATE_WIDGET_KEYS.items():
        if param_key in values:
            st.session_state[widget_key] = float(values[param_key])


def clear_initial_state_widget_values() -> None:
    for widget_key in INITIAL_STATE_WIDGET_KEYS.values():
        st.session_state.pop(widget_key, None)


def build_initial_state_snapshot(
    init_inv_1: float,
    init_inv_2: float,
    init_inv_3: float,
    init_inv_4: float,
    init_bl_1: float,
    init_bl_2: float,
    init_bl_3: float,
    init_bl_4: float,
    base_rm_init: float,
    rm4_init: float,
    rm7_init: float,
    rm8_init: float,
    lt_warm_start: bool,
    initial_pipeline: dict[tuple[int, int], float],
) -> dict[str, Any]:
    return {
        'initial_inventory': {1: init_inv_1, 2: init_inv_2, 3: init_inv_3, 4: init_inv_4},
        'initial_backlog': {1: init_bl_1, 2: init_bl_2, 3: init_bl_3, 4: init_bl_4},
        'base_rm_init': base_rm_init,
        'rm4_init': rm4_init,
        'rm7_init': rm7_init,
        'rm8_init': rm8_init,
        'initial_pipeline': dict(initial_pipeline),
        'lt_warm_start': lt_warm_start,
    }


def pipeline_rows_to_dict(
    pipeline_rows,
    date_to_legacy_day: dict[Any, int] | None = None,
) -> dict[tuple[int, int], float]:
    merged: dict[tuple[int, int], float] = {}
    if pipeline_rows is None:
        return merged

    if isinstance(pipeline_rows, dict):
        for (m, d), q in pipeline_rows.items():
            mat = int(m)
            arr_day = int(d)
            qty = float(q)
            if mat >= 1 and arr_day >= 1 and qty > 0:
                merged[(mat, arr_day)] = merged.get((mat, arr_day), 0.0) + qty
        return merged

    if isinstance(pipeline_rows, pd.DataFrame):
        records = pipeline_rows.to_dict("records")
    elif isinstance(pipeline_rows, list):
        records = pipeline_rows
    else:
        return merged

    for row in records:
        material_val = row.get("material")
        qty_val = row.get("qty")
        if material_val is None or qty_val is None:
            continue
        if bool(pd.isna(material_val)) or bool(pd.isna(qty_val)):
            continue
        arrival_day_val = row.get("arrival_day")
        if arrival_day_val is None or bool(pd.isna(arrival_day_val)):
            date_val = row.get("expected_delivery_date")
            if date_val is None or bool(pd.isna(date_val)):
                date_val = row.get("arrival_date")
            date_obj = coerce_date(date_val) if date_val is not None else None
            if date_obj is not None and date_to_legacy_day is not None:
                arrival_day_val = date_to_legacy_day.get(date_obj)
        if arrival_day_val is None or bool(pd.isna(arrival_day_val)):
            continue
        mat = int(material_val)
        arr_day = int(arrival_day_val)
        qty = float(qty_val)
        if mat >= 1 and arr_day >= 1 and qty > 0:
            merged[(mat, arr_day)] = merged.get((mat, arr_day), 0.0) + qty

    return merged


def save_rm_usage_defaults_yaml(rm_usage: dict[tuple[int, int], float]) -> None:
    path = Path(__file__).parent.parent / "config" / "rm_usage_defaults.yaml"
    serial = {f"{i}_{s}": float(q) for (i, s), q in rm_usage.items()}
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({"rm_usage": serial}, f, sort_keys=False, allow_unicode=True)


def maybe_seed_bom_from_defaults(defaults: dict[str, Any]) -> None:
    if st.session_state.get("bom_defaults_loaded"):
        return
    rm_raw = defaults.get("rm_usage")
    if not rm_raw:
        st.session_state["bom_defaults_loaded"] = True
        return
    try:
        validated = complete_rm_usage_matrix(rm_raw, _I_PROD_BOM, _S_RM_BOM)
    except (ValueError, TypeError):
        st.session_state["bom_defaults_loaded"] = True
        return
    st.session_state["applied_rm_usage"] = validated
    st.session_state["bom_df"] = usage_matrix_to_dataframe(validated, _I_PROD_BOM, _S_RM_BOM)
    st.session_state["use_custom_rm_usage"] = True
    st.session_state["bom_defaults_loaded"] = True