"""Tests for scripts.assemble_certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import assemble_certificate as ac


def _prepare_repo(tmp_path: Path) -> Path:
    """Minimal anchor.json fixture (real shape, synthetic entries)."""
    anchor = {
        "schema_version": 1,
        "generated_at": "2026-04-29T00:00:00+00:00",
        "input": "logs/status_matrix.json",
        "input_sha256": "a" * 64,
        "leaves": [
            {
                "component": "Lean_Foo",
                "leaf_hash": "b" * 64,
                "row_digest": {
                    "component": "Lean_Foo",
                    "status": "VERIFIED",
                    "dependencies": ["A1", "S2"],
                    "audit_checksum": "c" * 16,
                },
            },
            {
                "component": "Test_Bar",
                "leaf_hash": "d" * 64,
                "row_digest": {
                    "component": "Test_Bar",
                    "status": "VERIFIED",
                    "dependencies": ["A4"],
                    "audit_checksum": "e" * 16,
                },
            },
        ],
        "levels": [["b" * 64, "d" * 64], ["f" * 64]],
        "merkle_root": "f" * 64,
        "n_components": 2,
    }
    p = tmp_path / "anchor.json"
    p.write_text(json.dumps(anchor))
    return p


def test_build_certificate_shape(tmp_path):
    anchor = _prepare_repo(tmp_path)
    cert = ac.build_certificate(anchor_path=anchor, n_points=32)

    for k in ("schema_version", "regge", "pl", "bootstrap_optical",
              "s1_distributional_limit", "boundary_vectors", "merkle",
              "assumptions", "status", "signature", "basis", "generated_at"):
        assert k in cert, f"missing key: {k}"

    assert cert["merkle"]["merkle_root"] == "f" * 64
    assert cert["merkle"]["n_components"] == 2
    assert cert["assumptions"] == ["A1", "A4", "S2"]
    # All component gates should pass in the default configuration.
    assert cert["regge"]["fakeon_virtualized"] is True
    assert cert["pl"]["pl_passed"] is True
    assert cert["bootstrap_optical"]["optical_inequality_satisfied"] is True
    assert cert["s1_distributional_limit"]["satisfied"] is True
    assert cert["boundary_vectors"]["weight7_pv_real"] is True
    if cert["boundary_vectors"]["source"] == "hyperint":
        assert cert["status"] == "VERIFIED"
    else:
        assert cert["status"] == "DEMONSTRATED"


def test_s1_block_content(tmp_path):
    """The S.1 certificate block carries the probe's actual numerics."""
    anchor = _prepare_repo(tmp_path)
    cert = ac.build_certificate(anchor_path=anchor, n_points=32)
    s1 = cert["s1_distributional_limit"]
    import math
    assert s1["probe"] == "gaussian"
    assert s1["target"] == pytest.approx(-math.pi)
    assert len(s1["eta_ladder"]) == len(s1["integrals"]) == len(s1["abs_residuals"])
    assert s1["best_residual"] == min(s1["abs_residuals"])
    assert s1["monotone"] is True
    assert s1["satisfied"] is True


def test_signature_is_deterministic_and_covers_payload(tmp_path):
    anchor = _prepare_repo(tmp_path)
    cert = ac.build_certificate(anchor_path=anchor, n_points=32)
    # The signature is SHA-256 of canonical JSON excluding the signature
    # field itself (generated_at IS covered).
    s = cert.pop("signature")
    canonical = json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == s


def test_signature_changes_when_payload_changes(tmp_path):
    anchor = _prepare_repo(tmp_path)
    c1 = ac.build_certificate(anchor_path=anchor, n_points=32, M2_sq=1.0)
    c2 = ac.build_certificate(anchor_path=anchor, n_points=32, M2_sq=1.5)
    assert c1["signature"] != c2["signature"]
    assert c1["regge"]["M2_sq"] != c2["regge"]["M2_sq"]


def test_cli_writes_file_and_exit_zero(tmp_path, monkeypatch):
    anchor = _prepare_repo(tmp_path)
    out = tmp_path / "FakeonCertificate.json"
    rc = ac.main([
        "--anchor", str(anchor),
        "--out", str(out),
        "--n-points", "32",
    ])
    assert rc == 0
    assert out.exists()
    cert = json.loads(out.read_text())
    assert cert["status"] in {"VERIFIED", "DEMONSTRATED"}
    assert len(cert["signature"]) == 64


def test_demonstrated_when_boundary_vectors_are_fallback(tmp_path, monkeypatch):
    anchor = _prepare_repo(tmp_path)
    monkeypatch.setattr(ac, "_boundary_vectors_block", lambda: {
        "source": "analytic_fallback",
        "weight7_pv_real": True,
        "c7_linf": 1.0,
        "c5_linf": 1.0,
    })
    cert = ac.build_certificate(anchor_path=anchor, n_points=32)
    assert cert["status"] == "DEMONSTRATED"


def test_cli_require_verified_fails_when_missing_anchor(tmp_path):
    with pytest.raises(FileNotFoundError):
        ac.build_certificate(anchor_path=tmp_path / "does-not-exist.json")
