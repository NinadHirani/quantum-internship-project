"""Tests for src.classical — OR-Tools and MILP solvers."""

import pytest

from src.classical.ortools_solver import solve_cvrp_ortools


class TestORToolsSolver:
    """Verify OR-Tools returns feasible, constraint-respecting routes."""

    def test_all_customers_visited(self):
        pytest.skip("Not implemented yet")

    def test_capacity_respected(self):
        pytest.skip("Not implemented yet")

    def test_returns_expected_schema(self):
        pytest.skip("Not implemented yet")
