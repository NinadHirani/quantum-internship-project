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
    *,
    coord_range: tuple[float, float] = (0.0, 100.0),
    save_path: str | Path | None = None,
) -> dict[str, Any]:
    """Generate a random CVRP instance deterministically from *seed*.

    Coordinates are drawn uniformly from *coord_range*. Demands are drawn
    uniformly from [1, capacity // 2] to ensure feasibility is likely (but
    not guaranteed for every partition).

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    num_customers : int
        Number of customer nodes (excluding depot).
    num_vehicles : int
        Number of available vehicles.
    capacity : int
        Uniform capacity for every vehicle.
    coord_range : tuple[float, float]
        Min/max for x and y coordinates.
    save_path : str | Path | None
        If provided, save the instance as JSON to this path.

    Returns
    -------
    dict
        Instance dict matching the ``data/instance_seed42.json`` schema.
    """
    rng = np.random.default_rng(seed)
    lo, hi = coord_range

    # Depot at a random location (seeded)
    depot_x, depot_y = rng.uniform(lo, hi, size=2)

    # Customer locations and demands
    customers = []
    max_demand = max(1, capacity // 2)
    for i in range(1, num_customers + 1):
        cx, cy = rng.uniform(lo, hi, size=2)
        demand = int(rng.integers(1, max_demand + 1))
        customers.append({
            "id": i,
            "x": round(float(cx), 4),
            "y": round(float(cy), 4),
            "demand": demand,
        })

    instance = {
        "seed": seed,
        "depot": {"x": round(float(depot_x), 4), "y": round(float(depot_y), 4)},
        "customers": customers,
        "num_vehicles": num_vehicles,
        "vehicle_capacity": capacity,
    }

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(instance, f, indent=2)

    return instance


def load_instance(path: str | Path) -> dict[str, Any]:
    """Load a CVRP instance from a JSON file.

    Parameters
    ----------
    path : str | Path
        Path to the instance JSON file.

    Returns
    -------
    dict
        Instance dict with keys: seed, depot, customers, num_vehicles,
        vehicle_capacity.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    KeyError
        If required keys are missing from the JSON.
    """
    path = Path(path)
    with open(path) as f:
        instance = json.load(f)

    # Validate required keys
    required_keys = {"seed", "depot", "customers", "num_vehicles", "vehicle_capacity"}
    missing = required_keys - set(instance.keys())
    if missing:
        raise KeyError(f"Instance JSON missing required keys: {missing}")

    return instance


def compute_distance_matrix(instance: dict[str, Any]) -> np.ndarray:
    """Return the Euclidean distance matrix with depot as node 0.

    Parameters
    ----------
    instance : dict
        CVRP instance (from ``generate_instance`` or ``load_instance``).

    Returns
    -------
    np.ndarray
        Symmetric (n+1) × (n+1) distance matrix where entry [i][j] is the
        Euclidean distance between node i and node j.  Node 0 = depot,
        nodes 1..n = customers in order.
    """
    depot = instance["depot"]
    customers = instance["customers"]

    # Build coordinate list: depot first, then customers in id order
    coords = [(depot["x"], depot["y"])]
    for c in sorted(customers, key=lambda c: c["id"]):
        coords.append((c["x"], c["y"]))

    n = len(coords)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            d = math.sqrt(dx * dx + dy * dy)
            dist[i][j] = d
            dist[j][i] = d

    return dist
