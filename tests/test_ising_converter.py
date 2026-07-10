"""Tests for src.quantum.ising_converter — QUBO-to-Ising conversion."""

import pytest

from src.quantum.ising_converter import qubo_to_ising


class TestQuboToIsing:
    """Verify Ising conversion produces valid Hamiltonian."""

    def test_returns_operator_and_offset(self):
        pytest.skip("Not implemented yet")
