#!/usr/bin/env python3
"""
scripts/audit_status.py

Single-pass auditor for the Fakeon verification stack.  Auto-discovers
Lean modules, Python modules, pytest files, and CI workflow stages and
emits a Markdown report at `docs/STATUS.md`.

Design goals
------------
* **Zero hardcoding.**  The script walks the repository, so adding a new
  `Fakeon/Foo/Bar.lean` or `tests/test_*.py` makes it appear in the next
  report automatically.
* **Per-file granularity.**  We record `axiom / theorem / lemma / def /
  sorry` counts per Lean file and report a "content-bearing" ratio
  (declarations without an inner `sorry`).
* **Cheap to extend.**  Adding a new metric is one helper function
  appended to the `_collect` block plus one row in `_render_md`.

Usage
-----
    python scripts/audit_status.py                       # writes docs/STATUS.md
    python scripts/audit_status.py --out -               # prints to stdout
    python scripts/audit_status.py --root /app/Fakeon    # alternate root

The script is read-only outside its `--out` target.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data classes.
# ---------------------------------------------------------------------------

@dataclass
class LeanFileStats:
    path: str
    n_axiom: int = 0
    n_theorem: int = 0
    n_lemma: int = 0
    n_def: int = 0
    n_sorry: int = 0
    n_decls_with_sorry: int = 0

    @property
    def n_decls(self) -> int:
        return self.n_axiom + self.n_theorem + self.n_lemma + self.n_def

    @property
    def n_provable(self) -> int:
        """Theorems + lemmas (definitions don't have a proof obligation)."""
        return self.n_theorem + self.n_lemma

    @property
    def n_content_bearing(self) -> int:
        return max(0, self.n_provable - self.n_decls_with_sorry)


@dataclass
class PythonFileStats:
    path: str
    n_lines: int = 0
    n_def: int = 0
    n_class: int = 0


@dataclass
class TestStats:
    path: str
    n_collected: int = 0


@dataclass
class CIStage:
    workflow: str
    job: str
    step_name: str
    runs: str  # the command


@dataclass
class Report:
    generated_at: str
    root: str
    lean: list[LeanFileStats] = field(default_factory=list)
    python: list[PythonFileStats] = field(default_factory=list)
    tests: list[TestStats] = field(default_factory=list)
    ci: list[CIStage] = field(default_factory=list)
    pytest_summary: dict[str, int] = field(default_factory=dict)

    # ---------- aggregate properties ----------
    @property
    def total_axioms(self) -> int:
        return sum(f.n_axiom for f in self.lean)

    @property
    def total_sorrys(self) -> int:
        return sum(f.n_sorry for f in self.lean)

    @property
    def total_provable(self) -> int:
        return sum(f.n_provable for f in self.lean)

    @property
    def total_content_bearing(self) -> int:
        return sum(f.n_content_bearing for f in self.lean)

    @property
    def content_ratio(self) -> float:
        return (
            self.total_content_bearing / self.total_provable
            if self.total_provable
            else 1.0
        )


# ---------------------------------------------------------------------------
# Lean parsing.
# ---------------------------------------------------------------------------

# A "declaration" starts at a line whose first non-whitespace token is one of
# the keywords below.  We split the file into [decl_i, decl_{i+1}) blocks and
# look for `sorry` inside each.

_DECL_KW = ("axiom", "theorem", "lemma", "def", "noncomputable def", "noncomputable axiom")
_DECL_RE = re.compile(
    r"^\s*(?:noncomputable\s+)?(axiom|theorem|lemma|def)\b",
    re.MULTILINE,
)
_SORRY_RE = re.compile(r"\bsorry\b")
# crude single-line comment stripper for `--` and block comments `/- ... -/`.
_LINE_COMMENT_RE = re.compile(r"--[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/-.*?-/", re.DOTALL)


def _strip_comments(src: str) -> str:
    return _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", src))


def parse_lean_file(path: Path) -> LeanFileStats:
    raw = path.read_text(encoding="utf-8", errors="replace")
    src = _strip_comments(raw)

    matches = list(_DECL_RE.finditer(src))
    stats = LeanFileStats(path=str(path))

    for i, m in enumerate(matches):
        kind = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
        block = src[start:end]
        block_has_sorry = bool(_SORRY_RE.search(block))

        if kind == "axiom":
            stats.n_axiom += 1
        elif kind == "theorem":
            stats.n_theorem += 1
            if block_has_sorry:
                stats.n_decls_with_sorry += 1
        elif kind == "lemma":
            stats.n_lemma += 1
            if block_has_sorry:
                stats.n_decls_with_sorry += 1
        elif kind == "def":
            stats.n_def += 1

    # Total sorries (may exceed n_decls_with_sorry if a single block has > 1).
    stats.n_sorry = len(_SORRY_RE.findall(src))
    return stats


def collect_lean(root: Path) -> list[LeanFileStats]:
    out = []
    for p in sorted((root / "Fakeon").rglob("*.lean")):
        out.append(parse_lean_file(p))
    return out


# ---------------------------------------------------------------------------
# Python module parsing.
# ---------------------------------------------------------------------------

_PY_DEF_RE = re.compile(r"^def\s", re.MULTILINE)
_PY_CLASS_RE = re.compile(r"^class\s", re.MULTILINE)


def parse_python_file(path: Path) -> PythonFileStats:
    src = path.read_text(encoding="utf-8", errors="replace")
    return PythonFileStats(
        path=str(path),
        n_lines=src.count("\n") + 1,
        n_def=len(_PY_DEF_RE.findall(src)),
        n_class=len(_PY_CLASS_RE.findall(src)),
    )


def collect_python(root: Path) -> list[PythonFileStats]:
    targets = ["fakeon_numeric", "scripts"]
    out = []
    for sub in targets:
        base = root / sub
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            if p.name == "__pycache__":
                continue
            out.append(parse_python_file(p))
    return out


# ---------------------------------------------------------------------------
# Pytest collection.
# ---------------------------------------------------------------------------

def collect_tests(
    root: Path, run_pytest: bool = True
) -> tuple[list[TestStats], dict[str, int]]:
    test_dir = root / "tests"
    if not test_dir.exists():
        return [], {}

    out: list[TestStats] = []

    if not run_pytest:
        for p in sorted(test_dir.rglob("test_*.py")):
            out.append(TestStats(path=str(p.relative_to(root)), n_collected=0))
        return out, {}

    # 1.  Per-file collected count via `pytest --collect-only -q`.
    out: list[TestStats] = []
    try:
        cp = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q",
             str(test_dir)],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        per_file: dict[str, int] = {}
        # Two pytest output dialects:
        #   (a) "tests/test_foo.py: 7"          (pytest >= 8 default -q)
        #   (b) "tests/test_foo.py::test_bar"   (older / non-q)
        for line in cp.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(tests/[^:\s]+\.py)\s*:\s*(\d+)\s*$", line)
            if m:
                per_file[m.group(1)] = int(m.group(2))
                continue
            if "::" in line:
                rel = line.split("::", 1)[0]
                if rel.endswith(".py"):
                    per_file[rel] = per_file.get(rel, 0) + 1
        for p in sorted(test_dir.rglob("test_*.py")):
            rel = str(p.relative_to(root))
            out.append(TestStats(path=rel, n_collected=per_file.get(rel, 0)))
    except Exception:  # pragma: no cover
        for p in sorted(test_dir.rglob("test_*.py")):
            out.append(TestStats(path=str(p.relative_to(root)), n_collected=0))

    # 2.  Pytest summary: pass / fail / skip via a real run (short).
    summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    try:
        cp = subprocess.run(
            [sys.executable, "-m", "pytest", "--tb=no",
             str(test_dir)],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        # Search the whole captured stdout — the summary line ordering
        # varies between pytest versions and between -q / non-q output.
        for kw in summary:
            m = re.search(rf"(\d+)\s+{kw}", cp.stdout)
            if m:
                summary[kw] = int(m.group(1))
    except Exception:  # pragma: no cover
        pass

    return out, summary


# ---------------------------------------------------------------------------
# CI workflow parsing.
# ---------------------------------------------------------------------------

def collect_ci(repo_root: Path) -> list[CIStage]:
    """Walk every YAML under .github/workflows and pick out steps with names."""
    if yaml is None:
        return []
    wf_root = repo_root / ".github" / "workflows"
    if not wf_root.exists():
        return []
    out: list[CIStage] = []
    for wf in sorted(wf_root.glob("*.y*ml")):
        try:
            data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover
            continue
        if not isinstance(data, dict):
            continue
        for job_name, job in (data.get("jobs") or {}).items():
            steps = (job or {}).get("steps") or []
            for step in steps:
                name = (step or {}).get("name")
                if not name:
                    continue
                runs = step.get("run", "")
                if isinstance(runs, str):
                    runs = runs.strip().splitlines()[0] if runs else ""
                out.append(CIStage(
                    workflow=wf.name, job=job_name, step_name=name, runs=runs,
                ))
    return out


# ---------------------------------------------------------------------------
# Markdown rendering.
# ---------------------------------------------------------------------------

def _badge(ok: bool) -> str:
    return "✅" if ok else "🟡"


def render_md(report: Report) -> str:
    lines: list[str] = []
    lines.append("# Fakeon Verification — Status")
    lines.append("")
    lines.append(
        f"_Generated {report.generated_at} from `{report.root}`._"
    )
    lines.append(
        "_Auto-discovered:_ Lean modules, Python modules, pytest files, "
        ".github/workflows."
    )
    lines.append("")

    # ------------------------------------------------------------------ Headline
    lines.append("## Headline")
    lines.append("")
    lines.append(
        f"- **Content-bearing theorems / lemmas:** "
        f"{report.total_content_bearing} / {report.total_provable} "
        f"({report.content_ratio * 100:.1f} %)"
    )
    lines.append(f"- **Open `sorry`s:** {report.total_sorrys}")
    lines.append(f"- **Open axioms:** {report.total_axioms}")
    s = report.pytest_summary
    if s:
        lines.append(
            f"- **pytest:** {s.get('passed', 0)} passed · "
            f"{s.get('failed', 0)} failed · {s.get('skipped', 0)} skipped · "
            f"{s.get('errors', 0)} errors"
        )
    lines.append("")

    # ------------------------------------------------------------------ Lean
    lines.append("## Lean modules")
    lines.append("")
    lines.append(
        "| File | axiom | theorem | lemma | def | sorry | content-bearing |"
    )
    lines.append("|------|------:|--------:|------:|----:|------:|----------------:|")
    for f in report.lean:
        lines.append(
            f"| `{f.path}` | {f.n_axiom} | {f.n_theorem} | {f.n_lemma} | "
            f"{f.n_def} | {f.n_sorry} | "
            f"{f.n_content_bearing} / {f.n_provable} |"
        )
    lines.append("")

    # ------------------------------------------------------------------ Python
    lines.append("## Python modules")
    lines.append("")
    lines.append("| File | lines | def | class |")
    lines.append("|------|------:|----:|------:|")
    for f in report.python:
        lines.append(
            f"| `{f.path}` | {f.n_lines} | {f.n_def} | {f.n_class} |"
        )
    lines.append("")

    # ------------------------------------------------------------------ Tests
    lines.append("## Tests")
    lines.append("")
    lines.append("| File | collected |")
    lines.append("|------|----------:|")
    for t in report.tests:
        lines.append(f"| `{t.path}` | {t.n_collected} |")
    lines.append("")

    # ------------------------------------------------------------------ CI
    lines.append("## CI stages")
    lines.append("")
    if report.ci:
        lines.append("| Workflow | Job | Step |")
        lines.append("|----------|-----|------|")
        for c in report.ci:
            lines.append(
                f"| `{c.workflow}` | `{c.job}` | {c.step_name} |"
            )
    else:
        lines.append("_No workflows discovered._")
    lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------

def build_report(
    root: Path, repo_root: Path | None = None, run_pytest: bool = True
) -> Report:
    repo_root = repo_root or root.parent
    # Guard against recursive invocation: audit → pytest → test_audit → audit.
    import os
    if os.environ.get("FAKEON_AUDIT_RUNNING") == "1":
        run_pytest = False
    os.environ["FAKEON_AUDIT_RUNNING"] = "1"
    try:
        tests, pytest_summary = collect_tests(root, run_pytest=run_pytest)
        return Report(
            generated_at=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            root=str(root),
            lean=collect_lean(root),
            python=collect_python(root),
            tests=tests,
            pytest_summary=pytest_summary,
            ci=collect_ci(repo_root),
        )
    finally:
        os.environ.pop("FAKEON_AUDIT_RUNNING", None)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("/app/Fakeon"))
    p.add_argument("--repo-root", type=Path, default=None,
                   help="Repository root (parent of --root). "
                        "Used to locate .github/workflows.")
    p.add_argument("--out", type=str, default=None,
                   help="Output file (default: <root>/docs/STATUS.md). "
                        "Use '-' to write to stdout.")
    p.add_argument("--json", action="store_true",
                   help="Also dump the raw report next to --out as JSON.")
    args = p.parse_args(argv)

    report = build_report(args.root, args.repo_root)
    md = render_md(report)

    if args.out == "-":
        sys.stdout.write(md)
        return 0

    out_path = (
        Path(args.out)
        if args.out is not None
        else args.root / "docs" / "STATUS.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"wrote {out_path}")

    if args.json:
        json_path = out_path.with_suffix(".json")
        json_path.write_text(
            json.dumps(_to_json(report), indent=2),
            encoding="utf-8",
        )
        print(f"wrote {json_path}")
    return 0


def _to_json(report: Report) -> dict[str, Any]:
    d = asdict(report)
    d["headline"] = {
        "total_axioms": report.total_axioms,
        "total_sorrys": report.total_sorrys,
        "total_provable": report.total_provable,
        "total_content_bearing": report.total_content_bearing,
        "content_ratio": report.content_ratio,
    }
    return d


if __name__ == "__main__":
    raise SystemExit(main())
