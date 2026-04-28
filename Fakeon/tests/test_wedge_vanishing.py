"""
tests/test_wedge_vanishing.py

Numerical counterpart of `Fakeon/Geometry/WedgeVanishing.lean`.

Strategy
--------
The 2-form d ln α_i ∧ d ln α_j vanishes on a 1D RG flow because the
matrix `D[t, i] = d/dt ln α_i(t)` has rank ≤ 1.  We verify this on a
synthetic-but-nontrivial trajectory obtained from the Frobenius
reduction α_i(t) = f_i(α_1(t)) with smooth, monotone `f_i`.

Wired to real data: swap `_synthetic_trajectory` for
`fakeon_numeric.rg_flow.load_rge_trajectory()` once the RG solver ships.
"""

from __future__ import annotations

import numpy as np
import pytest


def _synthetic_trajectory(
    n_steps: int = 200, n_params: int = 5, seed: int = 42
) -> np.ndarray:
    """α(t) ∈ ℝ_{>0}^{n_params} constrained to a 1D Frobenius curve.

    We pick a scalar driver `u(t) = 0.3 + 1.2 t` and set
    `α_i(t) = a_i · u(t)**p_i`, so that every component is a smooth
    function of α_1 (hence of u).  The resulting `d/dt ln α_i` matrix
    has rank exactly 1.
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, n_steps)
    u = 0.3 + 1.2 * t
    a = rng.uniform(0.5, 2.0, size=n_params)
    p = rng.uniform(0.2, 3.0, size=n_params)
    # Broadcasting: (n_steps, n_params)
    alpha = a[None, :] * u[:, None] ** p[None, :]
    return alpha


def verify_wedge_vanishing(
    alpha_traj: np.ndarray, tol: float = 1e-8
) -> bool:
    """Return True iff `d ln α_i ∧ d ln α_j = 0` for every pair (i, j).

    Equivalent to `rank(D[t, i]) ≤ 1` for the matrix of logarithmic
    derivatives along the trajectory.
    """
    if alpha_traj.ndim != 2:
        raise ValueError("alpha_traj must have shape (n_steps, n_params).")
    safe = np.maximum(alpha_traj, 1e-15)
    dln_alpha = np.gradient(np.log(safe), axis=0)
    rank = np.linalg.matrix_rank(dln_alpha, tol=tol)
    return bool(rank <= 1)


def test_rg_flow_1d_rank() -> None:
    traj = _synthetic_trajectory()
    assert verify_wedge_vanishing(traj), (
        "Wedge product non-zero: synthetic trajectory is not 1D."
    )


def test_rg_flow_violation_detected() -> None:
    """Sanity: a genuinely 2D trajectory must be flagged as non-flat."""
    rng = np.random.default_rng(0)
    n_steps = 200
    t = np.linspace(0.0, 1.0, n_steps)
    u = 0.3 + 1.2 * t
    v = 0.5 + 0.7 * np.sin(3 * t)
    # Two independent drivers  →  rank 2.
    alpha_2d = np.stack(
        [u, v, u * v, u + v, np.sqrt(u * v)], axis=1
    ) + 0.01 * rng.standard_normal((n_steps, 5))
    assert not verify_wedge_vanishing(alpha_2d, tol=1e-6), (
        "Rank check failed: genuinely 2D flow incorrectly certified as 1D."
    )


@pytest.mark.parametrize("n_params", [3, 5, 8])
def test_rg_flow_various_widths(n_params: int) -> None:
    traj = _synthetic_trajectory(n_params=n_params)
    assert verify_wedge_vanishing(traj)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
