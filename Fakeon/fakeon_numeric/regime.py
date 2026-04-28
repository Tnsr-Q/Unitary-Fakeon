"""fakeon_numeric.regime — regime detector for reality / flatness diagnostics.

Maps the two analytic guardrails to a single regime classifier:

    * |Im[c_n]| > 1e-12  ⇒  DISPERSIVE_BREAKDOWN
    * rank(d ln α) > 1    ⇒  NON_PERTURBATIVE_BREAKDOWN

Returns `PERTURBATIVE` when both checks pass.  Numeric implementations
live in `tests/test_dispersive_reality.py` and
`tests/test_wedge_vanishing.py`; this module exposes the same predicates
for downstream callers.
"""

from __future__ import annotations

from enum import Enum

import numpy as np


class Regime(str, Enum):
    PERTURBATIVE = "PERTURBATIVE"
    DISPERSIVE_BREAKDOWN = "DISPERSIVE_BREAKDOWN"
    NON_PERTURBATIVE_BREAKDOWN = "NON_PERTURBATIVE_BREAKDOWN"


def classify(
    c_values: np.ndarray,
    alpha_traj: np.ndarray,
    im_tol: float = 1e-12,
    rank_tol: float = 1e-8,
) -> Regime:
    """Classify the current run into one of three regimes.

    Parameters
    ----------
    c_values : (N,) complex array of dispersive boundary constants.
    alpha_traj : (n_steps, n_params) RG trajectory.
    """
    if np.any(np.abs(np.asarray(c_values).imag) > im_tol):
        return Regime.DISPERSIVE_BREAKDOWN
    safe = np.maximum(alpha_traj, 1e-15)
    dln = np.gradient(np.log(safe), axis=0)
    if np.linalg.matrix_rank(dln, tol=rank_tol) > 1:
        return Regime.NON_PERTURBATIVE_BREAKDOWN
    return Regime.PERTURBATIVE
