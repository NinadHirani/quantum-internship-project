# %% [markdown]
# # Quantum Vehicle Routing — Interactive Exploration
#
# This notebook provides a hands-on walkthrough of the Quantum Vehicle Routing
# project. We generate a CVRP instance, solve it classically (OR-Tools) and
# quantumly (QAOA via Qiskit), and compare the results.
#
# **Requirements:** Run `pip install -r requirements.txt` from the project root.

# %% [markdown]
# ## 1. Setup & Imports

# %%
import sys
from pathlib import Path

# Ensure the project root is on the path
project_root = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Use inline backend in Jupyter, Agg in script mode
try:
    get_ipython()  # noqa: F821
    matplotlib.use("module://matplotlib_inline.backend_inline")
except NameError:
    matplotlib.use("Agg")

from src.problem import generate_instance, compute_distance_matrix
from src.classical.ortools_solver import solve_cvrp_ortools
from src.quantum.qubo_builder import build_cvrp_qubo, decode_qubo_solution
from src.quantum.ising_converter import qubo_to_ising
from src.quantum.qaoa_solver import solve_cvrp_qaoa
from src.visualize.plots import plot_routes, plot_convergence

print("All imports successful!")

# %% [markdown]
# ## 2. Generate a CVRP Instance
#
# We create a problem with:
# - **1 depot** (node 0) + **5 customers** (nodes 1–5)
# - **2 vehicles**, each with capacity **Q = 15**
# - Deterministic via `seed=42` for reproducibility

# %%
instance = generate_instance(
    seed=42,
    num_customers=3,
    num_vehicles=2,
    capacity=15,
)

print(f"Depot:    ({instance['depot']['x']:.2f}, {instance['depot']['y']:.2f})")
print(f"Vehicles: {instance['num_vehicles']}")
print(f"Capacity: {instance['vehicle_capacity']}")
print()
for c in instance["customers"]:
    print(f"  Customer {c['id']}: ({c['x']:.2f}, {c['y']:.2f}), demand={c['demand']}")

# %% [markdown]
# ## 3. Distance Matrix
#
# Euclidean distances between all node pairs. Node 0 = depot.

# %%
dist_matrix = compute_distance_matrix(instance)
n_nodes = dist_matrix.shape[0]

print(f"Distance matrix shape: {dist_matrix.shape}")
print(f"Symmetry check: {np.allclose(dist_matrix, dist_matrix.T)}")
print(f"Zero diagonal: {np.allclose(np.diag(dist_matrix), 0)}")
print()

# Display as a formatted table
node_labels = ["Depot"] + [f"C{i}" for i in range(1, n_nodes)]
df_dist = pd.DataFrame(dist_matrix.round(2), index=node_labels, columns=node_labels)
print(df_dist.to_string())

# %% [markdown]
# ## 4. Visualize the Problem Instance

# %%
fig, ax = plt.subplots(figsize=(8, 6))

depot = instance["depot"]
ax.plot(depot["x"], depot["y"], "rs", markersize=14, label="Depot", zorder=5)
ax.annotate("Depot", (depot["x"], depot["y"]),
            textcoords="offset points", xytext=(8, 8), fontweight="bold")

for c in instance["customers"]:
    ax.plot(c["x"], c["y"], "bo", markersize=10, zorder=4)
    ax.annotate(f"C{c['id']} (d={c['demand']})", (c["x"], c["y"]),
                textcoords="offset points", xytext=(6, 6), fontsize=9)

ax.set_title("CVRP Instance — 3 Customers, 2 Vehicles, Capacity 15")
ax.set_xlabel("X coordinate")
ax.set_ylabel("Y coordinate")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(str(project_root / "results" / "figures" / "instance_map.png"), dpi=150)
plt.show()
print("Instance map saved.")

# %% [markdown]
# ## 5. Classical Solver — OR-Tools (Guided Local Search)
#
# OR-Tools uses a metaheuristic (Guided Local Search) to find high-quality
# solutions quickly. For this small instance, it finds the optimal solution
# almost instantly.

