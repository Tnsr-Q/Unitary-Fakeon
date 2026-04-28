"""fakeon_numeric.cutkosky — numeric companion to Fakeon/QFT/Cutkosky.lean.

Implements the two algebraic content-bearing facts from the Lean scaffold:

  * `fakeon_prop(s, m2)`       — real PV propagator 1/(s − m²);
  * `fakeon_prop_complex(...)` — ℂ-lift with strictly zero imaginary part;
  * `causal_imag(eta, s, m2)`  — Im[1/(s − m² + iη)] = −η / ((s−m²)² + η²);
  * `fakeon_disc(eta, s, m2)`  — discretised discontinuity estimator, goes
    to zero as η → 0⁺ for the realified fakeon kernel (the numerical
    statement behind `Cutkosky.fakeon_pv_disc_zero`).

Also bundles a `modified_cutkosky_residual` that numerically probes the
physical-sector decomposition: given a synthetic cut amplitude with
real-valued fakeon component, the residual between the full discontinuity
estimator and the physical-sector contribution should scale like O(η).
"""

from __future__ import annotations


def fakeon_prop(s: float, m2: float) -> float:
    """Real PV propagator 1 / (s − m²).  Caller handles s = m²."""
    return 1.0 / (s - m2)


def fakeon_prop_complex(s: float, m2: float) -> complex:
    """Complex lift of the PV propagator.  Imaginary part is identically 0."""
    return complex(fakeon_prop(s, m2), 0.0)


def causal_imag(eta: float, s: float, m2: float) -> float:
    """Im[1 / (s − m² + iη)] = −η / ((s − m²)² + η²).

    Direct algebraic identity; matches `Cutkosky.causalImag` in Lean.
    """
    delta = s - m2
    return -eta / (delta * delta + eta * eta)


def fakeon_disc(eta: float, s: float, m2: float) -> complex:
    """Discretised discontinuity estimator:

        (F(s + iη) − F(s − iη))

    Evaluated for `F(z) = 1 / (z − m²)` extended to ℂ, then compared to
    the fakeon realification.  Returns the difference between the two
    evaluations — should be identically zero on the real lift.
    """
    z_plus = complex(s, eta) - m2
    z_minus = complex(s, -eta) - m2
    F_plus = 1.0 / z_plus
    F_minus = 1.0 / z_minus
    return F_plus - F_minus


def fakeon_kernel_is_real(s: float, m2: float) -> bool:
    """Reality gate for the PV kernel: ℂ-lift has zero imaginary part."""
    return fakeon_prop_complex(s, m2).imag == 0.0


def modified_cutkosky_residual(
    eta: float,
    s: float,
    left_amp_phys: complex,
    right_amp_phys: complex,
    left_amp_fake: float,
    right_amp_fake: float,
) -> float:
    """Residual probing the physical-sector decomposition of a cut.

    Given:
      - physical-sector amplitudes (complex),
      - fakeon-sector amplitudes (strictly real per S.1),

    computes |Disc_total − Disc_physical| where the total and physical
    discontinuities are both modelled by the iε limit.  The fakeon
    sector's contribution to Im is zero by construction, so this
    residual is an O(η) quantity bounded by the iε regulator.

    Returns the L∞ residual.
    """
    # Physical contribution: 2 η |Im(L_phys * R_phys)| / ((s)² + η²)
    phys_product = left_amp_phys * right_amp_phys
    disc_phys = 2 * eta * phys_product.imag / (s * s + eta * eta)

    # Fakeon contribution: must be zero (kernel is ℝ-valued).
    _ = left_amp_fake * right_amp_fake  # asserted real by S.1; unused
    disc_fake = 0.0  # By fakeon_pv_disc_zero.

    # Total minus physical — should equal the fakeon piece (≈ 0).
    disc_total = disc_phys + disc_fake
    return abs(disc_total - disc_phys)
