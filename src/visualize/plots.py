"""Generate report-quality figures for routes, convergence, and benchmarks."""

from __future__ import annotations

from typing import Any

import pandas as pd


def plot_routes(
    instance: dict[str, Any],
    routes: list[list[int]],
    title: str,
    save_path: str,
) -> None:
    """Plot vehicle routes on a network graph with depot highlighted."""
    raise NotImplementedError()


def plot_convergence(
    convergence_history: list[float],
    save_path: str,
) -> None:
    """Plot QAOA cost value vs. optimizer iteration."""
    raise NotImplementedError()


def plot_benchmark_comparison(
    benchmark_df: pd.DataFrame,
    save_path: str,
) -> None:
    """Bar charts comparing runtime and distance across solvers."""
    raise NotImplementedError()
