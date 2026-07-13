# Mathematical Derivation — Quantum Vehicle Routing Project

This document contains the theoretical foundations (Part A) and the complete mathematical formulation (Part B) for the Capacitated Vehicle Routing Problem (CVRP) solved in this project. The code in `src/` implements exactly what is derived here.

---

## Part A — Theory Foundations

### A1. Graph Theory Basics

A **graph** G = (V, E) consists of a set of vertices (nodes) V and edges E connecting pairs of vertices. In this project the CVRP instance is represented as a **complete weighted graph**:

- **Vertices:** V = {0, 1, 2, …, n} where node 0 is the depot and nodes 1–n are customers.
- **Edges:** Every pair of nodes is connected (complete graph), so |E| = n(n+1)/2.
- **Edge weights:** w(i, j) = Euclidean distance between node i and node j:

$$
d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}
$$

The distance matrix D is symmetric (d_ij = d_ji) with zero diagonal (d_ii = 0).

**Why CVRP is a graph problem:** A vehicle route is a path (or cycle) through this graph — it starts at the depot, visits a subset of customer nodes, and returns to the depot. The total route cost is the sum of edge weights along the path. The optimization task is to find the set of routes (one per vehicle) that covers all customers at minimum total cost.

---

### A2. Vehicle Routing Problem & NP-Hardness

**Formal definition of CVRP:**

Given:
- A complete weighted graph G = (V, E) with depot node 0 and customer nodes {1, …, n}
- K vehicles, each with capacity Q
- Demand q_i for each customer i

Find a set of K routes, each starting and ending at the depot, such that:
1. Every customer is visited by exactly one vehicle
2. The total demand served by each vehicle does not exceed Q
3. The total distance across all routes is minimized

**NP-hardness:** CVRP generalizes the Traveling Salesman Problem (TSP). If we set K = 1 and Q = ∞, CVRP reduces to TSP, which is itself NP-hard. Since any TSP instance can be expressed as a CVRP instance, CVRP is at least as hard as TSP — and therefore NP-hard.

The practical consequence: the solution space grows combinatorially with customer count. For n customers and K vehicles, the number of possible route assignments is super-exponential. Exact methods become infeasible for large n, which is precisely why both classical heuristics (fast approximate solutions) and quantum optimization (exploiting superposition to explore many candidates simultaneously) are relevant approaches.

---

### A3. Optimization Theory & Operations Research Basics

An optimization problem has three components:

- **Objective function:** The quantity to minimize (or maximize) — here, total route distance.
- **Constraints:** Conditions that a valid solution must satisfy — here, capacity limits and full customer coverage.
- **Feasible region:** The set of all solutions satisfying all constraints.

Optimization problems are broadly classified as:

- **Continuous optimization:** Variables take real values (e.g., linear programming). Gradient-based methods are often effective.
- **Combinatorial (discrete) optimization:** Variables take discrete values (integers, binary). The feasible region is a finite but potentially enormous set. CVRP is combinatorial — the decision variables are binary (does vehicle k travel edge i→j?).

Combinatorial problems generally cannot be solved by gradient descent on the original variables. Instead, they require specialized approaches: exact methods (branch-and-bound, MILP), heuristics/metaheuristics (local search, genetic algorithms), or quantum-inspired methods (QAOA, quantum annealing).

---

### A4. Classical Optimization Approaches

Two classical approaches are used in this project:

**Mixed-Integer Linear Programming (MILP):**
- Models CVRP with binary/integer decision variables and linear constraints.
- Solvers (PuLP, Gurobi, CPLEX) use branch-and-bound with LP relaxations to systematically explore the solution space.
- **Guarantees optimality** — if the solver completes, the solution is provably optimal.
- **Scales poorly:** Worst-case exponential runtime. Practical for small-to-medium instances (tens of customers) but becomes intractable for large ones.

