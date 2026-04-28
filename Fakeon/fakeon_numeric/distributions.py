"""fakeon_numeric.distributions — numeric companion to `Analysis/Distributions.lean`.

Lightweight evaluators used by the Chen-integration test.  These are
self-contained and do not require the HyperInt pipeline; they enforce
the fakeon spectral-density axiom (ρ ≡ 0) so that every dispersive
integral evaluates to a real number.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.integrate import quad


def causal_propagator(z: float, mu: float, eta: float = 1e-12) -> complex:
    """Regularised 1 / (z − μ + iη)."""
    return 1.0 / (z - mu + 1j * eta)


def check_spectral_density_zero(
    rho: Callable[[int, float], float],
    n: int = 0,
    mu_grid: np.ndarray | None = None,
) -> bool:
    """Return True iff `ρ(n, μ) = 0` on the supplied μ-grid."""
    grid = mu_grid if mu_grid is not None else np.logspace(-3, 3, 25)
    return all(float(rho(n, float(mu))) == 0.0 for mu in grid)


def evaluate_c_n(
    n: int,
    rho: Callable[[int, float], float],
    z0: float,
    eta: float = 1e-9,
    limit: float = 50.0,
) -> complex:
    """Dispersive boundary constant `c_n = lim_{η → 0⁺} ∫ ρ(n, μ) / (z₀ − μ + iη) dμ`.

    Under the fakeon axiom `ρ ≡ 0` the integrand vanishes identically and
    the result is `0 + 0j` to machine precision.
    """
    def integrand_re(mu: float) -> float:
        return float(rho(n, mu) * causal_propagator(z0, mu, eta).real)

    def integrand_im(mu: float) -> float:
        return float(rho(n, mu) * causal_propagator(z0, mu, eta).imag)

    val_re, _ = quad(integrand_re, -limit, limit, limit=200)
    val_im, _ = quad(integrand_im, -limit, limit, limit=200)
    return complex(val_re, val_im)
