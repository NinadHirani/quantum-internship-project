#!/usr/bin/env python3
"""Run the full Quantum Vehicle Routing benchmark pipeline.

Executes every step from instance generation through plotting:
  1. Generate (or load) the CVRP instance
  2. Run the OR-Tools classical solver
  3. Build the QUBO and run the QAOA quantum solver
  4. Save benchmark comparison to CSV
  5. Generate all report-quality figures

Usage:
    python run_all.py                  # default: 5 customers, seed 42
    python run_all.py --customers 6    # 6 customers (more qubits)
    python run_all.py --seed 123       # different random instance
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from src.problem import generate_instance, compute_distance_matrix
from src.classical.ortools_solver import solve_cvrp_ortools
from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution
from src.quantum.ising_converter import qubo_to_ising
from src.quantum.qaoa_solver import solve_cvrp_qaoa
from src.benchmark.compare import run_benchmark
from src.visualize.plots import plot_routes, plot_convergence, plot_benchmark_comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full CVRP benchmark.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--customers", type=int, default=4, help="Number of customers (default: 4)")
    parser.add_argument("--vehicles", type=int, default=2, help="Number of vehicles (default: 2)")
    parser.add_argument("--capacity", type=int, default=15, help="Vehicle capacity (default: 15)")
    parser.add_argument("--qaoa-layers", type=int, default=2, help="QAOA p-layers (default: 2)")
    parser.add_argument("--qaoa-shots", type=int, default=1024, help="QAOA shots (default: 1024)")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    results_dir = project_root / "results"
    figures_dir = results_dir / "figures"

    # Ensure directories exist
    for d in [data_dir, results_dir, figures_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("QUANTUM VEHICLE ROUTING — FULL BENCHMARK PIPELINE")
    print("=" * 60)

    # ------------------------------------------------------------------
    # STEP 1: Generate instance
    # ------------------------------------------------------------------
    instance_path = data_dir / f"instance_seed{args.seed}.json"
    print(f"\n[Step 1] Generating CVRP instance (seed={args.seed}, "
          f"n={args.customers}, K={args.vehicles}, Q={args.capacity})...")

    instance = generate_instance(
        seed=args.seed,
        num_customers=args.customers,
        num_vehicles=args.vehicles,
        capacity=args.capacity,
        save_path=instance_path,
    )
    dist_matrix = compute_distance_matrix(instance)
    print(f"  → Instance saved to {instance_path}")
    print(f"  → Distance matrix shape: {dist_matrix.shape}")
    print(f"  → Customers: {[c['id'] for c in instance['customers']]}")
    print(f"  → Demands:   {[c['demand'] for c in instance['customers']]}")

    # ------------------------------------------------------------------
    # STEP 2: Classical solver (OR-Tools)
    # ------------------------------------------------------------------
    print(f"\n[Step 2] Running OR-Tools solver (Guided Local Search)...")
    t0 = time.perf_counter()
    ortools_result = solve_cvrp_ortools(instance, dist_matrix, time_limit_seconds=5)
    t_ortools = time.perf_counter() - t0
    print(f"  → Feasible: {ortools_result['feasible']}")
    print(f"  → Routes:   {ortools_result['routes']}")
    print(f"  → Distance: {ortools_result['total_distance']}")
    print(f"  → Runtime:  {ortools_result['runtime_seconds']}s")

    # Plot OR-Tools routes
    plot_routes(
        instance, ortools_result["routes"],
        title=f"OR-Tools Routes (distance={ortools_result['total_distance']:.1f})",
        save_path=str(figures_dir / "ortools_routes.png"),
    )
    print(f"  → Route plot saved to results/figures/ortools_routes.png")

    # ------------------------------------------------------------------
    # STEP 3: Build QUBO
    # ------------------------------------------------------------------
    print(f"\n[Step 3] Building QUBO from CVRP instance...")
    max_dist = dist_matrix.max()
    n = len(instance["customers"])
    default_penalty = float(max_dist * n)
    penalty_weights = {"coverage": default_penalty, "capacity": default_penalty}
    print(f"  → Penalty weights: coverage={default_penalty:.2f}, capacity={default_penalty:.2f}")

    qubo = build_cvrp_qubo(instance, dist_matrix, penalty_weights)
    num_vars = qubo.get_num_vars()
    print(f"  → QUBO variables (qubits): {num_vars}")

    # Show Ising conversion info
    ising_op, offset = qubo_to_ising(qubo)
    print(f"  → Ising Hamiltonian terms: {len(ising_op)}")
    print(f"  → Ising offset: {offset:.4f}")

    # ------------------------------------------------------------------
    # STEP 4: QAOA solver
    # ------------------------------------------------------------------
    print(f"\n[Step 4] Running QAOA solver (p={args.qaoa_layers}, "
          f"shots={args.qaoa_shots})...")
    print(f"  → This may take several minutes for {num_vars} qubits...")

    qaoa_result = solve_cvrp_qaoa(
        qubo,
        p_layers=args.qaoa_layers,
        shots=args.qaoa_shots,
        seed=args.seed,
    )
    print(f"  → Runtime: {qaoa_result['runtime_seconds']}s")
    print(f"  → Best value: {qaoa_result['best_value']:.4f}")
    print(f"  → Convergence iterations: {len(qaoa_result['convergence_history'])}")

    # Decode QAOA result
    decoded = decode_qubo_solution(
        qaoa_result["best_bitstring"], instance, dist_matrix
    )
    print(f"  → Decoded feasible: {decoded['feasible']}")
    print(f"  → Decoded routes:   {decoded['routes']}")
    print(f"  → Decoded distance: {decoded['total_distance']}")

    # Plot QAOA routes (even if infeasible, for visual inspection)
    plot_routes(
        instance, decoded["routes"],
        title=f"QAOA Routes (distance={decoded['total_distance']:.1f}, "
              f"feasible={decoded['feasible']})",
        save_path=str(figures_dir / "qaoa_routes.png"),
    )
    print(f"  → Route plot saved to results/figures/qaoa_routes.png")

    # Plot convergence
    if qaoa_result["convergence_history"]:
        plot_convergence(
            qaoa_result["convergence_history"],
            save_path=str(figures_dir / "qaoa_convergence.png"),
        )
        print(f"  → Convergence plot saved to results/figures/qaoa_convergence.png")

    # ------------------------------------------------------------------
    # STEP 5: Benchmark comparison
    # ------------------------------------------------------------------
    print(f"\n[Step 5] Building benchmark comparison table...")

    # Approximation ratio
    approx_ratio = None
    if (decoded["feasible"] and ortools_result["feasible"]
            and ortools_result["total_distance"] > 0):
        approx_ratio = round(
            decoded["total_distance"] / ortools_result["total_distance"], 4
        )

    rows = [
        {
            "method": "OR-Tools (GLS)",
            "total_distance": ortools_result["total_distance"],
            "runtime_seconds": ortools_result["runtime_seconds"],
            "approximation_ratio": 1.0,
            "feasible": True,
            "qubit_count": None,
            "circuit_depth": None,
        },
        {
            "method": f"QAOA (p={args.qaoa_layers})",
            "total_distance": decoded["total_distance"] if decoded["feasible"] else None,
            "runtime_seconds": qaoa_result["runtime_seconds"],
            "approximation_ratio": approx_ratio,
            "feasible": decoded["feasible"],
            "qubit_count": num_vars,
            "circuit_depth": None,
        },
    ]

    df = pd.DataFrame(rows)
    csv_path = results_dir / "benchmark_table.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  → Benchmark table saved to {csv_path}")
    print(df.to_string(index=False))

    # Plot benchmark comparison
    plot_benchmark_comparison(df, str(figures_dir / "benchmark_comparison.png"))
    print(f"  → Comparison plot saved to results/figures/benchmark_comparison.png")

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nInstance:  {args.customers} customers, {args.vehicles} vehicles, "
          f"capacity {args.capacity}")
    print(f"OR-Tools: distance={ortools_result['total_distance']}, "
          f"time={ortools_result['runtime_seconds']}s")
    print(f"QAOA:     distance={decoded['total_distance']}, "
          f"time={qaoa_result['runtime_seconds']}s, "
          f"feasible={decoded['feasible']}")
    if approx_ratio is not None:
        print(f"Approx ratio (QAOA/OR-Tools): {approx_ratio}")
    else:
        print("Approx ratio: N/A (QAOA solution infeasible)")
    print(f"\nAll results in: {results_dir}/")
    print(f"All figures in: {figures_dir}/")


if __name__ == "__main__":
    main()
