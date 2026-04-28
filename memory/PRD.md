# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system, with explicit assumption / status / certificate
ledger and a content-bearing audit trail.

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pyyaml, pytest)** — `fakeon_numeric/` + `tests/`.
- **CI** — `.github/workflows/fakeon-verify.yml` (12 named Python stages).
- **Audit + reproducibility** — `scripts/audit_status.py`, `fakeon_numeric/status_tracker.py`, `scripts/anchor_status.py`.

## Implemented (cumulative)
- Pass 1: A1..A4, c5, weight-5 scaffold.
- Pass 2: 2D flat connection, weight-7.
- Pass 3: dispersive reality + wedge vanishing.
- Pass 4: Sokhotski–Plemelj distributional foundation.
- Pass 5: Chen-series induction closed.
- Pass 6: perturbative unitarity closure.
- Pass 7: file-level audit script.
- Pass 8: S-matrix extension assumption architecture.
- Pass 9: component-level Status Matrix + JSON registry + tracker.
- Pass 10: Merkle reproducibility anchor.
- Pass 11: Inelastic dual bootstrap.
- **Pass 12 (this)**: HyperInt boundary-vector loader wired.
  - `fakeon_numeric/boundary_vectors.py` (new): `load_boundary_vectors()` returns `{"4","5","6","7"}` of 6-D real arrays; JSON-first (`fakeon_numeric/c_vectors.json`), analytic ζ/π fallback, `is_from_hyperint()` signal, `pv_reality_residual()` hook.
  - `fakeon_numeric/validation.py` (rewritten): legacy sympy bridge — `load_boundary_vectors() -> (c4, c5, c6)` and `load_c7() -> c7` as 6×1 sympy Matrices, backed by `boundary_vectors`.
  - `scripts/extract_cvec.py` (rewritten from stub): parses Mathematica `Master[i] = … + coeff*eps^n + …` dumps (HyperInt/DiffExp), translates `Pi^n` / `Zeta[n]` via mpmath, emits `fakeon_numeric/c_vectors.json`; CLI `--input / --out / --format`.
  - `tests/test_massive_flatness.py`: dropped import-based skip, added `test_boundary_vectors_loader_shapes` + `test_boundary_vectors_sympy_bridge` (both green today); weight-7 Chen recursion now gated on `c_vectors.json` presence with numerical tolerance `1e-9·‖c7‖`.
  - `tests/test_extract_cvec.py` (new, 8 tests): loader fallback / JSON precedence / shape validation; Mathematica→Python translator; zeta/pi evaluation; parser round-trip on a synthetic 6-master dump; end-to-end `extract_cvec.py` CLI → JSON → loader; missing-input CLI returns non-zero.

## Verification Status (live, 2026-04-29)
- pytest: **150 passed, 1 skipped, 0 failed** (+10 from Pass 11).
- Status tracker / audit: **33 components** auto-discovered (up from 29).
- Merkle root: **`894d7778a1b8a43f42f77dff3ef96123f4a68e89cff77202a16207f40a09d1f5`** (ANCHOR VERIFIED).
- ruff: clean.
- `lake build`: deferred.

## Open `sorry`s
- `Distributions.lean::causalProp_im`, `imaginary_limit_delta`.
- `FakeonUnitarity.lean::bootstrap_unitarity_bound` (channel-index spot).
- `InelasticBootstrap.lean::optical_inequality_from_bound` (`‖1+2iT‖²` algebraic identity).

## Backlog
- **P0**: populate `A5 (α₅=y)` and `A6 (α₆=y+1)` residue matrices from the y-evolution derivation, then run HyperInt/DiffExp + `scripts/extract_cvec.py` to activate the weight-7 Chen recursion test.
- **P0**: discharge the remaining 4 open `sorry`s; introduce `Cutkosky.lean`.
- **P1**: `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`, real Lean L1..L5.
- **P1**: reduce the 40 open axioms by converting Mathlib-backable ones to proved theorems.
- **P2**: real PyTorch Lightning `CertifiedPLHessianCallback`; `FakeonLSZ`, `SiegelThetaPV`, higher-genus.