**OR-Tools Routing Solver (metaheuristic):**
- Google's OR-Tools library provides a specialized routing solver built on constraint programming.
- Uses heuristics for initial solution construction (e.g., cheapest arc, savings algorithm) followed by metaheuristic improvement via **Guided Local Search (GLS)**.
- GLS augments the objective function with penalties for frequently used edges, escaping local optima.
- **Fast and scalable** — can handle hundreds of customers in seconds.
- **Not guaranteed optimal** — returns the best solution found within a time limit, which may be suboptimal.

---

### A5. Quantum Computing Basics

**Qubit:** The fundamental unit of quantum information. Unlike a classical bit (0 or 1), a qubit exists in a **superposition** of |0⟩ and |1⟩:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
$$

where α and β are complex amplitudes with |α|² + |β|² = 1. Upon **measurement**, the qubit collapses to |0⟩ with probability |α|² or |1⟩ with probability |β|².

**Superposition** allows a register of n qubits to simultaneously represent all 2ⁿ possible binary strings. This is the key property exploited by quantum optimization — a system of n qubits can, in some sense, "explore" an exponentially large solution space in parallel.

**Entanglement** is a quantum correlation between qubits: measuring one qubit instantaneously constrains the possible outcomes of measuring another, even though neither had a definite value before measurement. Entanglement is essential for quantum algorithms to create correlations between decision variables that reflect the problem structure.

**Measurement** extracts classical information from qubits but destroys the superposition. A quantum algorithm must carefully structure the amplitudes so that measurement is likely to yield a good solution.

**Quantum circuits** are the mechanism for manipulating qubit states. A circuit is a sequence of quantum gates (unitary operations) applied to qubits, analogous to a classical logic circuit. The QAOA algorithm is implemented as a parameterized quantum circuit whose gate angles are tuned by a classical optimizer.

---

### A6. QUBO (Quadratic Unconstrained Binary Optimization)

**General form:** Given a binary vector x ∈ {0, 1}ⁿ and an n×n matrix Q:

$$
\text{minimize } f(x) = x^T Q x = \sum_{i} Q_{ii} x_i + \sum_{i < j} 2Q_{ij} x_i x_j
$$

The diagonal entries Q_ii encode linear terms (since x_i² = x_i for binary variables), and off-diagonal entries Q_ij encode quadratic interactions between pairs of variables.

**Why QUBO is the "bridge" format:** Any combinatorial optimization problem with binary decision variables can be reformulated as a QUBO by:

1. Expressing the objective function in terms of binary variables (gives the "original" quadratic terms).
2. Converting each constraint into a **penalty term** — a non-negative quadratic expression that equals zero when the constraint is satisfied and is positive when violated.
3. Adding penalty terms to the objective with large multipliers (penalty weights λ) to discourage constraint violations.

The resulting unconstrained problem can then be mapped to an Ising Hamiltonian for quantum optimization. QUBO is thus the standard intermediate representation between a constrained combinatorial problem and a quantum algorithm.

---

### A7. Ising Model & Hamiltonian

The **Ising model** uses spin variables s_i ∈ {−1, +1} instead of binary variables x_i ∈ {0, 1}. The mapping between them is:

$$
x_i = \frac{1 + s_i}{2} \quad \Leftrightarrow \quad s_i = 2x_i - 1
$$

Under this substitution, a QUBO objective f(x) = xᵀQx becomes a **Hamiltonian** (energy function):

$$
H(s) = \sum_{i} h_i s_i + \sum_{i < j} J_{ij} s_i s_j + \text{const}
$$

where h_i are the local fields (linear coefficients) and J_ij are the coupling strengths (quadratic coefficients), both derived from Q by substituting x_i = (1 + s_i)/2 and expanding.

**Why this matters:** The ground state (minimum energy configuration) of H corresponds to the optimal solution of the original QUBO. Quantum algorithms like QAOA are designed to prepare quantum states that approximate this ground state — the Hamiltonian H is encoded directly into the quantum circuit as the "problem Hamiltonian."

---

