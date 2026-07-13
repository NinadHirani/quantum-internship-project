"""Tests for src.quantum.ising_converter — QUBO-to-Ising conversion."""

import pytest

from src.problem import compute_distance_matrix, generate_instance
from src.quantum.qubo_builder import build_cvrp_qubo
from src.quantum.ising_converter import qubo_to_ising


@pytest.fixture
def toy_qubo():
    """Build a small QUBO for Ising conversion tests."""
    inst = generate_instance(seed=99, num_customers=3, num_vehicles=1, capacity=15)
    dm = compute_distance_matrix(inst)
    penalties = {"coverage": 100.0, "capacity": 100.0}
    return build_cvrp_qubo(inst, dm, penalties)


class TestQuboToIsing:
    """Verify Ising conversion produces valid Hamiltonian."""

    def test_returns_operator_and_offset(self, toy_qubo):
        ising_op, offset = qubo_to_ising(toy_qubo)
        assert ising_op is not None
        assert isinstance(offset, float)

    def test_operator_qubit_count(self, toy_qubo):
        ising_op, _ = qubo_to_ising(toy_qubo)
        # The operator should have the same number of qubits as QUBO variables
        assert ising_op.num_qubits == toy_qubo.get_num_vars()
