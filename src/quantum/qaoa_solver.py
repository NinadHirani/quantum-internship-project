"""Run QAOA on the Ising Hamiltonian using Qiskit Aer simulator.

Implements the QAOA hybrid classical-quantum loop described in
``docs/math_derivation.md`` §A8.  Uses ``qiskit_optimization``'s
``MinimumEigenOptimizer`` with a QAOA-based minimum eigensolver on the
Aer statevector/qasm simulator.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA, SPSA
from qiskit_algorithms.utils import algorithm_globals
from qiskit.primitives import StatevectorSampler
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import SamplerV2 as AerSampler


class TranspiledStatevectorSampler(StatevectorSampler):
    """StatevectorSampler wrapper that transpiles circuits before running and caches results.

    Decomposes high-level instructions (like PauliEvolutionGate or QAOA ansatz)
    into standard basis gates ('u', 'cx') to prevent reference Statevector from
    converting them to large dense matrices using matrix exponentiation, which
    causes out-of-memory errors for larger qubit counts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transpile_cache = {}

    def run(self, pubs, *, shots=None):
        transpiled_pubs = []
        for pub in pubs:
            if isinstance(pub, tuple):
                circuit = pub[0]
                circ_id = id(circuit)
                if circ_id not in self._transpile_cache:
                    self._transpile_cache[circ_id] = transpile(
                        circuit, basis_gates=['u', 'cx'], optimization_level=1
                    )
                transpiled_circuit = self._transpile_cache[circ_id]
                new_pub = (transpiled_circuit,) + pub[1:]
                transpiled_pubs.append(new_pub)
            else:
                circ_id = id(pub)
                if circ_id not in self._transpile_cache:
                    self._transpile_cache[circ_id] = transpile(
                        pub, basis_gates=['u', 'cx'], optimization_level=1
                    )
                transpiled_circuit = self._transpile_cache[circ_id]
                transpiled_pubs.append(transpiled_circuit)
        return super().run(transpiled_pubs, shots=shots)


def solve_cvrp_qaoa(
    qubo: QuadraticProgram,
    p_layers: int = 2,
    optimizer: str = "COBYLA",
    max_iter: int = 100,
    shots: int = 1024,
    seed: int = 42,
) -> dict[str, Any]:
    """Solve the CVRP via QAOA on Aer simulator.

    Parameters
    ----------
    qubo : QuadraticProgram
        QUBO-form quadratic program (from ``build_cvrp_qubo``).
    p_layers : int
        Number of QAOA layers (p).  More layers → better approximation
        but deeper circuit.
    optimizer : str
        Classical optimizer name: ``"COBYLA"`` or ``"SPSA"``.
    max_iter : int
        Maximum number of classical optimization iterations.
    shots : int
        Number of measurement shots per circuit evaluation.
    seed : int
        Random seed for reproducibility across optimizer and simulator.

    Returns
    -------
    dict
        ``{best_bitstring, best_value, runtime_seconds,
        convergence_history, num_qubits, raw_result}``
    """
    # Seed reproducibility
    algorithm_globals.random_seed = seed

    # Convergence tracking
    convergence_history: list[float] = []

    def callback(eval_count: int, params: np.ndarray, value: float,
                 metadata: dict) -> None:
        convergence_history.append(value)
        print(f"    Iteration {eval_count:3d}: Energy/Value = {value:10.4f}", flush=True)

    # Select classical optimizer
    if optimizer.upper() == "COBYLA":
        opt = COBYLA(maxiter=max_iter)
    elif optimizer.upper() == "SPSA":
        opt = SPSA(maxiter=max_iter)

    else:
        raise ValueError(f"Unsupported optimizer: {optimizer}")

    # Build QAOA instance with sampler
    sampler = TranspiledStatevectorSampler(seed=seed)

    qaoa = QAOA(
        sampler=sampler,
        optimizer=opt,
        reps=p_layers,
        callback=callback,
    )

    # Wrap in MinimumEigenOptimizer for direct QUBO solving
    eigen_optimizer = MinimumEigenOptimizer(qaoa)

    # Solve with timing
    start_time = time.perf_counter()
    result = eigen_optimizer.solve(qubo)
    elapsed = time.perf_counter() - start_time

    # Extract bitstring
    best_bitstring = "".join(str(int(v)) for v in result.x)

    return {
        "best_bitstring": best_bitstring,
        "best_value": float(result.fval),
        "runtime_seconds": round(elapsed, 4),
        "convergence_history": convergence_history,
        "num_qubits": qubo.get_num_vars(),
        "raw_result": result,
    }
