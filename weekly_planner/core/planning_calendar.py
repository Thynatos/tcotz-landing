import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from dateutil.relativedelta import relativedelta
import pandas as pd

def coerce_date(value: Any) -> Optional[datetime.date]:
    if pd.isnull(value):
        return None
    if isinstance(value, datetime.date):
        if isinstance(value, datetime.datetime):
            return value.date()
        return value
    if isinstance(value, str):
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None
    try:
        if isinstance(value, pd.Timestamp):
            return value.date()
    except Exception:
        pass
    return None

def coerce_month_period(value: Any, planning_start_date: Optional[datetime.date] = None) -> Optional[str]:
    if pd.isnull(value):
        return None
    
    if isinstance(value, str) and len(value) == 7 and '-' in value:
        parts = value.split('-')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return value

    dt = coerce_date(value)
    if dt:
        return dt.strftime('%Y-%m')

    try:
        val_int = int(value)
        if planning_start_date:
            offset = val_int - 1
            target_date = planning_start_date + relativedelta(months=offset)
            return target_date.strftime('%Y-%m')
    except Exception as e:
        pass

    return None

def ensure_monday(value: datetime.date) -> datetime.date:
    if value.weekday() != 0:
        raise ValueError(f"Date {value} is not a Monday.")
    return value

def next_monday(reference: Optional[datetime.date] = None) -> datetime.date:
    if reference is None:
        reference = datetime.date.today()
    days_ahead = 0 - reference.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return reference + datetime.timedelta(days=days_ahead)

def normalize_closed_dates(closed_dates: List[Any], calendar_dates: List[datetime.date]) -> Set[datetime.date]:
    closed_set = set()
    for d in closed_dates:
        cd = coerce_date(d)
        if cd and cd in calendar_dates:
            closed_set.add(cd)
    return closed_set

def build_legacy_working_day_mapping(
    planning_start_date: datetime.date,
    planning_weeks: int,
    sundays_working: bool = False,
) -> Tuple[Dict[int, datetime.date], Dict[datetime.date, int]]:
    date_to_legacy = {}
    legacy_to_date = {}
    current_date = planning_start_date
    legacy_day = 1

    working_days_per_week = 7 if sundays_working else 6
    target_legacy_days = planning_weeks * working_days_per_week

    for _ in range(planning_weeks * 7 * 2):  # safe upper bound
        if sundays_working or current_date.weekday() != 6:
            date_to_legacy[current_date] = legacy_day
            legacy_to_date[legacy_day] = current_date
            legacy_day += 1
            if legacy_day > target_legacy_days:
                break
        current_date += datetime.timedelta(days=1)

    return legacy_to_date, date_to_legacy

def map_legacy_day_to_date(legacy_day: int, legacy_working_day_to_date: Dict[int, datetime.date]) -> Optional[datetime.date]:
    return legacy_working_day_to_date.get(legacy_day)

def build_planning_calendar(
    planning_start_date: datetime.date,
    planning_weeks: int,
    closed_dates: List[Any] = None,
    sundays_working: bool = False,
) -> Dict[str, Any]:
    ensure_monday(planning_start_date)
    
    total_days = planning_weeks * 7
    horizon_end_date = planning_start_date + datetime.timedelta(days=total_days - 1)
    
    calendar_dates = [planning_start_date + datetime.timedelta(days=i) for i in range(total_days)]
    
    normalized_closed = normalize_closed_dates(closed_dates or [], calendar_dates)
    
    day_to_date = {}
    date_to_day = {}
    weekday_by_day = {}
    production_allowed_by_day = {}
    production_allowed_day_indices = []
    closed_day_indices = []
    
    for i, d in enumerate(calendar_dates):
        day_idx = i + 1
        day_to_date[day_idx] = d
        date_to_day[d] = day_idx
        weekday_by_day[day_idx] = d.weekday()
        
        is_sunday = d.weekday() == 6 and not sundays_working
        is_closed = d in normalized_closed
        
        allowed = not is_sunday and not is_closed
        production_allowed_by_day[day_idx] = allowed
        
        if allowed:
            production_allowed_day_indices.append(day_idx)
        if is_closed:
            closed_day_indices.append(day_idx)
            
    leg_to_date, date_to_leg = build_legacy_working_day_mapping(
        planning_start_date, planning_weeks, sundays_working=sundays_working
    )
    
    week_definitions = []
    for w in range(planning_weeks):
        w_start = planning_start_date + datetime.timedelta(days=w*7)
        w_end = w_start + datetime.timedelta(days=6)
        day_indices = [date_to_day[w_start + datetime.timedelta(days=i)] for i in range(7)]
        prod_indices = [idx for idx in day_indices if production_allowed_by_day[idx]]
        has_closed = any(day_to_date[idx] in normalized_closed for idx in day_indices)
        
        week_definitions.append({
            'week_index': w + 1,
            'start_date': w_start,
            'end_date': w_end,
            'day_indices': day_indices,
            'production_day_indices': prod_indices,
            'contains_closed_dates': has_closed
        })

    return {
        'planning_start_date': planning_start_date,
        'planning_weeks': planning_weeks,
        'horizon_end_date': horizon_end_date,
        'calendar_dates': calendar_dates,
        'day_to_date': day_to_date,
        'date_to_day': date_to_day,
        'weekday_by_day': weekday_by_day,
        'production_allowed_by_day': production_allowed_by_day,
        'production_allowed_day_indices': production_allowed_day_indices,
        'closed_day_indices': closed_day_indices,
        'closed_dates_in_horizon': list(normalized_closed),
        'week_definitions': week_definitions,
        'legacy_working_day_to_date': leg_to_date,
        'date_to_legacy_working_day': date_to_leg,
        'sundays_working': sundays_working,
    }

