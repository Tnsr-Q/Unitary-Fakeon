"""tests/test_numeric_imports.py — smoke tests for the fakeon_numeric package.

Asserts that every advertised sub-module imports without error.  These are
placeholder modules today; the test guards against accidental layout drift.
"""

from __future__ import annotations

import importlib

import pytest

MODULES = [
    "fakeon_numeric",
    "fakeon_numeric.validation",
    "fakeon_numeric.partial_wave",
    "fakeon_numeric.omega_quadrature",
    "fakeon_numeric.radial_interpolator",
    "fakeon_numeric.siegel_theta",
    "fakeon_numeric.schwarzschild_radial_solver",
    "fakeon_numeric.regime",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_importable(module_name: str) -> None:
    importlib.import_module(module_name)
