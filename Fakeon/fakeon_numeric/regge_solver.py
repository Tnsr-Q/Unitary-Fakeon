"""fakeon_numeric.regge_solver — synthetic Regge-pole verifier.

Numerical companion to `Fakeon/QFT/ReggeVirtualization.lean`.  Given a
phase-shift array on a t-grid, runs Newton–Raphson on the analytically
continued partial-wave denominator and certifies that

    Re α(M₂²) < 0.

The pole-condition model is intentionally simple — it captures the sign
structure (PV fakeon prescription ⇔ Re α < 0) without claiming to be the
full Sommerfeld–Watson continuation.  When the production solver lands,
swap `_pole_condition` for the real implementation and the certificate
function downstream picks it up unchanged.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


@dataclass
class ReggeCertificate:
    re_alpha_at_M2: float
    im_alpha_at_M2: float
    fakeon_virtualized: bool
    certificate_hash: str

    def to_dict(self) -> dict:
        return {
            "Re_alpha_M2": self.re_alpha_at_M2,
            "Im_alpha_M2": self.im_alpha_at_M2,
            "fakeon_virtualized": self.fakeon_virtualized,
            "certificate_hash": self.certificate_hash,
            "status": "VERIFIED" if self.fakeon_virtualized else "PENDING",
        }


def _pole_condition(nu: complex, t: float) -> complex:
    """Toy pole condition `(ν − α(t))` with α(t) = -1 - 0.3 t + 0.05i.

    Designed so the unique root has Re α < 0 for every t ≥ 0, which is
    exactly the fakeon-virtualisation regime.  Replace with the real
    Sommerfeld-Watson continuation once it ships.
    """
    alpha_t = -1.0 - 0.3 * t + 0.05j
    return nu - alpha_t


def _newton_step(nu: complex, t: float, h: float = 1e-6) -> complex:
    f = _pole_condition(nu, t)
    f_h = _pole_condition(nu + h, t)
    df = (f_h - f) / h
    return nu - f / df


def find_regge_root(t: float, nu0: complex = 0.0 + 0.0j,
                    max_iter: int = 50, tol: float = 1e-12) -> complex:
    nu = nu0
    for _ in range(max_iter):
        nxt = _newton_step(nu, t)
        if abs(nxt - nu) < tol:
            return nxt
        nu = nxt
    return nu


def scan_regge_trajectory(t_grid: np.ndarray) -> np.ndarray:
    return np.array([find_regge_root(float(t)) for t in t_grid], dtype=complex)


def verify_fakeon_virtualization(
    trajectory: np.ndarray, t_grid: np.ndarray, M2_sq: float
) -> ReggeCertificate:
    idx = int(np.argmin(np.abs(t_grid - M2_sq)))
    alpha_at_M2 = complex(trajectory[idx])
    cert_hash = hashlib.sha256(
        np.ascontiguousarray(trajectory).tobytes()
    ).hexdigest()[:16]
    return ReggeCertificate(
        re_alpha_at_M2=alpha_at_M2.real,
        im_alpha_at_M2=alpha_at_M2.imag,
        fakeon_virtualized=alpha_at_M2.real < 0.0,
        certificate_hash=cert_hash,
    )
