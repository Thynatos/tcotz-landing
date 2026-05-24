"""
Data loading utilities for demand and configuration files.
"""
from __future__ import annotations

from typing import Any, Optional
import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import json
import yaml
from pathlib import Path
from typing import Optional

from .bom_classification import sayim_row_rm_bucket
from .validators import DataValidator


# Sheet name candidates (first match wins)
_DAILY_SHEET_NAMES = ['Daily', 'daily', 'ST', 'short_term', 'ShortTerm']
_MONTHLY_SHEET_NAMES = ['Monthly', 'monthly', 'LT', 'long_term', 'LongTerm', 'Forecast']
_INITIAL_SHEET_NAMES = ['Initial', 'Initial_State', 'Config', 'initial', 'initial_state', 'config']
_PIPELINE_SHEET_NAMES = ['In_Transit', 'in_transit', 'Pipeline', 'pipeline', 'RM_In_Transit', 'rm_in_transit']

# Valid parameter names for initial state file
_INITIAL_STATE_KEYS = {
    'p1_inv', 'p2_inv', 'p3_inv', 'p4_inv',
    'p1_bl', 'p2_bl', 'p3_bl', 'p4_bl',
    'base_rm', 'rm4', 'rm7', 'rm8',
}


class DemandLoader:
    """Loads and parses demand data from various sources."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize loader with optional config.
        
        Args:
            config_path: Path to defaults.yaml
        """
        self.config = {}
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
    
    def load_excel(self, file, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Load demand data from Excel file.
        
        Args:
            file: File path or file-like object
            sheet_name: Specific sheet to load (optional)
            
        Returns:
            DataFrame with demand data
            
        Raises:
            ValueError: If file cannot be parsed
        """
        try:
            # Try to load with specified sheet or first sheet
            if sheet_name:
                df = pd.read_excel(file, sheet_name=sheet_name)
            else:
                # Try common sheet names first
                excel_file = pd.ExcelFile(file)
                sheet_names = excel_file.sheet_names
                
                # Priority order for sheet detection
                priority_sheets = ['demand', 'Demand', 'DEMAND', 'data', 'Data', 'Sheet1']
                
                target_sheet = None
                for name in priority_sheets:
                    if name in sheet_names:
                        target_sheet = name
                        break
                
                if target_sheet is None:
                    target_sheet = sheet_names[0]
                
                df = pd.read_excel(file, sheet_name=target_sheet)
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    def convert_to_demand_dict(self, df: pd.DataFrame, time_col: str = 'day') -> dict:
        """
        Convert DataFrame to demand dictionary format.
        
        Args:
            df: DataFrame with columns: day/month, product, demand
            time_col: Name of the time column ('day' or 'month')
            
        Returns:
            Dictionary {(product, time_index): demand}
        """
        demand_dict = {}
        
        for _, row in df.iterrows():
            product = int(row['product'])
            time_index = int(row[time_col])
            demand = float(row['demand'])
            demand_dict[(product, time_index)] = demand
        
        return demand_dict
    
    def create_template_dataframe(self, horizon: int = 240) -> pd.DataFrame:
        """
        Create a template DataFrame for demand input.
        
        Args:
            horizon: Number of days
            
        Returns:
            Empty template DataFrame
        """
        days = list(range(1, horizon + 1)) * 3  # Products 1, 3, 4 (not 2)
        products = [1] * horizon + [3] * horizon + [4] * horizon
        demands = [0] * (horizon * 3)
        
        return pd.DataFrame({
            'day': days,
            'product': products,
            'demand': demands
        })
    
    def get_available_sheets(self, file) -> list[str]:
        """
        Get list of sheets in an Excel file.
        
        Args:
            file: File path or file-like object
            
        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file)
            return excel_file.sheet_names
        except Exception:
            return []

    def load_demand_from_file(self, file) -> tuple[pd.DataFrame | None, pd.DataFrame | None, list[str], list[str]]:
        """Load and validate demand data from an uploaded file (Excel or CSV).

        For Excel: expects a 'Daily' sheet (realized demand) and a 'Monthly'
        sheet (forecast).  For CSV: expects columns day, product, demand; an
        optional 'month' column enables monthly aggregation.

        Returns:
            (daily_demand, monthly_demand, errors, warnings)
            daily_demand:   {(product, day): demand} or None on failure
            monthly_demand: {(product, month): demand} or None
            errors:         list of error strings (empty on success)
            warnings:       list of warning strings
        """
        filename = getattr(file, 'name', '')
        is_csv = filename.lower().endswith('.csv')

        errors: list[str] = []
        warnings: list[str] = []
        validator = DataValidator()

        try:
            if is_csv:
                daily_df = pd.read_csv(file)
                daily_df.columns = daily_df.columns.str.strip().str.lower()
                monthly_df = None

                # If the CSV has a 'month' column, aggregate to monthly
                if 'month' in daily_df.columns:
                    monthly_rows = daily_df[['month', 'product', 'demand']].dropna(subset=['month'])
                    if not monthly_rows.empty:
                        monthly_df = monthly_rows.groupby(['product', 'month'], as_index=False)['demand'].sum()
            else:
                xl = pd.ExcelFile(file)
                sheets = xl.sheet_names

                # Find daily sheet
                daily_df = None
                for name in _DAILY_SHEET_NAMES:
                    if name in sheets:
                        daily_df = pd.read_excel(xl, sheet_name=name)
                        break
                if daily_df is None and len(sheets) >= 1:
                    daily_df = pd.read_excel(xl, sheet_name=0)

                # Find monthly sheet
                monthly_df = None
                for name in _MONTHLY_SHEET_NAMES:
                    if name in sheets:
                        monthly_df = pd.read_excel(xl, sheet_name=name)
                        break

            if daily_df is None:
                errors.append("Could not find daily demand sheet.")
                return None, None, errors, warnings

            # Normalize columns
            daily_df.columns = daily_df.columns.str.strip().str.lower()

            # Validate daily data
            vr = validator.validate_demand_file(daily_df)
            if not vr:
                return None, None, vr.errors, vr.warnings
            warnings.extend(vr.warnings)

            # Monthly is optional in the file if supplied elsewhere, but if present, validate it
            if monthly_df is not None:
                monthly_df.columns = monthly_df.columns.str.strip().str.lower()
                monthly_cols = set(monthly_df.columns)
                has_period_col = any(c in monthly_cols for c in ['month', 'period', 'date'])
                required_other = {'product', 'demand'}
                if not has_period_col or not required_other.issubset(monthly_cols):
                    errors.append(
                        "Monthly sheet must include product, demand, and one of: month, period, date"
                    )
                    return None, None, errors, warnings

                if monthly_df.empty:
                    warnings.append("Monthly forecast sheet is empty.")
                else:
                    total_monthly = monthly_df['demand'].sum()
                    if total_monthly <= 0:
                        warnings.append("Monthly forecast has zero total demand.")

                monthly_demand = monthly_df
            else:
                monthly_demand = None

            daily_demand = daily_df

            return daily_demand, monthly_demand, errors, warnings

        except Exception as e:
            errors.append(f"Error loading file: {str(e)}")
            return None, None, errors, warnings


