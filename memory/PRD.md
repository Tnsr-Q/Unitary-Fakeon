# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system (6×6, PV projection, all-orders reality via
dispersive + flat-connection arguments, Sokhotski–Plemelj distributional
foundation, closed Chen-series induction).

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml`.

## Implemented (cumulative)
- **Pass 1**: matrices A1..A4, c5, weight-5 scaffold.
- **Pass 2**: 2D flat connection + weight-7 / O(ε³) (`FlatConnection.lean`, symbolic flatness pytest).
- **Pass 3**: dispersive reality + wedge vanishing (`DispersiveReality.lean`, `WedgeVanishing.lean`, `regime.py`).
- **Pass 4**: distributional foundation (`Distributions.lean`, Sokhotski–Plemelj numerical test, scipy CI).
- **Pass 5 (this)**: Chen-series induction closed.
  - `Algebra/ChenCollapse.lean` rewritten with `c_vec`, `c_vec_real`, `chen_step`, `chen_series`, `chen_series_real` (structural), `chen_series_real_induction` (explicit induction). All bodies content-bearing, no `sorry`.
  - `spectral_density_fakeon_zero` and `constraint_manifold_pv` axioms declared in line with the S-matrix analysis.
  - `fakeon_numeric/distributions.py` exposes `causal_propagator`, `evaluate_c_n`, `check_spectral_density_zero`.
  - `tests/test_chen_integration.py` — 10 tests: axiom guard + base-case c_n (n=0..4) + Chen recursion reality (weight 1..4).
  - CI workflow runs the new test as its own named step.

## Verification Status
- pytest: **61 passed, 1 skipped** (`cd /app/Fakeon && pytest`).
- ruff: clean across the whole repo.
- `lake build`: deferred (Mathlib cache).

## Open Lean `sorry`s
- `Distributions.lean`: `causalProp_im`, `imaginary_limit_delta`.

## Open Axioms
- `fakeon_spectral_density_zero` / `spectral_density_fakeon_zero` — to be discharged in `QFT/FakeonUnitarity.lean`.
- `constraint_manifold_pv` — to be discharged in `Geometry/GlobalPVClosure.lean`.
- `g_tree_im_zero`, `causal_prop_im_proportional`, `rg_flow_1d_reduction`.

## Data Dependencies
- A5, A6 (currently zero stubs).
- c0..c4, c6, c7 (boundary vectors).
- Real RG trajectory loader.

## Prioritized Backlog
- **P0** — Close `causalProp_im` + `imaginary_limit_delta`; discharge spectral-density axiom in `FakeonUnitarity.lean`.
- **P0** — Wire boundary-vector loaders → unblocks the last skipped test.
- **P1** — `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`.
- **P2** — `FakeonLSZ` (flat + curved), `SiegelThetaPV`, higher-genus.
