"""Build the QUBO matrix from a CVRP instance.

Implements the derivation from ``docs/math_derivation.md`` Part B5.
Uses a position-based encoding where binary variable ``y[i, p]`` indicates
customer *i* is at position *p* in a linearised route sequence across all
vehicles.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_cvrp_qubo(
    instance: dict[str, Any],
    distance_matrix: np.ndarray,
    penalty_weights: dict[str, float],
) -> QuadraticProgram:
    """Construct a QUBO-ready ``QuadraticProgram`` for the CVRP instance.

    The formulation uses a **one-hot position encoding**: for *n* customers
    and *K* vehicles, we create *n* route-slots (positions) and assign each
    customer to exactly one slot.  Vehicle boundaries are derived from the
    slot ordering after decoding.

    Parameters
    ----------
    instance : dict
        CVRP instance (depot, customers, num_vehicles, vehicle_capacity).
    distance_matrix : np.ndarray
        (n+1)×(n+1) Euclidean distance matrix, node 0 = depot.
    penalty_weights : dict
        ``{"coverage": float, "capacity": float}`` — λ multipliers for
        the constraint penalty terms (see math_derivation.md §B5).

    Returns
    -------
    QuadraticProgram
        The resulting QUBO-form quadratic program (all constraints converted
        to penalty terms).
    """
    customers = sorted(instance["customers"], key=lambda c: c["id"])
    n = len(customers)
    num_vehicles = instance["num_vehicles"]
    capacity = instance["vehicle_capacity"]

    # Number of route positions = number of customers
    # (each customer occupies exactly one position in the flattened route)
    num_positions = n

    qp = QuadraticProgram("CVRP")

    # --- Binary variables: x_{i,p} (customer i at position p) ---
    var_names: list[str] = []
    for i in range(n):
        for p in range(num_positions):
            name = f"x_{customers[i]['id']}_{p}"
            qp.binary_var(name)
            var_names.append(name)

    # Helper to get variable name
    def vname(cust_idx: int, pos: int) -> str:
        return f"x_{customers[cust_idx]['id']}_{pos}"

    # --- Objective: distance ---
    # Distance contribution: sum over consecutive positions in the route
    # d(depot, first) + d(pos_p, pos_{p+1}) + d(last, depot)
    # This is expressed as quadratic terms between position variables.
    linear_obj: dict[str, float] = {}
    quadratic_obj: dict[tuple[str, str], float] = {}

    for p in range(num_positions):
        for i in range(n):
            ci = customers[i]["id"]  # node index in distance matrix
            vi = vname(i, p)

            # Distance from depot to first position / from last position to depot
            if p == 0 or p == num_positions - 1:
                depot_dist = distance_matrix[0][ci]
                linear_obj[vi] = linear_obj.get(vi, 0.0) + depot_dist

            # Distance between consecutive positions
            if p < num_positions - 1:
                for j in range(n):
                    cj = customers[j]["id"]
                    vj = vname(j, p + 1)
                    d = distance_matrix[ci][cj]
                    if d != 0:
                        key = (vi, vj) if vi <= vj else (vj, vi)
                        quadratic_obj[key] = quadratic_obj.get(key, 0.0) + d

    qp.minimize(linear=linear_obj, quadratic=quadratic_obj)

    # --- Constraint 1: each customer visited exactly once ---
    lam1 = penalty_weights.get("coverage", 10.0)
    for i in range(n):
        constraint_vars = [vname(i, p) for p in range(num_positions)]
        coeffs = [1.0] * num_positions
        qp.linear_constraint(
            linear={v: c for v, c in zip(constraint_vars, coeffs)},
            sense="==",
            rhs=1.0,
            name=f"coverage_cust{customers[i]['id']}",
        )

    # --- Constraint 2: each position occupied by exactly one customer ---
    for p in range(num_positions):
        constraint_vars = [vname(i, p) for i in range(n)]
        coeffs = [1.0] * n
        qp.linear_constraint(
            linear={v: c for v, c in zip(constraint_vars, coeffs)},
            sense="==",
            rhs=1.0,
            name=f"position_{p}",
        )

    # --- Constraint 3: capacity (simplified — split route at midpoint) ---
    # For K=2 vehicles: first half of positions → vehicle 1,
    # second half → vehicle 2.
    lam2 = penalty_weights.get("capacity", 10.0)
    split = num_positions // num_vehicles
    for k in range(num_vehicles):
        start_pos = k * split
        end_pos = start_pos + split if k < num_vehicles - 1 else num_positions
        cap_vars = {}
        for p in range(start_pos, end_pos):
            for i in range(n):
                vi = vname(i, p)
                cap_vars[vi] = cap_vars.get(vi, 0.0) + customers[i]["demand"]
        qp.linear_constraint(
            linear=cap_vars,
            sense="<=",
            rhs=float(capacity),
            name=f"capacity_vehicle{k}",
        )

    # --- Convert to QUBO (move constraints into objective as penalties) ---
    converter = QuadraticProgramToQubo(penalty=max(lam1, lam2))
    qubo = converter.convert(qp)

    # Attach the converter so we can interpret solutions later
    qubo._cvrp_converter = converter  # type: ignore[attr-defined]
    qubo._cvrp_instance = instance  # type: ignore[attr-defined]
    qubo._cvrp_customers = customers  # type: ignore[attr-defined]
    qubo._cvrp_distance_matrix = distance_matrix  # type: ignore[attr-defined]

    return qubo


def decode_qubo_solution(
    bitstring: str,
    instance: dict[str, Any],
    distance_matrix: np.ndarray | None = None,
) -> dict[str, Any]:
    """Convert a measured bitstring back into vehicle routes.

    Parameters
    ----------
    bitstring : str
        Binary string of length n², where ``bitstring[i*n + p]`` corresponds
        to variable ``x_{customer_i, position_p}``.
    instance : dict
        CVRP instance.
    distance_matrix : np.ndarray | None
        If provided, used to compute total distance.

    Returns
    -------
    dict
        ``{routes: [[node_ids]], total_distance: float, feasible: bool}``
    """
    customers = sorted(instance["customers"], key=lambda c: c["id"])
    n = len(customers)
    num_vehicles = instance["num_vehicles"]
    capacity = instance["vehicle_capacity"]

    # Parse bitstring into assignment matrix
    bits = [int(b) for b in bitstring]
    if len(bits) < n * n:
        # Pad if the QUBO added auxiliary variables
        bits.extend([0] * (n * n - len(bits)))

    # Build position → customer mapping
    position_customer: dict[int, int] = {}
    customer_count: dict[int, int] = {}

    for i in range(n):
        for p in range(n):
            idx = i * n + p
            if idx < len(bits) and bits[idx] == 1:
                if p not in position_customer:
                    position_customer[p] = customers[i]["id"]
                customer_count[customers[i]["id"]] = (
                    customer_count.get(customers[i]["id"], 0) + 1
                )

    # Check feasibility: each customer exactly once, each position exactly once
    all_customers = {c["id"] for c in customers}
    visited = set(customer_count.keys())
    feasible = (
        visited == all_customers
        and all(v == 1 for v in customer_count.values())
        and len(position_customer) == n
    )

    # Build routes by splitting positions across vehicles
    split = n // num_vehicles
    routes: list[list[int]] = []
    for k in range(num_vehicles):
        start_pos = k * split
        end_pos = start_pos + split if k < num_vehicles - 1 else n
        route = [0]  # start at depot
        for p in range(start_pos, end_pos):
            if p in position_customer:
                route.append(position_customer[p])
        route.append(0)  # return to depot
        routes.append(route)

    # Check capacity feasibility
    demands = {c["id"]: c["demand"] for c in customers}
    for route in routes:
        route_demand = sum(demands.get(node, 0) for node in route)
        if route_demand > capacity:
            feasible = False

    # Compute total distance
    total_distance = 0.0
    if distance_matrix is not None and feasible:
        for route in routes:
            for i in range(len(route) - 1):
                total_distance += distance_matrix[route[i]][route[i + 1]]

    return {
        "routes": routes,
        "total_distance": round(total_distance, 4),
        "feasible": feasible,
    }
