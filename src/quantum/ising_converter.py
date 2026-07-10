"""Convert QUBO to Ising Hamiltonian (implements Part B6 derivation)."""

from __future__ import annotations

from qiskit_optimization import QuadraticProgram


def qubo_to_ising(
    qp: QuadraticProgram,
) -> tuple:
    """Convert a QuadraticProgram (QUBO) to its Ising Hamiltonian form.

    Returns
    -------
    tuple
        ``(ising_hamiltonian, offset)`` where the Hamiltonian is a
        ``SparsePauliOp`` and offset is the constant energy shift.
    """
    raise NotImplementedError()
