"""CVRP instance generation, loading, and distance matrix computation."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def generate_instance(
    seed: int,
    num_customers: int,
    num_vehicles: int,
    capacity: int,
) -> dict[str, Any]:
    """Generate a random CVRP instance deterministically from *seed*.

    Returns a dict matching the schema in ``data/instance_seed42.json``.
    """
    raise NotImplementedError()


def load_instance(path: str | Path) -> dict[str, Any]:
    """Load a CVRP instance from a JSON file."""
    raise NotImplementedError()


def compute_distance_matrix(instance: dict[str, Any]) -> np.ndarray:
    """Return the Euclidean distance matrix (depot = node 0)."""
    raise NotImplementedError()
