# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system, with explicit assumption / status / certificate
ledger and a content-bearing audit trail.

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pyyaml, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml` (10 named Python stages).
- **Audit** — `scripts/audit_status.py` (file-level metrics) + `fakeon_numeric/status_tracker.py` (component-level, JSON-driven).

## Implemented (cumulative)
- Pass 1: A1..A4, c5, weight-5 scaffold.
- Pass 2: 2D flat connection, weight-7.
- Pass 3: dispersive reality + wedge vanishing.
- Pass 4: Sokhotski–Plemelj distributional foundation.
- Pass 5: Chen-series induction closed.
- Pass 6: perturbative unitarity closure.
- Pass 7: file-level audit script (`audit_status.py`).
- Pass 8: S-matrix extension assumption architecture (`Assumptions.lean`, `tolerance_ledger`, `THEOREM_STATUS.md`).
- **Pass 9 (this)**: component-level Status Matrix.
  - `docs/STATUS_MATRIX.md`: 5-section target matrix (lemmas, Lean modules, tests, physics outputs, predictions).
  - `docs/status_components.json`: live registry, schema v1, 27 components covering lemmas L1..L5, supplementary S.1..S.3, every Lean module, every pytest file, two stub external modules, four experimental predictions.
  - `fakeon_numeric/status_tracker.py`: per-status verification rules (PROVED requires Lean file *and* no `sorry`; VERIFIED checks tolerance ledger; CALCULATED/DEMONSTRATED check Lean file existence; PENDING/METADATA pass by definition). `--strict` mode + JSON export.
  - `fakeon_numeric/tolerance_ledger.py`: now exposes `check_pass`, `get_hash` for tracker integration.
  - `tests/test_status_tracker.py`: 10 tests — per-status rule unit tests + end-to-end live-repo verification.
  - CI: new `Status matrix audit` stage runs `python -m fakeon_numeric.status_tracker --strict`.

## Verification Status (live)
- pytest: **98 passed, 1 skipped, 0 failed**.
- Status matrix: **27/27 components verified**.
- Audit: 14/16 Lean theorems content-bearing (87.5 %), 3 open `sorry`s, 27 declared axioms.
- ruff: clean.
- `lake build`: deferred.

## Open `sorry`s
- `Distributions.lean::causalProp_im`, `imaginary_limit_delta`.
- `FakeonUnitarity.lean::bootstrap_unitarity_bound` (channel-index spot).

## Data dependencies
- A5, A6, c0..c4, c6, c7, real RG trajectory loader.

## Backlog
- **P0**: discharge the two `Distributions.lean` `sorry`s; introduce `Cutkosky.lean`; wire boundary-vector loaders.
- **P1**: `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`; populate L1 with a real Lean module to upgrade from PENDING to PROVED.
- **P2**: `FakeonLSZ`, `SiegelThetaPV`, higher-genus.