def build_lt_blocks(planning_calendar: Dict[str, Any], total_blocks: int = 12) -> List[Dict[str, Any]]:
    blocks = []
    start_date = planning_calendar['planning_start_date']
    date_to_day = planning_calendar.get('date_to_day', {})
    prod_allowed = planning_calendar.get('production_allowed_by_day', {})
    sundays_working = bool(planning_calendar.get('sundays_working', False))

    current_block_start = start_date
    
    for b in range(1, total_blocks + 1):
        if current_block_start.month == 12:
            next_month = current_block_start.replace(year=current_block_start.year + 1, month=1, day=1)
        else:
            next_month = current_block_start.replace(month=current_block_start.month + 1, day=1)
        block_end = next_month - datetime.timedelta(days=1)
        
        period_key = current_block_start.strftime('%Y-%m')
        demand_source = "daily" if b in (1, 2) else "monthly"
        
        cal_indices = []
        prod_indices = []
        
        d = current_block_start
        prod_days = 0
        cal_days = 0
        
        while d <= block_end:
            cal_days += 1
            idx = date_to_day.get(d)
            if idx is not None:
                cal_indices.append(idx)
                if prod_allowed.get(idx, False):
                    prod_indices.append(idx)
                    prod_days += 1
            else:
                if sundays_working or d.weekday() != 6:
                    prod_days += 1
            d += datetime.timedelta(days=1)
            
        blocks.append({
            'block_index': b,
            'start_date': current_block_start,
            'end_date': block_end,
            'period_key': period_key,
            'demand_source': demand_source,
            'calendar_day_indices': cal_indices,
            'production_day_indices': prod_indices,
            'production_days_available': prod_days,
            'calendar_days_in_block': cal_days
        })
        
        current_block_start = next_month
        
    return blocks

def normalize_daily_demand_records(demand_df: pd.DataFrame, planning_calendar: Dict[str, Any]) -> Tuple[Dict[Tuple[int, datetime.date], float], Dict[Tuple[int, int], float]]:
    by_date = {}
    by_day = {}
    
    date_to_day = planning_calendar['date_to_day']
    legacy_map = planning_calendar['legacy_working_day_to_date']
    
    for _, row in demand_df.iterrows():
        product = int(row['product'])
        demand_val = float(row['demand'])
        
        target_date = None
        if 'date' in row and not pd.isnull(row['date']):
            target_date = coerce_date(row['date'])
        
        if not target_date and 'day' in row and not pd.isnull(row['day']):
            leg_day = int(row['day'])
            target_date = legacy_map.get(leg_day)
            
        if target_date:
            key_date = (product, target_date)
            by_date[key_date] = by_date.get(key_date, 0.0) + demand_val
            
            day_idx = date_to_day.get(target_date)
            if day_idx is not None:
                key_day = (product, day_idx)
                by_day[key_day] = by_day.get(key_day, 0.0) + demand_val
                
    return by_date, by_day


