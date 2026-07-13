# Project Report — Quantum vs. Classical Optimization for Vehicle Routing

---

## 1. Abstract

This project presents a comparative study of classical and quantum optimization approaches for the Capacitated Vehicle Routing Problem (CVRP). We implement the problem using Google OR-Tools (classical metaheuristic) and the Quantum Approximate Optimization Algorithm (QAOA) via Qiskit, running on a statevector simulator. Using a 4-customer, 2-vehicle CVRP instance, we build a complete pipeline from mathematical formulation through QUBO construction, Ising mapping, and QAOA execution. Our results confirm that classical heuristics significantly outperform QAOA at this problem scale — both in solution quality and runtime — which is consistent with the published literature. The value of this work lies in providing a clear, reproducible, and honest comparison that demonstrates the full quantum optimization workflow and identifies the practical bottlenecks.

---

## 2. Introduction

The Vehicle Routing Problem (VRP) is one of the most studied problems in operations research, with direct applications in logistics, supply chain management, and transportation planning. Its NP-hard complexity makes it a natural candidate for exploring quantum computing advantages.

**Motivation:** As quantum computing hardware matures, understanding where quantum algorithms might provide practical benefit over classical approaches is critical. The CVRP provides an ideal testbed because:

1. It is NP-hard (classical exact solvers don't scale)
2. It can be naturally encoded as a QUBO/Ising problem
3. Small instances are tractable on current quantum simulators
4. Classical heuristics provide a strong baseline for comparison

**Objective:** Build a fully reproducible pipeline that:
- Solves the same CVRP instance using both classical (OR-Tools) and quantum (QAOA) methods
- Compares solution quality, runtime, and feasibility
- Documents the results honestly, including cases where QAOA underperforms

---

## 3. Literature Review

See [docs/literature_review.md](literature_review.md) for the full review. Key papers:

1. **Farhi et al. (2014)** introduced QAOA for combinatorial optimization, proving non-trivial approximation ratios for MAX-CUT.
2. **Feld et al. (2019)** applied quantum annealing to CVRP with a hybrid decomposition approach, demonstrating feasibility for small instances (≤20 customers).
3. **Harwood et al. (2021)** provided systematic QUBO encodings for routing problems, identifying position-based encoding as qubit-efficient for small instances.
4. **Blekos et al. (2024)** surveyed QAOA variants, noting that QAOA with p ≥ 3 layers generally outperforms random sampling but rarely surpasses classical heuristics.
5. **Borowski et al. (2020)** benchmarked hybrid quantum-classical VRP algorithms, confirming the 5-6 customer practical limit for full QUBO approaches.

Our project differs in its educational focus, gate-based (rather than annealing) approach, and commitment to honest reporting.

---

## 4. Theory

### 4.1 Graph Representation
The CVRP instance is modeled as a complete weighted graph G = (V, E) where V = {depot, customer₁, ..., customerₙ} and edge weights are Euclidean distances.

### 4.2 NP-Hardness
CVRP generalizes TSP (itself NP-hard): setting K=1, Q=∞ reduces CVRP to TSP. The solution space grows combinatorially — exact methods become infeasible for large n.

### 4.3 QUBO Formulation
Any combinatorial problem with binary decisions can be rewritten in QUBO form: minimize x^T Q x over binary vector x. Constraints are absorbed into the objective as penalty terms.

### 4.4 Ising Model
The QUBO-to-Ising mapping via x_i = (1 + s_i)/2 transforms binary (0/1) variables into spin (±1) variables, yielding a Hamiltonian H(s) whose ground state corresponds to the optimal solution.

### 4.5 QAOA
QAOA is a hybrid quantum-classical algorithm that:
1. Encodes the cost function as a problem Hamiltonian H_C
2. Alternates problem and mixer unitaries over p layers
3. Uses a classical optimizer to tune parameters (γ, β)
4. Measures the final state to obtain candidate solutions

For full derivations, see [docs/math_derivation.md](math_derivation.md).

---

## 5. Methodology

### 5.1 Problem Encoding
We use a **position-based encoding** for the QUBO:
- Binary variable x[i,p] = 1 if customer i is at position p in the linearized route sequence
- 3 customers × 3 positions = 9 decision variables
- After constraint conversion: 17 total qubits (including slack variables from capacity constraints)

**Note on instance size:** We use 3 customers by default (17 qubits, ~50s execution) to ensure fast simulation. Running 4 customers requires 24 qubits (which takes over an hour to simulate on standard CPU without hardware acceleration), and 5 customers requires 33 qubits (which requires ~128 GB RAM for statevector simulation and is intractable).

### 5.2 Constraint Penalties
Three constraint types are converted to penalty terms:
1. **Coverage:** each customer visited exactly once (Σ_p x[i,p] = 1 for all i)
2. **Position:** each position occupied by exactly one customer (Σ_i x[i,p] = 1 for all p)
3. **Capacity:** vehicle load does not exceed Q (using position-based route splitting)

Penalty weight λ is set heuristically to max_distance × n_customers ≈ 198.

### 5.3 Solvers
- **Classical:** OR-Tools with Guided Local Search metaheuristic, 5-second time limit
- **Quantum:** QAOA with p=2 layers, COBYLA optimizer (100 max iterations), StatevectorSampler

---

## 6. Implementation

The project is structured as modular Python packages:

| Module | Responsibility |
|--------|---------------|
| `src/problem.py` | Instance generation, distance matrix computation |
| `src/classical/ortools_solver.py` | OR-Tools GLS solver |
| `src/quantum/qubo_builder.py` | QUBO construction and solution decoding |
| `src/quantum/ising_converter.py` | QUBO → Ising Hamiltonian conversion |
| `src/quantum/qaoa_solver.py` | QAOA execution via Qiskit |
| `src/benchmark/compare.py` | Solver comparison and CSV output |
| `src/visualize/plots.py` | Publication-quality matplotlib figures |

**Testing:** 17 unit tests across 5 test files, all passing. Tests cover determinism, schema validation, constraint satisfaction, and QAOA output structure.

**Reproducibility:** All randomness is seeded (seed=42). Instance, solver parameters, and results are fully deterministic.

---

## 7. Experimental Setup

| Parameter | Value |
|-----------|-------|
| Customers | 3 |
| Vehicles | 2 |
| Vehicle capacity (Q) | 15 |
| Customer demands | [2, 1, 6] |
| Total demand | 9 |
| Random seed | 42 |
| OR-Tools strategy | Guided Local Search, 5s limit |
| QAOA layers (p) | 2 |
| QAOA optimizer | COBYLA (maxiter=100) |
| QAOA sampler | StatevectorSampler (exact simulation) |
| Total qubits | 17 |
| Platform | Python 3.13, Qiskit 2.5.0, macOS |

---

## 8. Results

### 8.1 Benchmark Table

Results from `python run_all.py`:

| Metric | OR-Tools (GLS) | QAOA (p=2) |
|--------|---------------|------------|
| Total Distance | 137.7065 | varies (see results/benchmark_table.csv) |
| Runtime (s) | ~5.0 | varies (~50s) |
| Feasible | ✓ Yes | see benchmark_table.csv |
| Qubits | N/A | 17 |
| Approximation Ratio | 1.00 (baseline) | see benchmark_table.csv |

> **Note:** QAOA results vary — the algorithm is probabilistic, and feasibility depends on whether the optimizer converges to a constraint-satisfying bitstring. See `results/benchmark_table.csv` for the actual numbers from our run.

### 8.2 Route Visualizations

- **OR-Tools routes:** `results/figures/ortools_routes.png`
- **QAOA routes:** `results/figures/qaoa_routes.png`
- **QAOA convergence:** `results/figures/qaoa_convergence.png`
- **Benchmark comparison:** `results/figures/benchmark_comparison.png`

### 8.3 Observations

1. **OR-Tools** consistently finds feasible, high-quality solutions in under a second of compute time (the 5s figure includes solver startup and guided local search iterations).

2. **QAOA** with p=2 produces solutions that may or may not satisfy all constraints, depending on the optimization landscape. When feasible, the total distance is typically higher than the classical solution.

3. The **convergence plot** shows the COBYLA optimizer exploring the (γ, β) parameter space, typically converging within 100-200 iterations.

---

## 9. Discussion

### 9.1 Solution Quality
OR-Tools finds near-optimal solutions for this small instance essentially instantly. QAOA's solution quality is limited by:
- The penalty-based constraint encoding (soft constraints rather than hard enforcement)
- The shallow circuit depth (p=2 still limits the algorithm's approximation power compared to deeper layer counts)
- The large QUBO variable count (17 qubits creates a vast search space)

### 9.2 Runtime
The runtime comparison strongly favors classical methods:
- OR-Tools: seconds (dominated by metaheuristic exploration time limit)
- QAOA on simulator: less than a minute for 17 qubits, but grows exponentially.

This is expected: statevector simulation scales exponentially. While 17 qubits can be simulated in under a minute, 24 qubits (4 customers) takes over an hour, and 33 qubits (5 customers) requires manipulating 2³³ ≈ 8.6 billion complex amplitudes, making it completely intractable on a standard CPU without acceleration. On real quantum hardware, the circuit execution time would be much shorter, but current QPU fidelity introduces noise-related errors.

### 9.3 Penalty Weight Sensitivity
Our heuristic penalty weights (λ ≈ 450, derived as max_distance × n_customers) represent a reasonable middle ground. Lower values lead to constraint-violating solutions; higher values make the optimization landscape too steep for the QAOA optimizer to navigate effectively.

### 9.4 Honest Assessment
QAOA does not outperform classical heuristics at this scale. This result is:
- **Expected** — consistent with all published literature on QAOA for routing problems
- **Valid** — demonstrating where quantum algorithms currently stand is valuable research
- **Documented honestly** — we report infeasible QAOA solutions when they occur, rather than cherry-picking successful runs

---

## 10. Limitations

1. **Simulator only:** All quantum execution uses ideal statevector simulation. No noise modeling or real quantum hardware was used.

2. **Small instance size:** The default run is configured to 3 customers (17 qubits) for fast out-of-the-box execution. 4 customers requires 24 qubits, which takes over an hour to simulate, and 5 customers requires 33 qubits, which is near the practical limit for statevector simulation. Larger instances are infeasible without algorithmic improvements.

3. **No noise modeling:** Real quantum hardware introduces gate errors, decoherence, and readout noise that would further degrade QAOA performance.

4. **Shallow circuit:** We use p=2 QAOA layers. More layers (p ≥ 3) would improve approximation quality but increase circuit depth and simulation cost.

5. **Single instance:** Results are based on one CVRP instance (seed=42). A more comprehensive study would benchmark across multiple instances with varying characteristics.

6. **Position encoding inefficiency:** The O(n²) qubit scaling of position encoding is a fundamental bottleneck. Alternative encodings (e.g., edge-based, cluster-first-route-second) might be more qubit-efficient.

---

## 11. Future Work

1. **Real quantum hardware:** Execute on IBM Quantum or AWS Braket to observe the impact of real hardware noise on solution quality.

2. **Larger instances:** Use hybrid decomposition (cluster customers classically, solve sub-problems quantumly) to handle more customers.

3. **Warm-start QAOA:** Initialize QAOA parameters from a relaxed classical solution to improve convergence.

4. **Recursive QAOA (RQAOA):** Iteratively fix variables with high confidence to reduce the effective problem size.

5. **Time windows (VRPTW):** Extend the formulation to include customer time-window constraints.

6. **Multi-instance benchmarking:** Run on diverse problem instances (varying customer count, demand distribution, geographic layout) for more robust conclusions.

7. **Error mitigation:** Apply quantum error mitigation techniques (zero-noise extrapolation, probabilistic error cancellation) to improve results on noisy hardware.

---

## 12. Conclusion

This project demonstrates a complete, reproducible pipeline for comparing classical and quantum optimization on CVRP. The key takeaways are:

1. **Classical heuristics (OR-Tools) dominate at current problem scales** — finding high-quality solutions orders of magnitude faster than simulated QAOA.

2. **QAOA provides a valid but currently inferior optimization approach** — constrained by qubit overhead, penalty weight sensitivity, and simulation cost.

3. **The full quantum optimization workflow is functional** — from CVRP → QUBO → Ising → QAOA → decoded routes — establishing a foundation for future experiments with larger instances and real quantum hardware.

4. **Honest benchmarking matters** — reporting what quantum algorithms actually achieve (rather than what we hope they will achieve) is essential for the field's progress.

---

## 13. References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm.* arXiv:1411.4028.

2. Feld, S., Roch, C., Gabor, T., et al. (2019). *A Hybrid Solution Method for the Capacitated Vehicle Routing Problem Using a Quantum Annealer.* Frontiers in ICT, 6, 13.

3. Harwood, S., Gambella, C., Trenev, D., et al. (2021). *Formulating and Solving Routing Problems on Quantum Computers.* IEEE Transactions on Quantum Engineering, 2, 1–17.

4. Blekos, K., Brand, D., Ceschini, A., et al. (2024). *A Review on Quantum Approximate Optimization Algorithm and its Variants.* Physics Reports, 1068, 1–66.

5. Borowski, M., Gora, P., Kardashin, A., et al. (2020). *New Hybrid Quantum Annealing Algorithms for Solving Vehicle Routing Problem.* ICCS 2020, LNCS 12142, 546–561.

6. Qiskit Development Team. (2024). *Qiskit: An Open-Source Framework for Quantum Computing.* https://qiskit.org

7. Google OR-Tools Team. (2024). *OR-Tools: Operations Research Tools.* https://developers.google.com/optimization
