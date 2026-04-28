"""fakeon_numeric.lightning.hessian_pl_callback

Lightning callback enforcing the certified PL constants
(:mod:`fakeon_numeric.pl_certification`) at training time.

The callback computes a stochastic Lanczos estimate of the Hessian
spectrum extrema (μ_est, L_est) on every probe step, evaluates the PL
ratio against the certificate's `MU_LB`, and adapts the learning rate
to the optimal `η_opt = 1 / (L + μ)` whenever both PL and conditioning
gates pass.

Imports of `torch` / `pytorch_lightning` are *module-level* on purpose:
this file is only imported when the user opts in via
`from fakeon_numeric.lightning.hessian_pl_callback import HessianPLCallback`.
The rest of the verification stack remains torch-free.

Differences from the user-supplied draft
----------------------------------------
* `loss_star` tracks the **running minimum** of observed losses (rather
  than freezing on the first observation), so `loss_gap` cannot go
  negative as training improves.
* `pl_tol` defaults to the *certified* `pl_certification.MU_LB = 2.4e-2`,
  not `2.4e-3` (which would be a 10× weaker threshold than the proof).
* The conditioning gate defaults to the *certified* `pl_certification.KAPPA`
  rather than a magic `50`.
* `outputs["loss"]` is reused; the callback never re-runs `training_step`.
* The Lanczos start vector is RNG-seeded for reproducibility.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

import numpy as np
import pytorch_lightning as pl
import torch

from fakeon_numeric.pl_certification import KAPPA as CERT_KAPPA
from fakeon_numeric.pl_certification import L_UB as CERT_L_UB
from fakeon_numeric.pl_certification import MU_LB as CERT_MU_LB

log = logging.getLogger("fakeon_numeric.lightning.hessian_pl_callback")


def _extract_loss(outputs: Any) -> torch.Tensor:
    """Pull the loss tensor out of Lightning's ``outputs`` payload.

    Lightning forwards the value returned by ``training_step``, which can
    be either a tensor (loss) or a dict with a ``loss`` key.
    """
    if isinstance(outputs, torch.Tensor):
        return outputs
    if isinstance(outputs, dict) and "loss" in outputs:
        return outputs["loss"]
    raise TypeError(
        f"HessianPLCallback: cannot extract loss from outputs of type "
        f"{type(outputs).__name__}; expected Tensor or dict with 'loss'."
    )


class HessianPLCallback(pl.Callback):
    """Lightning callback for stochastic Hessian estimates and PL checks.

    Parameters
    ----------
    reg_lambda
        Tikhonov regularisation added to the Hessian spectrum estimates
        (numerical stabiliser; matches the QFT-side prior).
    k_lanczos
        Number of Lanczos iterations for the spectrum estimate.  Defaults
        to 20 (a meaningful tridiagonal); increase to 40+ for tighter
        bounds at additional HVP cost.
    pl_tol
        PL threshold μ.  Defaults to the certified `MU_LB = 2.4e-2`.
    monitor_every_n_steps
        Stride in batches between probes.
    warmup_steps
        Skip probing during the first `warmup_steps` global steps.
    max_lr, min_lr
        Hard clamps on the adaptive LR.  `max_lr` is also bounded above
        by `0.9 · 2/L_est` so we stay strictly inside the smoothness
        stability ball.
    kappa_gate
        Maximum condition number admitted before LR adaptation kicks in.
        Defaults to the certificate's `KAPPA`.
    seed
        RNG seed for the Lanczos start vector (reproducibility).
    """

    def __init__(
        self,
        reg_lambda: float = 1e-4,
        k_lanczos: int = 20,
        pl_tol: float = CERT_MU_LB,
        monitor_every_n_steps: int = 50,
        warmup_steps: int = 100,
        max_lr: float = 3.0,
        min_lr: float = 1e-5,
        kappa_gate: float = CERT_KAPPA,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.reg_lambda = float(reg_lambda)
        self.k = int(k_lanczos)
        self.pl_tol = float(pl_tol)
        self.monitor_every = int(monitor_every_n_steps)
        self.warmup_steps = int(warmup_steps)
        self.max_lr = float(max_lr)
        self.min_lr = float(min_lr)
        self.kappa_gate = float(kappa_gate)
        self._gen = torch.Generator()
        self._gen.manual_seed(int(seed))

        # Running state
        self.mu_est: Optional[float] = None
        self.L_est: Optional[float] = None
        self.loss_star: Optional[float] = None  # running minimum of observed losses

    # ------------------------------------------------------------------
    # Hessian-vector products + Lanczos
    # ------------------------------------------------------------------
    @staticmethod
    def _hvp(
        loss: torch.Tensor,
        params: List[torch.Tensor],
        vec: List[torch.Tensor],
    ) -> List[torch.Tensor]:
        """Compute H·v via double backprop."""
        grad = torch.autograd.grad(loss, params, create_graph=True)
        grad_v = sum(torch.sum(g * v_elem) for g, v_elem in zip(grad, vec))
        hv = torch.autograd.grad(grad_v, params, retain_graph=False)
        return [h.detach() for h in hv]

    def _stochastic_lanczos(
        self,
        params: List[torch.Tensor],
        loss: torch.Tensor,
    ) -> np.ndarray:
        """Lanczos tridiagonalisation; returns eigenvalues of T_k."""
        device = loss.device

        q_prev = [torch.zeros_like(p) for p in params]
        # Reproducible start vector.
        q = [
            torch.randn(p.shape, generator=self._gen, device="cpu").to(device)
            for p in params
        ]
        q_norm = torch.sqrt(sum(torch.sum(x * x) for x in q))
        q = [x / (q_norm + 1e-12) for x in q]

        alphas: list[float] = []
        betas: list[float] = []
        beta_prev = torch.tensor(0.0, device=device)

        for _ in range(self.k):
            z = self._hvp(loss, params, q)
            alpha = sum(torch.sum(qi * zi) for qi, zi in zip(q, z))
            alphas.append(float(alpha.detach().cpu()))

            r = [
                zi - alpha * qi - beta_prev * qpi
                for zi, qi, qpi in zip(z, q, q_prev)
            ]
            beta = torch.sqrt(sum(torch.sum(ri * ri) for ri in r))
            beta_val = float(beta.detach().cpu())
            if beta_val < 1e-10:
                break
            betas.append(beta_val)

            q_prev = [qi.detach().clone() for qi in q]
            q = [ri / (beta + 1e-12) for ri in r]
            beta_prev = beta.detach()

        n = len(alphas)
        if n == 0:
            return np.array([self.reg_lambda, self.reg_lambda])

        T = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            T[i, i] = alphas[i]
            if i < n - 1 and i < len(betas):
                T[i, i + 1] = betas[i]
                T[i + 1, i] = betas[i]
        return np.linalg.eigvalsh(T)

    # ------------------------------------------------------------------
    # PL check
    # ------------------------------------------------------------------
    def _verify_pl_condition(
        self, grad_norm_sq: float, loss_gap: float
    ) -> tuple[bool, float]:
        """Return ``(satisfied, ratio)``.

        With `loss_star` tracked as the running minimum, `loss_gap ≥ 0`
        always.  An exactly-zero gap means we are at the empirical
        optimum; the PL inequality is vacuously satisfied.
        """
        if loss_gap < 1e-12:
            return True, float("inf")
        ratio = 0.5 * grad_norm_sq / loss_gap
        return (ratio >= self.pl_tol), float(ratio)

    # ------------------------------------------------------------------
    # Lightning hooks
    # ------------------------------------------------------------------
    def on_train_batch_end(
        self,
        trainer: pl.Trainer,
        pl_module: pl.LightningModule,
        outputs: Any,
        batch: Any,
        batch_idx: int,
    ) -> None:
        del batch  # unused; the loss already lives in `outputs`
        if (
            batch_idx % self.monitor_every != 0
            or trainer.global_step < self.warmup_steps
        ):
            return

        loss = _extract_loss(outputs)

        # Update running minimum loss.
        loss_val = float(loss.detach())
        if self.loss_star is None or loss_val < self.loss_star:
            self.loss_star = loss_val

        # Trainable parameters.
        params = [p for p in pl_module.parameters() if p.requires_grad]
        if not params:
            return

        # Need a graph; if `outputs` was returned with `retain_graph=False`
        # at backward time, the autograd graph for `loss` may be gone.
        if not loss.requires_grad:
            log.debug("HessianPLCallback: loss has no autograd graph; skipping probe.")
            return

        grad = torch.autograd.grad(loss, params, retain_graph=True, create_graph=False)
        grad_norm_sq = float(sum(torch.sum(g * g) for g in grad).detach())

        eigvals = self._stochastic_lanczos(params, loss)
        self.mu_est = float(eigvals.min()) + self.reg_lambda
        self.L_est = float(eigvals.max()) + self.reg_lambda
        cond_num = self.L_est / max(self.mu_est, 1e-10)

        loss_gap = max(loss_val - (self.loss_star or loss_val), 0.0)
        pl_satisfied, pl_ratio = self._verify_pl_condition(grad_norm_sq, loss_gap)

        eta_opt = 1.0 / max(self.L_est + self.mu_est, 1e-10)
        eta_bar = 2.0 / max(self.L_est, 1e-10)
        max_allowed = min(self.max_lr, eta_bar * 0.9)
        new_lr = float(np.clip(eta_opt, self.min_lr, max_allowed))

        pl_module.log_dict(
            {
                "hessian/mu": self.mu_est,
                "hessian/L": self.L_est,
                "hessian/condition_number": cond_num,
                "optimizer/pl_satisfied": float(pl_satisfied),
                "optimizer/pl_ratio": pl_ratio if np.isfinite(pl_ratio) else 0.0,
                "optimizer/adaptive_lr": new_lr,
            },
            prog_bar=True,
            logger=True,
        )

        if pl_satisfied and cond_num < self.kappa_gate and trainer.optimizers:
            for pg in trainer.optimizers[0].param_groups:
                pg["lr"] = new_lr
        elif not pl_satisfied:
            log.warning(
                "PL violation at step %s: μ=%.2e, gap=%.2e, ratio=%.2e (< %.2e)",
                trainer.global_step,
                self.mu_est,
                loss_gap,
                pl_ratio,
                self.pl_tol,
            )

    def on_validation_epoch_end(
        self, trainer: pl.Trainer, pl_module: pl.LightningModule
    ) -> None:
        del trainer
        pl_module.log("certification/mu_final", self.mu_est or 0.0)
        pl_module.log("certification/L_final", self.L_est or 0.0)
        if self.mu_est is not None and self.mu_est >= self.pl_tol:
            log.info(
                "Hessian PL certificate: mu_final=%.3e >= mu_lb=%.3e (PASS)",
                self.mu_est,
                self.pl_tol,
            )
        else:
            log.warning(
                "Hessian PL certificate: mu_final=%s < mu_lb=%.3e (FAIL)",
                self.mu_est,
                self.pl_tol,
            )


# Re-export the certificate constants for downstream introspection.
__all__ = [
    "HessianPLCallback",
    "CERT_MU_LB",
    "CERT_L_UB",
    "CERT_KAPPA",
]
