"""tests/test_anchor_status.py — coverage for `scripts/anchor_status.py`."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.anchor_status import (  # type: ignore[import-not-found]
    _leaf_hash,
    _merkle_levels,
    _merkle_proof,
    _verify_proof,
    build_anchor,
)


REPO_ROOT = Path(__file__).resolve().parent.parent  # /app/Fakeon


@pytest.fixture()
def status_matrix(tmp_path: Path) -> Path:
    """Tiny but representative status_matrix.json for unit tests."""
    matrix = {
        "Alpha": {"status": "PROVED",
                  "dependencies": ["A1"],
                  "audit_checksum": "1234567890abcdef",
                  "ci_verified": True, "note": ""},
        "Beta":  {"status": "VERIFIED",
                  "dependencies": ["A2", "S2"],
                  "audit_checksum": "abcdef1234567890",
                  "ci_verified": True, "note": ""},
        "Gamma": {"status": "DEMONSTRATED",
                  "dependencies": [],
                  "audit_checksum": "deadbeefcafebabe",
                  "ci_verified": True, "note": ""},
    }
    p = tmp_path / "status_matrix.json"
    p.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Determinism.
# ---------------------------------------------------------------------------

def test_build_anchor_is_deterministic(status_matrix: Path) -> None:
    a1 = build_anchor(status_matrix)
    a2 = build_anchor(status_matrix)
    assert a1.merkle_root == a2.merkle_root
    assert a1.input_sha256 == a2.input_sha256
    assert a1.leaves == a2.leaves


def test_components_are_sorted(status_matrix: Path) -> None:
    a = build_anchor(status_matrix)
    names = [leaf["component"] for leaf in a.leaves]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# Tamper detection.
# ---------------------------------------------------------------------------

def test_root_changes_when_row_modified(status_matrix: Path) -> None:
    original = build_anchor(status_matrix)

    matrix = json.loads(status_matrix.read_text())
    matrix["Beta"]["audit_checksum"] = "0" * 16
    status_matrix.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    tampered = build_anchor(status_matrix)
    assert tampered.merkle_root != original.merkle_root
    assert tampered.input_sha256 != original.input_sha256


def test_root_changes_when_row_added(status_matrix: Path) -> None:
    original = build_anchor(status_matrix)

    matrix = json.loads(status_matrix.read_text())
    matrix["Delta"] = {
        "status": "PENDING", "dependencies": [],
        "audit_checksum": "1111111111111111",
        "ci_verified": True, "note": "",
    }
    status_matrix.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    bigger = build_anchor(status_matrix)
    assert bigger.merkle_root != original.merkle_root
    assert bigger.n_components == original.n_components + 1


# ---------------------------------------------------------------------------
# Merkle proof correctness.
# ---------------------------------------------------------------------------

def test_inclusion_proof_round_trip(status_matrix: Path) -> None:
    a = build_anchor(status_matrix)
    for i, leaf in enumerate(a.leaves):
        proof = _merkle_proof(a.levels, i)
        assert _verify_proof(leaf["leaf_hash"], proof, a.merkle_root), (
            f"proof failed for component {leaf['component']!r}"
        )


def test_invalid_proof_fails(status_matrix: Path) -> None:
    a = build_anchor(status_matrix)
    leaf = a.leaves[0]["leaf_hash"]
    bad_proof = _merkle_proof(a.levels, 0)
    if bad_proof:
        # Flip one bit in the first sibling.
        h = bad_proof[0]["hash"]
        flipped = "f" + h[1:] if h[0] != "f" else "0" + h[1:]
        bad_proof[0]["hash"] = flipped
        assert not _verify_proof(leaf, bad_proof, a.merkle_root)


def test_leaf_hash_format_is_64_hex_chars() -> None:
    h = _leaf_hash("X", {"status": "PROVED",
                          "dependencies": ["A"],
                          "audit_checksum": "0" * 16})
    assert len(h) == 64
    int(h, 16)  # must parse as hex


# ---------------------------------------------------------------------------
# Padding behaviour for odd leaf counts.
# ---------------------------------------------------------------------------

def test_odd_leaf_padding() -> None:
    # 3 leaves → padded to 4 at level 0 (last duplicated)
    leaves = ["aa" * 32, "bb" * 32, "cc" * 32]
    levels = _merkle_levels(leaves)
    # level 0 stays at 3 in our representation, but the level 1 hash
    # is computed as if cc were duplicated.
    assert len(levels[0]) == 3
    # Level 1 has two nodes.
    assert len(levels[1]) == 2
    # Top-of-tree is a single root.
    assert len(levels[-1]) == 1


# ---------------------------------------------------------------------------
# CLI smoke test.
# ---------------------------------------------------------------------------

def test_cli_build_then_verify(status_matrix: Path, tmp_path: Path) -> None:
    anchor_out = tmp_path / "anchor.json"
    cp = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "anchor_status.py"),
         "build", "--input", str(status_matrix), "--out", str(anchor_out)],
        capture_output=True, text=True, check=False,
    )
    assert cp.returncode == 0, cp.stderr
    assert anchor_out.exists()

    cp = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "anchor_status.py"),
         "verify", "--anchor", str(anchor_out), "--input", str(status_matrix)],
        capture_output=True, text=True, check=False,
    )
    assert cp.returncode == 0
    assert "ANCHOR VERIFIED" in cp.stdout


def test_cli_verify_detects_tamper(status_matrix: Path, tmp_path: Path) -> None:
    anchor_out = tmp_path / "anchor.json"
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "anchor_status.py"),
         "build", "--input", str(status_matrix), "--out", str(anchor_out)],
        check=True, capture_output=True, text=True,
    )
    # Tamper the matrix.
    matrix = json.loads(status_matrix.read_text())
    matrix["Alpha"]["audit_checksum"] = "ffffffffffffffff"
    status_matrix.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    cp = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "anchor_status.py"),
         "verify", "--anchor", str(anchor_out), "--input", str(status_matrix)],
        capture_output=True, text=True, check=False,
    )
    assert cp.returncode != 0
    assert "FAILED" in cp.stderr
