"""
Step 1: Load Data — demand file, optional forecast, and initial-state file uploads.
"""
from __future__ import annotations

import datetime
from typing import Any, Optional, Tuple

import streamlit as st
import pandas as pd

from core.bom_classification import RM_LABELS, RM_BUCKET_LABELS
from core.data_loader import DemandLoader, load_initial_state_from_file, load_custom_forecast
from core.validators import DataValidator
from core.planning_calendar import next_monday
from components.shared import (
    set_initial_state_widget_values,
    clear_initial_state_widget_values,
    get_initial_state_defaults,
    load_defaults,
)


_MANUAL_DAILY_KEY = "manual_daily_df"
_MANUAL_MONTHLY_KEY = "manual_monthly_df"


def _empty_manual_daily() -> pd.DataFrame:
    return pd.DataFrame({
        'date': pd.Series([], dtype='object'),
        'product': pd.Series([], dtype='Int64'),
        'demand': pd.Series([], dtype='float'),
    })


def _empty_manual_monthly() -> pd.DataFrame:
    return pd.DataFrame({
        'month': pd.Series([], dtype='object'),
        'product': pd.Series([], dtype='Int64'),
        'demand': pd.Series([], dtype='float'),
    })


def render_step_data() -> dict[str, Any]:
    demand_loaded = st.session_state.get('demand_data') is not None
    tag_text = "✅ Ready" if demand_loaded else "⚠ Required"
    tag_color = "background:rgba(87,171,90,0.15);color:#8ddb8c;border:1px solid rgba(87,171,90,0.3);" if demand_loaded else "background:rgba(83,155,245,0.15);color:#a2cdff;border:1px solid rgba(83,155,245,0.3);"

    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">'
            f'<span style="font-size:1.15rem;font-weight:700;color:#cdd9e5;">📂 Load Data</span>'
            f'<span style="font-size:0.78rem;font-weight:600;padding:4px 12px;border-radius:999px;{tag_color}">{tag_text}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        upload_tab, manual_tab = st.tabs(["Upload file", "Enter manually"])

        uploaded_file = None
        uploaded_forecast = None
        load_demand_clicked = False

        with upload_tab:
            uploaded_file = st.file_uploader(
                "Upload demand file",
                type=['xlsx', 'xls', 'csv'],
                help="Excel: Daily + Monthly sheets. CSV: date/day, product, demand.",
                label_visibility="collapsed",
                key="main_demand_file_uploader",
            )
            if uploaded_file:
                st.caption(f"File: {uploaded_file.name}")

            with st.expander("Monthly forecast override (optional)", expanded=False):
                uploaded_forecast = st.file_uploader(
                    "Upload monthly forecast",
                    type=['xlsx', 'xls', 'csv'],
                    help="Optional override for the monthly forecast input.",
                    label_visibility="collapsed",
                    key="main_forecast_file_uploader",
                )
                if uploaded_forecast:
                    st.caption(f"Forecast: {uploaded_forecast.name}")

            load_demand_clicked = st.button("Load Data", type="primary", key="main_load_demand_btn", width="stretch")

            if load_demand_clicked:
                if uploaded_file is not None:
                    daily_demand, monthly_demand = _load_demand_data(uploaded_file)
                    if daily_demand is not None:
                        st.session_state.demand_data = daily_demand
                        st.session_state.monthly_demand = monthly_demand
                        st.session_state.result = None

                    if uploaded_forecast is not None:
                        planning_start_date = st.session_state.get("planning_start_date", next_monday())
                        custom_forecast = load_custom_forecast(
                            uploaded_forecast,
                            planning_start_date=planning_start_date,
                        )
                        if isinstance(custom_forecast, pd.DataFrame) and not custom_forecast.empty:
                            existing_monthly = st.session_state.get('monthly_demand')
                            if existing_monthly is None:
                                st.session_state.monthly_demand = custom_forecast
                            else:
                                st.session_state.monthly_demand = pd.concat([existing_monthly, custom_forecast], ignore_index=True)
                            st.success("Custom forecast loaded successfully.")
                else:
                    st.error("Please upload a demand file first.")

        with manual_tab:
            _render_manual_entry()

    st.divider()

    with st.container(border=True):
        st.subheader("Initial State", divider=False)

        uploaded_initial_state_file = st.file_uploader(
            "Upload initial state file",
            type=['xlsx', 'xls', 'csv'],
            help=(
                "Upload SAYIM / ERP inventory (Excel: ÜRÜN İSMİ + SİSTEM STOK or FİZİKİ) — preferred when present. "
                "Or BobaCo parameter/value table (Initial sheet). CSV: either format."
            ),
            label_visibility="collapsed",
            key="main_init_state_file",
        )
        if uploaded_initial_state_file:
            st.caption(f"File: {uploaded_initial_state_file.name}")

        if "initial_state_from_file" in st.session_state:
            st.success("Initial state file loaded.", icon="✅")
            pipeline_loaded = st.session_state.get('initial_pipeline_from_file')
            if pipeline_loaded:
                st.caption(f"{len(pipeline_loaded)} in-transit RM shipment(s) loaded.")
            if st.button("Clear loaded state", key="main_clear_init_btn"):
                st.session_state.pop('initial_state_from_file', None)
                st.session_state.pop('initial_pipeline_from_file', None)
                st.session_state.pop("applied_initial_state_snapshot", None)
                config_init = load_defaults().get('initial_state', {}) or {}
                clear_initial_state_widget_values()
                set_initial_state_widget_values(get_initial_state_defaults(config_init))
                st.rerun()

        load_init_clicked = st.button("Load Initial State", key="main_load_init_btn", width="stretch")

        if load_init_clicked:
            if uploaded_initial_state_file is None:
                st.warning("Upload an initial-state file before clicking Load Initial State.")
            else:
                init_dict, pipeline, errors, warnings = load_initial_state_from_file(uploaded_initial_state_file)
                for w in warnings:
                    st.warning(w)
                for e in errors:
                    st.error(e)
                if init_dict is not None:
                    st.session_state.initial_state_from_file = init_dict
                    st.session_state.initial_pipeline_from_file = pipeline
                    st.session_state.pop("applied_initial_state_snapshot", None)
                    set_initial_state_widget_values(init_dict)
                    st.success("Initial state file loaded. Review and apply in Step 2.")
                    st.rerun()

        with st.expander("File format help", expanded=False):
            st.markdown("**Demand file**")
            st.markdown(
                "**Sheet: Daily** — columns: `date`, `product`, `demand` "
                "(preferred) **or** `day`, `product`, `demand` (legacy)"
            )
            st.markdown(
                "- **`date`**: actual calendar date (e.g. `2026-04-14`). "
                "Automatically mapped to the correct day index based on planning start date.\n"
                "- **`day`**: legacy working-day index (1-based, skips Sundays)."
            )
            st.markdown("**Sheet: Monthly** — columns: month, product, demand")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Daily (date-based — preferred)")
                example_daily = pd.DataFrame({
                    'date': ['2026-04-13', '2026-04-13', '2026-04-13', '...', '2026-05-30'],
                    'product': [1, 3, 4, '...', 4],
                    'demand': [3023, 321, 659, '...', 1900]
                })
                st.dataframe(example_daily, hide_index=True, width="stretch")
            with col2:
                example_monthly = pd.DataFrame({
                    'month': [1, 1, 1, '...', 12],
                    'product': [1, 3, 4, '...', 4],
                    'demand': [72000, 50000, 40000, '...', 35000]
                })
                st.dataframe(example_monthly, hide_index=True, width="stretch")
            st.caption("Both sheets are required. Daily = short-term demand. Monthly = company forecast for long-term planning.")
            st.markdown("---")
            st.markdown("**Initial state file** (optional)")
            st.markdown("**Sheet: Initial** — columns: parameter, value")
            st.markdown("**Sheet: In_Transit** (optional) — columns: material, arrival_day, qty")
            col3, col4 = st.columns(2)
            with col3:
                example_init = pd.DataFrame({
                    'parameter': ['p1_inv', 'p3_inv', 'base_rm', 'rm4'],
                    'value': [10000, 250000, 2000000, 6000000]
                })
                st.dataframe(example_init, hide_index=True, width="stretch")
            with col4:
                example_transit = pd.DataFrame({
                    'material': [1, 4, 7],
                    'arrival_day': [7, 12, 25],
                    'qty': [50000, 100000, 80000]
                })
                st.dataframe(example_transit, hide_index=True, width="stretch")

            st.markdown("**Raw material IDs and ERP stock buckets**")
            bucket_title = {k: v['title'].split(' — ')[0] for k, v in RM_BUCKET_LABELS.items()}
            rm_rows = []
            for s in sorted(RM_LABELS):
                meta = RM_LABELS[s]
                rm_rows.append({
                    'RM': f"RM{s}",
                    'Description': meta['description'],
                    'ERP stock bucket': bucket_title.get(meta['bucket'], meta['bucket']),
                })
            st.dataframe(pd.DataFrame(rm_rows), hide_index=True, width="stretch")
            st.caption(
                "Initial-state keys map to ERP stock buckets: "
                "**base_rm** (bulk ingredients + misc. packaging — RM1, RM2, RM3, RM5, RM6, RM9, RM10), "
                "**rm4** (bubble packaging — KOVA-KAPAK, ETIKET), "
                "**rm7** (drink upper film — BASKISIZ / CPP), "
                "**rm8** (drink cartons — KOLI / KUTU)."
            )

    return {
        'load_demand_clicked': load_demand_clicked,
        'uploaded_file': uploaded_file,
        'uploaded_forecast': uploaded_forecast,
        'load_init_clicked': load_init_clicked,
        'uploaded_initial_state_file': uploaded_initial_state_file,
    }


