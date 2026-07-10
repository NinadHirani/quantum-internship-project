"""Tests for src.quantum.qaoa_solver — QAOA execution and feasibility."""

import pytest

from src.quantum.qaoa_solver import solve_cvrp_qaoa


class TestQAOASolver:
    """Verify QAOA returns valid results and handles infeasible solutions."""

    def test_returns_expected_schema(self):
        pytest.skip("Not implemented yet")

    def test_feasibility_rate(self):
        # Run N times on toy instance, check success rate >= threshold
        pytest.skip("Not implemented yet")
