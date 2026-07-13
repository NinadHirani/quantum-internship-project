# Literature Review

This review surveys key contributions at the intersection of quantum computing and vehicle routing / combinatorial optimization, with a focus on QAOA-based approaches.

---

## 1. Farhi, Goldstone & Gutmann (2014) — "A Quantum Approximate Optimization Algorithm"

**Reference:** Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm.* arXiv:1411.4028.

**Objective:** Introduce a quantum algorithm (QAOA) for approximately solving combinatorial optimization problems on near-term quantum devices.

**Method:** The algorithm alternates between a problem Hamiltonian unitary (encoding the objective function) and a mixer Hamiltonian unitary (driving exploration), parameterized by angles (γ, β) repeated over *p* layers. A classical optimizer tunes these parameters in a hybrid quantum-classical loop to minimize the expectation value of the cost Hamiltonian.

**Results:** For the MAX-CUT problem on bounded-degree graphs, the authors proved that even p = 1 achieves a non-trivial approximation ratio. Performance improves with increasing p (more layers), approaching exact solutions as p → ∞.

**Limitations:** The theoretical guarantees are specific to MAX-CUT; extension to general constrained optimization problems (like VRP) requires encoding constraints as penalty terms, which can significantly expand the search landscape. Practical performance on near-term hardware remains limited by circuit depth and noise.

**Relevance to this project:** QAOA is the core quantum algorithm used in this project. We adopt the same hybrid loop architecture, applying it to a QUBO-formulated CVRP instance rather than MAX-CUT.

---

## 2. Feld, Gabor, Hähner et al. (2019) — "A Hybrid Solution Method for the Capacitated Vehicle Routing Problem Using a Quantum Annealer"

**Reference:** Feld, S., Roch, C., Gabor, T., Seidel, C., Neukart, F., Galter, I., Mauerer, W., & Linnhoff-Popien, C. (2019). *A Hybrid Solution Method for the Capacitated Vehicle Routing Problem Using a Quantum Annealer.* Frontiers in ICT, 6, 13.

**Objective:** Solve the CVRP using a quantum annealing approach (D-Wave) combined with classical pre- and post-processing.

**Method:** The authors decompose the CVRP into a clustering step (assigning customers to vehicles) solved on a quantum annealer, and a per-cluster TSP step solved classically. The clustering is formulated as a QUBO with customer-assignment binary variables and capacity/coverage constraints as penalty terms.

**Results:** Demonstrated feasibility of the hybrid approach on small instances (up to ~20 customers). Solution quality was competitive with classical heuristics for small problem sizes but degraded as instance size grew beyond the annealer's qubit capacity.

**Limitations:** The decomposition into clustering + TSP introduces suboptimality (the globally optimal CVRP solution might not correspond to the independently optimal clustering). Limited to D-Wave's qubit connectivity and noise profile. Problem instances beyond ~20 customers required extensive embedding overhead.

**Relevance to this project:** This work validates the QUBO-based formulation for CVRP that we also use. Our project differs in using QAOA (gate-based) rather than quantum annealing, and we solve the full problem in one QUBO rather than decomposing into clustering + TSP.

---

## 3. Harwood, Gambella, Trenev et al. (2021) — "Formulating and Solving Routing Problems on Quantum Computers"

**Reference:** Harwood, S., Gambella, C., Trenev, D., Simonetto, A., Bernal Neira, D., & Greber, D. (2021). *Formulating and Solving Routing Problems on Quantum Computers.* IEEE Transactions on Quantum Engineering, 2, 1–17.

**Objective:** Provide a systematic framework for encoding various vehicle routing problem variants (TSP, VRP, CVRP, VRPTW) as QUBO/Ising formulations suitable for quantum computers.

**Method:** The authors derive position-based and edge-based binary encodings for routing problems, systematically convert constraints (capacity, time windows, flow conservation) into quadratic penalty terms, and benchmark the resulting QUBOs on both quantum annealing (D-Wave) and gate-based (QAOA) platforms.

**Results:** For small instances (5–8 nodes), QAOA with sufficient layers could find near-optimal or optimal solutions. The position-based encoding (which we also use) was found to be more qubit-efficient than the edge-based encoding for small instances. Penalty weight tuning was identified as critical — poorly chosen weights led to constraint-violating solutions.

