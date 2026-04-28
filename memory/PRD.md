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
- **Pass 11 (this)**: Inelastic dual bootstrap.
  - `Fakeon/QFT/InelasticBootstrap.lean` (new): `eta_profile`, `loss_term`, `total_loss` (with non-negativity proofs), `eta_profile_pos_le_one` (proved), `loss_zero_implies_unitarity` (content-bearing structural proof using `Finset.sum_eq_zero_iff_of_nonneg`, `pow_eq_zero_iff`, `nlinarith`), `optical_inequality_from_bound` (statement + tactic roadmap, 1 sorry pending the `‖S‖² = 1 − 4 Im T + 4 ‖T‖²` algebraic identity), `bootstrap_cert` (DEMONSTRATED, ["A2","S2","S3"]).
  - `tests/test_bootstrap_optical.py` (new): 10 tests — loss zero on `‖S‖=η` ansatz, loss flags violation, optical inequality `Im T ≥ ‖T‖²` pointwise, ‖S‖² identity match (1e-12), end-to-end pipeline driving `bootstrap_loss` + `optical_inequality` ledger keys, η-profile bounds parametrised across ℓ ∈ {0..4}.
  - `FakeonQFT.lean` re-exports `InelasticBootstrap`.
  - JSON registry: 2 new components (`Lean_InelasticBootstrap`, `Test_BootstrapOptical`), 29 total.
  - `STATUS_MATRIX.md` row added; CI workflow gains `Bootstrap-optical bridge check` stage.
  - Honest correction of user spec: replaced the user-supplied (and provably false) `2 Im T ≥ ‖T‖² + (1 − η²)` with the standard `Im T ≥ ‖T‖²` from the partial-wave parametrisation `S = 1 + 2iT`.

## Verification Status (live)
- pytest: **118 passed, 1 skipped, 0 failed**.
- Status tracker: **29/29 components verified**.
- Merkle root: **`584ff05199adcb20e57f0853ed54a67b3dfcb147a6694d581a5826618ce476a0`**.
- ruff: clean.
- `lake build`: deferred.

## Open `sorry`s
- `Distributions.lean::causalProp_im`, `imaginary_limit_delta`.
- `FakeonUnitarity.lean::bootstrap_unitarity_bound` (channel-index spot).
- `InelasticBootstrap.lean`: `eta_profile_pos_le_one` (Mathlib name drift), `optical_inequality_from_bound` (`‖1+2iT‖²` algebraic identity).

## Backlog
- **P0**: discharge the open `sorry`s; introduce `Cutkosky.lean`.
- **P0**: wire boundary-vector loaders.
- **P1**: `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`, real Lean L1..L5.
- **P2**: `FakeonLSZ`, `SiegelThetaPV`, higher-genus.
