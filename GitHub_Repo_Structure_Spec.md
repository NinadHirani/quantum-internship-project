# AI Coding Assistant Instructions — Repository Scaffolding

## Purpose
This document specifies the exact GitHub repository structure for the **Quantum Vehicle Routing Project** (Comparative Study of Classical and Quantum Optimization for CVRP). Execute this as a scaffolding task: create every file and folder listed below, with the specified starter content where indicated. Do not implement algorithm logic yet — that is covered in a separate execution spec. This task is purely: **create the skeleton, correctly, so the project is buildable from day one.**

---

## 1. Root-Level Files

### `README.md`
Create with this section skeleton (leave content minimal/placeholder — filled in later):
```markdown
# Quantum Vehicle Routing Project

Comparative study of classical (OR-Tools/MILP) and quantum (QAOA/Qiskit) optimization
for a Capacitated Vehicle Routing Problem (CVRP).

## Overview
[TODO]

## Problem Instance
[TODO]

## Installation
\`\`\`bash
git clone <repo-url>
cd quantum-vrp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
\`\`\`

## Project Structure
[TODO - link to docs/repo_structure.md]

## Usage
[TODO]

## Results
[TODO]

## License
[TODO]
```

### `requirements.txt`
```
ortools>=9.9
qiskit>=1.0
qiskit-optimization>=0.6
qiskit-aer>=0.14
numpy>=1.26
scipy>=1.12
matplotlib>=3.8
networkx>=3.2
pandas>=2.2
pytest>=8.0
pulp>=2.8
```

### `.gitignore`
```
__pycache__/
*.pyc
venv/
.venv/
.env
.ipynb_checkpoints/
results/figures/*.png
*.egg-info/
.pytest_cache/
.DS_Store
```

### `LICENSE`
Use MIT License, standard template, current year, author name = repo owner.

### `.env.example`
```
# No API keys required for this project (fully local: OR-Tools + Qiskit Aer simulator)
# Placeholder for future extensions (e.g., IBM Quantum hardware access token)
# IBM_QUANTUM_TOKEN=
```

---

## 2. Directory Structure to Create

```
quantum-vrp/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── .env.example
│
├── data/
│   └── instance_seed42.json
│
├── src/
│   ├── __init__.py
│   ├── problem.py
│   ├── classical/
│   │   ├── __init__.py
│   │   ├── ortools_solver.py
│   │   └── milp_solver.py
│   ├── quantum/
│   │   ├── __init__.py
│   │   ├── qubo_builder.py
│   │   ├── ising_converter.py
│   │   └── qaoa_solver.py
│   ├── benchmark/
│   │   ├── __init__.py
│   │   └── compare.py
│   └── visualize/
│       ├── __init__.py
│       └── plots.py
│
├── notebooks/
│   └── exploration.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_problem.py
│   ├── test_qubo_builder.py
│   ├── test_ising_converter.py
│   ├── test_classical_solvers.py
│   └── test_qaoa_solver.py
│
├── results/
│   ├── benchmark_table.csv
│   └── figures/
│       └── .gitkeep
│
├── docs/
│   ├── repo_structure.md
│   ├── math_derivation.md
│   ├── literature_review.md
│   └── report.md
│
└── presentation/
    └── .gitkeep
```

---

## 3. File Creation Rules

1. **Every `__init__.py`** should be created empty except a one-line module docstring identifying the package (e.g., `"""Classical optimization solvers for CVRP."""`).
2. **Every `.py` module file** should be created with:
   - A module-level docstring stating its single responsibility (one sentence)
   - Necessary imports (based on the stack in `requirements.txt`)
   - Function/class stubs with type hints and docstrings, but **`raise NotImplementedError()` in the body** — no logic yet
3. **`data/instance_seed42.json`**: create with this exact placeholder structure (values will be finalized during implementation, but the schema must be set now):
```json
{
  "seed": 42,
  "depot": {"x": 0.0, "y": 0.0},
  "customers": [
    {"id": 1, "x": 0.0, "y": 0.0, "demand": 0},
    {"id": 2, "x": 0.0, "y": 0.0, "demand": 0},
    {"id": 3, "x": 0.0, "y": 0.0, "demand": 0},
    {"id": 4, "x": 0.0, "y": 0.0, "demand": 0},
    {"id": 5, "x": 0.0, "y": 0.0, "demand": 0}
  ],
  "num_vehicles": 2,
  "vehicle_capacity": 10
}
```
4. **`notebooks/exploration.ipynb`**: create as a valid empty Jupyter notebook (single empty code cell), used only for scratch work — never the source of truth for final code.
5. **`results/figures/.gitkeep`** and **`presentation/.gitkeep`**: empty files, just to preserve empty directories in git.
6. **`docs/repo_structure.md`**: paste a copy of the directory tree from Section 2 here, so the structure is self-documenting inside the repo itself.
7. Leave `docs/math_derivation.md`, `docs/literature_review.md`, and `docs/report.md` as files containing only a top-level heading and `> Content pending — see project execution spec.` — these get filled in during the theory and documentation phases, not during scaffolding.

---

## 4. Git Initialization Commands

After scaffolding, run:
```bash
git init
git add .
git commit -m "Initial repository scaffold: folder structure, config, empty modules"
```

Do **not** push to a remote yet — that happens after the owner reviews the scaffold.

---

## 5. Completion Checklist

- [ ] All directories created exactly as in Section 2
- [ ] All files created with correct placeholder/stub content
- [ ] `pip install -r requirements.txt` succeeds in a clean virtual environment
- [ ] `pytest tests/` runs without import errors (tests will fail/skip since logic isn't implemented — that's expected)
- [ ] Repo committed locally with the initial scaffold commit
- [ ] Report back: confirm structure created, flag any package version conflicts encountered during `pip install`