def check_demand_date_coverage(demand_df: pd.DataFrame, planning_calendar: Dict[str, Any]) -> List[str]:
    """Check if any demand records fall outside the planning horizon.

    Returns a list of warning strings (empty if all demands are within range).
    Only applies when the demand DataFrame has a 'date' column.
    """
    warnings: List[str] = []
    if demand_df is None or demand_df.empty:
        return warnings

    cols = set(demand_df.columns.str.lower())
    if 'date' not in cols:
        return warnings

    planning_start = planning_calendar['planning_start_date']
    horizon_end = planning_calendar['horizon_end_date']

    before_start = []
    after_end = []

    for _, row in demand_df.iterrows():
        raw = row.get('date')
        if raw is None or pd.isnull(raw):
            continue
        d = coerce_date(raw)
        if d is None:
            continue
        if d < planning_start:
            before_start.append(d)
        elif d > horizon_end:
            after_end.append(d)

    if before_start:
        n = len(before_start)
        earliest = min(before_start)
        warnings.append(
            f"⚠️ {n} demand record(s) have dates before the planning start "
            f"({planning_start}). Earliest: {earliest}. "
            f"These demands are ignored by the optimizer. "
            f"If they represent unmet orders, add them to Initial Backlog instead."
        )

    if after_end:
        n = len(after_end)
        latest = max(after_end)
        warnings.append(
            f"⚠️ {n} demand record(s) have dates after the planning horizon end "
            f"({horizon_end}). Latest: {latest}. "
            f"These demands are ignored. Consider extending the planning horizon."
        )

    return warnings

def zero_fill_daily_demand(daily_demand_by_day: Dict[Tuple[int, int], float], planning_calendar: Dict[str, Any], products: List[int] = None) -> Dict[Tuple[int, int], float]:
    if products is None:
        products = [1, 2, 3, 4]
        
    filled = {}
    total_days = len(planning_calendar['calendar_dates'])
    
    for p in products:
        for t in range(1, total_days + 1):
            filled[(p, t)] = daily_demand_by_day.get((p, t), 0.0)
            
    return filled

def normalize_monthly_forecast_records(forecast_df: pd.DataFrame, planning_calendar: Dict[str, Any]) -> Dict[Tuple[int, str], float]:
    by_period = {}
    planning_start = planning_calendar['planning_start_date']
    
    for _, row in forecast_df.iterrows():
        product = int(row['product'])
        demand_val = float(row.get('demand', 0.0))

        
        period_key = None
        if 'period' in row and not pd.isnull(row['period']):
            period_key = coerce_month_period(row['period'], planning_start)
        elif 'month' in row and not pd.isnull(row['month']):
            period_key = coerce_month_period(row['month'], planning_start)
            
        if period_key:
            key = (product, period_key)
            by_period[key] = by_period.get(key, 0.0) + demand_val
            
    return by_period

def normalize_pipeline_records(pipeline_df: pd.DataFrame, planning_calendar: Dict[str, Any]) -> Tuple[Dict[Tuple[int, datetime.date], float], Dict[Tuple[int, int], float]]:
    by_date = {}
    by_day = {}
    
    date_to_day = planning_calendar['date_to_day']
    legacy_map = planning_calendar['legacy_working_day_to_date']
    
    for _, row in pipeline_df.iterrows():
        material = int(row['material'])
        qty = float(row['qty'])
        
        target_date = None
        if 'expected_delivery_date' in row and not pd.isnull(row['expected_delivery_date']):
            target_date = coerce_date(row['expected_delivery_date'])
        elif 'arrival_date' in row and not pd.isnull(row['arrival_date']):
            target_date = coerce_date(row['arrival_date'])
            
        if not target_date and 'arrival_day' in row and not pd.isnull(row['arrival_day']):
            leg_day = int(row['arrival_day'])
            target_date = legacy_map.get(leg_day)
            
        if target_date:
            key_date = (material, target_date)
            by_date[key_date] = by_date.get(key_date, 0.0) + qty
            
            day_idx = date_to_day.get(target_date)
            if day_idx is not None:
                key_day = (material, day_idx)
                by_day[key_day] = by_day.get(key_day, 0.0) + qty
                
    return by_date, by_day

def build_lt_block_demand(by_date: Dict[Tuple[int, datetime.date], float], by_period: Dict[Tuple[int, str], float], lt_blocks: List[Dict[str, Any]], products: List[int] = None) -> Dict[Tuple[int, int], float]:
    if products is None:
        products = [1, 2, 3, 4]
        
    block_demand = {}
    
    for b_info in lt_blocks:
        b_idx = b_info['block_index']
        d_source = b_info['demand_source']
        
        for p in products:
            if d_source == "daily":
                b_start = b_info['start_date']
                b_end = b_info['end_date']
                
                total = 0.0
                curr = b_start
                while curr <= b_end:
                    total += by_date.get((p, curr), 0.0)
                    curr += datetime.timedelta(days=1)
                block_demand[(p, b_idx)] = total
            else:
                p_key = b_info['period_key']
                block_demand[(p, b_idx)] = by_period.get((p, p_key), 0.0)
                
    return block_demand