def _dataframe_is_erp_inventory_layout(df: pd.DataFrame) -> bool:
    """True if columns look like SAYIM / ERP export (product name + physical or system qty)."""
    if df is None or df.empty:
        return False
    low = df.copy()
    low.columns = low.columns.str.strip().str.lower()
    prod_col = next((c for c in low.columns if "ismi" in c or "ürün" in c), None)
    fiziki_col = next((c for c in low.columns if "fiziki" in c or "sayim" in c), None)
    sistem_col = next((c for c in low.columns if "sistem" in c or "stok" in c), None)
    return prod_col is not None and (fiziki_col is not None or sistem_col is not None)


def load_initial_state_from_file(file) -> tuple[dict | None, pd.DataFrame | None, list[str], list[str]]:
    """Load initial state (inventory, backlog, RM stock, in-transit orders).

    For **Excel**, the first sheet whose columns match **SAYIM / ERP inventory** (ÜRÜN İSMİ +
    FİZİKİ/SAYIM or SİSTEM STOK) is parsed via :func:`_parse_erp_inventory` and takes **precedence**
    over a BobaCo ``Initial`` parameter/value sheet in the same workbook.

    Otherwise expects a key-value table with columns 'parameter' (or 'key') and 'value'.
    Valid keys: p1_inv..p4_inv, p1_bl..p4_bl, base_rm, rm4, rm7, rm8.
    Unknown keys are ignored. Missing keys are acceptable (caller merges with defaults).

    For Excel files, an optional sheet (In_Transit / Pipeline / RM_In_Transit)
    can specify in-transit RM orders with columns: material, arrival_day, qty.

    Returns:
        (initial_state_dict, pipeline, errors, warnings)
        initial_state_dict: {param_name: float} or None on failure
        pipeline:           {(material, arrival_day): qty} or None
        errors:             list of error strings
        warnings:           list of warning strings
    """
    errors: list[str] = []
    warnings: list[str] = []
    filename = getattr(file, 'name', '')
    is_csv = filename.lower().endswith('.csv')
    xl = None

    try:
        if is_csv:
            df = pd.read_csv(file)
        else:
            xl = pd.ExcelFile(file)
            sheets = xl.sheet_names
            if not sheets:
                errors.append("File has no sheets.")
                return None, None, errors, warnings

            skip_erp_scan = {n.lower() for n in _PIPELINE_SHEET_NAMES}
            df = None
            for name in sheets:
                if name.lower() in skip_erp_scan:
                    continue
                df_try = pd.read_excel(xl, sheet_name=name)
                if _dataframe_is_erp_inventory_layout(df_try):
                    df = df_try
                    break

            if df is not None:
                df.columns = df.columns.str.strip().str.lower()
                erp_result = _parse_erp_inventory(df, warnings)
                pipeline = _parse_pipeline_sheet(xl, warnings)
                return erp_result, pipeline, errors, warnings

            target = None
            for name in _INITIAL_SHEET_NAMES:
                if name in sheets:
                    target = name
                    break
            if target is None:
                target = sheets[0]
            df = pd.read_excel(xl, sheet_name=target)

        df.columns = df.columns.str.strip().str.lower()

        # Find parameter and value columns
        key_col = None
        for c in ['parameter', 'key', 'param']:
            if c in df.columns:
                key_col = c
                break
                
        if key_col is None:
            # Single-sheet CSV or odd Excel fallback: ERP layout without parameter column
            prod_col = next((c for c in df.columns if 'ismi' in c or 'ürün' in c), None)
            fiziki_col = next((c for c in df.columns if 'fiziki' in c or 'sayim' in c), None)
            sistem_col = next((c for c in df.columns if 'sistem' in c or 'stok' in c), None)
            
            if prod_col and (fiziki_col or sistem_col):
                erp_result = _parse_erp_inventory(df, warnings)
                pipeline = _parse_pipeline_sheet(xl, warnings) if xl is not None else None
                return erp_result, pipeline, errors, warnings

            errors.append("Missing 'parameter' or 'key' column.")
            return None, None, errors, warnings
            
        if 'value' not in df.columns:
            errors.append("Missing 'value' column.")
            return None, None, errors, warnings

        result: dict[str, float] = {}
        for _, row in df.iterrows():
            param = str(row[key_col]).strip().lower()
            if param not in _INITIAL_STATE_KEYS:
                continue
            try:
                val = float(row['value'])
                if val < 0:
                    errors.append(f"Negative value for {param}: {val}")
                    continue
                result[param] = val
            except (ValueError, TypeError):
                errors.append(f"Invalid value for {param}: {row['value']}")
                continue

        if errors:
            return None, None, errors, warnings

        # Parse optional In_Transit sheet (Excel only)
        pipeline = _parse_pipeline_sheet(xl, warnings) if xl is not None else None

        return result, pipeline, errors, warnings

    except Exception as e:
        errors.append(f"Error loading file: {str(e)}")
        return None, None, errors, warnings


