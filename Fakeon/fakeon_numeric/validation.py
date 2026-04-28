"""fakeon_numeric.validation — bridge between numeric loaders and sympy tests.

Exposes the legacy sympy API consumed by
``tests/test_massive_flatness.py``:

    load_boundary_vectors() -> (c4, c5, c6)   # sympy column Matrices
    load_c7()               -> c7             # sympy column Matrix

Backed by :mod:`fakeon_numeric.boundary_vectors`.
"""

from __future__ import annotations

from typing import Tuple

import sympy as sp

from .boundary_vectors import load_boundary_vectors as _load_np


def _to_sp_col(arr) -> sp.Matrix:
    return sp.Matrix(6, 1, [sp.nsimplify(float(x), rational=False) for x in arr])


def load_boundary_vectors() -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return (c4, c5, c6) as 6×1 sympy Matrices.

    Entries are promoted from the numpy loader via ``sp.nsimplify`` with
    no rationalisation, so numerical HyperInt data stays numerical while
    analytic fallbacks (ζ, π combinations pre-floated) keep full float
    precision.
    """
    vecs = _load_np()
    return _to_sp_col(vecs["4"]), _to_sp_col(vecs["5"]), _to_sp_col(vecs["6"])


def load_c7() -> sp.Matrix:
    """Return c7 as a 6×1 sympy Matrix."""
    vecs = _load_np()
    return _to_sp_col(vecs["7"])


def validate_masters(*_args, **_kwargs) -> bool:  # pragma: no cover
    """Stub.  Returns True until the contour-integration validator lands."""
    raise NotImplementedError("fakeon_numeric.validation.validate_masters: stub")


__all__ = ["load_boundary_vectors", "load_c7", "validate_masters"]
