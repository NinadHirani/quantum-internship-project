"""Run QAOA on the Ising Hamiltonian using Qiskit Aer simulator."""

from __future__ import annotations

from typing import Any

from qiskit_optimization import QuadraticProgram


def solve_cvrp_qaoa(
    qubo: QuadraticProgram,
    p_layers: int = 2,
    optimizer: str = "COBYLA",
    shots: int = 1024,
    seed: int = 42,
) -> dict[str, Any]:
    """Solve the CVRP via QAOA on Aer simulator.

    Returns
    -------
    dict
        ``{best_bitstring, routes, total_distance, runtime_seconds,
        feasible, convergence_history}``
    """
    raise NotImplementedError()
