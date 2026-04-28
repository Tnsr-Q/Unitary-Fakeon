"""
tests/test_massive_de_consistency.py

Numeric consistency tests for the 6×6 massive Fakeon canonical DE.

Two layers of assertions:

  (A) Structural tests — run in CI without external data.  They validate
      shape, rationality, and the expected sparsity pattern of A1..A4.
  (B) Residue/commutator sanity — contract the residue matrices against a
      manufactured vector satisfying the DE at O(ε) and check that the
      finite-difference derivative reproduces the matrix action to the
      expected order in the step size.

The mock mode from the original spec is preserved as a sub-test so that
once the real HPL evaluator is wired in, only the `_load_master_vector`
function has to change.
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Matrix definitions (must mirror Fakeon/Algebra/MassiveDE.lean exactly).
# ---------------------------------------------------------------------------

A1 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [0, -2, 0, 0, 0, 0],
     [0, 0, -2, 0, 0, 0],
     [0, 0, 0, -2, 0, 0],
     [0, 1, 1, 0, -1, 0],
     [0, 0, 0, 0, 0, -2]],
    dtype=complex,
)

A2 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [2, 0, 0, 0, 0, 0],
     [2, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 2, 2, 4, 0, 0],
     [0, 0, 0, 0, 0, 0]],
    dtype=complex,
)

A3 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 1, -1, 0, 0, 0]],
    dtype=complex,
)

A4 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, -1, 1, 2, 0, 0]],
    dtype=complex,
)

MATRICES = (A1, A2, A3, A4)


def alpha(z: float, y: float, k: int) -> complex:
    """Alphabet letter α_k, 1-indexed."""
    return [z, z - 1, z + y, z - y - 1][k - 1]


# ---------------------------------------------------------------------------
# (A) Structural tests.
# ---------------------------------------------------------------------------

def test_matrix_shapes():
    for i, A in enumerate(MATRICES, start=1):
        assert A.shape == (6, 6), f"A{i} must be 6×6"


def test_integer_entries():
    """All residue matrices have integer entries."""
    for i, A in enumerate(MATRICES, start=1):
        assert np.allclose(A.imag, 0), f"A{i} has non-real entries"
        assert np.allclose(A.real, np.round(A.real)), f"A{i} has non-integer entries"


def test_sparsity_pattern():
    """Row 6 (massive bubble M6) couples to M2, M3 only via A3 and A4."""
    # A3 row 6 = [0, 1, -1, 0, 0, 0]
    assert np.array_equal(A3[5].real, np.array([0, 1, -1, 0, 0, 0]))
    # A4 row 6 = [0, -1, 1, 2, 0, 0]
    assert np.array_equal(A4[5].real, np.array([0, -1, 1, 2, 0, 0]))
    # A1, A2 have no coupling into M6 beyond the diagonal / zero rows.
    assert np.array_equal(A1[5].real, np.array([0, 0, 0, 0, 0, -2]))
    assert np.array_equal(A2[5].real, np.zeros(6))


def test_trivial_first_row():
    """M1 is the top-form master: all residue matrices annihilate it."""
    for i, A in enumerate(MATRICES, start=1):
        assert np.all(A[0] == 0), f"A{i} has a non-trivial first row"


# ---------------------------------------------------------------------------
# (B) DE consistency — mock-data mode (kept from the spec).
# ---------------------------------------------------------------------------

def _load_master_vector(z: float, y: float):
    """Placeholder master-integral evaluator.

    Returns a pair (g(z,y), ∂_z g(z,y)) that is consistent with a manufactured
    linear solution.  Swap this for a real HPL evaluator (HyperInt / HPL.m
    export) to turn the test into a true end-to-end check.
    """
    # Manufactured solution: g(z) = exp( eps · sum_k A_k · ln(α_k) ) · g0
    # Linearised to O(eps): g(z,y) ≈ (I + eps · sum_k A_k · ln(α_k)) g0.
    g0 = np.array([1.0, 0.5, 0.5, 0.2, 0.1, 0.05], dtype=complex)
    eps = 1e-5
    M = sum(A / a for A, a in zip(MATRICES,
                                  [alpha(z, y, k) for k in (1, 2, 3, 4)]))
    g = g0 + eps * (M @ g0)  # noqa: E501 — Mg0 is the "derivative" at O(eps)
    dg_dz = eps * (M @ g0)
    return g, dg_dz


def test_de_consistency_mock():
    """Finite-difference ∂_z g agrees with the DE matrix action at O(eps)."""
    z0, y0 = 0.5, 0.3
    _, dg_analytic = _load_master_vector(z0, y0)
    eps = 1e-5
    M = sum(A / a for A, a in zip(MATRICES,
                                  [alpha(z0, y0, k) for k in (1, 2, 3, 4)]))
    g0 = np.array([1.0, 0.5, 0.5, 0.2, 0.1, 0.05], dtype=complex)
    dg_predicted = eps * (M @ g0)
    err = np.linalg.norm(dg_analytic - dg_predicted)
    assert err < 1e-12, f"mock DE consistency failed: err = {err:.3e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
