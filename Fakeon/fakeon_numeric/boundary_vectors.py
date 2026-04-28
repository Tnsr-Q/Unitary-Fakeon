"""fakeon_numeric.boundary_vectors — single source of truth for c_k.

Loads weight-k boundary vectors c4..c7 for the massive Fakeon canonical DE,
evaluated at the PV base point (z0, y0) = (1/2, 1/3).

Source precedence:
  1. ``fakeon_numeric/c_vectors.json`` — produced by
     ``scripts/extract_cvec.py`` from a HyperInt/DiffExp master dump.
  2. Analytic fallback — closed-form zeta/Pi expressions, PV-real by
     construction.  Intended as a placeholder until HyperInt is run.

All vectors are 6-dimensional (one entry per master), real-valued.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np
from mpmath import mp, pi, zeta

mp.dps = 50

_JSON_PATH = Path(__file__).parent / "c_vectors.json"


def _analytic_fallback() -> Dict[str, np.ndarray]:
    """Closed-form PV-real boundary vectors (zeta / Pi basis).

    These are the weight-w literature values for the PV-projected
    crossed-box masters at (z0, y0) = (1/2, 1/3).  They are *not*
    guaranteed to satisfy the Chen weight-7 recursion against the
    current Lean-sourced M matrices (A5, A6 are still zero stubs),
    so the weight-7 cross-check is only activated when a real
    ``c_vectors.json`` is produced by HyperInt/DiffExp.
    """
    z3 = float(zeta(3))
    z5 = float(zeta(5))
    z7 = float(zeta(7))
    p2 = float(pi ** 2)
    p4 = float(pi ** 4)

    c4 = np.array(
        [-4 * p4 / 15, -2 * p4 / 15, -2 * p4 / 15, 0.0, -p4 / 5, -p4 / 15],
        dtype=float,
    )

    c5 = np.array(
        [32 * z5, -8 * z5, -8 * z5, 4 * z5, -12 * z5, -8 * z5],
        dtype=float,
    )

    # HyperInt fills the exact ζ₃² / π⁶ mix; leave zeros until then.
    c6 = np.zeros(6, dtype=float)

    c7 = np.array(
        [
            128 * z7 - 64 / 3 * p2 * z5 + 32 / 15 * p4 * z3,
            -64 * z7 + 32 / 3 * p2 * z5 - 16 / 15 * p4 * z3,
            -64 * z7 + 32 / 3 * p2 * z5 - 16 / 15 * p4 * z3,
            32 * z7 - 16 / 3 * p2 * z5 + 8 / 15 * p4 * z3,
            -96 * z7 + 16 * p2 * z5 - 24 / 5 * p4 * z3,
            -64 * z7 + 32 / 3 * p2 * z5 - 16 / 15 * p4 * z3,
        ],
        dtype=float,
    )

    return {"4": c4, "5": c5, "6": c6, "7": c7}


def load_boundary_vectors() -> Dict[str, np.ndarray]:
    """Return {"4": c4, "5": c5, "6": c6, "7": c7} as 6D float arrays.

    Pulls from ``c_vectors.json`` when present (HyperInt/DiffExp run),
    else from the analytic fallback.
    """
    if _JSON_PATH.exists():
        data = json.loads(_JSON_PATH.read_text())
        vecs = {k: np.asarray(v, dtype=float) for k, v in data.items()}
        for w in ("4", "5", "6", "7"):
            if w not in vecs:
                raise ValueError(
                    f"c_vectors.json is missing weight-{w} vector"
                )
            if vecs[w].shape != (6,):
                raise ValueError(
                    f"c_vectors.json weight-{w} has shape {vecs[w].shape}, "
                    f"expected (6,)"
                )
        return vecs
    return _analytic_fallback()


def is_from_hyperint() -> bool:
    """True if boundary vectors were loaded from a HyperInt dump."""
    return _JSON_PATH.exists()


def pv_reality_residual(vecs: Dict[str, np.ndarray]) -> float:
    """Max |Im| across all entries — zero for PV-real loads (by
    construction, since we store real arrays, but the hook exists for
    future complex intermediate parses)."""
    return 0.0 if all(np.isrealobj(v) for v in vecs.values()) else float(
        max(np.abs(np.asarray(v).imag).max() for v in vecs.values())
    )


__all__ = [
    "load_boundary_vectors",
    "is_from_hyperint",
    "pv_reality_residual",
]
