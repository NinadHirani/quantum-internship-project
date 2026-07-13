"""Tests for src.classical — OR-Tools solver."""

import pytest

from src.problem import compute_distance_matrix, generate_instance
from src.classical.ortools_solver import solve_cvrp_ortools


@pytest.fixture
def small_instance():
    """5-customer instance for solver tests."""
    return generate_instance(seed=42, num_customers=5, num_vehicles=2, capacity=10)


@pytest.fixture
def small_distance_matrix(small_instance):
    return compute_distance_matrix(small_instance)


class TestORToolsSolver:
    """Verify OR-Tools returns feasible, constraint-respecting routes."""

    def test_all_customers_visited(self, small_instance, small_distance_matrix):
        result = solve_cvrp_ortools(small_instance, small_distance_matrix)
        # Collect all non-depot nodes across all routes
        visited = set()
        for route in result["routes"]:
            for node in route:
                if node != 0:
                    visited.add(node)
        expected = {c["id"] for c in small_instance["customers"]}
        assert visited == expected, f"Not all customers visited: {visited} != {expected}"

    def test_capacity_respected(self, small_instance, small_distance_matrix):
        result = solve_cvrp_ortools(small_instance, small_distance_matrix)
        demands = {c["id"]: c["demand"] for c in small_instance["customers"]}
        cap = small_instance["vehicle_capacity"]
        for route in result["routes"]:
            route_demand = sum(demands.get(node, 0) for node in route)
            assert route_demand <= cap, (
                f"Route {route} has demand {route_demand} > capacity {cap}"
            )

    def test_returns_expected_schema(self, small_instance, small_distance_matrix):
        result = solve_cvrp_ortools(small_instance, small_distance_matrix)
        assert "routes" in result
        assert "total_distance" in result
        assert "runtime_seconds" in result
        assert "feasible" in result
        assert result["feasible"] is True
        assert result["total_distance"] > 0

    def test_routes_start_and_end_at_depot(self, small_instance, small_distance_matrix):
        result = solve_cvrp_ortools(small_instance, small_distance_matrix)
        for route in result["routes"]:
            assert route[0] == 0, f"Route does not start at depot: {route}"
            assert route[-1] == 0, f"Route does not end at depot: {route}"
