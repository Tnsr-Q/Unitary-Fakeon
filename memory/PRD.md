# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system (6×6, PV projection, all-orders reality via
dispersive + flat-connection arguments).

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, sympy, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml`.
- Layout frozen to the user-provided tree.

## Implemented
### Pass 1 — weight 5
- Matrices A1..A4, boundary c5, HyperInt config, full layout scaffold.

### Pass 2 — weight 7 / O(ε³)
- `FlatConnection.lean` (2D alphabet, `flat_connection`, `chen_pv_reality`).
- `ChenCollapse.lean` recursion + `chen_collapse` theorem.
- Symbolic flatness pytest (15 parametrised pairs).
- HyperInt bumped to 6 letters, `order = 3`.

### Pass 3 — dispersive + wedge proofs
- `Analysis/DispersiveReality.lean`: `im_eq_zero` theorem, axioms `fakeon_spectral_density_zero`, `g_tree_im_zero`, `causal_prop_im_proportional`, `g_disp`, `c_n`.
- `Geometry/WedgeVanishing.lean`: `rg_flow_1d_reduction` axiom, `dlog_α` definition, `wedge_vanishes_on_rg_flow` lemma.
- `FakeonQFT.lean` re-exports Analysis + Geometry.
- `tests/test_dispersive_reality.py` — 7 tests, parametrised n=0..5 plus axiom guard.
- `tests/test_wedge_vanishing.py` — 5 tests: synthetic 1D trajectory certified, genuinely 2D trajectory rejected, width sweep.
- `fakeon_numeric/regime.py` — `Regime` enum and `classify(c, α)` mapping the two guardrails to `PERTURBATIVE` / `DISPERSIVE_BREAKDOWN` / `NON_PERTURBATIVE_BREAKDOWN`.
- `.github/workflows/fakeon-verify.yml` — Python job (lint + full pytest) always on; Lean job on workflow_dispatch.

## Verification Status
- pytest: **42 passed, 1 skipped** (`cd /app/Fakeon && pytest`).
- ruff: clean.
- `lake build`: still deferred (Mathlib cache).

## Open Axioms
- `fakeon_spectral_density_zero` → `QFT/FakeonUnitarity.lean`.
- `g_tree_im_zero` → tree-amplitude catalogue.
- `causal_prop_im_proportional` → future `Analysis/PrincipalValue.lean`.
- `rg_flow_1d_reduction` → future `Geometry/FrobeniusReduction.lean`.

## Data Dependencies
- A5, A6 (y-evolution residue matrices).
- c0..c4, c6, c7 (boundary vectors — unblocks the skipped weight-7 Chen test).
- Real RG trajectory loader (replaces `_synthetic_trajectory` in `test_wedge_vanishing.py`).

## Prioritized Backlog
- **P0** — Discharge `fakeon_spectral_density_zero` against `FakeonUnitarity.lean`; promote `flat_connection` from stub to full wedge statement.
- **P0** — Wire `validation.load_boundary_vectors` + `load_c7` to flip the skipped Chen test to asserting real content.
- **P1** — `Geometry/PicardLefschetzPV.lean`, `Geometry/GlobalPVClosure.lean`, `Analysis/PrincipalValue.lean`.
- **P2** — `FakeonLSZ` (flat + curved), `SiegelThetaPV`, higher-genus closure.

## Next Tasks
1. Plug real A5, A6, c_k data into the existing slots.
2. Run `lake exe cache get && lake build` locally (or enable the CI Lean job).
3. Begin formal discharge of the four open axioms in the order listed.
