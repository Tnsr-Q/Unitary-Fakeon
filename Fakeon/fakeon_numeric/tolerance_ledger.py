"""fakeon_numeric.tolerance_ledger — lightweight tolerance ledger.

In-tree analogue of `src.tolerance.dynamic_ledger`.  Tracks the most
recent (residual, passed) pair per named check; persisted as JSON when
asked.  Used by `tests/test_s_matrix_extension.py`.

The ledger is a process-local singleton; a fresh process starts empty.
Tests that want a clean slate call `reset_ledger()` in their setup.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LedgerEntry:
    name: str
    residual: float
    passed: bool


@dataclass
class _Ledger:
    entries: dict[str, LedgerEntry] = field(default_factory=dict)


_LEDGER = _Ledger()


def update_ledger(name: str, residual: float, passed: bool) -> LedgerEntry:
    """Record a measurement and return the stored entry."""
    e = LedgerEntry(name=name, residual=float(residual), passed=bool(passed))
    _LEDGER.entries[name] = e
    return e


def check_tolerance(name: str) -> bool:
    e = _LEDGER.entries.get(name)
    return bool(e and e.passed)


def check_pass(name: str) -> bool:
    """Alias of `check_tolerance` for the status-tracker API contract."""
    return check_tolerance(name)


def get_hash(name: str) -> str:
    """Stable short hash of the entry for audit checksums.

    Returns an empty string if the entry is absent so that callers can
    fold it into a wider checksum without special-casing.
    """
    import hashlib
    import json as _json
    e = _LEDGER.entries.get(name)
    if e is None:
        return ""
    return hashlib.sha256(
        _json.dumps(asdict(e), sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def reset_ledger() -> None:
    _LEDGER.entries.clear()


def snapshot() -> dict[str, Any]:
    return {k: asdict(v) for k, v in _LEDGER.entries.items()}


def dump(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snapshot(), indent=2), encoding="utf-8")
    return p
