"""scripts/fakeon_validation_ci.py — CI entry point for the Fakeon suite.

Runs the pytest battery under `tests/` with verbose output.  Intended to
be invoked from CI; exits non-zero on any failure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    return subprocess.call(
        [sys.executable, "-m", "pytest", "-v", str(repo / "tests")]
    )


if __name__ == "__main__":
    raise SystemExit(main())
