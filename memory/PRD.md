# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system, with a closed perturbative unitarity proof
on the physical Hilbert space and an explicit assumption / status ledger.

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pyyaml, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml`.
- **Audit** — `scripts/audit_status.py` → `docs/STATUS.md` (auto-discovers everything).

## Implemented (cumulative)
- **Pass 1**: A1..A4, c5, weight-5 scaffold.
- **Pass 2**: 2D flat connection, weight-7.
- **Pass 3**: dispersive reality + wedge vanishing.
- **Pass 4**: Sokhotski–Plemelj distributional foundation.
- **Pass 5**: Chen-series induction closed.
- **Pass 6**: perturbative unitarity closure.
- **Pass 7**: audit script `scripts/audit_status.py` (auto-discovery, content-bearing ratio, JSON sidecar).
- **Pass 8 (this)**: S-matrix extension assumption architecture.
  - `Fakeon/QFT/Assumptions.lean`: A1..A5 + S.1..S.3 axioms with explicit docstrings, `VerificationStatus` enum (PROVED / VERIFIED / CALCULATED / DEMONSTRATED / PENDING), `SMatrixCertificate` struct, four pre-registered certificates (`smatrix_unitarity_cert`, `spectral_density_cert`, `froissart_cert`, `beta_closure_cert`).
  - `fakeon_numeric/tolerance_ledger.py`: in-tree `update_ledger`, `check_tolerance`, `snapshot`, `dump`.
  - `tests/test_s_matrix_extension.py`: 9 tests — S.1 spectral density, S.2 inelasticity profile (parametrised ℓ ∈ {0,1,2,3}), Froissart pass + Froissart violation correctly rejected, S.3 β-closure, end-to-end pipeline (drives all four hooks, fills ledger, asserts every entry passed).
  - CI workflow: new `S-matrix extension validation (S.1–S.3)` stage and a final `Audit + status report` stage that runs the audit script and folds STATUS.md into the build log.
  - `docs/THEOREM_STATUS.md`: cross-reference between physical claims, Lean homes, status tags, and Python hooks; includes a status promotion-rules table.
  - `FakeonQFT.lean` re-exports `Assumptions`.

## Verification Status (live, from `audit_status.py`)
- Content-bearing theorems / lemmas: **14 / 16 (87.5 %)**.
- Open `sorry`s: **3** (2 in `Distributions.lean`, 1 in `FakeonUnitarity.lean::bootstrap_unitarity_bound`).
- Open axioms: **27** (was 14 + 13 new from `Assumptions.lean` opaque types & A/S axioms).
- pytest: **87 passed, 1 skipped, 0 failed**.
- ruff: clean.

## Open Lean `sorry`s
- `Distributions.lean::causalProp_im`, `Distributions.lean::imaginary_limit_delta`.
- `FakeonUnitarity.lean::bootstrap_unitarity_bound` (channel-index spot).

## Open Axioms (grouped)
- Physics S.1–S.3 + A1–A5 (`QFT/Assumptions.lean`).
- Cutkosky machinery: `IsFakeonCut`, `discCut`, `fakeon_spectral_cut_zero`.
- Projector: `P_phys_properties`.
- Distributional: `g_tree_im_zero`, `causal_prop_im_proportional`.
- Geometric: `rg_flow_1d_reduction`, `constraint_manifold_pv`.

## Data Dependencies
- A5, A6 residue matrices, c0..c4, c6, c7 boundary vectors, real RG trajectory loader.

## Prioritized Backlog
- **P0** — Close the two `Distributions.lean` `sorry`s; introduce `Cutkosky.lean` and discharge `fakeon_spectral_cut_zero`.
- **P0** — Wire boundary-vector loaders.
- **P1** — `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`.
- **P2** — `FakeonLSZ`, `SiegelThetaPV`, higher-genus.
