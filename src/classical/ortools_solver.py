"""Solve CVRP using Google OR-Tools routing library (metaheuristic).

Uses Guided Local Search (GLS) for improvement after an initial cheapest-arc
solution.  Returns structured results compatible with the benchmark module.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def solve_cvrp_ortools(
    instance: dict[str, Any],
    distance_matrix: np.ndarray,
    time_limit_seconds: int = 30,
) -> dict[str, Any]:
    """Solve the CVRP instance with OR-Tools guided local search.

    Parameters
    ----------
    instance : dict
        CVRP instance dict (depot, customers, num_vehicles, vehicle_capacity).
    distance_matrix : np.ndarray
        Euclidean distance matrix (node 0 = depot).
    time_limit_seconds : int
        Maximum solver runtime in seconds.

    Returns
    -------
    dict
        ``{routes: [[node_ids...], ...], total_distance: float,
        runtime_seconds: float, feasible: bool}``

    Raises
    ------
    RuntimeError
        If no feasible solution is found within the time limit.
    """
    num_nodes = distance_matrix.shape[0]
    num_vehicles = instance["num_vehicles"]
    depot_index = 0

    # OR-Tools expects integer distances — scale to avoid precision loss
    scale = 1000
    int_dist = (distance_matrix * scale).astype(int)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int_dist[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity constraint
    demands = [0]  # depot has zero demand
    for c in sorted(instance["customers"], key=lambda c: c["id"]):
        demands.append(c["demand"])

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        slack_max=0,
        vehicle_capacities=[instance["vehicle_capacity"]] * num_vehicles,
        fix_start_cumul_to_zero=True,
        name="Capacity",
    )

    # Search parameters
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.FromSeconds(time_limit_seconds)

    # Solve
    start_time = time.perf_counter()
    solution = routing.SolveWithParameters(search_params)
    elapsed = time.perf_counter() - start_time

    if solution is None:
        raise RuntimeError(
            f"OR-Tools found no feasible solution within {time_limit_seconds}s"
        )

    # Extract routes
    routes: list[list[int]] = []
    total_distance = 0.0

    for vehicle_id in range(num_vehicles):
        route: list[int] = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        # Append depot at end to close the loop
        route.append(depot_index)
        routes.append(route)

        # Compute real (unscaled) distance for this route
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]

    return {
        "routes": routes,
        "total_distance": round(total_distance, 4),
        "runtime_seconds": round(elapsed, 4),
        "feasible": True,
    }
