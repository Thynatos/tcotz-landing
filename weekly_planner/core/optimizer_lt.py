"""
Long-term optimization model helpers.
"""
from __future__ import annotations

import time
from typing import Any, Callable

from pulp import LpMinimize, LpProblem, LpStatus, LpVariable, getSolver, lpSum, value
from .optimizer_helpers import round_inventory_target


def solve_long_term_deterministic(
    d_lt: dict,
    a_lt: dict,
    cur_day: int,
    i_init: dict[int, float],
    b_init: dict[int, float],
    config: Any,
    h_lt: dict[int, float],
    b_lt: dict[int, float],
    u_lt: dict[int, float],
    r_lt: dict[int, float],
    i_prod: list[int],
) -> dict:
    """Solve the deterministic LT model."""
    time_blocks = list(a_lt.keys())
    prob = LpProblem(f"LT_{cur_day}", LpMinimize)

    production = {(i, t): LpVariable(f"P_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}
    inventory = {(i, t): LpVariable(f"I_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}
    backlog = {(i, t): LpVariable(f"B_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}

    prob += lpSum(
        b_lt[i] * backlog[(i, t)] + h_lt[i] * inventory[(i, t)]
        for i in i_prod
        for t in time_blocks
    )

    for t in time_blocks:
        prob += lpSum(production[(i, t)] for i in [1, 2]) <= 3500 * a_lt[t]
        prob += (production[(3, t)] / 35000.0) + (production[(4, t)] / 80000.0) <= a_lt[t]

    for t in time_blocks:
        i2_prev = i_init[2] if t == 1 else inventory[(2, t - 1)]
        prob += i2_prev + production[(2, t)] - (
            u_lt[3] * production[(3, t)] + u_lt[4] * production[(4, t)]
        ) == inventory[(2, t)]

    for i in [1, 3, 4]:
        for t in time_blocks:
            if t == 1:
                i_prev, b_prev = i_init[i], b_init[i]
            else:
                i_prev, b_prev = inventory[(i, t - 1)], backlog[(i, t - 1)]
            prob += i_prev + production[(i, t)] - d_lt[(i, t)] - b_prev + backlog[(i, t)] == inventory[(i, t)]

    for t in time_blocks:
        prob += lpSum(r_lt[i] * inventory[(i, t)] for i in i_prod) <= config.max_product_inventory

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

    inv_lt = {(i, t): float(inventory[(i, t)].varValue or 0) for i in i_prod for t in time_blocks}
    prod_lt = {(i, t): float(production[(i, t)].varValue or 0) for i in i_prod for t in time_blocks}
    backlog_lt = {(i, t): float(backlog[(i, t)].varValue or 0) for i in i_prod for t in time_blocks}

    targets = {}
    b1 = next((b for b in config.lt_blocks if b['block_index'] == 1), None)
    b2 = next((b for b in config.lt_blocks if b['block_index'] == 2), None)
    
    if b1 and b1.get('calendar_day_indices') and b1['calendar_day_indices'][-1] <= config.total_days:
        for i in i_prod:
            targets[(b1['calendar_day_indices'][-1], i)] = round_inventory_target(i, inv_lt[(i, 1)])
    if b2 and b2.get('calendar_day_indices') and b2['calendar_day_indices'][-1] <= config.total_days:
        for i in i_prod:
            targets[(b2['calendar_day_indices'][-1], i)] = round_inventory_target(i, inv_lt[(i, 2)])

    return {
        "status": status,
        "objective": objective,
        "targets": targets,
        "duration": duration,
        "gap": gap,
        "production": prod_lt,
        "inventory": inv_lt,
        "backlog": backlog_lt,
        "demand": dict(d_lt),
    }


def solve_long_term(
    cur_day: int,
    i_init: dict[int, float],
    b_init: dict[int, float],
    config: Any,
    i_prod: list[int],
    h_lt: dict[int, float],
    b_lt: dict[int, float],
    u_lt: dict[int, float],
    r_lt: dict[int, float],
    scenarios: list[Any] | None = None,
) -> dict:
    """Solve the LT model in deterministic or stochastic mode."""
    time_blocks = [b['block_index'] for b in config.lt_blocks]
    stage1_blocks = time_blocks[:2]
    stage2_blocks = time_blocks[2:]

    d_lt = {}
    a_lt = {}
    for b in config.lt_blocks:
        t = b['block_index']
        a_lt[t] = b['production_days_available']
        for i in i_prod:
            if t <= 2:
                val = sum(config.daily_demand_by_day.get((i, day_idx), 0.0) for day_idx in b['calendar_day_indices'])
            else:
                val = config.monthly_forecast_by_period.get((i, b['period_key']), 0.0)
            d_lt[(i, t)] = val

    if scenarios is None:
        return solve_long_term_deterministic(
            d_lt=d_lt,
            a_lt=a_lt,
            cur_day=cur_day,
            i_init=i_init,
            b_init=b_init,
            config=config,
            h_lt=h_lt,
            b_lt=b_lt,
            u_lt=u_lt,
            r_lt=r_lt,
            i_prod=i_prod,
        )

    scenario_count = len(scenarios)
    prob = LpProblem(f"LT_stoch_{cur_day}", LpMinimize)

    p1 = {(i, t): LpVariable(f"P1_{i}_{t}", lowBound=0) for i in i_prod for t in stage1_blocks}
    inv1 = {(i, t): LpVariable(f"I1_{i}_{t}", lowBound=0) for i in i_prod for t in stage1_blocks}
    b1 = {(i, t): LpVariable(f"B1_{i}_{t}", lowBound=0) for i in i_prod for t in stage1_blocks}

    p2 = {
        (i, t, w): LpVariable(f"P2_{i}_{t}_{w}", lowBound=0)
        for i in i_prod for t in stage2_blocks for w in range(scenario_count)
    }
    inv2 = {
        (i, t, w): LpVariable(f"I2_{i}_{t}_{w}", lowBound=0)
        for i in i_prod for t in stage2_blocks for w in range(scenario_count)
    }
    b2 = {
        (i, t, w): LpVariable(f"B2_{i}_{t}_{w}", lowBound=0)
        for i in i_prod for t in stage2_blocks for w in range(scenario_count)
    }

    d_s = {}
    for w, scenario in enumerate(scenarios):
        for t in stage2_blocks:
            for i in [1, 3, 4]:
                d_s[(i, t, w)] = scenario.demands.get(t, {}).get(i, d_lt.get((i, t), 0.0))

    stage1_cost = lpSum(
        b_lt[i] * b1[(i, t)] + h_lt[i] * inv1[(i, t)]
        for i in i_prod for t in stage1_blocks
    )
    stage2_cost = lpSum(
        scenarios[w].probability * (b_lt[i] * b2[(i, t, w)] + h_lt[i] * inv2[(i, t, w)])
        for i in i_prod for t in stage2_blocks for w in range(scenario_count)
    )
    prob += stage1_cost + stage2_cost

    for t in stage1_blocks:
        prob += lpSum(p1[(i, t)] for i in [1, 2]) <= 3500 * a_lt[t]
        prob += (p1[(3, t)] / 35000.0) + (p1[(4, t)] / 80000.0) <= a_lt[t]
        prob += lpSum(r_lt[i] * inv1[(i, t)] for i in i_prod) <= config.max_product_inventory

    for t in stage1_blocks:
        i2_prev = i_init[2] if t == 1 else inv1[(2, t - 1)]
        prob += i2_prev + p1[(2, t)] - (u_lt[3] * p1[(3, t)] + u_lt[4] * p1[(4, t)]) == inv1[(2, t)]

    for i in [1, 3, 4]:
        for t in stage1_blocks:
            if t == 1:
                i_prev, b_prev = i_init[i], b_init[i]
            else:
                i_prev, b_prev = inv1[(i, t - 1)], b1[(i, t - 1)]
            prob += i_prev + p1[(i, t)] - d_lt[(i, t)] - b_prev + b1[(i, t)] == inv1[(i, t)]

    for w in range(scenario_count):
        for t in stage2_blocks:
            prob += lpSum(p2[(i, t, w)] for i in [1, 2]) <= 3500 * a_lt[t]
            prob += (p2[(3, t, w)] / 35000.0) + (p2[(4, t, w)] / 80000.0) <= a_lt[t]
            prob += lpSum(r_lt[i] * inv2[(i, t, w)] for i in i_prod) <= config.max_product_inventory

        for t in stage2_blocks:
            i2_prev = inv1[(2, 2)] if t == 3 else inv2[(2, t - 1, w)]
            prob += i2_prev + p2[(2, t, w)] - (u_lt[3] * p2[(3, t, w)] + u_lt[4] * p2[(4, t, w)]) == inv2[(2, t, w)]

        for i in [1, 3, 4]:
            for t in stage2_blocks:
                if t == 3:
                    i_prev, b_prev = inv1[(i, 2)], b1[(i, 2)]
                else:
                    i_prev, b_prev = inv2[(i, t - 1, w)], b2[(i, t - 1, w)]
                prob += i_prev + p2[(i, t, w)] - d_s[(i, t, w)] - b_prev + b2[(i, t, w)] == inv2[(i, t, w)]

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

    stage1_value = value(stage1_cost) if stage1_cost is not None else 0.0
    stage2_value = value(stage2_cost) if stage2_cost is not None else 0.0

    inv_lt = {(i, t): float(inv1[(i, t)].varValue or 0) for i in i_prod for t in stage1_blocks}
    prod_lt = {(i, t): float(p1[(i, t)].varValue or 0) for i in i_prod for t in stage1_blocks}
    backlog_lt = {(i, t): float(b1[(i, t)].varValue or 0) for i in i_prod for t in stage1_blocks}

    targets = {}
    b1 = next((b for b in config.lt_blocks if b['block_index'] == 1), None)
    b2 = next((b for b in config.lt_blocks if b['block_index'] == 2), None)
    
    if b1 and b1.get('calendar_day_indices') and b1['calendar_day_indices'][-1] <= config.total_days:
        for i in i_prod:
            targets[(b1['calendar_day_indices'][-1], i)] = round_inventory_target(i, inv_lt[(i, 1)])
    if b2 and b2.get('calendar_day_indices') and b2['calendar_day_indices'][-1] <= config.total_days:
        for i in i_prod:
            targets[(b2['calendar_day_indices'][-1], i)] = round_inventory_target(i, inv_lt[(i, 2)])

    return {
        "status": status,
        "objective": objective,
        "stage1_cost": stage1_value,
        "stage2_cost": stage2_value,
        "targets": targets,
        "duration": duration,
        "gap": gap,
        "production": prod_lt,
        "inventory": inv_lt,
        "backlog": backlog_lt,
        "demand": dict(d_lt),
    }


def compute_warm_start_initial_state(
    config: Any,
    i_prod: list[int],
    h_lt: dict[int, float],
    b_lt: dict[int, float],
    u_lt: dict[int, float],
    r_lt: dict[int, float],
    u23: float,
    u24: float,
) -> dict[int, float]:
    """Solve LT model at day 0 to determine recommended initial inventory."""
    i_zero = {i: 0.0 for i in i_prod}
    b_zero = {i: 0.0 for i in i_prod}
    
    time_blocks = [b['block_index'] for b in config.lt_blocks]
    d_lt = {}
    a_lt = {}
    for b in config.lt_blocks:
        t = b['block_index']
        a_lt[t] = b['production_days_available']
        for i in i_prod:
            if t <= 2:
                val = sum(config.daily_demand_by_day.get((i, day_idx), 0.0) for day_idx in b['calendar_day_indices'])
            else:
                val = config.monthly_forecast_by_period.get((i, b['period_key']), 0.0)
            d_lt[(i, t)] = val

    try:
        prob = LpProblem("LT_warm_start", LpMinimize)

        production = {(i, t): LpVariable(f"P_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}
        inventory = {(i, t): LpVariable(f"I_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}
        backlog = {(i, t): LpVariable(f"B_{i}_{t}", lowBound=0) for i in i_prod for t in time_blocks}

        prob += lpSum(
            b_lt[i] * backlog[(i, t)] + h_lt[i] * inventory[(i, t)]
            for i in i_prod for t in time_blocks
        )

        for t in time_blocks:
            prob += lpSum(production[(i, t)] for i in [1, 2]) <= 3500 * a_lt[t]
            prob += (production[(3, t)] / 35000.0) + (production[(4, t)] / 80000.0) <= a_lt[t]

        for t in time_blocks:
            i2_prev = i_zero[2] if t == 1 else inventory[(2, t - 1)]
            prob += i2_prev + production[(2, t)] - (
                u_lt[3] * production[(3, t)] + u_lt[4] * production[(4, t)]
            ) == inventory[(2, t)]

        for i in [1, 3, 4]:
            for t in time_blocks:
                if t == 1:
                    i_prev, b_prev = i_zero[i], b_zero[i]
                else:
                    i_prev, b_prev = inventory[(i, t - 1)], backlog[(i, t - 1)]
                prob += i_prev + production[(i, t)] - d_lt[(i, t)] - b_prev + backlog[(i, t)] == inventory[(i, t)]

        for t in time_blocks:
            prob += lpSum(r_lt[i] * inventory[(i, t)] for i in i_prod) <= config.max_product_inventory

        solver = getSolver("HiGHS", msg=False, timeLimit=config.time_limit, gapRel=config.gap_tolerance)
        prob.solve(solver)

        if LpStatus[prob.status] != "Optimal":
            p3_demand_block1 = d_lt.get((3, 1), 0.0)
            p2_needed = p3_demand_block1 * u23
            p2_safety = 35000 * 12 * u23
            return {1: 10000.0, 2: max(p2_needed, p2_safety, 20000.0), 3: 250000.0, 4: 0.0}

        p_block1 = {i: float(production[(i, 1)].varValue or 0) for i in i_prod}
        inv_block1 = {i: float(inventory[(i, 1)].varValue or 0) for i in i_prod}

        p2_consumption_block1 = u23 * p_block1[3] + u24 * p_block1[4]
        p2_production_block1 = p_block1[2]
        p2_initial = max(0, p2_consumption_block1 - p2_production_block1)
        p2_safety = 35000 * 6 * u23
        p2_recommended = max(p2_initial, p2_safety, 20000.0)

        p3_recommended = min(inv_block1[3] * 0.3, 250000.0)
        p1_demand_block1 = d_lt.get((1, 1), 0.0)
        p1_production_block1 = p_block1[1]
        p1_initial = max(0, p1_demand_block1 - p1_production_block1)
        p1_recommended = max(p1_initial, 10000.0)

        return {
            1: p1_recommended,
            2: p2_recommended,
            3: max(p3_recommended, 100000.0),
            4: 0.0,
        }
    except Exception:
        p3_demand_block1 = d_lt.get((3, 1), 0.0)
        p2_needed = p3_demand_block1 * u23
        p2_safety = 35000 * 12 * u23
        return {1: 10000.0, 2: max(p2_needed, p2_safety, 20000.0), 3: 250000.0, 4: 0.0}