def _load_demand_data(file: Any) -> Tuple[Optional[dict], Optional[dict]]:
    loader = DemandLoader()
    daily_demand, monthly_demand, errors, warnings = loader.load_demand_from_file(file)

    for w in warnings:
        st.warning(w)
    for e in errors:
        st.error(e)

    if daily_demand is not None:
        st.success(
            f"Loaded {len(daily_demand)} daily demand records"
            + (f" and {len(monthly_demand)} monthly forecast records." if (monthly_demand is not None and not monthly_demand.empty) else ".")
        )

    return daily_demand, monthly_demand


def _render_manual_entry() -> None:
    """Manual demand / forecast entry using data_editor grids.

    Contents persist in session_state (manual_daily_df / manual_monthly_df)
    across reruns. On Load, rows are validated and written into the same
    session_state slots used by the upload flow.
    """
    planning_start_date = st.session_state.get("planning_start_date", next_monday())
    planning_weeks = int(st.session_state.get("planning_weeks", 8) or 8)

    if _MANUAL_DAILY_KEY not in st.session_state:
        st.session_state[_MANUAL_DAILY_KEY] = _empty_manual_daily()
    if _MANUAL_MONTHLY_KEY not in st.session_state:
        st.session_state[_MANUAL_MONTHLY_KEY] = _empty_manual_monthly()

    st.caption(
        "Enter demand directly below. Dates must fall within the planning horizon; "
        f"valid product IDs are 1-4. Horizon starts {planning_start_date} for {planning_weeks} week(s)."
    )

    fill1, fill2, fill3 = st.columns([1, 1, 1])
    with fill1:
        if st.button("Seed horizon (P1-P4)", key="manual_seed_btn", width="stretch"):
            st.session_state[_MANUAL_DAILY_KEY] = _seed_daily_grid(planning_start_date, planning_weeks)
            st.session_state[_MANUAL_MONTHLY_KEY] = _seed_monthly_grid(planning_start_date)
            st.rerun()
    with fill2:
        if st.button("Add blank row (daily)", key="manual_add_daily_row", width="stretch"):
            current = st.session_state[_MANUAL_DAILY_KEY]
            blank = pd.DataFrame([{'date': None, 'product': None, 'demand': None}])
            st.session_state[_MANUAL_DAILY_KEY] = pd.concat([current, blank], ignore_index=True)
            st.rerun()
    with fill3:
        if st.button("Clear grids", key="manual_clear_btn", width="stretch"):
            st.session_state[_MANUAL_DAILY_KEY] = _empty_manual_daily()
            st.session_state[_MANUAL_MONTHLY_KEY] = _empty_manual_monthly()
            st.rerun()

    st.markdown("**Daily demand**")
    daily_df = st.data_editor(
        st.session_state[_MANUAL_DAILY_KEY],
        key="manual_daily_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "product": st.column_config.NumberColumn("Product", min_value=1, max_value=4, step=1),
            "demand": st.column_config.NumberColumn("Demand", min_value=0.0, format="%.2f"),
        },
    )
    st.session_state[_MANUAL_DAILY_KEY] = daily_df

    st.markdown("**Monthly forecast**")
    monthly_df = st.data_editor(
        st.session_state[_MANUAL_MONTHLY_KEY],
        key="manual_monthly_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "month": st.column_config.TextColumn("Month (YYYY-MM)", help="Use YYYY-MM format, e.g. 2026-05"),
            "product": st.column_config.NumberColumn("Product", min_value=1, max_value=4, step=1),
            "demand": st.column_config.NumberColumn("Demand", min_value=0.0, format="%.2f"),
        },
    )
    st.session_state[_MANUAL_MONTHLY_KEY] = monthly_df

    if st.button("Load Manual Data", type="primary", key="manual_load_btn", width="stretch"):
        _commit_manual_entry(daily_df, monthly_df)