# %%
ortools_result = solve_cvrp_ortools(instance, dist_matrix, time_limit_seconds=5)

print(f"Feasible:  {ortools_result['feasible']}")
print(f"Distance:  {ortools_result['total_distance']}")
print(f"Runtime:   {ortools_result['runtime_seconds']}s")
print()
for i, route in enumerate(ortools_result["routes"]):
    demands_on_route = sum(
        next((c["demand"] for c in instance["customers"] if c["id"] == node), 0)
        for node in route
    )
    print(f"  Vehicle {i+1}: {' → '.join(str(n) for n in route)}  "
          f"(demand={demands_on_route}/{instance['vehicle_capacity']})")

# %%
plot_routes(
    instance, ortools_result["routes"],
    title=f"OR-Tools Routes (distance={ortools_result['total_distance']:.1f})",
    save_path=str(project_root / "results" / "figures" / "ortools_routes.png"),
)
print("OR-Tools route plot saved.")

# %% [markdown]
# ## 6. QUBO Formulation
#
# We convert the CVRP into a Quadratic Unconstrained Binary Optimization
# (QUBO) problem. This uses a **position-based encoding** where binary
# variable `x[i,p]` = 1 means customer `i` is at position `p` in the
# linearized route sequence.
#
# Constraints (coverage, capacity) are moved into the objective as penalty
# terms with weights λ.

# %%
# Penalty weights — heuristic: max_distance × num_customers
max_dist = dist_matrix.max()
n_customers = len(instance["customers"])
penalty = float(max_dist * n_customers)
penalty_weights = {"coverage": penalty, "capacity": penalty}

qubo = build_cvrp_qubo(instance, dist_matrix, penalty_weights)

print(f"Penalty weights: λ_coverage = λ_capacity = {penalty:.2f}")
print(f"QUBO decision variables: {qubo.get_num_vars()}")
print(f"  (3 customers × 3 positions = 9 original vars + auxiliary slack vars)")

# %% [markdown]
# ## 7. Ising Mapping
#
# Convert the QUBO to an Ising Hamiltonian via the substitution:
#
# $$x_i = \frac{1 + s_i}{2}$$
#
# This gives: $H(s) = \sum_i h_i s_i + \sum_{i<j} J_{ij} s_i s_j + C$

# %%
ising_op, offset = qubo_to_ising(qubo)

print(f"Ising Hamiltonian:")
print(f"  Number of Pauli terms: {len(ising_op)}")
print(f"  Number of qubits:      {ising_op.num_qubits}")
print(f"  Constant offset:       {offset:.4f}")
print()
print(f"This Hamiltonian H is encoded into the QAOA problem unitary")
print(f"U_C(γ) = exp(-iγH), which is applied in the quantum circuit.")

# %% [markdown]
# ## 8. QAOA Solver
#
# We run the Quantum Approximate Optimization Algorithm with:
# - **p = 2 layers** (alternating problem + mixer unitaries)
# - **COBYLA optimizer** (classical parameter tuning)
# - **StatevectorSampler** (exact simulation, no shot noise)
#
# ⚠️ This step takes several minutes due to the quantum simulation.

# %%
print("Running QAOA (this may take a few minutes)...")
qaoa_result = solve_cvrp_qaoa(
    qubo,
    p_layers=2,
    shots=1024,
    seed=42,
)

print(f"\nQAOA completed in {qaoa_result['runtime_seconds']:.1f}s")
print(f"Best QUBO value:   {qaoa_result['best_value']:.4f}")
print(f"Best bitstring:    {qaoa_result['best_bitstring']}")
print(f"Qubits used:       {qaoa_result['num_qubits']}")
print(f"Optimizer iterations: {len(qaoa_result['convergence_history'])}")

# %%
# Decode the best bitstring into vehicle routes
decoded = decode_qubo_solution(
    qaoa_result["best_bitstring"], instance, dist_matrix
)

