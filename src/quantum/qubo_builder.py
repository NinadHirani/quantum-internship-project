"""Build the QUBO matrix from a CVRP instance (implements Part B5 derivation)."""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit_optimization import QuadraticProgram


def build_cvrp_qubo(
    instance: dict[str, Any],
    distance_matrix: np.ndarray,
    penalty_weights: dict[str, float],
) -> QuadraticProgram:
    """Construct the QUBO for the CVRP instance.

    Parameters
    ----------
    penalty_weights : dict
        Keys: ``"coverage"``, ``"capacity"``, ``"subtour"`` → λ values.

    Returns
    -------
    QuadraticProgram
        Ready for conversion to Ising or direct solving.
    """
    raise NotImplementedError()


def decode_qubo_solution(
    bitstring: str,
    instance: dict[str, Any],
) -> dict[str, Any]:
    """Convert a measured bitstring back into vehicle routes.

    Returns
    -------
    dict
        ``{routes, total_distance, feasible}``
    """
    raise NotImplementedError()
