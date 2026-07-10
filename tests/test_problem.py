"""Tests for src.problem — instance generation, loading, and distance matrix."""

import pytest

from src.problem import compute_distance_matrix, generate_instance, load_instance


@pytest.fixture
def toy_instance():
    """Small deterministic instance for unit tests."""
    return generate_instance(seed=42, num_customers=3, num_vehicles=1, capacity=15)


class TestGenerateInstance:
    """Verify instance generation determinism and schema."""

    def test_determinism(self):
        a = generate_instance(seed=42, num_customers=5, num_vehicles=2, capacity=10)
        b = generate_instance(seed=42, num_customers=5, num_vehicles=2, capacity=10)
        assert a == b

    def test_schema_keys(self):
        inst = generate_instance(seed=1, num_customers=3, num_vehicles=1, capacity=10)
        assert "depot" in inst
        assert "customers" in inst
        assert len(inst["customers"]) == 3


class TestDistanceMatrix:
    """Verify distance matrix properties."""

    def test_symmetry(self, toy_instance):
        dm = compute_distance_matrix(toy_instance)
        assert (dm == dm.T).all()

    def test_zero_diagonal(self, toy_instance):
        dm = compute_distance_matrix(toy_instance)
        assert (dm.diagonal() == 0).all()
