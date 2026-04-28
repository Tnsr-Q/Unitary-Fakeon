"""
tests/test_chen_integration.py

End-to-end numeric check of the Chen-series reality induction:

  1. Verify the fakeon spectral-density axiom `ρ(n, μ) = 0`
     (`check_spectral_density_zero`).
  2. Evaluate the dispersive boundary constants `c_n` via
     `evaluate_c_n`; under the axiom each `c_n` is identically zero, hence
     real, providing the *base case* of the induction.
  3. Iterate the canonical Chen recursion

         g^(n+1) = Σ_k  M_k · g^(n) · ln |α_k|  +  c_{n+1}

     starting from a real seed vector and confirm that the imaginary
     part stays at machine zero through weight 4.

This is the numerical counterpart of
`Fakeon.Algebra.ChenCollapse.chen_series_real` and protects against
silent regressions in the (numpy) reduction or the (scipy) dispersive
quadrature.
"""

from __future__ import annotations

import numpy as np
import pytest

from fakeon_numeric.distributions import (
    check_spectral_density_zero,
    evaluate_c_n,
)

# ---------------------------------------------------------------------------
# Residue matrices (must mirror Fakeon/Algebra/MassiveDE.lean).
# ---------------------------------------------------------------------------

A1 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [0, -2, 0, 0, 0, 0],
     [0, 0, -2, 0, 0, 0],
     [0, 0, 0, -2, 0, 0],
     [0, 1, 1, 0, -1, 0],
     [0, 0, 0, 0, 0, -2]],
    dtype=float,
)
A2 = np.array(
    [[0, 0, 0, 0, 0, 0],
     [2, 0, 0, 0, 0, 0],
     [2, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 2, 2, 4, 0, 0],
     [0, 0, 0, 0, 0, 0]],
    dtype=float,
)
A3 = np.array(
    [[0, 0, 0, 0, 0, 0]] * 5
    + [[0, 1, -1, 0, 0, 0]],
    dtype=float,
)
A4 = np.array(
    [[0, 0, 0, 0, 0, 0]] * 5
    + [[0, -1, 1, 2, 0, 0]],
    dtype=float,
)
A5 = np.zeros((6, 6), dtype=float)
A6 = np.zeros((6, 6), dtype=float)
M_LIST = [A1, A2, A3, A4, A5, A6]


def alpha_values(z: float, y: float) -> list[float]:
    return [z, z - 1.0, z + y, z - y - 1.0, y, y + 1.0]


# Fakeon spectral density: ρ(n, μ) = 0 for every n, μ.
def rho_fakeon(_n: int, _mu: float) -> float:
    return 0.0


# ---------------------------------------------------------------------------
# (1) Axiom guard.
# ---------------------------------------------------------------------------

def test_spectral_density_axiom_holds() -> None:
    for n in range(5):
        assert check_spectral_density_zero(rho_fakeon, n), (
            f"Spectral-density axiom violated at n = {n}"
        )


# ---------------------------------------------------------------------------
# (2) Dispersive c_n base case.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_c_n_real_under_fakeon_axiom(n: int) -> None:
    z0 = 0.5
    c = evaluate_c_n(n, rho_fakeon, z0)
    assert abs(c.imag) < 1e-12, (
        f"c_{n} acquired imaginary part {c.imag:.3e} despite ρ ≡ 0."
    )
    assert abs(c.real) < 1e-12, (
        f"c_{n} should also vanish under ρ ≡ 0; got real part {c.real:.3e}."
    )


# ---------------------------------------------------------------------------
# (3) Inductive Chen step preserves reality.
# ---------------------------------------------------------------------------

def _chen_step(g: np.ndarray, z: float, y: float) -> np.ndarray:
    """One iteration of g  ↦  Σ_k M_k · g · ln |α_k|."""
    out = np.zeros_like(g, dtype=complex)
    alphas = alpha_values(z, y)
    for Mk, ak in zip(M_LIST, alphas):
        if ak == 0.0:
            continue
        out += (Mk @ g) * np.log(abs(ak))
    return out


@pytest.mark.parametrize("weight", [1, 2, 3, 4])
def test_chen_recursion_preserves_reality(weight: int) -> None:
    z, y = 0.5, 0.3
    rng = np.random.default_rng(2024)
    g = rng.standard_normal((6, 1)).astype(complex)  # real seed
    z0 = 0.5

    for n in range(1, weight + 1):
        g = _chen_step(g, z, y)
        c_n = evaluate_c_n(n, rho_fakeon, z0)
        # c_n broadcasts to all six rows (matches the Lean `c_vec` definition).
        g = g + c_n * np.ones((6, 1), dtype=complex)
        assert np.max(np.abs(g.imag)) < 1e-12, (
            f"Chen step n={n} leaked imaginary part: "
            f"max |Im| = {np.max(np.abs(g.imag)):.3e}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