### A8. QAOA (Quantum Approximate Optimization Algorithm)

QAOA (Farhi, Goldstone, Gutmann, 2014) is a hybrid classical-quantum algorithm for approximate combinatorial optimization.

**Structure:** The QAOA circuit for p layers consists of:

1. **Initial state:** All qubits in uniform superposition |+⟩⊗ⁿ (apply Hadamard gates).
2. **Problem unitary:** U_C(γ) = exp(−iγH_C), where H_C is the problem Hamiltonian (encodes the cost function). This "imprints" the problem structure onto the quantum state — low-cost solutions receive favorable phase rotations.
3. **Mixer unitary:** U_M(β) = exp(−iβH_M), where H_M is typically Σ_i X_i (sum of Pauli-X operators). The mixer drives exploration by rotating amplitudes between computational basis states, preventing the algorithm from getting stuck.
4. **Repeat:** Alternate U_C(γ_k) and U_M(β_k) for k = 1, …, p, with distinct angle pairs per layer.
5. **Measure:** Sample from the final state to obtain a candidate bitstring solution.

**Hybrid loop:** The angles {γ_1, …, γ_p, β_1, …, β_p} are free parameters (2p total). A **classical optimizer** (e.g., COBYLA, Nelder-Mead) tunes these angles to minimize the expectation value ⟨ψ(γ,β)|H_C|ψ(γ,β)⟩. Each iteration:
1. Classical optimizer proposes new angles.
2. Quantum circuit is executed with those angles.
3. Multiple shots are measured to estimate the expected cost.
4. Classical optimizer updates angles based on the result.

**Layer tradeoff (p):** More layers generally improve solution quality because:
- At p = 1, QAOA can only explore a limited subspace.
- As p → ∞, QAOA can theoretically converge to the exact ground state.

However, increasing p has costs:
- **Circuit depth** grows linearly with p, increasing decoherence on real hardware.
- **Parameter space** grows (2p parameters), making the classical optimization harder.
- **Simulation cost** on classical computers grows significantly with p.

For this project (simulator-based, 15–25 qubits), p = 1–3 is the practical range.

---

## Part B — Mathematical Formulation for This CVRP Instance

### B1. Problem Instance Definition

- **Depot:** Node 0 at coordinates (x₀, y₀)
- **Customers:** Nodes 1, …, n where n = 5 (extendable to 6)
- **Vehicles:** K = 2
- **Vehicle capacity:** Q (uniform across vehicles)
- **Demand:** q_i for each customer i, where Σ q_i ≤ K × Q for feasibility
- **Distance matrix:** D ∈ ℝ^{(n+1)×(n+1)}, where d_{ij} = Euclidean distance between nodes i and j

The total number of nodes (including depot) is N = n + 1 = 6.

---

### B2. Classical Decision Variables

Define binary variables:

$$
x_{ijk} = \begin{cases} 1 & \text{if vehicle } k \text{ travels directly from node } i \text{ to node } j \\ 0 & \text{otherwise} \end{cases}
$$

for i, j ∈ {0, 1, …, n} and k ∈ {1, …, K}.

**Total variable count (full encoding):** N² × K = 6² × 2 = 72 binary variables.

**Simplified encoding for QUBO:** To reduce qubit count, we can use a position-based encoding. Define:

$$
y_{i,p} = \begin{cases} 1 & \text{if customer } i \text{ is visited at position } p \text{ in the route sequence} \\ 0 & \text{otherwise} \end{cases}
$$

where p ranges over all positions in all vehicle routes. For K vehicles each visiting at most n customers, there are n × K positions, but we can constrain this further based on instance knowledge.

For this project with n = 5 customers and K = 2 vehicles, we use a route-assignment + position encoding, yielding approximately n × (n + K) ≈ 15–25 binary variables depending on the exact formulation chosen during implementation.

---

### B3. Objective Function

Using the edge-based formulation:

