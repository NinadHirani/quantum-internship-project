# Quantum Vehicle Routing Project

Comparative study of classical (OR-Tools) and quantum (QAOA/Qiskit) optimization for a Capacitated Vehicle Routing Problem (CVRP).

## Overview

This project implements a complete pipeline for solving CVRP using both classical and quantum approaches:

- **Classical:** Google OR-Tools with Guided Local Search (GLS) metaheuristic
- **Quantum:** Quantum Approximate Optimization Algorithm (QAOA) via Qiskit, running on a statevector simulator

The goal is to provide a clear, reproducible comparison that demonstrates the full quantum optimization workflow — from mathematical formulation through QUBO construction, Ising mapping, and QAOA execution — and honestly benchmarks quantum performance against classical baselines.

## Problem Instance

| Parameter | Value |
|-----------|-------|
| Customers | 4 (nodes 1–4) |
| Depot | Node 0 |
| Vehicles | 2 |
| Vehicle Capacity (Q) | 15 |
| Random Seed | 42 |

The instance is generated deterministically from `seed=42` and saved to `data/instance_seed42.json`.

## Project Structure

```
quantum-vehicle-routing/
├── data/                           # Generated CVRP instances (JSON)
├── docs/
│   ├── math_derivation.md          # Full theory + QUBO derivation
│   ├── literature_review.md        # Survey of 5 key papers
│   ├── report.md                   # Complete project report
│   └── repo_structure.md           # Repository structure docs
├── notebooks/
│   └── exploration.py              # Interactive walkthrough (Jupyter-compatible)
├── presentation/
│   └── slides.html                 # Self-contained HTML presentation
├── results/
│   ├── benchmark_table.csv         # Solver comparison metrics
│   └── figures/                    # All generated plots
├── src/
│   ├── problem.py                  # Instance generation & distance matrix
│   ├── classical/
│   │   ├── ortools_solver.py       # OR-Tools GLS solver
│   │   └── milp_solver.py          # MILP solver (stub — stretch goal)
│   ├── quantum/
│   │   ├── qubo_builder.py         # CVRP → QUBO (position encoding)
│   │   ├── ising_converter.py      # QUBO → Ising Hamiltonian
│   │   └── qaoa_solver.py          # QAOA via Qiskit
│   ├── benchmark/
│   │   └── compare.py              # Solver comparison & CSV output
│   └── visualize/
│       └── plots.py                # Publication-quality matplotlib figures
├── tests/                          # 17 unit tests (pytest)
├── run_all.py                      # One-command full pipeline execution
├── requirements.txt                # Python dependencies
└── README.md
```

## Installation

```bash
git clone <repo-url>
cd quantum-vehicle-routing
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Requirements:** Python 3.11+ | Qiskit 2.x | OR-Tools 9.x

## Usage

### Run the full pipeline (recommended)

```bash
python run_all.py
```

This generates the instance, runs both solvers, saves the benchmark CSV, and produces all figures. Results appear in `results/`.

**Options:**
```bash
python run_all.py --customers 4       # number of customers (default: 4)
python run_all.py --qaoa-layers 2     # QAOA circuit depth (default: 2)
python run_all.py --seed 42           # random seed (default: 42)
```

### Run individual solvers

```python
from src.problem import generate_instance, compute_distance_matrix
from src.classical.ortools_solver import solve_cvrp_ortools
from src.quantum.qubo_builder import build_cvrp_qubo
from src.quantum.qaoa_solver import solve_cvrp_qaoa

# Generate instance
instance = generate_instance(seed=42, num_customers=4, num_vehicles=2, capacity=15)
dist_matrix = compute_distance_matrix(instance)

# Classical solve
ortools_result = solve_cvrp_ortools(instance, dist_matrix)

# Quantum solve
qubo = build_cvrp_qubo(instance, dist_matrix, {"coverage": 300.0, "capacity": 300.0})
qaoa_result = solve_cvrp_qaoa(qubo, p_layers=2)
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Interactive exploration

Open `notebooks/exploration.py` in VS Code or Jupyter (supports `# %%` cell markers):

```bash
# In VS Code: just open the file — it supports interactive Python cells
# In Jupyter: jupyter notebook, then open the .py file
```

### View presentation

Open `presentation/slides.html` in any browser. Navigate with arrow keys.

## Results

See `results/benchmark_table.csv` for the full comparison. Key findings:

- **OR-Tools** finds near-optimal solutions instantly
- **QAOA** provides a valid but currently inferior approach — limited by qubit overhead, penalty sensitivity, and simulation cost
- This is consistent with published literature — quantum advantage for VRP is not expected at this problem scale

## Documentation

- [Mathematical Derivation](docs/math_derivation.md) — Full theory from graph basics through QUBO and Ising mapping
- [Literature Review](docs/literature_review.md) — Survey of 5 key papers on quantum VRP
- [Project Report](docs/report.md) — Complete 12-section report with results and discussion

## Tech Stack

| Component | Tool |
|-----------|------|
| Language | Python 3.13 |
| Quantum SDK | Qiskit 2.5, qiskit-optimization 0.7, qiskit-aer 0.17 |
| Classical Optimizer | Google OR-Tools 9.15 |
| Visualization | Matplotlib 3.11 |
| Testing | pytest 9.1 |

## License

MIT License — see [LICENSE](LICENSE).