print(f"\nDecoded QAOA solution:")
print(f"  Feasible: {decoded['feasible']}")
print(f"  Distance: {decoded['total_distance']}")
print()
for i, route in enumerate(decoded["routes"]):
    demands_on_route = sum(
        next((c["demand"] for c in instance["customers"] if c["id"] == node), 0)
        for node in route
    )
    print(f"  Vehicle {i+1}: {' → '.join(str(n) for n in route)}  "
          f"(demand={demands_on_route}/{instance['vehicle_capacity']})")

# %%
plot_routes(
    instance, decoded["routes"],
    title=f"QAOA Routes (distance={decoded['total_distance']:.1f}, "
          f"feasible={decoded['feasible']})",
    save_path=str(project_root / "results" / "figures" / "qaoa_routes.png"),
)
print("QAOA route plot saved.")

# %% [markdown]
# ## 9. Convergence Plot
#
# The QAOA cost function value vs. classical optimizer iteration.

# %%
if qaoa_result["convergence_history"]:
    fig, ax = plt.subplots(figsize=(10, 5))
    iters = range(1, len(qaoa_result["convergence_history"]) + 1)
    ax.plot(list(iters), qaoa_result["convergence_history"], "b-o", markersize=3)
    ax.set_title("QAOA Convergence")
    ax.set_xlabel("Optimizer Iteration")
    ax.set_ylabel("Cost Function Value")
    ax.grid(True, alpha=0.3)

    min_val = min(qaoa_result["convergence_history"])
    min_idx = qaoa_result["convergence_history"].index(min_val) + 1
    ax.axhline(y=min_val, color="r", linestyle="--", alpha=0.5,
               label=f"Min = {min_val:.2f} (iter {min_idx})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(str(project_root / "results" / "figures" / "qaoa_convergence.png"), dpi=150)
    plt.show()
    print(f"Minimum cost: {min_val:.2f} at iteration {min_idx}")

# %% [markdown]
# ## 10. Benchmark Comparison
#
# Side-by-side comparison of classical vs. quantum solvers.

# %%
approx_ratio = None
if (decoded["feasible"] and ortools_result["feasible"]
        and ortools_result["total_distance"] > 0):
    approx_ratio = round(decoded["total_distance"] / ortools_result["total_distance"], 4)

comparison = pd.DataFrame([
    {
        "Method": "OR-Tools (GLS)",
        "Distance": ortools_result["total_distance"],
        "Runtime (s)": ortools_result["runtime_seconds"],
        "Feasible": ortools_result["feasible"],
        "Approx Ratio": 1.0,
        "Qubits": "—",
    },
    {
        "Method": f"QAOA (p=2)",
        "Distance": decoded["total_distance"] if decoded["feasible"] else "N/A",
        "Runtime (s)": qaoa_result["runtime_seconds"],
        "Feasible": decoded["feasible"],
        "Approx Ratio": approx_ratio if approx_ratio else "N/A",
        "Qubits": qaoa_result["num_qubits"],
    },
])

print(comparison.to_string(index=False))

# %% [markdown]
# ## 11. Discussion
#
# **Key observations:**
#
# - **Solution quality:** OR-Tools finds a high-quality (likely optimal) solution
#   near-instantly. QAOA's solution quality depends on whether the optimizer
#   converges to a feasible, low-cost bitstring.
#
# - **Runtime:** QAOA on a simulator is orders of magnitude slower than OR-Tools
#   for this problem size. This is expected — simulation of quantum circuits
#   scales exponentially with qubit count.
#
# - **Qubit overhead:** 3 customers require ~9–17 qubits in position encoding,
#   which is near the practical limit for statevector simulation (~25 qubits).
#
# - **Feasibility:** QAOA may produce infeasible solutions (violated constraints)
#   because constraints are encoded as soft penalties. This is a known challenge
#   and is documented honestly.
#
# This comparison demonstrates that while QAOA provides a valid optimization
# approach, it does not currently outperform classical heuristics for small VRP
# instances — which is consistent with the published literature.

# %%
print("Exploration complete!")
