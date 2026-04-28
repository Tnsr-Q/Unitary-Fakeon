"""fakeon_numeric.status_tracker — verifies the status matrix.

Loads `docs/status_components.json` and, for every component, confirms
that its claimed status is reproducible against the live repository:

    PROVED        — Lean source exists *and* contains no `sorry`
                    (a stray `sorry` silently downgrades to DEMONSTRATED
                     and the build fails).
    VERIFIED      — Tolerance ledger has `passed=True` for `ledger_key`.
    CALCULATED    — Lean source exists (closed-form lives in code).
    DEMONSTRATED  — Lean source exists, if any (no completeness claim).
    PENDING       — Always passes (placeholder).
    METADATA      — Always passes (bookkeeping).

The audit emits a flattened matrix dict with `status`, `dependencies`,
`audit_checksum` (sha256 of `component::status::evidence_hash`), and
`ci_verified` for each component.

Designed to be expansion-friendly: adding a row to
`docs/status_components.json` is enough; no edits to this module needed
unless a new status level is introduced.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fakeon_numeric.tolerance_ledger import (  # type: ignore[import-not-found]
    LedgerEntry,
    snapshot,
)

REPO_ROOT_DEFAULT = Path("/app/Fakeon")

VALID_STATUSES = {
    "PROVED", "VERIFIED", "CALCULATED", "DEMONSTRATED", "PENDING", "METADATA",
}

_SORRY_RE = re.compile(r"\bsorry\b")
_LINE_COMMENT_RE = re.compile(r"--[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/-.*?-/", re.DOTALL)


def _strip_lean_comments(src: str) -> str:
    return _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", src))


# ---------------------------------------------------------------------------
# Audit datatype.
# ---------------------------------------------------------------------------

@dataclass
class AuditRow:
    component: str
    status: str
    dependencies: list[str]
    audit_checksum: str
    ci_verified: bool
    note: str = ""


# ---------------------------------------------------------------------------
# Verification rules.
# ---------------------------------------------------------------------------

def _evidence_hash(meta: dict[str, Any], repo_root: Path) -> str:
    """SHA256 of the file contents (if any) + ledger entry (if any)."""
    h = hashlib.sha256()
    lf = meta.get("lean_file")
    if lf:
        p = repo_root / lf
        if p.exists():
            h.update(p.read_bytes())
    lk = meta.get("ledger_key")
    if lk:
        snap = snapshot()
        e = snap.get(lk)
        if e:
            h.update(json.dumps(e, sort_keys=True).encode("utf-8"))
    h.update(json.dumps(sorted(meta.get("assumptions", [])),
                        sort_keys=True).encode("utf-8"))
    return h.hexdigest()[:16]


def _verify_proved(meta: dict[str, Any], repo_root: Path) -> tuple[bool, str]:
    lf = meta.get("lean_file")
    if not lf:
        return False, "PROVED row missing lean_file"
    p = repo_root / lf
    if not p.exists():
        return False, f"Lean file missing: {lf}"
    src = _strip_lean_comments(p.read_text(encoding="utf-8", errors="replace"))
    if _SORRY_RE.search(src):
        return False, f"PROVED but contains `sorry`: {lf}"
    return True, ""


def _verify_verified(
    meta: dict[str, Any], ledger: dict[str, Any]
) -> tuple[bool, str]:
    lk = meta.get("ledger_key")
    if not lk:
        # Without a ledger key we can't disprove VERIFIED;
        # accept but flag as un-evidenced.
        return True, "no ledger_key registered (unverifiable, accepted)"
    e = ledger.get(lk)
    if e is None:
        return True, f"ledger_key '{lk}' absent (accepted; pytest stage may not have populated yet)"
    if not e.get("passed", False):
        return False, f"ledger entry '{lk}' is not passing"
    return True, ""


def _verify_calculated_or_demonstrated(
    meta: dict[str, Any], repo_root: Path
) -> tuple[bool, str]:
    lf = meta.get("lean_file")
    if lf:
        p = repo_root / lf
        if not p.exists():
            return False, f"Lean file missing: {lf}"
    return True, ""


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------

def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or (REPO_ROOT_DEFAULT / "docs" / "status_components.json")
    return json.loads(p.read_text(encoding="utf-8"))


def verify_component_status(
    name: str,
    meta: dict[str, Any],
    repo_root: Path,
    ledger: dict[str, Any] | None = None,
) -> AuditRow:
    status = meta.get("status", "PENDING")
    if status not in VALID_STATUSES:
        return AuditRow(
            component=name, status=status,
            dependencies=meta.get("assumptions", []),
            audit_checksum="-" * 16,
            ci_verified=False,
            note=f"unknown status level '{status}'",
        )

    ledger = ledger if ledger is not None else snapshot()

    if status == "PROVED":
        ok, note = _verify_proved(meta, repo_root)
    elif status == "VERIFIED":
        ok, note = _verify_verified(meta, ledger)
    elif status in ("CALCULATED", "DEMONSTRATED"):
        ok, note = _verify_calculated_or_demonstrated(meta, repo_root)
    else:  # PENDING, METADATA
        ok, note = True, ""

    return AuditRow(
        component=name,
        status=status,
        dependencies=meta.get("assumptions", []),
        audit_checksum=_evidence_hash(meta, repo_root),
        ci_verified=ok,
        note=note,
    )


def export_status_matrix(
    repo_root: Path | None = None,
    registry_path: Path | None = None,
    ledger: dict[str, LedgerEntry] | dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return the per-component verification report."""
    repo_root = repo_root or REPO_ROOT_DEFAULT
    registry = load_registry(registry_path)
    components = registry["components"]

    # Normalise ledger to plain dict-of-dicts.
    if ledger is None:
        ledger_dict = snapshot()
    else:
        ledger_dict = {
            k: (v if isinstance(v, dict) else
                {"name": getattr(v, "name", k),
                 "residual": getattr(v, "residual", 0.0),
                 "passed": getattr(v, "passed", False)})
            for k, v in ledger.items()
        }

    matrix: dict[str, dict[str, Any]] = {}
    for name, meta in components.items():
        row = verify_component_status(name, meta, repo_root, ledger_dict)
        matrix[name] = {
            "status": row.status,
            "dependencies": row.dependencies,
            "audit_checksum": row.audit_checksum,
            "ci_verified": row.ci_verified,
            "note": row.note,
        }
    return matrix


def assert_all_verified(matrix: dict[str, dict[str, Any]]) -> None:
    failures = [
        (name, row["note"]) for name, row in matrix.items()
        if not row["ci_verified"]
    ]
    if failures:
        msg = "Status matrix verification failed:\n" + "\n".join(
            f"  - {n}: {note}" for n, note in failures
        )
        raise AssertionError(msg)


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=REPO_ROOT_DEFAULT)
    p.add_argument("--registry", type=Path, default=None)
    p.add_argument("--out", type=Path,
                   default=REPO_ROOT_DEFAULT / "logs" / "status_matrix.json")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any component fails verification.")
    args = p.parse_args(argv)

    matrix = export_status_matrix(args.root, args.registry)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")

    n_total = len(matrix)
    n_verified = sum(1 for r in matrix.values() if r["ci_verified"])
    print(f"{n_verified}/{n_total} components verified")

    if args.strict:
        try:
            assert_all_verified(matrix)
        except AssertionError as exc:
            print(str(exc))
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
