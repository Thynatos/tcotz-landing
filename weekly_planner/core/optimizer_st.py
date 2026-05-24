"""
Short-term optimization model helpers.
"""
from __future__ import annotations

import time
from typing import Any, Callable

from pulp import LpBinary, LpMinimize, LpProblem, LpStatus, LpVariable, getSolver, lpSum


def solve_short_term(
    demand: dict,
    w_global: dict,
    cur_day: int,
    i_init: dict[int, float],
    b_init: dict[int, float],
    rm_init: dict[int, float],
    pipeline: dict,
    i_target_map: dict,
    config: Any,
    i_prod: list[int],
    s_rm: list[int],
    nis: dict,
    policy_mats: set[int],
    line1_m: list[int],
    cap_l1: dict[int, float],
    line2_m3: list[int],
    cap_p3: dict[int, float],
    cap_p4: float,
    lt_rm: dict[int, int],
    moq_rm: dict[int, float],
    ui: dict[int, float],
    rui: dict[int, float],
    u23: float,
    u24: float,
    week_first_day_local_fn: Callable[[int, int], int],
    shift_arrival_to_monday_fn: Callable[[int, int, int], int | None],
) -> dict:
    """Solve the ST daily scheduling model with machine-level binaries."""
    time_days = range(1, config.short_term_horizon + 1)
    num_weeks = len(getattr(config, "week_definitions", []) or [])
    if num_weeks <= 0:
        num_weeks = config.short_term_horizon // config.short_term_step
    weeks = range(1, num_weeks + 1)

    d_st = {(i, t): 0.0 for i in i_prod for t in time_days}
    for t in time_days:
        gday = cur_day + t - 1
        if 1 <= gday <= config.total_days:
            for i in [1, 3, 4]:
                d_st[(i, t)] = float(demand.get((i, gday), 0.0))

    arr_fixed_week = {(s, w): 0.0 for s in s_rm for w in weeks}
    for (s, arrival_day), qty in pipeline.items():
        w = shift_arrival_to_monday_fn(cur_day, arrival_day, step=config.short_term_step)
        if w is not None and 1 <= w <= num_weeks:
            arr_fixed_week[(s, w)] += float(qty)

    arrival_week_from_order = {(s, k): None for s in s_rm for k in weeks}
    for s in s_rm:
        for k in weeks:
            order_day_global = cur_day + (k - 1) * config.short_term_step
            arrival_day_global = order_day_global + lt_rm[s]
            w_arr = shift_arrival_to_monday_fn(cur_day, arrival_day_global, step=config.short_term_step)
            if w_arr is not None and 1 <= w_arr <= num_weeks:
                arrival_week_from_order[(s, k)] = w_arr

    prob = LpProblem(f"ST_{cur_day}", LpMinimize)

    x12 = {(m, i, t): LpVariable(f"X12_{m}_{i}_{t}", 0, 1, cat=LpBinary) for m in line1_m for i in [1, 2] for t in time_days}
    x3 = {(k, t): LpVariable(f"X3_{k}_{t}", 0, 1, cat=LpBinary) for k in line2_m3 for t in time_days}
    x4 = {t: LpVariable(f"X4_{t}", 0, 1, cat=LpBinary) for t in time_days}
    production = {(i, t): LpVariable(f"P_{i}_{t}", lowBound=0) for i in i_prod for t in time_days}

    for t in time_days:
        gday = cur_day + t - 1
        allowed = config.production_allowed_by_day.get(gday, True)
        
        for m in line1_m:
            prob += x12[(m, 1, t)] + x12[(m, 2, t)] <= (1 if allowed else 0)
            
        if allowed:
            prob += x3[(1, t)] + x3[(2, t)] <= 2 * (1 - x4[t])
        else:
            prob += x3[(1, t)] + x3[(2, t)] <= 0
            prob += x4[t] <= 0
            
        prob += production[(1, t)] == lpSum(cap_l1[m] * x12[(m, 1, t)] for m in line1_m)
        prob += production[(2, t)] == lpSum(cap_l1[m] * x12[(m, 2, t)] for m in line1_m)
        prob += production[(3, t)] == cap_p3[1] * x3[(1, t)] + cap_p3[2] * x3[(2, t)]
        prob += production[(4, t)] == cap_p4 * x4[t]

    inventory = {(i, t): LpVariable(f"Inv_{i}_{t}", lowBound=0) for i in i_prod for t in time_days}
    backlog = {(i, t): LpVariable(f"B_{i}_{t}", lowBound=0) for i in i_prod for t in time_days}
    b12 = {(i, t): LpVariable(f"B12_{i}_{t}", lowBound=0) for i in i_prod for t in time_days}

    rm_inv_week = {(s, w): LpVariable(f"RMInvW_{s}_{w}", lowBound=0) for s in s_rm for w in weeks}
    rm_order_week = {(s, w): LpVariable(f"RMorderW_{s}_{w}", lowBound=0) for s in s_rm for w in weeks}
    order_on = {(s, w): LpVariable(f"OrderOn_{s}_{w}", 0, 1, cat=LpBinary) for s in s_rm for w in weeks}
    big_q = 10_000_000

    for s in policy_mats:
        for w in weeks:
            prob += rm_order_week[(s, w)] == 0
            prob += order_on[(s, w)] == 0

    due_slack = {(i, t): LpVariable(f"DueSlack_{i}_{t}", lowBound=0) for i in i_prod for t in time_days}
    big_m = 10000.0

    prob += (
        lpSum(
            config.backlog_cost * backlog[(i, t)]
            + config.holding_cost * inventory[(i, t)]
            + config.b12_penalty * b12[(i, t)]
            for i in i_prod for t in time_days
        )
        + lpSum(config.rm_holding_cost * rm_inv_week[(s, w)] for s in s_rm for w in weeks)
        + big_m * lpSum(due_slack[(i, t)] for i in i_prod for t in time_days)
    )

    for t in time_days:
        cons2 = u23 * production[(3, t)] + u24 * production[(4, t)]
        if t == 1:
            prob += inventory[(2, 1)] == i_init[2] + production[(2, 1)] - cons2
        else:
            prob += inventory[(2, t)] == inventory[(2, t - 1)] + production[(2, t)] - cons2

    for i in [1, 3, 4]:
        for t in time_days:
            if t == 1:
                prob += inventory[(i, 1)] == i_init[i] + production[(i, 1)] - (d_st[(i, 1)] + b_init[i]) + backlog[(i, 1)]
            else:
                prob += inventory[(i, t)] == inventory[(i, t - 1)] + production[(i, t)] - (d_st[(i, t)] + backlog[(i, t - 1)]) + backlog[(i, t)]

    for t in time_days:
        prob += backlog[(2, t)] == 0
        prob += b12[(2, t)] == 0

    for i in [1, 3, 4]:
        for t in time_days:
            gday = cur_day + t - 1
            w_val = w_global.get((i, gday), 0.0) if (1 <= gday <= config.total_days) else 0.0
            prob += b12[(i, t)] >= backlog[(i, t)] - w_val
            prob += b12[(i, t)] <= backlog[(i, t)]

    for s in s_rm:
        for w in weeks:
            prob += rm_order_week[(s, w)] >= moq_rm[s] * order_on[(s, w)]
            prob += rm_order_week[(s, w)] <= big_q * order_on[(s, w)]

    for s in s_rm:
        for w in weeks:
            t_start = week_first_day_local_fn(w, step=config.short_term_step)
            t_end = min(t_start + config.short_term_step - 1, config.short_term_horizon)

            cons_week = lpSum(
                lpSum(nis[(i, s)] * production[(i, t)] for i in i_prod)
                for t in range(t_start, t_end + 1)
            )

            arr_from_orders = lpSum(
                rm_order_week[(s, k)]
                for k in weeks
                if arrival_week_from_order[(s, k)] == w
            )

            if w == 1:
                prob += rm_inv_week[(s, 1)] == rm_init[s] + arr_fixed_week[(s, 1)] + arr_from_orders - cons_week
            else:
                prob += rm_inv_week[(s, w)] == rm_inv_week[(s, w - 1)] + arr_fixed_week[(s, w)] + arr_from_orders - cons_week

    for w in weeks:
        prob += lpSum(rui[s] * rm_inv_week[(s, w)] for s in s_rm) <= config.max_rm_inventory

    for t in time_days:
        prob += lpSum(ui[i] * inventory[(i, t)] for i in i_prod) <= config.max_product_inventory

    for (boundary_day, i), target_val in i_target_map.items():
        t_local = boundary_day - cur_day + 1
        if 1 <= t_local <= config.short_term_horizon:
            prob += inventory[(i, t_local)] + due_slack[(i, t_local)] >= float(target_val)

    solver = getSolver("HiGHS", msg=False, timeLimit=config.time_limit, gapRel=config.gap_tolerance)
    start_time = time.time()
    prob.solve(solver)
    duration = time.time() - start_time

    status = LpStatus[prob.status]
    objective = prob.objective.value() if prob.objective else 0
    gap = None
    try:
        pass
    except Exception:
        gap = None

    def val(v: Any) -> float:
        return float(v) if v is not None else 0.0

    y_count = {}
    for t in time_days:
        y_count[(1, t)] = val(x12[(1, 1, t)].varValue) + val(x12[(2, 1, t)].varValue) + val(x12[(3, 1, t)].varValue)
        y_count[(2, t)] = val(x12[(1, 2, t)].varValue) + val(x12[(2, 2, t)].varValue) + val(x12[(3, 2, t)].varValue)
        y_count[(3, t)] = val(x3[(1, t)].varValue) + val(x3[(2, t)].varValue)
        y_count[(4, t)] = val(x4[t].varValue)

    rm_order_day = {(s, t): 0.0 for s in s_rm for t in time_days}
    rm_inv_day = {(s, t): 0.0 for s in s_rm for t in time_days}
    for s in s_rm:
        for w in weeks:
            t_first = week_first_day_local_fn(w, step=config.short_term_step)
            rm_order_day[(s, t_first)] = val(rm_order_week[(s, w)].varValue)

            inv_w = val(rm_inv_week[(s, w)].varValue)
            t_end = min(t_first + config.short_term_step - 1, config.short_term_horizon)
            for tt in range(t_first, t_end + 1):
                rm_inv_day[(s, tt)] = inv_w

    x12_out = {(m, i, t): val(x12[(m, i, t)].varValue) for m in line1_m for i in [1, 2] for t in time_days}
    x3_out = {(k, t): val(x3[(k, t)].varValue) for k in line2_m3 for t in time_days}
    x4_out = {t: val(x4[t].varValue) for t in time_days}

    return {
        "status": status,
        "objective": objective,
        "Y": y_count,
        "P": {(i, t): val(production[(i, t)].varValue) for i in i_prod for t in time_days},
        "Inv": {(i, t): val(inventory[(i, t)].varValue) for i in i_prod for t in time_days},
        "B": {(i, t): val(backlog[(i, t)].varValue) for i in i_prod for t in time_days},
        "B12": {(i, t): val(b12[(i, t)].varValue) for i in i_prod for t in time_days},
        "RMInv": {(s, t): rm_inv_day[(s, t)] for s in s_rm for t in time_days},
        "RMorder": {(s, t): rm_order_day[(s, t)] for s in s_rm for t in time_days},
        "X12": x12_out,
        "X3": x3_out,
        "X4": x4_out,
        "duration": duration,
        "gap": gap,
    }
