"""Solve CVRP using Google OR-Tools routing library (metaheuristic)."""

from __future__ import annotations

from typing import Any

import numpy as np


def solve_cvrp_ortools(
    instance: dict[str, Any],
    distance_matrix: np.ndarray,
    time_limit_seconds: int = 30,
) -> dict[str, Any]:
    """Solve the CVRP instance with OR-Tools guided local search.

    Returns
    -------
    dict
        ``{routes, total_distance, runtime_seconds, feasible}``
    """
    raise NotImplementedError()
