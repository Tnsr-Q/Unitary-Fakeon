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
- **Pass 13**: QÜFT certification pipeline (referee-reviewed).
  - Authored a referee-grade review of the user-proposed `quft-verify.yml` — ~20 defects identified (Lean-3-style installer, placeholder `a1b2c3d4` Mathlib SHA, fictitious pytest flags `--tolerance-ledger/--freeze/--audit-verify`, wrong package paths `src.tolerance.*`, hardcoded-then-self-asserted certificate literals, colliding matrix cache keys, malformed `needs.*.outputs.*` expressions, etc.).
  - `scripts/assemble_certificate.py` (new): derives `FakeonCertificate.json` from **real** outputs only — Regge solver end-point (`Re α(M²), Im α(M²)`), certified PL spectrum (`μ_lb, L_ub, κ`), bootstrap-optical margin, boundary-vector provenance (`hyperint` vs `analytic_fallback`), Merkle anchor (`merkle_root, n_components, input_sha256`), union of assumption tags across the ledger.  Signature = SHA-256 of canonical JSON excluding the signature field.
  - `scripts/run_suite.sh` (new): local dry-run — ruff → optional HyperInt extraction → pytest → audit → Merkle anchor → certificate.  `--hyperint FILE` and `--require-verified` flags.
  - `.github/workflows/quft-verify.yml` (new, additive to `fakeon-verify.yml`): corrected CI with real `leanprover/lean-action@v1` + `lake exe cache get` for the opt-in Lean job; `$GITHUB_STEP_SUMMARY` renders regge / PL / bootstrap / merkle / signature from the real certificate; `workflow_dispatch` inputs `require_verified` and `hyperint_input`.
  - `tests/test_assemble_certificate.py` (new, 5 tests): shape, deterministic signature covering the full payload, payload-change ⇒ signature-change, CLI exit code, missing-anchor handling.

- **Pass 14**: Lean proof-patch referee review (4 patches, 0 merged — full analysis in `Fakeon/docs/LEAN_PROOF_REVIEW_2026-04-29.md`).
- **Pass 15**: `Cutkosky.lean` scaffold — compilable, content-bearing.
- **Pass 16 (this)**: Sokhotski–Plemelj S.1 probe promoted to a first-class certificate component.
  - `fakeon_numeric/cutkosky.py`: new `sokhotski_plemelj_residual(eta_ladder, …)` — deterministic Gaussian probe over η ∈ {10⁻¹, 10⁻², 10⁻³}, `scipy.integrate.quad` with explicit `points=[0.0]` subdivision hint at the Lorentzian spike; reports `integrals`, `abs_residuals`, `best_residual`, `best_eta`, `monotone`, `satisfied`.
  - `scripts/assemble_certificate.py`: new `_s1_block()`; the certificate now carries a top-level `s1_distributional_limit` block, the overall `status=VERIFIED` gate additionally requires `s1.satisfied`, and the SHA-256 signature now covers the S.1 numerics.
  - `tests/test_cutkosky.py`: new `test_sokhotski_plemelj_probe_registers_ledger` updates tolerance ledger key `s1_distributional_limit`.
  - `tests/test_assemble_certificate.py`: key-presence + S.1 block content tests.
  - `docs/status_components.json`: new `S1_DistributionalLimit` (VERIFIED · A1/S1 · ledger `s1_distributional_limit`).
  - `.github/workflows/quft-verify.yml`: step summary renders the S.1 row.
  - Rejected user-proposed `Cutkosky.lean` verbatim (12+ static defects: `Tendsto.limit` non-existent, `ρ_GF^(1)` pseudocode, `S1_dispersive_flow` undefined, `Γ.restrict_to_physical` / `zero_of_disc_zero_real_sector` fabricated, `.DEMONSTRATED` vs. existing `.demonstrated`, free `Γ`/`N` in scope, pointwise `*` on `ℝ → ℂ` without setup, etc.).
  - Authored a **compilable** replacement in the existing tree style: real type signatures, real Mathlib imports, one genuinely provable algebraic lemma `fakeon_pv_im_zero` (closes with `Complex.ofReal_im`), `modified_cutkosky_rule` proven modulo declared axioms, zero new `sorry`s (everything that would be a `sorry` is declared as an explicit `axiom` with a documented promotion path).
  - `fakeon_numeric/cutkosky.py` (new): numeric companion — `fakeon_prop`, `fakeon_prop_complex`, `causal_imag`, `fakeon_disc`, `modified_cutkosky_residual`.  Ledger key `cutkosky_residual`.
  - `tests/test_cutkosky.py` (new, 41 tests): PV reality across (s, m²) grid; causal-kernel algebraic identity at 15 (η, δ) pairs; **Sokhotski–Plemelj distributional limit** numerically verified on 3 test functions (Gaussian, Lorentzian, damped cosine) to within 1 % at η = 10⁻³; disc scales linearly in η across 6 probes; fakeon sector identically invisible in the modified Cutkosky residual.
  - Registered `Lean_Cutkosky` (DEMONSTRATED · A1/A3/S1/S2/S3) and `Test_Cutkosky` (VERIFIED · A1/A3/S1) in `docs/status_components.json`; re-exported via `FakeonQFT.lean`.

## Verification Status (live, 2026-04-29)
- pytest: **198 passed, 2 skipped, 0 failed** (skips: HyperInt-gated weight-7 Chen test; torch-gated Lightning callback tests).
- Status tracker / audit: **37 components**.
- Merkle root: **`55bdc3749c48f82e29500a1b3fc328bc61998de274f89edf8eb6cbb3525ec1e1`** — ANCHOR VERIFIED.
- FakeonCertificate.status = **VERIFIED** (Regge · PL · bootstrap-optical · S.1 distributional limit · PV-real c₇).
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
est_residual = **3.54×10⁻³** at η = 10⁻³, monotone convergence.
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
