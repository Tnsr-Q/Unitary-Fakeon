"""Tests for scripts.extract_cvec — HyperInt/DiffExp master dump parser
and for fakeon_numeric.boundary_vectors loader."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from fakeon_numeric import boundary_vectors as bv
from scripts import extract_cvec as ex


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def test_loader_analytic_fallback_shapes(tmp_path, monkeypatch):
    """With no c_vectors.json the analytic fallback yields four 6-D arrays."""
    monkeypatch.setattr(bv, "_JSON_PATH", tmp_path / "does_not_exist.json")
    vecs = bv.load_boundary_vectors()
    assert set(vecs.keys()) == {"4", "5", "6", "7"}
    for w, v in vecs.items():
        assert v.shape == (6,)
        assert np.isrealobj(v)
        assert np.all(np.isfinite(v))
    assert not bv.is_from_hyperint() is True  # tautology; path missing
    assert bv.pv_reality_residual(vecs) == 0.0


def test_loader_prefers_json(tmp_path, monkeypatch):
    """When c_vectors.json exists, its contents override the fallback."""
    payload = {
        "4": [1, 2, 3, 4, 5, 6],
        "5": [0, 0, 0, 0, 0, 0],
        "6": [-1, -1, -1, -1, -1, -1],
        "7": [0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625],
    }
    p = tmp_path / "c_vectors.json"
    p.write_text(json.dumps(payload))
    monkeypatch.setattr(bv, "_JSON_PATH", p)

    vecs = bv.load_boundary_vectors()
    np.testing.assert_allclose(vecs["4"], payload["4"])
    np.testing.assert_allclose(vecs["7"], payload["7"])
    assert bv.is_from_hyperint()


def test_loader_rejects_bad_shape(tmp_path, monkeypatch):
    p = tmp_path / "c_vectors.json"
    p.write_text(json.dumps({"4": [1, 2], "5": [], "6": [], "7": []}))
    monkeypatch.setattr(bv, "_JSON_PATH", p)
    with pytest.raises(ValueError):
        bv.load_boundary_vectors()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


_SAMPLE_DUMP = """
(* synthetic HyperInt output, PV base point (1/2, 1/3) *)
Master[1] = 1 + 0*eps + (Pi^2/6)*eps^2 + (-Pi^4/15)*eps^4 + (32*Zeta[5])*eps^5 + 0*eps^6 + (128*Zeta[7])*eps^7;
Master[2] = 2 + (Zeta[3])*eps^3 + (-2*Pi^4/15)*eps^4 + (-8*Zeta[5])*eps^5 + 0*eps^6 + (-64*Zeta[7])*eps^7;
Master[3] = 0 + (-2*Pi^4/15)*eps^4 + (-8*Zeta[5])*eps^5 + 0*eps^6 + (-64*Zeta[7])*eps^7;
Master[4] = 0 + 0*eps^4 + (4*Zeta[5])*eps^5 + 0*eps^6 + (32*Zeta[7])*eps^7;
Master[5] = 0 + (-Pi^4/5)*eps^4 + (-12*Zeta[5])*eps^5 + 0*eps^6 + (-96*Zeta[7])*eps^7;
Master[6] = 0 + (-Pi^4/15)*eps^4 + (-8*Zeta[5])*eps^5 + 0*eps^6 + (-64*Zeta[7])*eps^7;
"""


def test_mma_to_python_translation():
    assert "mp.pi" in ex._mma_to_python("Pi")
    assert ex._mma_to_python("Pi^4") == "(mp.pi**4)"
    assert ex._mma_to_python("Zeta[5]") == "zeta(5)"
    assert "**" in ex._mma_to_python("x^2")


def test_safe_eval_basic():
    import math

    assert ex._safe_eval("1") == pytest.approx(1.0)
    assert ex._safe_eval("Pi^2/6") == pytest.approx(math.pi ** 2 / 6)
    # Zeta[3] ≈ 1.20205690315959...
    assert ex._safe_eval("Zeta[3]") == pytest.approx(1.2020569031595942, rel=1e-10)


def test_parse_mathematica_dump_roundtrip(tmp_path):
    src = tmp_path / "masters.m"
    src.write_text(_SAMPLE_DUMP)
    coeffs = ex.parse_mathematica_dump(src)

    # Shapes
    for w in ("4", "5", "6", "7"):
        assert coeffs[w].shape == (6,)

    # Weight-5 vector should match the analytic fallback literals.
    import math
    from mpmath import zeta as mpzeta

    z5 = float(mpzeta(5))
    expected_c5 = np.array(
        [32 * z5, -8 * z5, -8 * z5, 4 * z5, -12 * z5, -8 * z5]
    )
    np.testing.assert_allclose(coeffs["5"], expected_c5, rtol=1e-10, atol=1e-12)

    # Weight-6 is all zero in our sample.
    np.testing.assert_allclose(coeffs["6"], np.zeros(6), atol=1e-12)


def test_end_to_end_save_and_load(tmp_path, monkeypatch):
    src = tmp_path / "masters.m"
    src.write_text(_SAMPLE_DUMP)
    out = tmp_path / "c_vectors.json"

    rc = ex.main(["--input", str(src), "--out", str(out)])
    assert rc == 0
    assert out.exists()

    # Redirect loader to the produced file.
    monkeypatch.setattr(bv, "_JSON_PATH", out)
    vecs = bv.load_boundary_vectors()
    import math
    from mpmath import zeta as mpzeta

    z5 = float(mpzeta(5))
    np.testing.assert_allclose(
        vecs["5"],
        [32 * z5, -8 * z5, -8 * z5, 4 * z5, -12 * z5, -8 * z5],
        rtol=1e-10,
        atol=1e-12,
    )


def test_cli_missing_input_returns_nonzero(tmp_path):
    rc = ex.main(["--input", str(tmp_path / "nope.m")])
    assert rc != 0