def _parse_pipeline_sheet(xl: pd.ExcelFile, warnings: list[str]) -> pd.DataFrame | None:
    """Parse an optional In_Transit / Pipeline sheet from an Excel file.

    Returns {(material_id, arrival_day): qty} or None if no sheet found.
    Invalid rows are skipped with warnings; duplicates are summed.
    """
    sheets = xl.sheet_names
    target = None
    for name in _PIPELINE_SHEET_NAMES:
        if name in sheets:
            target = name
            break
    if target is None:
        return None

    df = pd.read_excel(xl, sheet_name=target)
    df.columns = df.columns.str.strip().str.lower()

    # Detect material column
    mat_col = None
    for c in ['material', 'rm', 'rm_id', 'material_id']:
        if c in df.columns:
            mat_col = c
            break
    if mat_col is None:
        warnings.append(f"In_Transit sheet '{target}' missing 'material' column — skipping.")
        return None

    qty_col = None
    for c in ['qty', 'quantity', 'amount']:
        if c in df.columns:
            qty_col = c
            break
    if qty_col is None:
        warnings.append(f"In_Transit sheet '{target}' missing 'qty' column — skipping.")
        return None

    valid_rows = []
    has_date = 'expected_delivery_date' in df.columns
    date_col = 'expected_delivery_date' if has_date else ('arrival_date' if 'arrival_date' in df.columns else None)
    
    if 'arrival_day' not in df.columns and not date_col:
        warnings.append(f"In_Transit sheet '{target}' missing arrival time column — skipping.")
        return None

    for idx, row in df.iterrows():
        try:
            mat = int(row[mat_col])
        except (ValueError, TypeError):
            warnings.append(f"In_Transit row {idx + 2}: invalid material '{row[mat_col]}' — skipped.")
            continue
        if mat < 1 or mat > 10:
            warnings.append(f"In_Transit row {idx + 2}: material {mat} out of range 1–10 — skipped.")
            continue

        target_date = None
        if date_col and pd.notna(row.get(date_col)):
            target_date = row[date_col]
            
        leg_day = None
        if pd.isna(target_date) and 'arrival_day' in df.columns:
            try:
                leg_day = int(row['arrival_day'])
                if leg_day < 1:
                    warnings.append(f"In_Transit row {idx + 2}: arrival_day {leg_day} < 1 — skipped.")
                    continue
            except (ValueError, TypeError):
                warnings.append(f"In_Transit row {idx + 2}: invalid arrival_day '{row['arrival_day']}' — skipped.")
                continue

        try:
            qty = float(row[qty_col])
        except (ValueError, TypeError):
            warnings.append(f"In_Transit row {idx + 2}: invalid qty '{row[qty_col]}' — skipped.")
            continue
        if qty <= 0:
            warnings.append(f"In_Transit row {idx + 2}: qty {qty} <= 0 — skipped.")
            continue

        r_out = {'material': mat, 'qty': qty}
        if target_date is not None:
            r_out['expected_delivery_date'] = target_date
        if leg_day is not None:
            r_out['arrival_day'] = leg_day
        valid_rows.append(r_out)

    if not valid_rows:
        warnings.append(f"In_Transit sheet '{target}' has no valid rows.")
        return None

    return pd.DataFrame(valid_rows)


