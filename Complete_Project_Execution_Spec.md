# Complete Project Execution Spec — Quantum Vehicle Routing Project

## How to use this document
This is the **master build specification**. It covers everything: the theory content that must be documented, the exact mathematical formulation, and the full implementation for every module. Execute it in the order given — later modules depend on earlier ones. Do not skip the math sections even though they look like "documentation, not code" — the code implements exactly what's derived here, so getting the derivation right first prevents rebuilding the QUBO/Ising logic later.

Where this spec says "implement," write real, tested, modular code (no 500-line dumps — one function/class at a time, with docstrings and error handling). Where it says "document," write into the corresponding file under `docs/`.

---

## PART A — THEORY FOUNDATIONS
*(Target file: `docs/math_derivation.md`, plus inline docstrings referencing these concepts)*

Document each of the following with: **intuition → math → why it matters here**. Keep each section tight (this is a 2–4 week project, not a textbook) — a few paragraphs and the key equations per concept, not a full chapter.

### A1. Graph Theory Basics
- Represent the CVRP instance as a complete weighted graph G = (V, E): V = {depot, customer₁, ..., customerₙ}, edge weights = Euclidean distances
- Explain why CVRP is a graph problem: routes = paths/cycles through this graph

### A2. Vehicle Routing Problem & NP-Hardness
- Define CVRP formally: partition customers into vehicle routes starting/ending at depot, minimizing total distance, subject to each vehicle's total demand ≤ capacity
- Explain NP-hardness informally: CVRP generalizes TSP (itself NP-hard); solution space grows combinatorially with customer count — this is *why* both classical heuristics and quantum optimization are relevant approaches (exact solvers don't scale)

### A3. Optimization Theory & Operations Research Basics
- Objective function vs. constraints vs. feasible region
- Combinatorial optimization vs. continuous optimization — CVRP is combinatorial (discrete route/assignment decisions)

### A4. Classical Optimization Approaches
- MILP: exact method, models the problem with integer/binary decision variables and linear constraints, guarantees optimality but scales poorly
- OR-Tools' routing solver: metaheuristic-based (uses local search + guided local search), fast and scalable but not guaranteed optimal

### A5. Quantum Computing Basics
- Qubit, superposition, entanglement, measurement — one paragraph each, framed around "why this lets us represent many candidate routes simultaneously"
- Quantum circuits as the mechanism for manipulating qubit states before measurement

### A6. QUBO (Quadratic Unconstrained Binary Optimization)
- General form: minimize xᵀQx over binary vector x
- Why QUBO is the "bridge" format: any combinatorial problem with binary decision variables and constraints can be rewritten as QUBO by moving constraints into the objective as penalty terms

### A7. Ising Model & Hamiltonian
- Mapping from QUBO (binary 0/1 variables) to Ising spins (±1 variables) via xᵢ = (1 + sᵢ)/2
- The Hamiltonian H(s) as the "energy function" whose minimum corresponds to the optimal solution — this is what QAOA is built to find

### A8. QAOA (Quantum Approximate Optimization Algorithm)
- Structure: alternating problem Hamiltonian (encodes the cost function) and mixer Hamiltonian (drives exploration), parameterized by angles (β, γ), repeated across p layers
- Classical-quantum hybrid loop: classical optimizer tunes (β, γ) based on measured expectation value of the cost Hamiltonian
- Why more layers (p) generally improve solution quality but increase circuit depth and simulation cost — this is a real design tradeoff to document, not hand-wave

---

## PART B — MATHEMATICAL FORMULATION
*(Target file: `docs/math_derivation.md`, second half — the actual derivation for THIS problem instance)*

### B1. Problem Instance Definition
- 1 depot (node 0), n customer nodes (n = 5, extendable to 6), K = 2 vehicles, capacity Q per vehicle
- Distance matrix `d[i][j]` = Euclidean distance between node i and node j
- Demand vector `q[i]` for each customer i

### B2. Classical Decision Variables
- Binary variable `x[i][j][k]` = 1 if vehicle k travels directly from node i to node j, else 0
- (For QUBO simplification, may collapse the vehicle index if using a single aggregated route-assignment encoding — derive and justify whichever encoding is used, don't just state it)

### B3. Objective Function
```
minimize  Σᵢ Σⱼ Σₖ d[i][j] * x[i][j][k]
```
Derive this explicitly from the variable definitions above — show the summation logic, don't just present the formula.

### B4. Constraints (classical form)
1. Each customer visited exactly once: `Σᵢ Σₖ x[i][j][k] = 1` for all customers j
2. Vehicle capacity: `Σᵢ q[i] * (visited by vehicle k) ≤ Q` for all k
3. Flow conservation: vehicles that enter a node must leave it
4. Subtour elimination (standard MTZ or flow-based constraints) — explain why this is necessary (without it, solutions can form disconnected loops not touching the depot)

### B5. QUBO Formulation
- Convert each constraint into a penalty term: `P * (constraint_violation)²`, added to the objective
- Full QUBO objective:
```
minimize  [original distance objective] + λ₁*(coverage penalty) + λ₂*(capacity penalty) + λ₃*(subtour penalty)
```
- Explicitly derive at least the coverage penalty term algebraically (expand the square, show it reduces to linear + quadratic binary terms — this is the part graders/reviewers will actually check)
- Discuss penalty weight (λ) selection: too small → infeasible solutions accepted; too large → objective landscape becomes hard for QAOA to optimize. Document the actual values chosen and why (empirical tuning is acceptable, but must be documented, not silently hardcoded)

### B6. Ising Mapping
- Apply xᵢ = (1 + sᵢ)/2 substitution to the full QUBO expression
- Derive the resulting Hamiltonian H(s) = Σ hᵢsᵢ + Σ Jᵢⱼsᵢsⱼ + constant
- This H is what gets encoded into the QAOA problem Hamiltonian circuit

### B7. Complexity Analysis
- State qubit count as a function of n (customers) and K (vehicles) for the chosen encoding
- Confirm the chosen instance size (5–6 customers) keeps total qubits in the ~15–25 range, and explain why that's the practical ceiling for Aer statevector simulation in this timeframe

---

## PART C — IMPLEMENTATION

### C1. `src/problem.py`
**Responsibility:** instance generation and shared data structures.
- `generate_instance(seed: int, num_customers: int, num_vehicles: int, capacity: int) -> dict`: generates random depot + customer coordinates and demands, deterministic via seed, saves to `data/instance_seed42.json`
- `load_instance(path: str) -> dict`: loads instance from JSON
- `compute_distance_matrix(instance: dict) -> np.ndarray`: Euclidean distance matrix including depot as node 0
- Unit tests: verify determinism (same seed → same instance), verify distance matrix symmetry and zero diagonal

### C2. `src/classical/ortools_solver.py`
**Responsibility:** solve the CVRP instance using OR-Tools routing library.
- `solve_cvrp_ortools(instance: dict, distance_matrix: np.ndarray, time_limit_seconds: int = 30) -> dict`
  - Returns: `{routes: [[node_ids...], ...], total_distance: float, runtime_seconds: float, feasible: bool}`
- Use OR-Tools' `RoutingIndexManager` + `RoutingModel`, set the capacity dimension, use guided local search metaheuristic
- Error handling: raise a clear exception if no feasible solution is found within the time limit
- Unit test: verify returned routes respect capacity and visit every customer exactly once

### C3. `src/classical/milp_solver.py` (stretch goal — implement only if Week 2 timeline allows)
**Responsibility:** exact MILP solve for small instances, used as an optimality cross-check against OR-Tools.
- `solve_cvrp_milp(instance: dict, distance_matrix: np.ndarray, time_limit_seconds: int = 60) -> dict`
- Use PuLP or python-mip, encode constraints from Part B4 directly
- Same return schema as C2 for easy comparison

### C4. `src/quantum/qubo_builder.py`
**Responsibility:** build the QUBO matrix from the CVRP instance, implementing the derivation in Part B5.
- `build_cvrp_qubo(instance: dict, distance_matrix: np.ndarray, penalty_weights: dict) -> QuadraticProgram`
  - Use `qiskit_optimization.QuadraticProgram`, add binary variables, objective terms, and constraints, then convert to QUBO via `QuadraticProgramToQubo`
- `decode_qubo_solution(bitstring: str, instance: dict) -> dict`: converts a measured bitstring back into vehicle routes
- Unit test: build QUBO for a toy 3-node instance, verify the matrix dimensions and that a known-good solution evaluates to the expected low energy

### C5. `src/quantum/ising_converter.py`
**Responsibility:** convert the QUBO to Ising form (implements Part B6), mostly a thin wrapper if using `qiskit_optimization`'s built-in conversion, but must **document what the conversion does**, not just call it silently.
- `qubo_to_ising(qp: QuadraticProgram) -> tuple` returning (Ising Hamiltonian operator, offset)

### C6. `src/quantum/qaoa_solver.py`
**Responsibility:** run QAOA on the Ising Hamiltonian using Qiskit Aer simulator.
- `solve_cvrp_qaoa(qubo: QuadraticProgram, p_layers: int = 2, optimizer: str = "COBYLA", shots: int = 1024, seed: int = 42) -> dict`
  - Returns: `{best_bitstring: str, routes: [[...]], total_distance: float, runtime_seconds: float, feasible: bool, convergence_history: list}`
- Use `qiskit_optimization.algorithms.MinimumEigenOptimizer` with `QAOA` from `qiskit_algorithms`, backend = `AerSimulator`
- Capture the optimizer's convergence history (cost value per iteration) for the convergence plot in Phase 8/C8
- Explicitly handle infeasible/invalid decoded solutions (some measured bitstrings will violate constraints — document how these are filtered or penalized, don't just ignore the issue)
- Unit test: run on the toy 3-node instance from C4, verify it returns a feasible route at least most of the time across repeated runs (QAOA is probabilistic — the test should account for this, e.g., run N times and check success rate ≥ threshold)

### C7. `src/benchmark/compare.py`
**Responsibility:** run classical and quantum solvers on the same instance, compute comparison metrics.
- `run_benchmark(instance: dict) -> pd.DataFrame` with columns: `method, total_distance, runtime_seconds, approximation_ratio, feasible, qubit_count (quantum only), circuit_depth (quantum only)`
- `approximation_ratio` = quantum_distance / classical_optimal_distance (compute only when both are feasible)
- Save result to `results/benchmark_table.csv`
- **Never fabricate results** — if QAOA fails to find a feasible solution on a given run, record that honestly (feasible=False), don't substitute a plausible-looking number

### C8. `src/visualize/plots.py`
**Responsibility:** generate all report-quality figures.
- `plot_routes(instance: dict, routes: list, title: str, save_path: str)`: network graph, depot highlighted, each vehicle route in a different color
- `plot_convergence(convergence_history: list, save_path: str)`: QAOA cost value vs. iteration
- `plot_benchmark_comparison(benchmark_df: pd.DataFrame, save_path: str)`: bar charts for runtime and distance, classical vs. quantum
- Use matplotlib with clean, labeled, presentation-quality styling (titles, axis labels, legend) — these figures go directly into the report

### C9. Testing (`tests/`)
- Every module above gets a corresponding test file (already scaffolded in the repo structure spec)
- Use pytest fixtures for the shared toy instance so tests aren't duplicating setup code
- Target: all core-path modules (C1, C2, C4, C6, C7) have passing tests before moving to documentation phase

---

## PART D — DOCUMENTATION
*(Target files under `docs/`)*

### D1. `docs/literature_review.md`
- Summarize 3–5 relevant papers on QAOA for VRP/TSP (find via search — do not fabricate citations)
- For each: objective, method, results, limitations
- Close with: how this project's scope differs (smaller instance, educational/comparative focus vs. novel algorithmic contribution)

### D2. `docs/report.md`
Full report using this structure — write substantively, not just headers:
1. Abstract
2. Introduction (motivation: why compare classical vs quantum for VRP)
3. Literature Review (link/summarize D1)
4. Theory (condensed from Part A)
5. Methodology (condensed from Part B)
6. Implementation (summary of Part C modules, not full code dump — reference the repo)
7. Experimental Setup (instance parameters, hardware/simulator specs, hyperparameters used)
8. Results (benchmark table + figures from C7/C8)
9. Discussion (interpret the approximation ratio, runtime tradeoffs — be honest if quantum underperforms classical, that's an expected and valid research finding at this scale)
10. Limitations (simulator-only, small instance size, no real quantum hardware noise modeled)
11. Future Work (larger instances, real QPU execution, VRPTW extension)
12. Conclusion
13. References (from D1)

### D3. `README.md` (finalize, building on the scaffolded skeleton)
- Fill in Overview, Problem Instance, Usage (how to run each solver + benchmark), Results (summary table + link to figures), License

---

## PART E — EXECUTION ORDER (for the coding assistant)

Work strictly in this order; do not jump ahead:

1. Part A + B documentation (math first — code implements the math, not the other way around)
2. C1 (`problem.py`) + its tests
3. C2 (`ortools_solver.py`) + its tests
4. C4 (`qubo_builder.py`) + its tests
5. C5 (`ising_converter.py`)
6. C6 (`qaoa_solver.py`) + its tests
7. C7 (`compare.py`) — run the actual benchmark, save real results
8. C8 (`plots.py`) — generate real figures from the real results in step 7
9. D1, D2, D3 — write documentation referencing the actual numbers/figures produced, never placeholder numbers
10. C3 (MILP) only if time remains
11. Final review: rerun everything from a clean clone to confirm reproducibility end-to-end

## PART F — HARD RULES (non-negotiable)

- Never generate benchmark numbers or figures that weren't actually produced by running the code
- Every module must have tests before being marked "done" in the roadmap
- No single file/function should be a monolithic dump — keep functions focused and under roughly 50 lines where reasonable
- All randomness (instance generation, QAOA optimizer, shot sampling) must be seeded for reproducibility
- If QAOA repeatedly fails to find feasible solutions even after penalty tuning, document that honestly as a limitation/finding — do not hide it or silently swap in a fabricated success case
