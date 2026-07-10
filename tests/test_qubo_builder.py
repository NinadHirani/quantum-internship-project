"""Tests for src.quantum.qubo_builder — QUBO construction and solution decoding."""

import pytest

from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution


class TestBuildQubo:
    """Verify QUBO matrix dimensions and energy evaluation."""

    def test_qubo_dimensions(self):
        # TODO: build QUBO for toy 3-node instance, check matrix shape
        pytest.skip("Not implemented yet")

    def test_known_solution_energy(self):
        # TODO: verify a known-good solution evaluates to expected low energy
        pytest.skip("Not implemented yet")


class TestDecodeQuboSolution:
    """Verify bitstring → route decoding."""

    def test_decode_returns_routes(self):
        pytest.skip("Not implemented yet")
