"""fakeon_numeric.pl_certification — PL-condition spectrum verifier.

Numerical companion to `Fakeon/Optimization/PLCertification.lean`.

Exposes the certified spectral constants (μ_lb, L_ub, κ, η_opt, γ),
provides `check_pl_inequality(θ)` and `verify_hessian_spectrum(H)`, and
ships a numpy-only PL ratio sampler that can be plugged into any
training loop.  A PyTorch Lightning wrapper is provided as a docstring
sketch at the bottom for the day Lightning is in the dependency set.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


# ---------------------------------------------------------------------------
# Certified spectral constants (mirror the Lean module).
# ---------------------------------------------------------------------------

MU_LB: float = 2.4e-2
L_UB:  float = 5.3e-1
KAPPA: float = L_UB / MU_LB                 # ≈ 22.083
ETA_OPT: float = 1.0 / (L_UB + MU_LB)       # ≈ 1.79
GAMMA: float = 2.0 * MU_LB / (L_UB + MU_LB) # ≈ 0.0876


@dataclass
class HessianSpectrumReport:
    lambda_min: float
    lambda_max: float
    kappa: float
    pl_passed: bool
    smoothness_passed: bool
    note: str = ""


def verify_hessian_spectrum(
    H: np.ndarray,
    mu_lb: float = MU_LB,
    L_ub: float = L_UB,
) -> HessianSpectrumReport:
    """Diagonalise H and check the certified bounds on the eigenspectrum."""
    H = 0.5 * (H + H.T)  # symmetrise (numerical noise tolerance)
    eigs = np.linalg.eigvalsh(H)
    lam_min = float(eigs.min())
    lam_max = float(eigs.max())
    kappa = lam_max / max(lam_min, 1e-18)
    pl_passed = lam_min >= mu_lb
    smooth_passed = lam_max <= L_ub
    note = ""
    if not pl_passed:
        note += f"λ_min = {lam_min:.3e} < μ_lb = {mu_lb:.3e}; "
    if not smooth_passed:
        note += f"λ_max = {lam_max:.3e} > L_ub = {L_ub:.3e}; "
    return HessianSpectrumReport(
        lambda_min=lam_min, lambda_max=lam_max, kappa=kappa,
        pl_passed=pl_passed, smoothness_passed=smooth_passed, note=note,
    )


def check_pl_inequality(
    grad_norm_sq: float,
    loss_gap: float,
    mu_lb: float = MU_LB,
    eps: float = 1e-12,
) -> tuple[bool, float]:
    """Return `(passed, ratio)` for the PL inequality.

    `½ ‖∇𝓛‖² ≥ μ_lb · (𝓛 − 𝓛★)` ⇔ ratio = ½ ‖∇𝓛‖² / (𝓛 − 𝓛★) ≥ μ_lb.
    """
    denom = max(loss_gap, eps)
    ratio = 0.5 * grad_norm_sq / denom
    return (ratio >= mu_lb, ratio)


def adaptive_step_size(L_estimate: float,
                       safety: float = 0.9,
                       lo: float = 1e-5) -> float:
    """Step size honouring `η < 2/L_ub` with a safety factor."""
    return float(np.clip(ETA_OPT, lo, safety * (2.0 / max(L_estimate, 1e-18))))


def linear_rate_bound(eta: float,
                      mu_lb: float = MU_LB,
                      L_ub: float = L_UB) -> float:
    """Per-step contraction factor `(1 − γ η)` from the PL theorem."""
    g = 2.0 * mu_lb / (L_ub + mu_lb)
    return float(max(0.0, 1.0 - g * eta))


# ---------------------------------------------------------------------------
# Numpy-only PL ratio sampler.
# ---------------------------------------------------------------------------

def sample_pl_ratio_along_path(
    loss_fn: Callable[[np.ndarray], float],
    grad_fn: Callable[[np.ndarray], np.ndarray],
    theta: np.ndarray,
    L_star: float,
    n_samples: int = 64,
    sigma: float = 1e-6,
    seed: int = 0,
) -> np.ndarray:
    """Sample the PL ratio at `n_samples` perturbations of `theta`.

    Returns the array of ratios.  `min(ratios) ≥ MU_LB` is the empirical
    PL certificate.
    """
    rng = np.random.default_rng(seed)
    out = np.empty(n_samples, dtype=float)
    for i in range(n_samples):
        delta = sigma * rng.standard_normal(theta.shape)
        th = theta + delta
        g = grad_fn(th)
        gap = loss_fn(th) - L_star
        out[i] = 0.5 * float(np.dot(g, g)) / max(gap, 1e-18)
    return out


# ---------------------------------------------------------------------------
# PyTorch Lightning recipe (kept as a sketch — Lightning not installed).
# ---------------------------------------------------------------------------

_LIGHTNING_RECIPE = r"""
class CertifiedPLHessianCallback(pytorch_lightning.Callback):
    \"\"\"Drop-in callback enforcing the certified PL constants at runtime.\"\"\"

    MU_LB = 2.4e-2
    L_UB  = 5.3e-1
    ETA_OPT = 1.0 / (L_UB + MU_LB)

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, idx):
        m = pl_module.metrics
        passed, ratio = check_pl_inequality(m['grad_norm_sq'], m['loss_gap'])
        kappa = m['lambda_max'] / max(m['lambda_min'], 1e-12)
        eta = adaptive_step_size(m['lambda_max'])
        for pg in pl_module.optimizer.param_groups:
            pg['lr'] = eta
        trainer.logger.log_metrics({
            'pl_ratio': ratio, 'pl_passed': float(passed),
            'kappa': kappa, 'eta_adaptive': eta,
        })
        if not passed:
            trainer.print(f"PL VIOLATION: ratio={ratio:.3e} < {self.MU_LB:.3e}")
"""