$$
\text{minimize } Z = \sum_{k=1}^{K} \sum_{i=0}^{n} \sum_{j=0}^{n} d_{ij} \cdot x_{ijk}
$$

**Derivation:** Each vehicle k travels a route. The cost contribution of vehicle k is the sum of distances for every edge (i→j) it traverses. Summing over all vehicles gives the total cost.

Equivalently, Z counts each traversed edge exactly once because the constraint structure (below) ensures each x_{ijk} = 1 only for edges actually in vehicle k's route.

---

### B4. Constraints (Classical Form)

**Constraint 1 — Customer coverage (each customer visited exactly once):**

$$
\sum_{k=1}^{K} \sum_{i=0}^{n} x_{ijk} = 1 \quad \forall \, j \in \{1, \ldots, n\}
$$

Every customer j must have exactly one incoming edge from one vehicle.

**Constraint 2 — Vehicle capacity:**

$$
\sum_{j=1}^{n} q_j \cdot \left(\sum_{i=0}^{n} x_{ijk}\right) \leq Q \quad \forall \, k \in \{1, \ldots, K\}
$$

The total demand served by vehicle k (sum of demands of all customers it visits) must not exceed capacity Q.

**Constraint 3 — Flow conservation:**

$$
\sum_{i=0}^{n} x_{ijk} = \sum_{i=0}^{n} x_{jik} \quad \forall \, j \in \{0, \ldots, n\}, \, \forall \, k
$$

Every vehicle that enters a node must leave it. This ensures routes are connected paths, not isolated edges.

**Constraint 4 — Subtour elimination (MTZ formulation):**

Introduce auxiliary integer variables u_i ∈ {1, …, n} for each customer i. Then:

$$
u_i - u_j + n \cdot x_{ijk} \leq n - 1 \quad \forall \, i, j \in \{1, \ldots, n\}, \, i \neq j, \, \forall \, k
$$

**Why this is necessary:** Without subtour elimination, the optimizer can create disconnected loops (e.g., 1→2→1) that satisfy coverage and flow conservation but never touch the depot. MTZ constraints force a consistent ordering of customer visits that prevents any cycle not passing through the depot.

---

### B5. QUBO Formulation

Each constraint is converted into a **penalty term** added to the objective. A penalty term takes the form P × (violation)², which equals zero when the constraint is satisfied and is positive otherwise.

**Full QUBO objective:**

$$
\text{minimize } Q(x) = Z_{\text{distance}} + \lambda_1 P_{\text{coverage}} + \lambda_2 P_{\text{capacity}} + \lambda_3 P_{\text{subtour}}
$$

**Coverage penalty (algebraic derivation):**

For each customer j, the constraint is Σ_{i,k} x_{ijk} = 1. The penalty term is:

$$
P_{\text{coverage}} = \sum_{j=1}^{n} \left( \sum_{k=1}^{K} \sum_{i=0}^{n} x_{ijk} - 1 \right)^2
$$

Expanding the square for a single customer j (let S_j = Σ_{i,k} x_{ijk}):

$$
(S_j - 1)^2 = S_j^2 - 2S_j + 1
$$

Since x_{ijk} is binary (x² = x), expanding S_j²:

$$
S_j^2 = \left(\sum_a x_a\right)^2 = \sum_a x_a^2 + 2\sum_{a < b} x_a x_b = \sum_a x_a + 2\sum_{a < b} x_a x_b
$$

Therefore:

$$
(S_j - 1)^2 = \sum_a x_a + 2\sum_{a < b} x_a x_b - 2\sum_a x_a + 1 = -\sum_a x_a + 2\sum_{a < b} x_a x_b + 1
$$

This reduces to linear terms (−x_a) and quadratic terms (2x_a x_b), which fit directly into the QUBO matrix Q.

**Capacity penalty:**

$$
P_{\text{capacity}} = \sum_{k=1}^{K} \left( \max\left(0, \sum_{j=1}^{n} q_j \cdot v_{jk} - Q\right) \right)^2
$$

