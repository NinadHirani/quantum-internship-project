"""Convert QUBO to Ising Hamiltonian.

Implements Part B6 of ``docs/math_derivation.md``.

The transformation applies the substitution  xᵢ = (1 + sᵢ)/2  to every
binary variable in the QUBO objective, yielding the Ising Hamiltonian:

    H(s) = Σᵢ hᵢ sᵢ  +  Σᵢ<ⱼ Jᵢⱼ sᵢ sⱼ  +  C

where:
  • hᵢ  are local fields (linear coefficients)
  • Jᵢⱼ are coupling strengths (quadratic coefficients)
  • C   is a constant energy offset (does not affect optimization)

The Hamiltonian H is encoded into the QAOA problem unitary
U_C(γ) = exp(−iγH).  ``qiskit_optimization`` returns it as a
``SparsePauliOp``, which Qiskit can directly embed in a circuit.
"""

from __future__ import annotations

from qiskit_optimization import QuadraticProgram


def qubo_to_ising(
    qp: QuadraticProgram,
) -> tuple:
    """Convert a QuadraticProgram (QUBO form) to its Ising Hamiltonian.

    This is a thin wrapper around ``QuadraticProgram.to_ising()`` with
    explicit documentation of what the conversion does (see module docstring).

    Parameters
    ----------
    qp : QuadraticProgram
        Must already be in QUBO form (unconstrained, all-binary).  If the
        program still has constraints, call ``QuadraticProgramToQubo``
        first.

    Returns
    -------
    tuple[SparsePauliOp, float]
        ``(ising_operator, offset)`` where ``ising_operator`` is a
        ``SparsePauliOp`` representing H(s), and ``offset`` is the
        constant C that was factored out.  The ground state of
        ``ising_operator`` (minimum eigenvalue) corresponds to the optimal
        QUBO solution with objective value = eigenvalue + offset.
    """
    ising_op, offset = qp.to_ising()
    return ising_op, float(offset)