def _seed_daily_grid(planning_start_date: datetime.date, planning_weeks: int) -> pd.DataFrame:
    rows = []
    total_days = planning_weeks * 7
    for i in range(total_days):
        d = planning_start_date + datetime.timedelta(days=i)
        if d.weekday() == 6:
            continue
        for p in (1, 2, 3, 4):
            rows.append({'date': d, 'product': p, 'demand': 0.0})
    return pd.DataFrame(rows)


def _seed_monthly_grid(planning_start_date: datetime.date) -> pd.DataFrame:
    from dateutil.relativedelta import relativedelta

    rows = []
    for offset in range(12):
        month_start = (planning_start_date.replace(day=1) + relativedelta(months=offset))
        key = month_start.strftime('%Y-%m')
        for p in (1, 2, 3, 4):
            rows.append({'month': key, 'product': p, 'demand': 0.0})
    return pd.DataFrame(rows)


def _commit_manual_entry(daily_df: pd.DataFrame, monthly_df: pd.DataFrame) -> None:
    daily_clean = _normalize_manual_daily(daily_df)
    if daily_clean is None:
        return

    monthly_clean = _normalize_manual_monthly(monthly_df)
    if monthly_clean is None:
        return

    validator = DataValidator()
    vr = validator.validate_demand_file(daily_clean.copy())
    if not vr:
        for e in vr.errors:
            st.error(e)
        return
    for w in vr.warnings:
        st.warning(w)

    st.session_state.demand_data = daily_clean
    st.session_state.monthly_demand = monthly_clean if monthly_clean is not None and not monthly_clean.empty else None
    st.session_state.result = None

    monthly_note = (
        f" and {len(monthly_clean)} monthly forecast record(s)"
        if monthly_clean is not None and not monthly_clean.empty
        else ""
    )
    st.success(f"Loaded {len(daily_clean)} daily demand record(s){monthly_note} from manual entry.")


