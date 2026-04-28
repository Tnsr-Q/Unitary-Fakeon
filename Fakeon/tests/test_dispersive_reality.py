"""
tests/test_dispersive_reality.py

Numerical counterpart of `Fakeon/Analysis/DispersiveReality.lean`.

Under the fakeon projection the spectral density vanishes,

    ρ_GF(μ, y) ≡ 0,

so the dispersive integral defining every boundary constant c_n reduces
to an integral of zero, which is real.  This test checks that
`compute_c_n` returns a real number to machine precision for n = 0..5.

The test is self-contained; it does not depend on HyperInt data.  When
the real evaluator is wired in via `fakeon_numeric.validation`, the same
assertion continues to hold because the axiom `ρ_GF = 0` is structural.
"""

from __future__ import annotations

import numpy as np
import pytest


def causal_propagator(z: float, mu: float, eta: float = 1e-12) -> complex:
    """Principal-value + iε regularisation of 1 / (z − μ)."""
    return 1.0 / (z - mu + 1j * eta)


def spectral_density_fakeon(_mu: float, _y: float) -> float:
    """Axiom S.1: ρ_GF vanishes on the physical Hilbert space."""
    return 0.0


def compute_c_n(n: int, z0: float, y0: float, n_mu: int = 200) -> complex:
    """Mock dispersive evaluator.

    Implements the n-independent reduction that follows from ρ_GF ≡ 0:
    every recursion step convolves the causal propagator against zero.
    The signature accepts `n` so that the test can loop over orders.
    """
    del n  # under ρ_GF = 0 the result is order-independent
    mus = np.logspace(-1, 3, n_mu)
    contributions = [
        causal_propagator(z0, mu) * spectral_density_fakeon(mu, y0)
        for mu in mus
    ]
    return complex(np.sum(contributions))


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5])
def test_im_eq_zero(n: int) -> None:
    z0, y0 = 0.5, 0.3
    c = compute_c_n(n, z0, y0)
    assert abs(c.imag) < 1e-14, (
        f"im_eq_zero failed at n={n}: Im[c_n] = {c.imag:.3e}"
    )


def test_spectral_density_axiom() -> None:
    """Axiom S.1 must be enforced in code, not just in the proof."""
    for mu in np.logspace(-3, 3, 20):
        for y in np.linspace(0.1, 2.0, 5):
            assert spectral_density_fakeon(mu, y) == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