where v_{jk} = Σ_i x_{ijk} indicates whether vehicle k visits customer j. In practice, this inequality constraint is handled by introducing slack variables or by using a soft penalty with the squared violation.

**Subtour penalty:**

Subtour elimination is the most complex constraint to encode in QUBO form. The approach used in `qiskit_optimization`'s `QuadraticProgramToQubo` converter handles this by adding auxiliary variables and expanding the MTZ constraints into penalty terms.

**Penalty weight selection (λ values):**

- **Too small:** The optimizer may find solutions that violate constraints (infeasible) because the penalty cost is outweighed by the distance savings.
- **Too large:** The objective landscape becomes dominated by constraint penalties, making it hard for QAOA to distinguish between feasible solutions of different quality. The optimizer essentially ignores the distance objective.
- **Practical approach:** Start with λ values on the order of max(d_{ij}) × n (ensuring a single violation costs more than the worst-case feasible route), then tune empirically. The exact values used will be documented in the code and benchmark results.

---

### B6. Ising Mapping

Apply the substitution x_i = (1 + s_i)/2 to every binary variable in the QUBO objective Q(x).

For a single linear term:

$$
Q_{ii} x_i = Q_{ii} \cdot \frac{1 + s_i}{2} = \frac{Q_{ii}}{2} + \frac{Q_{ii}}{2} s_i
$$

For a quadratic term:

$$
Q_{ij} x_i x_j = Q_{ij} \cdot \frac{(1 + s_i)(1 + s_j)}{4} = \frac{Q_{ij}}{4}(1 + s_i + s_j + s_i s_j)
$$

Collecting all terms:

$$
H(s) = \sum_i h_i s_i + \sum_{i < j} J_{ij} s_i s_j + C
$$

where:

$$
h_i = \frac{Q_{ii}}{2} + \sum_{j \neq i} \frac{Q_{ij}}{4}
$$

$$
J_{ij} = \frac{Q_{ij}}{4}
$$

$$
C = \sum_i \frac{Q_{ii}}{2} + \sum_{i < j} \frac{Q_{ij}}{4} \quad \text{(constant offset, does not affect optimization)}
$$

This Hamiltonian H(s) is the operator encoded into the QAOA problem unitary U_C(γ) = exp(−iγH).

In the implementation, `qiskit_optimization`'s `to_ising()` method performs this conversion automatically, returning the SparsePauliOp representation of H and the offset C.

---

### B7. Complexity Analysis

**Qubit count as a function of instance size:**

The number of qubits equals the number of binary variables in the QUBO formulation:

- **Full edge encoding (x_{ijk}):** N² × K = (n+1)² × K qubits. For n = 5, K = 2: 72 qubits — **too many** for Aer statevector simulation (2⁷² amplitudes ≈ 10²¹).
- **Position-based encoding:** Approximately n × n variables for route sequencing + auxiliary variables. For n = 5: roughly 25–30 qubits.
- **Reduced encoding (route-assignment):** With careful variable elimination and problem-specific simplifications, 15–25 qubits is achievable for n = 5.

**Practical ceiling for Aer simulation:**

- **Statevector method:** Stores the full 2ⁿ-dimensional state vector. Memory = 2ⁿ × 16 bytes (complex128). At 25 qubits: 2²⁵ × 16 = 512 MB — feasible. At 30 qubits: 16 GB — tight. Beyond 32 qubits: impractical on standard hardware.
- **Shot-based (qasm) method:** Samples from the circuit, memory-efficient but requires many shots for good statistics.

**Conclusion:** The 5-customer instance with ~15–25 qubits is within the practical ceiling for statevector simulation. Extending to 6 customers may push toward the upper bound depending on the encoding efficiency. This is the primary reason the project uses a small instance — it's not a limitation of the formulation, but of the simulator's computational capacity.

---

*End of mathematical derivation. The code in `src/quantum/` implements exactly the formulations derived above.*
