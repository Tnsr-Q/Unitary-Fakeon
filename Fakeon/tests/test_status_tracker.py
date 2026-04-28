"""tests/test_status_tracker.py — coverage for `fakeon_numeric.status_tracker`."""

from __future__ import annotations

import json
from pathlib import Path


from fakeon_numeric.status_tracker import (
    VALID_STATUSES,
    AuditRow,
    assert_all_verified,
    export_status_matrix,
    load_registry,
    verify_component_status,
)
from fakeon_numeric.tolerance_ledger import (
    reset_ledger,
    update_ledger,
)


REPO_ROOT = Path(__file__).resolve().parent.parent  # /app/Fakeon


# ---------------------------------------------------------------------------
# Registry sanity.
# ---------------------------------------------------------------------------

def test_registry_loads_and_is_well_formed() -> None:
    reg = load_registry()
    assert reg["schema_version"] == 1
    assert set(reg["status_levels"]).issubset(VALID_STATUSES | {"METADATA"})
    components = reg["components"]
    assert len(components) >= 10
    for name, meta in components.items():
        assert meta["status"] in VALID_STATUSES, (
            f"{name} has unknown status {meta['status']!r}"
        )
        assert isinstance(meta.get("assumptions", []), list)


# ---------------------------------------------------------------------------
# Per-status verification rules.
# ---------------------------------------------------------------------------

def test_proved_with_sorry_fails(tmp_path: Path) -> None:
    """A PROVED row whose Lean file contains `sorry` must fail."""
    fake_lean = tmp_path / "Fake.lean"
    fake_lean.write_text("theorem foo : True := by sorry\n", encoding="utf-8")
    meta = {
        "status": "PROVED",
        "assumptions": [],
        "lean_file": "Fake.lean",
        "ledger_key": None,
    }
    row = verify_component_status("Fake_Proved", meta, tmp_path)
    assert isinstance(row, AuditRow)
    assert row.ci_verified is False
    assert "sorry" in row.note.lower()


def test_proved_without_sorry_passes(tmp_path: Path) -> None:
    fake_lean = tmp_path / "Fake.lean"
    fake_lean.write_text("theorem foo : True := trivial\n", encoding="utf-8")
    meta = {
        "status": "PROVED",
        "assumptions": [],
        "lean_file": "Fake.lean",
        "ledger_key": None,
    }
    row = verify_component_status("Fake_Proved", meta, tmp_path)
    assert row.ci_verified is True


def test_verified_uses_tolerance_ledger() -> None:
    reset_ledger()
    update_ledger("my_check", residual=1e-15, passed=True)
    meta = {
        "status": "VERIFIED",
        "assumptions": [],
        "lean_file": None,
        "ledger_key": "my_check",
    }
    row = verify_component_status("Fake_Verified", meta, REPO_ROOT)
    assert row.ci_verified is True

    update_ledger("my_check", residual=1.0, passed=False)
    row2 = verify_component_status("Fake_Verified", meta, REPO_ROOT)
    assert row2.ci_verified is False
    assert "not passing" in row2.note


def test_demonstrated_requires_lean_file_when_specified(tmp_path: Path) -> None:
    meta = {
        "status": "DEMONSTRATED",
        "assumptions": ["A1"],
        "lean_file": "DoesNotExist.lean",
        "ledger_key": None,
    }
    row = verify_component_status("Fake_Demonstrated", meta, tmp_path)
    assert row.ci_verified is False
    assert "missing" in row.note.lower()


def test_pending_always_passes() -> None:
    meta = {"status": "PENDING", "assumptions": [], "lean_file": None}
    row = verify_component_status("Fake_Pending", meta, REPO_ROOT)
    assert row.ci_verified is True


def test_metadata_always_passes() -> None:
    meta = {"status": "METADATA", "assumptions": [], "lean_file": None}
    row = verify_component_status("Fake_Metadata", meta, REPO_ROOT)
    assert row.ci_verified is True


def test_unknown_status_fails() -> None:
    meta = {"status": "MIRACULOUS", "assumptions": []}
    row = verify_component_status("Fake_Unknown", meta, REPO_ROOT)
    assert row.ci_verified is False
    assert "unknown status" in row.note.lower()


# ---------------------------------------------------------------------------
# End-to-end matrix export.
# ---------------------------------------------------------------------------

def test_export_status_matrix_runs() -> None:
    matrix = export_status_matrix(REPO_ROOT)
    # All rows must carry the four expected keys.
    for name, row in matrix.items():
        for key in ("status", "dependencies", "audit_checksum", "ci_verified"):
            assert key in row, f"row {name!r} missing key {key!r}"
    # At least one METADATA row exists (Assumptions cert).
    assert any(r["status"] == "METADATA" for r in matrix.values())


def test_assert_all_verified_on_live_repo() -> None:
    """Live repo must pass — the tracker is part of the build contract."""
    matrix = export_status_matrix(REPO_ROOT)
    # Persist for downstream tooling regardless of test outcome.
    out = REPO_ROOT / "logs" / "status_matrix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    assert_all_verified(matrix)
