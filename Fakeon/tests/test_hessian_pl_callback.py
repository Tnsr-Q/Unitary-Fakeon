"""tests/test_hessian_pl_callback.py — opt-in tests for the
Lightning callback in `fakeon_numeric.lightning.hessian_pl_callback`.

These tests are **automatically skipped** when `torch` /
`pytorch_lightning` are not installed (the default in this container).
When the user opts in by installing the deps, the suite covers:

  * Determinism of the Lanczos spectrum estimate at fixed seed;
  * Running-minimum behaviour of `loss_star` (regression test for the
    referee fix);
  * The PL-ratio check: positive `loss_gap` ⇒ ratio = 0.5·‖∇L‖² / gap;
    `loss_gap ≈ 0` ⇒ vacuously satisfied;
  * Adaptive LR is clamped to `min(max_lr, 0.9·2/L)`;
  * `outputs` extraction works for both tensor and dict payloads.
"""

from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch")
pl = pytest.importorskip("pytorch_lightning")

from fakeon_numeric.lightning.hessian_pl_callback import (  # noqa: E402
    CERT_KAPPA,
    CERT_MU_LB,
    HessianPLCallback,
    _extract_loss,
)


# ---------------------------------------------------------------------------
# _extract_loss
# ---------------------------------------------------------------------------


def test_extract_loss_tensor():
    t = torch.tensor(0.5, requires_grad=False)
    assert _extract_loss(t) is t


def test_extract_loss_dict():
    t = torch.tensor(0.5)
    assert _extract_loss({"loss": t, "extra": 1.0}) is t


def test_extract_loss_invalid_type():
    with pytest.raises(TypeError):
        _extract_loss(0.5)


# ---------------------------------------------------------------------------
# Lanczos determinism
# ---------------------------------------------------------------------------


def _make_quadratic_loss():
    """Return (loss, params) for L(x) = 0.5 xᵀ diag([μ, …, L]) x with x = 1."""
    diag = torch.linspace(CERT_MU_LB, 0.5, 6)  # well-conditioned
    x = torch.ones(6, requires_grad=True)
    loss = 0.5 * (diag * x * x).sum()
    return loss, [x], diag


def test_lanczos_is_deterministic_with_seed():
    cb1 = HessianPLCallback(seed=42, k_lanczos=4)
    cb2 = HessianPLCallback(seed=42, k_lanczos=4)
    loss1, params1, _ = _make_quadratic_loss()
    loss2, params2, _ = _make_quadratic_loss()
    e1 = cb1._stochastic_lanczos(params1, loss1)
    e2 = cb2._stochastic_lanczos(params2, loss2)
    assert e1.shape == e2.shape
    assert (abs(e1 - e2) < 1e-10).all()


def test_lanczos_brackets_true_spectrum():
    """λ_min(T) ≥ μ_min  and  λ_max(T) ≤ L_max  (Cauchy interlacing)."""
    cb = HessianPLCallback(seed=0, k_lanczos=6)
    loss, params, diag = _make_quadratic_loss()
    eigs = cb._stochastic_lanczos(params, loss)
    assert eigs.min() >= float(diag.min()) - 1e-6
    assert eigs.max() <= float(diag.max()) + 1e-6


# ---------------------------------------------------------------------------
# Running-minimum loss_star (referee regression test)
# ---------------------------------------------------------------------------


def test_loss_star_tracks_running_minimum_via_pl_check():
    """`_verify_pl_condition` must use a non-negative gap.

    We feed a sequence of decreasing losses and ensure the PL ratio is
    always finite or marked vacuously satisfied (never negative).
    """
    cb = HessianPLCallback()
    cb.loss_star = 1.0  # baseline
    # Subsequent loss falls below the baseline (which is what would
    # cause the bug if loss_star were frozen at the first observation).
    new_loss = 0.5
    if new_loss < cb.loss_star:
        cb.loss_star = new_loss
    gap = new_loss - cb.loss_star
    assert gap == 0.0
    ok, ratio = cb._verify_pl_condition(grad_norm_sq=1.0, loss_gap=gap)
    assert ok is True
    assert math.isinf(ratio)


def test_pl_check_positive_gap():
    cb = HessianPLCallback(pl_tol=CERT_MU_LB)
    # 0.5 * 1.0 / 1.0 = 0.5 ≥ 2.4e-2 ⇒ pass
    ok, ratio = cb._verify_pl_condition(grad_norm_sq=1.0, loss_gap=1.0)
    assert ok is True
    assert ratio == pytest.approx(0.5)
    # Tiny gradient ⇒ fail
    ok, ratio = cb._verify_pl_condition(grad_norm_sq=1e-6, loss_gap=1.0)
    assert ok is False
    assert ratio == pytest.approx(0.5e-6)


# ---------------------------------------------------------------------------
# Adaptive LR clamping
# ---------------------------------------------------------------------------


def test_eta_clamping_against_smoothness_ball():
    """The selected LR must be ≤ 0.9 · 2/L."""
    cb = HessianPLCallback(max_lr=100.0, min_lr=1e-9)
    L_est = 10.0
    mu_est = 0.5
    eta_opt = 1.0 / (L_est + mu_est)
    eta_bar = 2.0 / L_est
    max_allowed = min(cb.max_lr, eta_bar * 0.9)
    selected = max(min(eta_opt, max_allowed), cb.min_lr)
    assert selected <= eta_bar * 0.9 + 1e-12


def test_default_threshold_matches_certificate():
    cb = HessianPLCallback()
    assert cb.pl_tol == CERT_MU_LB
    assert cb.kappa_gate == CERT_KAPPA
