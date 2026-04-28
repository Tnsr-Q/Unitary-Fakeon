"""tests/test_pl_certification.py — Polyak–Łojasiewicz certificate hooks."""

from __future__ import annotations

import numpy as np
import pytest

from fakeon_numeric.pl_certification import (
    ETA_OPT,
    GAMMA,
    KAPPA,
    L_UB,
    MU_LB,
    adaptive_step_size,
    check_pl_inequality,
    linear_rate_bound,
    sample_pl_ratio_along_path,
    verify_hessian_spectrum,
)
from fakeon_numeric.tolerance_ledger import update_ledger


# ---------------------------------------------------------------------------
# Constant sanity.
# ---------------------------------------------------------------------------

def test_constants_match_certified_values() -> None:
    assert MU_LB == 2.4e-2
    assert L_UB == 5.3e-1
    assert abs(KAPPA - L_UB / MU_LB) < 1e-12
    assert abs(ETA_OPT - 1.0 / (L_UB + MU_LB)) < 1e-12
    assert abs(GAMMA - 2.0 * MU_LB / (L_UB + MU_LB)) < 1e-12


def test_kappa_under_1e3() -> None:
    """Spec: well-conditioned regime requires κ < 1e3."""
    assert KAPPA < 1e3


# ---------------------------------------------------------------------------
# Hessian spectrum verification.
# ---------------------------------------------------------------------------

def _hess_with_spectrum(eigvals: list[float], seed: int = 0) -> np.ndarray:
    n = len(eigvals)
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(A)
    return Q @ np.diag(eigvals) @ Q.T


def test_verify_hessian_spectrum_passes_certified_window() -> None:
    H = _hess_with_spectrum([0.05, 0.1, 0.3, 0.5])
    rep = verify_hessian_spectrum(H)
    assert rep.pl_passed
    assert rep.smoothness_passed
    update_ledger("hessian_spectrum",
                  rep.lambda_min, rep.pl_passed and rep.smoothness_passed)


def test_verify_hessian_spectrum_flags_pl_violation() -> None:
    """λ_min below μ_lb must fail."""
    H = _hess_with_spectrum([1e-3, 0.1, 0.3, 0.5])
    rep = verify_hessian_spectrum(H)
    assert not rep.pl_passed
    assert "μ_lb" in rep.note


def test_verify_hessian_spectrum_flags_smoothness_violation() -> None:
    H = _hess_with_spectrum([0.05, 0.1, 0.3, 5.0])
    rep = verify_hessian_spectrum(H)
    assert not rep.smoothness_passed
    assert "L_ub" in rep.note


# ---------------------------------------------------------------------------
# PL inequality check.
# ---------------------------------------------------------------------------

def test_pl_inequality_pass() -> None:
    # Pick `½‖∇‖² / gap = 0.05 > μ_lb = 0.024`.
    passed, ratio = check_pl_inequality(grad_norm_sq=0.1, loss_gap=1.0)
    assert passed
    assert abs(ratio - 0.05) < 1e-12


def test_pl_inequality_fail() -> None:
    passed, ratio = check_pl_inequality(grad_norm_sq=0.01, loss_gap=1.0)
    assert not passed
    assert ratio < MU_LB


# ---------------------------------------------------------------------------
# Adaptive step size and contraction rate.
# ---------------------------------------------------------------------------

def test_adaptive_step_size_respects_smoothness_bound() -> None:
    eta = adaptive_step_size(L_estimate=L_UB)
    # `< 0.9 · 2 / L_ub` is the safety bound.
    assert eta <= 0.9 * (2.0 / L_UB) + 1e-12


def test_linear_rate_bound_in_zero_one() -> None:
    r = linear_rate_bound(eta=ETA_OPT)
    assert 0.0 <= r < 1.0
    # Numeric expectation: `1 − γ · η_opt ≈ 1 − 0.0876·1.79 ≈ 0.843`.
    assert abs(r - (1 - GAMMA * ETA_OPT)) < 1e-12


# ---------------------------------------------------------------------------
# PL ratio sampler.
# ---------------------------------------------------------------------------

def test_sample_pl_ratio_on_quadratic_landscape() -> None:
    """On a strictly-convex quadratic with eigenvalues in [μ, L], the PL
    ratio at every point is at least μ.  Synthesise such a landscape and
    confirm the empirical certificate."""
    n = 8
    eigs = np.linspace(MU_LB * 1.5, L_UB * 0.8, n)
    rng = np.random.default_rng(13)
    A = rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(A)
    H = Q @ np.diag(eigs) @ Q.T

    def loss_fn(theta: np.ndarray) -> float:
        return 0.5 * float(theta @ H @ theta)

    def grad_fn(theta: np.ndarray) -> np.ndarray:
        return H @ theta

    theta_star = np.zeros(n)
    L_star = 0.0
    # Sample at perturbations of theta_star; each perturbation yields a
    # ratio ≥ μ_min by spectral theory.
    rng2 = np.random.default_rng(27)
    theta = theta_star + 1e-3 * rng2.standard_normal(n)

    ratios = sample_pl_ratio_along_path(
        loss_fn, grad_fn, theta=theta, L_star=L_star,
        n_samples=64, sigma=1e-4, seed=99,
    )
    assert ratios.min() >= float(eigs.min()) * 0.5  # spectral lower bound


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
