# Repository Structure

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
