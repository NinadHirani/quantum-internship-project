"""Tests for src.quantum.qubo_builder — QUBO construction and solution decoding."""

import pytest

from src.problem import compute_distance_matrix, generate_instance
from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution


@pytest.fixture
def toy_instance():
    """Tiny 3-customer instance for QUBO tests."""
    return generate_instance(seed=99, num_customers=3, num_vehicles=1, capacity=15)


@pytest.fixture
def toy_distance_matrix(toy_instance):
    return compute_distance_matrix(toy_instance)


@pytest.fixture
def default_penalties():
    return {"coverage": 100.0, "capacity": 100.0}


class TestBuildQubo:
    """Verify QUBO matrix dimensions and structure."""

    def test_qubo_num_variables(self, toy_instance, toy_distance_matrix, default_penalties):
        qubo = build_cvrp_qubo(toy_instance, toy_distance_matrix, default_penalties)
        n = len(toy_instance["customers"])
        # The QUBO may have additional slack variables from inequality constraints,
        # but should have at least n*n binary variables from the encoding
        assert qubo.get_num_vars() >= n * n

    def test_qubo_is_unconstrained(self, toy_instance, toy_distance_matrix, default_penalties):
        qubo = build_cvrp_qubo(toy_instance, toy_distance_matrix, default_penalties)
        # After conversion to QUBO, there should be no remaining linear constraints
        assert qubo.get_num_linear_constraints() == 0

    def test_qubo_all_binary(self, toy_instance, toy_distance_matrix, default_penalties):
        qubo = build_cvrp_qubo(toy_instance, toy_distance_matrix, default_penalties)
        for var in qubo.variables:
            assert var.vartype.name == "BINARY"


class TestDecodeQuboSolution:
    """Verify bitstring → route decoding."""

    def test_decode_returns_expected_keys(self, toy_instance, toy_distance_matrix):
        # Create a dummy bitstring (may not be feasible)
        n = len(toy_instance["customers"])
        bitstring = "0" * (n * n)
        result = decode_qubo_solution(bitstring, toy_instance, toy_distance_matrix)
        assert "routes" in result
        assert "total_distance" in result
        assert "feasible" in result

    def test_identity_permutation_is_feasible(self, toy_instance, toy_distance_matrix):
        """If customer i is assigned to position i, should be a valid permutation."""
        n = len(toy_instance["customers"])
        # Build identity permutation bitstring
        bits = []
        for i in range(n):
            row = ["0"] * n
            row[i] = "1"
            bits.extend(row)
        bitstring = "".join(bits)
        result = decode_qubo_solution(bitstring, toy_instance, toy_distance_matrix)
        assert result["feasible"] is True
        assert result["total_distance"] > 0
