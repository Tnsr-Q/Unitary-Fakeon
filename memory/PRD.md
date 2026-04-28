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
- Pass 12: HyperInt boundary-vector loader wired.
- **Pass 13 (this)**: QÜFT certification pipeline (referee-reviewed).
  - Authored a referee-grade review of the user-proposed `quft-verify.yml` — ~20 defects identified (Lean-3-style installer, placeholder `a1b2c3d4` Mathlib SHA, fictitious pytest flags `--tolerance-ledger/--freeze/--audit-verify`, wrong package paths `src.tolerance.*`, hardcoded-then-self-asserted certificate literals, colliding matrix cache keys, malformed `needs.*.outputs.*` expressions, etc.).
  - `scripts/assemble_certificate.py` (new): derives `FakeonCertificate.json` from **real** outputs only — Regge solver end-point (`Re α(M²), Im α(M²)`), certified PL spectrum (`μ_lb, L_ub, κ`), bootstrap-optical margin, boundary-vector provenance (`hyperint` vs `analytic_fallback`), Merkle anchor (`merkle_root, n_components, input_sha256`), union of assumption tags across the ledger.  Signature = SHA-256 of canonical JSON excluding the signature field.
  - `scripts/run_suite.sh` (new): local dry-run — ruff → optional HyperInt extraction → pytest → audit → Merkle anchor → certificate.  `--hyperint FILE` and `--require-verified` flags.
  - `.github/workflows/quft-verify.yml` (new, additive to `fakeon-verify.yml`): corrected CI with real `leanprover/lean-action@v1` + `lake exe cache get` for the opt-in Lean job; `$GITHUB_STEP_SUMMARY` renders regge / PL / bootstrap / merkle / signature from the real certificate; `workflow_dispatch` inputs `require_verified` and `hyperint_input`.
  - `tests/test_assemble_certificate.py` (new, 5 tests): shape, deterministic signature covering the full payload, payload-change ⇒ signature-change, CLI exit code, missing-anchor handling.

## Verification Status (live, 2026-04-29)
- pytest: **155 passed, 1 skipped, 0 failed** (+5 from Pass 12).
- Status tracker / audit: **33 components**.
- Merkle root: **`894d7778a1b8a43f42f77dff3ef96123f4a68e89cff77202a16207f40a09d1f5`** — ANCHOR VERIFIED.
- FakeonCertificate.status = **VERIFIED** (regge virtualised · PL passed · optical margin ≥ 0 · PV-real c₇).
- ruff: clean.
- End-to-end local dry-run (`bash scripts/run_suite.sh --require-verified`): green.
- `lake build`: opt-in via `workflow_dispatch` (deferred).

## Open `sorry`s (unchanged after 2026-04-29 Lean proof-patch review)
- `Distributions.lean::causalProp_im` — reviewed; patch plausible but unverified (no Lean), parked for activation when `lake build` runs.
- `Distributions.lean::imaginary_limit_delta` — reviewed; proposed patch rejected (type error + fabricated Mathlib names).
- `FakeonUnitarity.lean::bootstrap_unitarity_bound` — reviewed; proposed patch targets the wrong object (per-channel vs. matrix-level). The per-channel proof already exists in `InelasticBootstrap.loss_zero_implies_unitarity`.
- `InelasticBootstrap.lean::optical_inequality_from_bound` (internal `hSq`) — reviewed; proposed patch rejected (sign error, coefficient error, adds axioms, re-introduces Pass-11 rejected identity). A 6-line candidate for the single open line is recorded in `docs/LEAN_PROOF_REVIEW_2026-04-29.md`.

Full referee review: `Fakeon/docs/LEAN_PROOF_REVIEW_2026-04-29.md`.

## Backlog
- **P0**: populate `A5 (α₅=y)` and `A6 (α₆=y+1)` residue matrices from the y-evolution derivation, then run HyperInt/DiffExp + `scripts/extract_cvec.py` to activate the weight-7 Chen recursion test.
- **P0**: discharge the remaining 4 open `sorry`s; introduce `Cutkosky.lean`.
- **P1**: `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`, real Lean L1..L5.
- **P1**: reduce the 40 open axioms by converting Mathlib-backable ones to proved theorems.
- **P2**: real PyTorch Lightning `CertifiedPLHessianCallback`; `FakeonLSZ`, `SiegelThetaPV`, higher-genus.