def _normalize_manual_daily(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        st.error("Daily demand grid is empty. Add rows or switch to file upload.")
        return None

    working = df.copy()
    working = working.dropna(subset=['date', 'product', 'demand'], how='all')

    missing = working[working[['date', 'product', 'demand']].isna().any(axis=1)]
    if not missing.empty:
        st.error(f"Daily rows have missing fields at index(es): {missing.index.tolist()[:5]}. Every row needs date, product, and demand.")
        return None

    if working.empty:
        st.error("Daily demand grid has no complete rows.")
        return None

    try:
        working['date'] = pd.to_datetime(working['date']).dt.date
    except Exception as e:
        st.error(f"Could not parse 'date' column: {e}")
        return None

    try:
        working['product'] = working['product'].astype(int)
    except Exception:
        st.error("Column 'product' must be integer values 1-4.")
        return None

    try:
        working['demand'] = working['demand'].astype(float)
    except Exception:
        st.error("Column 'demand' must be numeric.")
        return None

    return working.reset_index(drop=True)


def _normalize_manual_monthly(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        return pd.DataFrame(columns=['month', 'product', 'demand'])

    working = df.copy()
    working = working.dropna(subset=['month', 'product', 'demand'], how='all')

    missing = working[working[['month', 'product', 'demand']].isna().any(axis=1)]
    if not missing.empty:
        st.error(f"Monthly rows have missing fields at index(es): {missing.index.tolist()[:5]}. Every row needs month, product, and demand.")
        return None

    if working.empty:
        return pd.DataFrame(columns=['month', 'product', 'demand'])

    working['month'] = working['month'].astype(str).str.strip()
    bad_months = [m for m in working['month'].unique() if not _looks_like_ym(m)]
    if bad_months:
        st.error(f"Monthly 'month' column must be YYYY-MM. Invalid: {bad_months[:5]}")
        return None

    try:
        working['product'] = working['product'].astype(int)
    except Exception:
        st.error("Monthly 'product' must be integer 1-4.")
        return None

    valid_products = {1, 2, 3, 4}
    bad_products = set(working['product'].unique()) - valid_products
    if bad_products:
        st.error(f"Monthly invalid product IDs: {bad_products}. Valid: 1, 2, 3, 4")
        return None

    try:
        working['demand'] = working['demand'].astype(float)
    except Exception:
        st.error("Monthly 'demand' must be numeric.")
        return None

    if (working['demand'] < 0).any():
        st.error("Monthly 'demand' cannot be negative.")
        return None

    return working.reset_index(drop=True)


def _looks_like_ym(s: str) -> bool:
    if not isinstance(s, str):
        return False
    if len(s) != 7 or s[4] != '-':
        return False
    y, m = s.split('-')
    return y.isdigit() and m.isdigit() and 1 <= int(m) <= 12