"""Generate report-quality figures for routes, convergence, and benchmarks.

All plots use matplotlib with clean, labeled, presentation-quality styling.
Figures are saved to ``results/figures/`` and are directly embeddable in
``docs/report.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for script/CI use
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd


# Consistent styling
COLORS = list(mcolors.TABLEAU_COLORS.values())
plt.rcParams.update({
    "figure.figsize": (10, 7),
    "figure.dpi": 150,
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.2,
})


def plot_routes(
    instance: dict[str, Any],
    routes: list[list[int]],
    title: str,
    save_path: str,
) -> None:
    """Plot vehicle routes on a 2-D scatter with depot highlighted.

    Each vehicle route is drawn in a distinct colour.  The depot is marked
    as a large red square, customers as blue circles with demand labels.

    Parameters
    ----------
    instance : dict
        CVRP instance (depot, customers).
    routes : list[list[int]]
        List of routes, each a list of node IDs (0 = depot).
    title : str
        Plot title.
    save_path : str
        File path to save the figure (PNG).
    """
    fig, ax = plt.subplots()

    depot = instance["depot"]
    customers = {c["id"]: c for c in instance["customers"]}

    # Plot depot
    ax.plot(depot["x"], depot["y"], "rs", markersize=14, label="Depot", zorder=5)
    ax.annotate("Depot", (depot["x"], depot["y"]),
                textcoords="offset points", xytext=(8, 8), fontweight="bold")

    # Plot customers
    for cid, c in customers.items():
        ax.plot(c["x"], c["y"], "bo", markersize=8, zorder=4)
        ax.annotate(f"C{cid} (d={c['demand']})", (c["x"], c["y"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=9)

    # Plot routes
    def get_coords(node_id: int) -> tuple[float, float]:
        if node_id == 0:
            return depot["x"], depot["y"]
        c = customers[node_id]
        return c["x"], c["y"]

    for idx, route in enumerate(routes):
        color = COLORS[idx % len(COLORS)]
        xs = [get_coords(n)[0] for n in route]
        ys = [get_coords(n)[1] for n in route]
        ax.plot(xs, ys, "-o", color=color, linewidth=2, markersize=5,
                label=f"Vehicle {idx + 1}", alpha=0.8)
        # Draw arrows for direction
        for i in range(len(route) - 1):
            ax.annotate("", xy=get_coords(route[i + 1]),
                        xytext=get_coords(route[i]),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

    ax.set_title(title)
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)


def plot_convergence(
    convergence_history: list[float],
    save_path: str,
) -> None:
    """Plot QAOA cost value vs. optimizer iteration.

    Parameters
    ----------
    convergence_history : list[float]
        Cost value at each classical optimizer iteration.
    save_path : str
        File path to save the figure.
    """
    fig, ax = plt.subplots()

    iterations = list(range(1, len(convergence_history) + 1))
    ax.plot(iterations, convergence_history, "b-o", markersize=3, linewidth=1.5)
    ax.set_title("QAOA Convergence")
    ax.set_xlabel("Optimizer Iteration")
    ax.set_ylabel("Cost Function Value")
    ax.grid(True, alpha=0.3)

    # Mark minimum
    if convergence_history:
        min_val = min(convergence_history)
        min_idx = convergence_history.index(min_val) + 1
        ax.axhline(y=min_val, color="r", linestyle="--", alpha=0.5,
                    label=f"Min = {min_val:.2f} (iter {min_idx})")
        ax.legend()

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)


def plot_benchmark_comparison(
    benchmark_df: pd.DataFrame,
    save_path: str,
) -> None:
    """Bar charts comparing runtime and total distance across solvers.

    Parameters
    ----------
    benchmark_df : pd.DataFrame
        DataFrame from ``run_benchmark()`` with columns: method,
        total_distance, runtime_seconds, feasible.
    save_path : str
        File path to save the figure.
    """
    # Filter to feasible results for distance comparison
    feasible_df = benchmark_df[benchmark_df["feasible"] == True].copy()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Distance comparison ---
    ax1 = axes[0]
    if not feasible_df.empty:
        methods = feasible_df["method"].tolist()
        distances = feasible_df["total_distance"].tolist()
        bars1 = ax1.bar(methods, distances, color=[COLORS[i] for i in range(len(methods))],
                        edgecolor="black", linewidth=0.5)
        for bar, dist in zip(bars1, distances):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f"{dist:.1f}", ha="center", va="bottom", fontsize=10)
    ax1.set_title("Total Route Distance")
    ax1.set_ylabel("Distance")
    ax1.grid(axis="y", alpha=0.3)

    # --- Runtime comparison ---
    ax2 = axes[1]
    all_methods = benchmark_df["method"].tolist()
    runtimes = benchmark_df["runtime_seconds"].fillna(0).tolist()
    bars2 = ax2.bar(all_methods, runtimes,
                    color=[COLORS[i] for i in range(len(all_methods))],
                    edgecolor="black", linewidth=0.5)
    for bar, rt in zip(bars2, runtimes):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f"{rt:.2f}s", ha="center", va="bottom", fontsize=10)
    ax2.set_title("Solver Runtime")
    ax2.set_ylabel("Time (seconds)")
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Classical vs. Quantum Solver Comparison", fontsize=16, fontweight="bold")
    plt.tight_layout()

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
