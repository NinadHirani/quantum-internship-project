"""Tests for src.quantum.qaoa_solver — QAOA execution and feasibility."""

import pytest

from src.problem import compute_distance_matrix, generate_instance
from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution
from src.quantum.qaoa_solver import solve_cvrp_qaoa


@pytest.fixture
def toy_qubo_and_instance():
    """Build a small QUBO + instance for QAOA tests."""
    inst = generate_instance(seed=99, num_customers=3, num_vehicles=1, capacity=15)
    dm = compute_distance_matrix(inst)
    penalties = {"coverage": 100.0, "capacity": 100.0}
    qubo = build_cvrp_qubo(inst, dm, penalties)
    return qubo, inst, dm


class TestQAOASolver:
    """Verify QAOA returns valid results."""

    def test_returns_expected_schema(self, toy_qubo_and_instance):
        qubo, inst, dm = toy_qubo_and_instance
        result = solve_cvrp_qaoa(qubo, p_layers=1, shots=512, seed=42)
        assert "best_bitstring" in result
        assert "best_value" in result
        assert "runtime_seconds" in result
        assert "convergence_history" in result
        assert "num_qubits" in result
        assert len(result["best_bitstring"]) == qubo.get_num_vars()

    def test_convergence_history_populated(self, toy_qubo_and_instance):
        qubo, inst, dm = toy_qubo_and_instance
        result = solve_cvrp_qaoa(qubo, p_layers=1, shots=512, seed=42)
        assert len(result["convergence_history"]) > 0
