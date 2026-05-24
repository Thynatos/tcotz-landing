"""
Shared helper functions for the production optimizer.
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd


def complete_rm_usage_matrix(
    rm_usage: dict[Any, Any],
    i_prod: list[int],
    s_rm: list[int],
) -> dict[tuple[int, int], float]:
    """Build full nis from sparse user input; unknown keys raise ValueError.

    Accepts keys as (i, s) tuples or "i_s" strings (e.g. "3_7" for product 3, material 7).
    Missing (i, s) pairs are 0.0. Values must be finite and >= 0.
    """
    out: dict[tuple[int, int], float] = {(i, s): 0.0 for i in i_prod for s in s_rm}
    valid_i = set(i_prod)
    valid_s = set(s_rm)
    for k, raw in rm_usage.items():
        if isinstance(k, tuple) and len(k) == 2:
            i, s = int(k[0]), int(k[1])
        elif isinstance(k, str):
            parts = k.strip().split("_", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid rm_usage key (expected 'i_s'): {k!r}")
            i, s = int(parts[0]), int(parts[1])
        else:
            raise ValueError(f"Invalid rm_usage key type: {type(k).__name__}")
        if i not in valid_i or s not in valid_s:
            raise ValueError(f"rm_usage key out of range: product={i}, material={s}")
        try:
            v = float(raw)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid rm_usage value for ({i},{s}): {raw!r}") from e
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"rm_usage value must be finite for ({i},{s}): {v}")
        if v < 0:
            raise ValueError(f"rm_usage value must be non-negative for ({i},{s}): {v}")
        out[(i, s)] = v
    return out


def usage_matrix_to_dataframe(
    nis: dict[tuple[int, int], float],
    i_prod: list[int],
    s_rm: list[int],
) -> pd.DataFrame:
    """4×10-style grid for BOM editor (rows P1..P4, columns RM1..RM10)."""
    rows = []
    for i in i_prod:
        rows.append([float(nis.get((i, s), 0.0)) for s in s_rm])
    return pd.DataFrame(
        rows,
        index=[f"P{p}" for p in i_prod],
        columns=[f"RM{s}" for s in s_rm],
    )


def dataframe_to_rm_usage_dict(df: pd.DataFrame, i_prod: list[int], s_rm: list[int]) -> dict[tuple[int, int], float]:
    """Read editor DataFrame into sparse dict (includes zeros for completeness)."""
    out: dict[tuple[int, int], float] = {}
    for i in i_prod:
        idx = f"P{i}"
        for s in s_rm:
            col = f"RM{s}"
            val = df.loc[idx, col]
            if pd.isna(val):
                q = 0.0
            else:
                q = float(val)
            out[(i, s)] = q
    return out


def build_usage_matrix(i_prod: list[int], s_rm: list[int]) -> dict[tuple[int, int], float]:
    """Build raw material usage matrix nis[(product, material)]."""
    nis = {(i, s): 0 for i in i_prod for s in s_rm}

    for s in [1, 2, 3]:
        for i in i_prod:
            nis[(i, s)] = 1

    nis[(3, 7)] = 1
    nis[(4, 7)] = 1
    nis[(3, 8)] = 1
    nis[(4, 8)] = 1

    nis[(1, 4)] = 2
    nis[(3, 4)] = 2

    nis[(2, 5)] = 2
    nis[(4, 5)] = 2

    nis[(1, 6)] = 2
    nis[(4, 6)] = 2

    nis[(1, 9)] = 1
    nis[(2, 9)] = 1

    nis[(4, 10)] = 2
    return nis


def compute_w_global(demand: dict, i_prod: list[int], total_days: int) -> dict:
    """Compute rolling 12-day demand sum for B12 constraint."""
    w_global = {}
    for i in i_prod:
        for t in range(1, total_days + 1):
            start = max(1, t - 11)
            w_global[(i, t)] = sum(demand.get((i, k), 0) for k in range(start, t + 1))
    return w_global





def round_inventory_target(product: int, value: float) -> float:
    """Round inventory target to product-specific capacity multiple."""
    if value is None or value <= 0:
        return 0.0
    if product in [1, 2]:
        cap = 500
    elif product == 3:
        cap = 10000
    else:
        cap = 80000
    return cap * math.ceil(value / cap)


def week_first_day_local(w: int, step: int = 7) -> int:
    """Return first local day of week w."""
    return 1 + (w - 1) * step


def shift_arrival_to_monday(cur_day: int, arrival_day: int, step: int = 7) -> int | None:
    """Map an arrival day to its calendar-week bucket index."""
    offset = arrival_day - cur_day
    if offset < 0:
        return None
    w = offset // step + 1
    return w


def weekly_need_max_for_material(
    s: int,
    nis: dict[tuple[int, int], float],
    line1_m: list[int],
    cap_l1: dict[int, float],
    cap_p3: dict[int, float],
    cap_p4: float,
    short_term_step: int,
) -> float:
    """Estimate maximum weekly consumption for a raw material."""
    l1_daily = 0.0
    for m in line1_m:
        per_unit = max(nis[(1, s)], nis[(2, s)])
        l1_daily += per_unit * cap_l1[m]

    p3_daily = nis[(3, s)] * (cap_p3[1] + cap_p3[2])
    p4_daily = nis[(4, s)] * cap_p4
    l2_daily = max(p3_daily, p4_daily)

    return (l1_daily + l2_daily) * short_term_step


def ceil_to_moq_multiple(q: float, moq: float) -> float:
    """Round up to nearest MOQ multiple."""
    if q <= 0:
        return 0.0
    if q < moq:
        return float(moq)
    return float(moq * math.ceil(q / moq))


def policy_order_qty(
    s: int,
    current_day: int,
    rm_onhand: float,
    pipeline: dict,
    config: Any,
    lt_rm: dict[int, int],
    moq_rm: dict[int, float],
    nis: dict[tuple[int, int], float],
    line1_m: list[int],
    cap_l1: dict[int, float],
    cap_p3: dict[int, float],
    cap_p4: float,
) -> float:
    """Calculate reorder quantity for policy-managed materials."""
    lt_weeks = lt_rm[s] // config.short_term_step
    weekly_need = weekly_need_max_for_material(
        s=s,
        nis=nis,
        line1_m=line1_m,
        cap_l1=cap_l1,
        cap_p3=cap_p3,
        cap_p4=cap_p4,
        short_term_step=config.short_term_step,
    )
    target = (lt_weeks + 1) * weekly_need

    window_end = current_day + (lt_weeks + 1) * config.short_term_step - 1
    pipe_in_window = sum(
        qty
        for (ss, arr_day), qty in pipeline.items()
        if ss == s and current_day <= arr_day <= window_end
    )

    position = rm_onhand + pipe_in_window
    deficit = target - position
    if deficit <= 0:
        return 0.0
    return ceil_to_moq_multiple(deficit, moq_rm[s])


def build_result_row(
    gday: int,
    t_local: int,
    result: dict,
    s_rm: list[int],
    policy_mats: set[int],
    policy_orders: dict[int, float] | None = None,
) -> dict[str, float]:
    """Build a single result row including machine binaries."""
    row = {
        "day": gday,
        "y1": result["Y"][(1, t_local)],
        "y2": result["Y"][(2, t_local)],
        "y3": result["Y"][(3, t_local)],
        "y4": result["Y"][(4, t_local)],
        "p1": result["P"][(1, t_local)],
        "p2": result["P"][(2, t_local)],
        "p3": result["P"][(3, t_local)],
        "p4": result["P"][(4, t_local)],
        "i1": result["Inv"][(1, t_local)],
        "i2": result["Inv"][(2, t_local)],
        "i3": result["Inv"][(3, t_local)],
        "i4": result["Inv"][(4, t_local)],
        "b1": result["B"][(1, t_local)],
        "b2": result["B"][(2, t_local)],
        "b3": result["B"][(3, t_local)],
        "b4": result["B"][(4, t_local)],
        "b12_1": result["B12"][(1, t_local)],
        "b12_2": result["B12"][(2, t_local)],
        "b12_3": result["B12"][(3, t_local)],
        "b12_4": result["B12"][(4, t_local)],
        "x1_1_1": result["X12"][(1, 1, t_local)],
        "x1_1_2": result["X12"][(2, 1, t_local)],
        "x1_1_3": result["X12"][(3, 1, t_local)],
        "x1_2_1": result["X12"][(1, 2, t_local)],
        "x1_2_2": result["X12"][(2, 2, t_local)],
        "x1_2_3": result["X12"][(3, 2, t_local)],
        "x2_3_1": result["X3"][(1, t_local)],
        "x2_3_2": result["X3"][(2, t_local)],
        "x2_4_1": result["X4"][t_local],
    }

    for s in s_rm:
        r_val = result["RMorder"][(s, t_local)]
        if policy_orders and s in policy_mats:
            r_val = policy_orders[s] if t_local == 1 else 0.0
        row[f"r{s}"] = r_val
        row[f"ir{s}"] = result["RMInv"][(s, t_local)]

    return row


def apply_block_control(
    rows: list[dict[str, float]],
    last_day: int,
    i_state: dict[int, float],
    b_state: dict[int, float],
    i_prod: list[int],
) -> tuple[list[dict[str, float]], dict[int, float], dict[int, float]]:
    """Apply inventory-backlog netting at block boundaries."""
    new_i = {}
    new_b = {}

    for i in i_prod:
        net = i_state[i] - b_state[i]
        if net >= 0:
            new_i[i] = net
            new_b[i] = 0.0
        else:
            new_i[i] = 0.0
            new_b[i] = -net

    for idx in range(len(rows) - 1, -1, -1):
        if rows[idx]["day"] == last_day:
            rows[idx]["i1"] = new_i[1]
            rows[idx]["i2"] = new_i[2]
            rows[idx]["i3"] = new_i[3]
            rows[idx]["i4"] = new_i[4]
            rows[idx]["b1"] = new_b[1]
            rows[idx]["b2"] = new_b[2]
            rows[idx]["b3"] = new_b[3]
            rows[idx]["b4"] = new_b[4]
            break

    return rows, new_i, new_b


def compute_costs(df: pd.DataFrame, config: Any) -> dict[str, float]:
    """Compute cost breakdown from result rows."""
    holding = (df["i1"] + df["i2"] + df["i3"] + df["i4"]).sum() * config.holding_cost
    backlog = (df["b1"] + df["b2"] + df["b3"] + df["b4"]).sum() * config.backlog_cost
    b12 = (df["b12_1"] + df["b12_2"] + df["b12_3"] + df["b12_4"]).sum() * config.b12_penalty
    return {
        "holding": holding,
        "backlog": backlog,
        "b12_penalty": b12,
        "total": holding + backlog + b12,
    }
