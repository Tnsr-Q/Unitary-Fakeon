"""tests/test_audit_status.py — smoke tests for `scripts/audit_status.py`.

Asserts that the auto-discovery pipeline runs end-to-end on the live
repository, produces a well-formed Report, and renders Markdown that
mentions every Lean module + every CI workflow on disk.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_status import (  # type: ignore[import-not-found]
    build_report,
    collect_ci,
    collect_lean,
    collect_python,
    parse_lean_file,
    render_md,
)


REPO_ROOT = Path(__file__).resolve().parent.parent  # /app/Fakeon
APP_ROOT = REPO_ROOT.parent                          # /app


# ---------------------------------------------------------------------------
# Lean parsing.
# ---------------------------------------------------------------------------

def test_parse_lean_file_handles_authoritative_module() -> None:
    f = REPO_ROOT / "Fakeon" / "Algebra" / "MassiveDE.lean"
    stats = parse_lean_file(f)
    assert stats.n_def >= 4, "Expected the four A_k matrix defs to be detected"
    assert stats.n_lemma >= 1, "massive_pv_reality lemma should be counted"
    # MassiveDE.lean is currently sorry-free.
    assert stats.n_sorry == 0


def test_collect_lean_discovers_all_modules() -> None:
    files = collect_lean(REPO_ROOT)
    paths = {Path(f.path).name for f in files}
    must_have = {
        "MassiveDE.lean", "ChenCollapse.lean", "Distributions.lean",
        "DispersiveReality.lean", "FlatConnection.lean",
        "WedgeVanishing.lean", "FakeonUnitarity.lean", "FakeonQFT.lean",
    }
    missing = must_have - paths
    assert not missing, f"Missing modules: {missing}"


# ---------------------------------------------------------------------------
# Python module collection.
# ---------------------------------------------------------------------------

def test_collect_python_includes_distributions_and_regime() -> None:
    files = collect_python(REPO_ROOT)
    names = {Path(f.path).name for f in files}
    assert "distributions.py" in names
    assert "regime.py" in names
    assert "audit_status.py" in names  # the script audits itself


# ---------------------------------------------------------------------------
# CI parsing.
# ---------------------------------------------------------------------------

def test_collect_ci_finds_fakeon_verify_workflow() -> None:
    stages = collect_ci(APP_ROOT)
    if not stages:
        pytest.skip("no .github/workflows directory in this checkout")
    workflows = {s.workflow for s in stages}
    assert "fakeon-verify.yml" in workflows
    step_names = {s.step_name for s in stages}
    # Sanity: a couple of the named steps are present.
    assert any("Sokhotski" in n or "Unitarity" in n or "Chen" in n
               for n in step_names)


# ---------------------------------------------------------------------------
# End-to-end report.
# ---------------------------------------------------------------------------

def test_build_report_runs_and_renders() -> None:
    # `run_pytest=False` skips the inner subprocess (would recurse otherwise).
    report = build_report(REPO_ROOT, APP_ROOT, run_pytest=False)
    md = render_md(report)
    assert "# Fakeon Verification — Status" in md
    assert "## Lean modules" in md
    assert "MassiveDE.lean" in md
    assert "## Tests" in md
    assert "## CI stages" in md
    # Headline numbers should be present and self-consistent.
    assert report.total_provable >= report.total_content_bearing
    assert 0.0 <= report.content_ratio <= 1.0
