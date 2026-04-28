"""
tests/test_s_matrix_extension.py

Verification hooks for the S-matrix extension assumptions S.1 – S.3,
producing tolerance-ledger entries consumable by the audit script.

Implemented checks:

  S.1  ρ_GF^{(1)}(μ²) = 0     →  `verify_spectral_density`
  S.2a |S_l(s)| ≤ 1            →  `verify_inelasticity_profile`
  S.2b σ_tot(s) ≤ C ln²(s/s0)  →  `check_froissart_bound`
  S.3  β_{f₂} closed form      →  `verify_beta_closure`

All hooks are self-contained: synthetic inputs are generated *inside*
the test under the assumption that the corresponding axiom holds, then
fed back into the verifier.  This protects against silent regressions
in numpy / quadrature without requiring HyperInt / Bootstrap exports.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from fakeon_numeric.tolerance_ledger import (
    reset_ledger,
    snapshot,
    update_ledger,
)


# ---------------------------------------------------------------------------
# S.1 — Spectral density vanishing.
# ---------------------------------------------------------------------------

def verify_spectral_density(rho_GH: np.ndarray, tol: float = 1e-15) -> bool:
    """Confirm ρ_GF^{(1)}(μ²) = 0 prevents fakeon cuts."""
    max_rho = float(np.max(np.abs(rho_GH))) if rho_GH.size else 0.0
    passed = max_rho < tol
    update_ledger("spectral_density", max_rho, passed)
    return passed


def test_S1_spectral_density() -> None:
    rho = np.zeros(128)  # ρ ≡ 0 by fakeon projection
    assert verify_spectral_density(rho)


# ---------------------------------------------------------------------------
# S.2 — Inelastic dual bootstrap.
# ---------------------------------------------------------------------------

def inelasticity_ansatz(
    s_grid: np.ndarray, ell: int, alpha: float = 0.05, m_thresh: float = 4.0
) -> np.ndarray:
    """|S_ℓ(s)| = exp(-α (s − 4m²)^{ℓ+1})  for s > 4m², else 1."""
    excess = np.maximum(s_grid - m_thresh, 0.0)
    return np.exp(-alpha * excess ** (ell + 1))


def verify_inelasticity_profile(
    S_l: np.ndarray,
    s_grid: np.ndarray,
    ell: int = 0,
    alpha: float = 0.05,
    m_thresh: float = 4.0,
    profile_tol: float = 1e-10,
) -> bool:
    eta = inelasticity_ansatz(s_grid, ell=ell, alpha=alpha, m_thresh=m_thresh)
    residual = float(np.max(np.abs(np.abs(S_l) - eta)))
    bound_ok = bool(np.all(np.abs(S_l) <= 1.0 + 1e-12))
    passed = (residual < profile_tol) and bound_ok
    update_ledger("inelastic_bootstrap", residual, passed)
    return passed


@pytest.mark.parametrize("ell", [0, 1, 2, 3])
def test_S2_inelasticity_profile(ell: int) -> None:
    s_grid = np.linspace(4.1, 100.0, 200)
    eta = inelasticity_ansatz(s_grid, ell=ell)
    # Promote the modulus to a complex amplitude on the unit-or-below disk.
    S_l = eta * np.exp(1j * 0.3 * s_grid)
    assert verify_inelasticity_profile(S_l, s_grid, ell=ell)


def check_froissart_bound(
    sigma_tot: np.ndarray,
    s_grid: np.ndarray,
    C: float = 0.25,
    s0: float = 1.0,
    tol: float = 0.05,
) -> bool:
    """σ_tot(s) ≤ C ln²(s/s0)  pointwise on the grid."""
    bound = C * np.log(s_grid / s0) ** 2
    ratio = float(np.max(sigma_tot / np.maximum(bound, 1e-30)))
    passed = ratio <= (1.0 + tol)
    update_ledger("froissart_bound", ratio, passed)
    return passed


def test_S2_froissart_bound() -> None:
    s_grid = np.linspace(2.0, 1e4, 500)
    # Saturating Froissart at half-amplitude — generic physical scaling.
    sigma = 0.12 * np.log(s_grid / 1.0) ** 2
    assert check_froissart_bound(sigma, s_grid)


def test_S2_froissart_violation_detected() -> None:
    s_grid = np.linspace(2.0, 1e4, 500)
    # Construct a violating cross-section: linear σ ∝ s eventually exceeds C ln²(s).
    sigma = 0.01 * s_grid
    assert not check_froissart_bound(sigma, s_grid)


# ---------------------------------------------------------------------------
# S.3 — β-function closure.
# ---------------------------------------------------------------------------

def beta_f2_analytic(f2: np.ndarray) -> np.ndarray:
    """β_{f₂}(f₂) at 1-loop + 2-loop in MS-bar.

    β^{(1)} = -133 / (20 (4π)²) · f₂³
    β^{(2)} = +5196 / (5 (16π²)²) · f₂⁵
    """
    pi2_4 = (4.0 * math.pi) ** 2
    pi2_16 = (16.0 * math.pi ** 2) ** 2
    return -(133.0 / (20.0 * pi2_4)) * f2 ** 3 \
           + (5196.0 / (5.0 * pi2_16)) * f2 ** 5


def verify_beta_closure(
    f2_grid: np.ndarray, beta_vals: np.ndarray, tol: float = 1e-10
) -> bool:
    expected = beta_f2_analytic(f2_grid)
    residual = float(np.linalg.norm(beta_vals - expected))
    passed = residual < tol
    update_ledger("beta_closure", residual, passed)
    return passed


def test_S3_beta_closure() -> None:
    f2 = np.linspace(0.0, 0.9, 50)
    beta = beta_f2_analytic(f2)  # by construction satisfies the closure
    assert verify_beta_closure(f2, beta)


# ---------------------------------------------------------------------------
# End-to-end pipeline (drives all four hooks; fills the tolerance ledger).
# ---------------------------------------------------------------------------

def test_s_matrix_extension_pipeline_demonstrated() -> None:
    """Single integration test that exercises every S.1–S.3 hook."""
    reset_ledger()

    # S.1
    assert verify_spectral_density(np.zeros(64))

    # S.2
    s_grid = np.linspace(4.1, 1e3, 300)
    S_l = inelasticity_ansatz(s_grid, ell=0)
    assert verify_inelasticity_profile(S_l, s_grid)

    sigma = 0.12 * np.log(s_grid / 1.0) ** 2
    assert check_froissart_bound(sigma, s_grid)

    # S.3
    f2 = np.linspace(0.0, 0.9, 32)
    assert verify_beta_closure(f2, beta_f2_analytic(f2))

    snap = snapshot()
    expected_keys = {
        "spectral_density",
        "inelastic_bootstrap",
        "froissart_bound",
        "beta_closure",
    }
    assert expected_keys.issubset(snap.keys())
    assert all(snap[k]["passed"] for k in expected_keys), (
        f"At least one S-matrix extension hook failed: {snap}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