**Limitations:** Problem size is severely limited by qubit count: an n-customer VRP requires O(n²) qubits in position encoding, making instances beyond ~8 customers impractical on current simulators or QPUs. Circuit depth for QAOA grows rapidly, limiting performance on noisy hardware.

**Relevance to this project:** We adopt the same position-based encoding derived in this paper. Our implementation directly reflects their QUBO construction methodology. Our findings on penalty weight sensitivity and the 5-customer practical limit align with their observations.

---

## 4. Blekos, Brand, Ceschini et al. (2024) — "A Review on Quantum Approximate Optimization Algorithm and its Variants"

**Reference:** Blekos, K., Brand, D., Ceschini, A., et al. (2024). *A Review on Quantum Approximate Optimization Algorithm and its Variants.* Physics Reports, 1068, 1–66.

**Objective:** Provide a comprehensive survey of QAOA, including theoretical foundations, algorithmic variants, practical implementations, and performance benchmarks.

**Method:** The review covers: the original QAOA formulation, warm-start QAOA, Recursive QAOA (RQAOA), multi-angle QAOA (ma-QAOA), Grover-Mixer QAOA, and constraint-preserving mixer strategies. It compares QAOA performance against classical algorithms for various combinatorial problems.

**Results:** QAOA with p ≥ 3 layers generally outperforms random sampling but rarely surpasses state-of-the-art classical heuristics for practical problem sizes. Warm-start and recursive variants show promise for bridging this gap. The choice of classical optimizer (COBYLA, SPSA, L-BFGS-B) significantly affects convergence speed and solution quality.

**Limitations:** Theoretical quantum advantage for QAOA remains unproven for general optimization problems. On current noisy intermediate-scale quantum (NISQ) hardware, noise-induced errors typically outweigh any algorithmic advantage for circuits deeper than a few dozen gates.

**Relevance to this project:** This survey contextualizes our use of p = 2 QAOA with COBYLA optimizer. Our finding that QAOA produces solutions of comparable but not superior quality to classical heuristics is consistent with the broader literature reviewed here.

---

## 5. Borowski, Gora, Kardashin et al. (2020) — "New Hybrid Quantum Annealing Algorithms for the Vehicle Routing Problem"

**Reference:** Borowski, M., Gora, P., Kardashin, A., et al. (2020). *New Hybrid Quantum Annealing Algorithms for Solving Vehicle Routing Problem.* In: Computational Science – ICCS 2020, LNCS 12142, pp. 546–561.

**Objective:** Develop and benchmark hybrid quantum-classical algorithms for VRP variants, combining quantum annealing with classical optimization techniques.

**Method:** The authors propose two hybrid strategies: (1) a full QUBO approach where the entire VRP is encoded and solved on a quantum annealer, and (2) a hybrid decomposition where quantum annealing handles sub-problems (e.g., customer clustering) while classical algorithms solve the remaining TSP sub-problems.

**Results:** The full QUBO approach worked only for very small instances (≤ 6 customers) due to qubit limitations on D-Wave hardware. The hybrid decomposition approach scaled better but introduced suboptimality at decomposition boundaries.

**Limitations:** Both approaches require careful penalty weight calibration. The full QUBO encoding requires O(n²K) binary variables for n customers and K vehicles, limiting practicality. Results on real quantum hardware showed significant degradation compared to simulated performance.

**Relevance to this project:** Our 5-customer instance falls within the same size range shown to be tractable in this work. Our use of simulation (rather than real QPU) means we avoid the noise degradation they observed, making our results a best-case scenario for QAOA performance on CVRP.

---

## Summary: How This Project Differs

The works above establish that quantum optimization for vehicle routing is a nascent but active research area. This project makes the following distinct contributions:

1. **Educational and comparative focus:** Unlike the papers above, which primarily aim to advance algorithmic capability, this project's goal is a clear, reproducible comparison of classical vs. quantum approaches on a small, well-defined CVRP instance — making the tradeoffs visible and understandable.

2. **Gate-based QAOA on a simulator:** Most VRP quantum papers use quantum annealing (D-Wave). We use gate-based QAOA via Qiskit, providing insight into the gate-model perspective on VRP optimization.

3. **Honest reporting:** We document QAOA's actual performance — including cases where it fails to find feasible solutions — rather than cherry-picking successful runs. This aligns with the growing call for transparency in quantum computing benchmarks.

4. **Fully open and reproducible:** All code, data, and results are seeded and deterministic, enabling exact reproduction of every number and figure in this report.
