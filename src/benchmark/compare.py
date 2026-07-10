"""Run classical and quantum solvers on the same instance and compare metrics."""

from __future__ import annotations

from typing import Any

import pandas as pd


def run_benchmark(instance: dict[str, Any]) -> pd.DataFrame:
    """Execute all solvers on *instance* and return a comparison DataFrame.

    Columns: ``method, total_distance, runtime_seconds,
    approximation_ratio, feasible, qubit_count, circuit_depth``.

    Results are also saved to ``results/benchmark_table.csv``.
    """
    raise NotImplementedError()
