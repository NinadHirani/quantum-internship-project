"""Exact MILP solver for CVRP (stretch-goal cross-check)."""

# NOTE: This solver is intentionally unimplemented as it is a stretch goal.


from __future__ import annotations

from typing import Any

import numpy as np


def solve_cvrp_milp(
    instance: dict[str, Any],
    distance_matrix: np.ndarray,
    time_limit_seconds: int = 60,
) -> dict[str, Any]:
    """Solve the CVRP instance exactly via Mixed-Integer Linear Programming.

    Returns
    -------
    dict
        ``{routes, total_distance, runtime_seconds, feasible}``
    """
    raise NotImplementedError()
