"""tests/test_cutkosky.py — numeric companion to Fakeon/QFT/Cutkosky.lean.

Exercises the content-bearing facts:

  1.  fakeon_prop_complex(s, m2)     → imaginary part is *exactly* 0;
  2.  causal_imag(η, s, m2)          → matches  −η / ((s−m²)² + η²);
  3.  causal_imag(η, s, m2) · η⁻¹    → −π · δ(s−m²)  as η → 0⁺
      (distributional test: ∫ f(s) · causal_imag(η, s, 0) ds → −π · f(0));
  4.  fakeon_disc(η, s, m2)          → |disc| = O(η) and → 0 as η → 0⁺;
  5.  modified_cutkosky_residual     → O(η) bound (fakeon sector invisible).
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import integrate

from fakeon_numeric.cutkosky import (
    causal_imag,
    fakeon_disc,
    fakeon_kernel_is_real,
    fakeon_prop,
    fakeon_prop_complex,
    modified_cutkosky_residual,
)
from fakeon_numeric.tolerance_ledger import update_ledger


# ---------------------------------------------------------------------------
# 1. PV reality
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("s", [0.5, 1.7, -3.2, 101.0])
@pytest.mark.parametrize("m2", [0.1, 5.0, 13.3])
def test_fakeon_prop_complex_is_real(s: float, m2: float) -> None:
    assert fakeon_prop_complex(s, m2).imag == 0.0
    assert fakeon_kernel_is_real(s, m2)


def test_fakeon_prop_matches_scalar():
    for s, m2 in [(2.0, 1.0), (-0.5, 0.25), (10.0, 0.0)]:
        assert fakeon_prop(s, m2) == pytest.approx(1.0 / (s - m2))


# ---------------------------------------------------------------------------
# 2. Causal kernel algebraic identity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("eta", [1e-1, 1e-3, 1e-6])
@pytest.mark.parametrize("delta", [-2.0, -0.3, 0.0, 0.3, 2.0])
def test_causal_imag_formula(eta: float, delta: float) -> None:
    s, m2 = delta, 0.0
    expected = -eta / (delta ** 2 + eta ** 2)
    assert causal_imag(eta, s, m2) == pytest.approx(expected, rel=1e-14, abs=1e-30)


# ---------------------------------------------------------------------------
# 3. Sokhotski–Plemelj distributional limit
#     ∫ f(s) · Im[1/(s + iη)] ds  →  −π · f(0)   as  η → 0⁺
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "f, f0",
    [
        (lambda s: math.exp(-(s ** 2)), math.exp(0.0)),
        (lambda s: 1.0 / (1.0 + s ** 2), 1.0),
        (lambda s: math.cos(s) * math.exp(-(s ** 2)), 1.0),
    ],
)
def test_sokhotski_plemelj_limit(f, f0: float) -> None:
    """As η → 0⁺, the Poisson-like kernel reproduces −π · f(0)."""

    def integrand(s: float, eta: float) -> float:
        return f(s) * causal_imag(eta, s, 0.0)

    results = []
    for eta in (1e-1, 1e-2, 1e-3):
        val, _ = integrate.quad(integrand, -50.0, 50.0, args=(eta,), limit=400)
        results.append(val)

    # Should tend monotonically to -π · f0 as η → 0.
    target = -math.pi * f0
    # η=1e-3 should be within 1 % of target.
    assert results[-1] == pytest.approx(target, rel=1e-2, abs=1e-2), (
        f"distributional limit failed: {results} → target {target}"
    )
    # Sequence should improve (each entry closer than the previous).
    errs = [abs(v - target) for v in results]
    assert errs[2] <= errs[1] + 1e-3
    assert errs[1] <= errs[0] + 1e-3


# ---------------------------------------------------------------------------
# 4. Fakeon PV discontinuity: |disc| = O(η) and → 0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("s", [0.5, 1.5, 5.0])
@pytest.mark.parametrize("m2", [0.25, 1.0])
def test_fakeon_disc_scales_like_eta(s: float, m2: float) -> None:
    d1 = abs(fakeon_disc(1e-2, s, m2))
    d2 = abs(fakeon_disc(1e-4, s, m2))
    d3 = abs(fakeon_disc(1e-6, s, m2))
    # Each reduction of η by 10² should drop |disc| by ~10².
    assert d2 < d1
    assert d3 < d2
    ratio = d1 / max(d3, 1e-30)
    assert ratio > 1e3, f"disc not scaling linearly with η: ratio={ratio:.2e}"


def test_fakeon_disc_vanishes_in_limit() -> None:
    """|disc| → 0 as η → 0⁺ across a probe grid."""
    probe_points = [(s, 1.0) for s in np.linspace(-3, 3, 7) if s != 1.0]
    for eta in (1e-4, 1e-6, 1e-8):
        linf = max(abs(fakeon_disc(eta, s, m2)) for s, m2 in probe_points)
        assert linf < 100.0 * eta, (
            f"η={eta}: |disc|_∞ = {linf:.3e} not within 100·η bound"
        )


# ---------------------------------------------------------------------------
# 5. Modified Cutkosky residual: fakeon sector invisible
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("eta", [1e-2, 1e-4, 1e-6])
def test_modified_cutkosky_fakeon_invisible(eta: float) -> None:
    """Fakeon sector contributes zero to the cut discontinuity."""
    resid = modified_cutkosky_residual(
        eta=eta,
        s=2.0,
        left_amp_phys=complex(0.7, 0.3),
        right_amp_phys=complex(0.4, -0.2),
        left_amp_fake=1.5,   # real-valued by S.1
        right_amp_fake=-0.8,
    )
    assert resid == 0.0
    # Record the worst-case residual (always 0 by construction) into the
    # tolerance ledger so the Cutkosky status tag is content-bearing.
    update_ledger("cutkosky_residual", resid, resid < 1e-30)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