def merge_initial_state(defaults: dict[str, Any], file_dict: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Merge default initial-state values with file-loaded values.

    File values override defaults. Use for sidebar initial-state inputs.
    Both dicts use keys like p1_inv, p2_inv, base_rm, rm4, rm7, rm8.

    Args:
        defaults: Default values from config/defaults.yaml or hardcoded
        file_dict: Values loaded from initial-state file (None or empty ok)

    Returns:
        Merged dict; file_dict values take precedence.
    """
    result = dict(defaults)
    if file_dict:
        for k in _INITIAL_STATE_KEYS:
            if k in file_dict:
                result[k] = file_dict[k]
    return result


def load_config(config_path: Path) -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict, config_path: Path) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def _parse_erp_inventory(df: pd.DataFrame, warnings: list[str]) -> dict[str, float]:
    """Parse ERP inventory format (SAYIM CIKTI SISTEM) returning tracked inventory keys.

    Only emits keys that are actually derived to avoid accidental zero-resets of other
    initial-state values.
    """
    prod_col = next((c for c in df.columns if 'ismi' in c or 'ürün' in c), None)
    fiziki_col = next((c for c in df.columns if 'fiziki' in c or 'sayim' in c), None)
    sistem_col = next((c for c in df.columns if 'sistem' in c or 'stok' in c), None)
    if prod_col is None:
        warnings.append("ERP parse skipped: missing product-name column.")
        return {}
    if fiziki_col is None and sistem_col is None:
        warnings.append("ERP parse skipped: missing quantity columns (fiziki/sayim or sistem/stok).")
        return {}
    
    p1_sum = 0.0
    p3_sum = 0.0
    base_rm_sum = 0.0
    rm4_sum = 0.0
    rm7_sum = 0.0
    rm8_sum = 0.0
    aciklama_col = next((c for c in df.columns if "klama" in str(c).lower()), None)

    def _to_float(v) -> float | None:
        if v is None or pd.isna(v):
            return None
        try:
            out = float(v)
        except (ValueError, TypeError):
            return None
        if pd.isna(out):
            return None
        return out

    for _, row in df.iterrows():
        name = str(row[prod_col]).upper().strip()
        qty = _to_float(row.get(fiziki_col)) if fiziki_col is not None else None
        if qty is None and sistem_col is not None:
            qty = _to_float(row.get(sistem_col))
        if qty is None:
            qty = 0.0
            
        is_p1 = (("3.4" in name or "3,4" in name) and ("KOVA" in name or "BUCKET" in name))
        if is_p1 and "ETIKET" not in name and "ETİKET" not in name:
            p1_sum += qty
            
        if "POPPING BUBBLE CUP" in name:
            p3_sum += qty

        urun_raw = None if pd.isna(row.get(prod_col)) else str(row[prod_col]).strip()
        ac_val = row.get(aciklama_col) if aciklama_col else None
        bkt = sayim_row_rm_bucket(urun_raw, ac_val)
        if bkt == "base_rm":
            base_rm_sum += qty
        elif bkt == "rm4":
            rm4_sum += qty
        elif bkt == "rm7":
            rm7_sum += qty
        elif bkt == "rm8":
            rm8_sum += qty

    result: dict[str, float] = {}
    if p1_sum > 0:
        result['p1_inv'] = p1_sum
    if p3_sum > 0:
        result['p3_inv'] = p3_sum
    if base_rm_sum > 0:
        result['base_rm'] = base_rm_sum
    if rm4_sum > 0:
        result['rm4'] = rm4_sum
    if rm7_sum > 0:
        result['rm7'] = rm7_sum
    if rm8_sum > 0:
        result['rm8'] = rm8_sum
    return result


def load_custom_forecast(file, planning_start_date: Optional[datetime.date] = None) -> pd.DataFrame | None:
    """Parse month-column forecast CSV and return normalized monthly demand rows.

    Output columns: product, period (YYYY-MM), demand.
    """
    try:
        df = pd.read_csv(file)
        cols = [str(c).upper().strip() for c in df.columns]
        months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
        
        if not any(m in cols for m in months):
            return None
            
        if planning_start_date is None:
            planning_start_date = datetime.date.today().replace(day=1)
        if isinstance(planning_start_date, datetime.datetime):
            planning_start_date = planning_start_date.date()

        month_columns = [
            c for c in df.columns
            if any(month_name in str(c).upper() for month_name in months)
        ]
        if not month_columns:
            return None

        monthly_demand = {}
        for period_idx, matched_col in enumerate(month_columns[:12]):
            if matched_col:
                numeric_series = pd.to_numeric(df[matched_col], errors='coerce').dropna()
                if not numeric_series.empty:
                    total_sum = numeric_series.sum()
                    last_val = numeric_series.iloc[-1]
                    # If last value is exactly half of total sum, it's a TOTAL row
                    if last_val * 2 == total_sum or abs(last_val * 2 - total_sum) < 1:
                        actual_sum = last_val
                    else:
                        actual_sum = total_sum

                    month_date = planning_start_date + relativedelta(months=period_idx)
                    period_key = month_date.strftime("%Y-%m")
                    monthly_demand[(3, period_key)] = float(actual_sum)
                else:
                    month_date = planning_start_date + relativedelta(months=period_idx)
                    period_key = month_date.strftime("%Y-%m")
                    monthly_demand[(3, period_key)] = 0.0
                
        rows = []
        for (prod, period_key), dem in monthly_demand.items():
            rows.append({'product': prod, 'period': period_key, 'demand': dem})
        return pd.DataFrame(rows)
    except Exception:
        return None


def load_in_transit_config(config_path: Path) -> list[dict]:
    """Load manual in-transit orders from JSON."""
    if not config_path.exists():
        return []
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_in_transit_config(orders: list[dict], config_path: Path) -> None:
    """Save manual in-transit orders to JSON."""
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2)
