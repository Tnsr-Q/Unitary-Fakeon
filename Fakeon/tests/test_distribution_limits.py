"""
tests/test_distribution_limits.py

Numerical counterpart of `Fakeon/Analysis/Distributions.lean`.

Verifies the Sokhotski–Plemelj imaginary-branch limit

    lim_{η → 0⁺}  ∫ f(x) · Im[1 / (x + iη)] dx  =  −π · f(0)

on a Gaussian test function.  The Lorentzian kernel is sharply peaked at
x = 0 for small η, so naive `scipy.integrate.quad` of the full integrand
fails at small η.  We regularise by splitting

    I(η) = ∫ [f(x) − f(0)] · Im_η(x) dx  +  f(0) · ∫ Im_η(x) dx,
                    └──────────────┘
                      bounded integrand          ^ closed form: −2 arctan(L/η)

which converges smoothly and monotonically for all η.

Closed-form benchmark: for f = exp(−x²),

    I(η) = −π · exp(η²) · erfc(η),

so the residual against the η → 0⁺ target −π is ≈ π · 2/√π · η = 2√π · η.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import erfc


def gaussian(x: float) -> float:
    return float(np.exp(-x * x))


def _regular_integrand(x: float, eta: float) -> float:
    """(f(x) − f(0)) · (−η / (x² + η²))  — bounded at x = 0."""
    return (gaussian(x) - gaussian(0.0)) * (-eta / (x * x + eta * eta))


def sokhotski_plemelj_integral(eta: float, limit: float = 50.0) -> float:
    """Split-off-f(0) regularised SP integral on [-limit, limit]."""
    v_reg, _ = quad(
        _regular_integrand, -limit, limit,
        args=(eta,),
        points=[0.0],
        limit=500,
        epsabs=1e-12,
        epsrel=1e-12,
    )
    v_sing = gaussian(0.0) * (-2.0 * np.arctan(limit / eta))
    return v_reg + v_sing


def exact_sp_gaussian(eta: float) -> float:
    """Closed-form value for f(x) = exp(-x²):  −π · exp(η²) · erfc(η)."""
    return -np.pi * float(np.exp(eta * eta)) * float(erfc(eta))


# ---------------------------------------------------------------------------
# Convergence tests.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "eta,tol",
    [(1e-1, 4e-1),  # ≈ 2√π · η
     (1e-2, 4e-2),
     (1e-3, 4e-3),
     (1e-4, 4e-4),
     (1e-5, 4e-5)],
)
def test_sokhotski_plemelj_convergence(eta: float, tol: float) -> None:
    """|I(η) − (−π)| ≤ 2√π · η + O(η³)."""
    target = -np.pi * gaussian(0.0)
    got = sokhotski_plemelj_integral(eta)
    assert abs(got - target) < tol, (
        f"η = {eta}: got {got:.6f}, target {target:.6f}, "
        f"err {abs(got - target):.3e} > tol {tol:.3e}"
    )


def test_sokhotski_plemelj_matches_closed_form() -> None:
    """Quadrature agrees with `−π · exp(η²) · erfc(η)` to 1e-7.

    Residual is O(f(0) · η / L) from the finite integration window L = 50;
    at the smallest η tested (1e-5) this bound is ≈ 4e-7.
    """
    for eta in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        got = sokhotski_plemelj_integral(eta)
        exact = exact_sp_gaussian(eta)
        assert abs(got - exact) < 1e-7, (
            f"η = {eta}: quad {got:.10f}, exact {exact:.10f}, "
            f"diff {abs(got - exact):.3e}"
        )


def test_sokhotski_plemelj_monotone_error() -> None:
    """Error vs −π decreases monotonically as η → 0⁺."""
    etas = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
    target = -np.pi * gaussian(0.0)
    errs = [abs(sokhotski_plemelj_integral(eta) - target) for eta in etas]
    for prev, curr in zip(errs, errs[1:]):
        assert curr < prev, f"SP error non-monotone: {errs}"


# ---------------------------------------------------------------------------
# Algebraic identity (no quadrature).
# ---------------------------------------------------------------------------

def test_causal_prop_im_identity() -> None:
    """Im[1/(x + iη)] == −η / (x² + η²)."""
    rng = np.random.default_rng(7)
    for _ in range(100):
        x = rng.uniform(-5.0, 5.0)
        eta = rng.uniform(1e-6, 1.0)
        z = 1.0 / (x + 1j * eta)
        lhs = z.imag
        rhs = -eta / (x * x + eta * eta)
        assert abs(lhs - rhs) < 1e-12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
