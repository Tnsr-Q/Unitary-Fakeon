"""
tests/test_bootstrap_optical.py

Numerical counterpart of `Fakeon/QFT/InelasticBootstrap.lean`.

Two checks:

  (A)  Loss → 0  ⇔  ‖S_ℓ‖ ≤ 1 on the grid.
       Tolerance ledger key: ``bootstrap_loss``.

  (B)  Optical bridge:   for S_ℓ = 1 + 2 i T_ℓ  with  ‖S_ℓ‖ ≤ 1,
                              Im T_ℓ ≥ ‖T_ℓ‖².
       This is the per-channel optical-theorem inequality.  We do NOT
       test the user-spec form ``Im T_ℓ ≥ ‖T_ℓ‖² + (1 − η²)`` because
       that inequality fails for generic phase shifts (counter-example:
       η = 0.5, δ = 0 ⇒ 1 ≥ 2 is false).  The standard form below is
       both rigorous and implied by the bootstrap loss vanishing.
"""

from __future__ import annotations

import numpy as np
import pytest

from fakeon_numeric.tolerance_ledger import (
    reset_ledger,
    snapshot,
    update_ledger,
)


# ---------------------------------------------------------------------------
# Synthetic bootstrap solution.
# ---------------------------------------------------------------------------

def _eta_profile(s: np.ndarray, ell: int,
                 alpha: float = 0.05, m: float = 1.0) -> np.ndarray:
    excess = np.maximum(s - 4.0 * m * m, 0.0)
    return np.exp(-alpha * excess ** (ell + 1))


def _build_S_grid(grid_l: np.ndarray, grid_s: np.ndarray,
                  alpha: float = 0.05, m: float = 1.0,
                  rng: np.random.Generator | None = None) -> np.ndarray:
    """`S_ℓ(s)` on the (ℓ, s) grid with ‖S_ℓ‖ = η_ℓ(s) by construction."""
    rng = rng or np.random.default_rng(7)
    out = np.empty((len(grid_l), len(grid_s)), dtype=complex)
    for i, ell in enumerate(grid_l):
        eta = _eta_profile(grid_s, int(ell), alpha=alpha, m=m)
        delta = rng.uniform(0.0, np.pi, size=len(grid_s))
        out[i] = eta * np.exp(2j * delta)
    return out


# ---------------------------------------------------------------------------
# (A) Loss → 0 ⇔ unitarity.
# ---------------------------------------------------------------------------

def bootstrap_loss(S_grid: np.ndarray) -> float:
    return float(np.sum(np.maximum(np.abs(S_grid) ** 2 - 1.0, 0.0) ** 2))


def test_bootstrap_loss_zero_for_inelastic_ansatz() -> None:
    grid_l = np.arange(0, 5)
    grid_s = np.linspace(4.1, 200.0, 64)
    S = _build_S_grid(grid_l, grid_s)

    loss = bootstrap_loss(S)
    update_ledger("bootstrap_loss", loss, loss < 1e-20)

    assert loss < 1e-20, f"Bootstrap loss should vanish for ‖S‖=η ≤ 1; got {loss:.3e}"
    assert np.max(np.abs(S)) <= 1.0 + 1e-12


def test_bootstrap_loss_detects_violation() -> None:
    grid_l = np.arange(0, 3)
    grid_s = np.linspace(4.1, 100.0, 32)
    S = _build_S_grid(grid_l, grid_s)
    # Manually break unitarity in one entry.
    S[1, 5] = 1.5 * np.exp(0.7j)

    loss = bootstrap_loss(S)
    assert loss > 1e-3, "Loss must flag ‖S‖ > 1 violation"


# ---------------------------------------------------------------------------
# (B) Optical bridge:  S = 1 + 2iT  and  ‖S‖ ≤ 1  ⇒  Im T ≥ ‖T‖².
# ---------------------------------------------------------------------------

def _T_from_S(S: np.ndarray) -> np.ndarray:
    return (S - 1.0) / (2.0j)


def optical_residual(S: np.ndarray) -> np.ndarray:
    """Pointwise   ‖T‖² − Im T   (negative or zero ⇔ inequality holds)."""
    T = _T_from_S(S)
    return np.abs(T) ** 2 - T.imag


def test_optical_inequality_holds_pointwise() -> None:
    grid_l = np.arange(0, 5)
    grid_s = np.linspace(4.1, 200.0, 64)
    S = _build_S_grid(grid_l, grid_s)
    res = optical_residual(S)
    update_ledger("optical_inequality",
                  float(np.max(res)),
                  bool(np.max(res) <= 1e-12))
    # `Im T ≥ ‖T‖²`  ⇔  residual ≤ 0.
    assert np.max(res) <= 1e-12, (
        f"Optical inequality violated; max residual = {np.max(res):.3e}"
    )


def test_optical_inequality_consistency_with_norm_squared() -> None:
    """Algebraic check:  ‖S‖² = 1 − 4 Im T + 4 ‖T‖²  exactly."""
    grid_l = np.arange(0, 5)
    grid_s = np.linspace(4.1, 200.0, 32)
    S = _build_S_grid(grid_l, grid_s)
    T = _T_from_S(S)
    lhs = np.abs(S) ** 2
    rhs = 1.0 - 4.0 * T.imag + 4.0 * np.abs(T) ** 2
    assert np.max(np.abs(lhs - rhs)) < 1e-12


# ---------------------------------------------------------------------------
# End-to-end pipeline: drives both ledger keys.
# ---------------------------------------------------------------------------

def test_bootstrap_optical_pipeline() -> None:
    reset_ledger()
    grid_l = np.arange(0, 4)
    grid_s = np.linspace(4.1, 150.0, 48)
    S = _build_S_grid(grid_l, grid_s)

    loss = bootstrap_loss(S)
    assert loss < 1e-20
    update_ledger("bootstrap_loss", loss, True)

    res = optical_residual(S)
    assert np.max(res) <= 1e-12
    update_ledger("optical_inequality", float(np.max(res)), True)

    snap = snapshot()
    assert snap["bootstrap_loss"]["passed"]
    assert snap["optical_inequality"]["passed"]


@pytest.mark.parametrize("ell", [0, 1, 2, 3, 4])
def test_eta_profile_bounds(ell: int) -> None:
    s = np.linspace(4.1, 1e3, 256)
    eta = _eta_profile(s, ell)
    # Mathematically 0 < η ≤ 1; numerically η can underflow to 0 for
    # large `s` and high `ℓ`, so we test the float-realisable form.
    assert np.all(eta >= 0.0)
    assert np.all(eta <= 1.0)
    # On a numerically safe envelope the strict bound holds.
    s_safe = np.linspace(4.1, 4.5, 64)
    eta_safe = _eta_profile(s_safe, ell)
    assert np.all(eta_safe > 0.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
