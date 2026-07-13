"""Run classical and quantum solvers on the same instance and compare metrics.

Results are saved to ``results/benchmark_table.csv`` and returned as a
``pandas.DataFrame``.  **Hard rule:** never fabricate numbers — if QAOA
fails to find a feasible solution, ``feasible=False`` is recorded honestly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.problem import compute_distance_matrix, load_instance
from src.classical.ortools_solver import solve_cvrp_ortools
from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution
from src.quantum.qaoa_solver import solve_cvrp_qaoa


def run_benchmark(
    instance: dict[str, Any],
    penalty_weights: dict[str, float] | None = None,
    qaoa_p_layers: int = 2,
    qaoa_max_iter: int = 100,
    qaoa_shots: int = 1024,
    qaoa_seed: int = 42,
    results_path: str | Path = "results/benchmark_table.csv",
) -> pd.DataFrame:
    """Execute all solvers on *instance* and return a comparison DataFrame.

    Parameters
    ----------
    instance : dict
        CVRP instance dict.
    penalty_weights : dict | None
        Penalty weights for QUBO builder.  Defaults to heuristic values.
    qaoa_p_layers : int
        QAOA layer count.
    qaoa_max_iter : int
        QAOA max classical optimization iterations.
    qaoa_shots : int
        Measurement shots per QAOA evaluation.
    qaoa_seed : int
        Seed for QAOA reproducibility.
    results_path : str | Path
        Where to save the benchmark CSV.

    Returns
    -------
    pd.DataFrame
        Columns: method, total_distance, runtime_seconds,
        approximation_ratio, feasible, qubit_count, circuit_depth.
    """
    dist_matrix = compute_distance_matrix(instance)
    rows: list[dict[str, Any]] = []

    # ---- Classical: OR-Tools ----
    try:
        ortools_result = solve_cvrp_ortools(instance, dist_matrix)
        rows.append({
            "method": "OR-Tools (GLS)",
            "total_distance": ortools_result["total_distance"],
            "runtime_seconds": ortools_result["runtime_seconds"],
            "approximation_ratio": 1.0,  # reference baseline
            "feasible": ortools_result["feasible"],
            "qubit_count": None,
            "circuit_depth": None,
        })
    except RuntimeError as e:
        rows.append({
            "method": "OR-Tools (GLS)",
            "total_distance": None,
            "runtime_seconds": None,
            "approximation_ratio": None,
            "feasible": False,
            "qubit_count": None,
            "circuit_depth": None,
        })
        ortools_result = None

    # ---- Quantum: QAOA ----
    if penalty_weights is None:
        # Heuristic: penalty ≈ max distance × num_customers
        max_dist = dist_matrix.max()
        n = len(instance["customers"])
        default_penalty = float(max_dist * n)
        penalty_weights = {
            "coverage": default_penalty,
            "capacity": default_penalty,
        }

    try:
        qubo = build_cvrp_qubo(instance, dist_matrix, penalty_weights)
        qaoa_result = solve_cvrp_qaoa(
            qubo,
            p_layers=qaoa_p_layers,
            max_iter=qaoa_max_iter,
            shots=qaoa_shots,
            seed=qaoa_seed,
        )

        # Decode the best bitstring into routes
        decoded = decode_qubo_solution(
            qaoa_result["best_bitstring"],
            instance,
            dist_matrix,
        )

        # Approximation ratio (quantum / classical)
        approx_ratio = None
        if (
            decoded["feasible"]
            and ortools_result is not None
            and ortools_result["feasible"]
            and ortools_result["total_distance"] > 0
        ):
            approx_ratio = round(
                decoded["total_distance"] / ortools_result["total_distance"], 4
            )

        rows.append({
            "method": "QAOA (p={})".format(qaoa_p_layers),
            "total_distance": decoded["total_distance"] if decoded["feasible"] else None,
            "runtime_seconds": qaoa_result["runtime_seconds"],
            "approximation_ratio": approx_ratio,
            "feasible": decoded["feasible"],
            "qubit_count": qaoa_result["num_qubits"],
            "circuit_depth": None,  # populated if circuit info available
        })
    except Exception as e:
        rows.append({
            "method": f"QAOA (p={qaoa_p_layers})",
            "total_distance": None,
            "runtime_seconds": None,
            "approximation_ratio": None,
            "feasible": False,
            "qubit_count": None,
            "circuit_depth": None,
        })

    # Build DataFrame and save
    df = pd.DataFrame(rows)
    path = Path(results_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    return df
