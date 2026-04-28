# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system (6×6, PV projection, all-orders reality via
dispersive + flat-connection arguments, Sokhotski–Plemelj distributional
foundation).

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml`.
- Layout frozen to the user-provided tree.

## Implemented
### Pass 1 — weight 5
Matrices A1..A4, boundary c5, HyperInt config, full layout scaffold.

### Pass 2 — weight 7 / O(ε³)
`FlatConnection.lean`, `ChenCollapse.lean`, symbolic flatness pytest, HyperInt bumped to 6 letters / `order = 3`.

### Pass 3 — dispersive + wedge proofs
`Analysis/DispersiveReality.lean`, `Geometry/WedgeVanishing.lean`, `regime.py`, CI workflow.

### Pass 4 — distributional foundation (this pass)
- `Analysis/Distributions.lean`: `causalProp`, `causalProp_im`, `imaginary_limit_delta` (Sokhotski–Plemelj, scaffold with full tactic roadmap), `dispersiveIntegral`, `im_eq_zero_dispersion` (proved under ρ ≡ 0).
- `ChenCollapse.lean` now imports `Distributions`, adds `c_n` + `c_n_real` lemma.
- `FakeonQFT.lean` re-exports `Distributions`.
- `tests/test_distribution_limits.py` — 12 tests: Hadamard-regularised SP integral, parametrised η∈{1e-1..1e-5} convergence, closed-form Voigt match `−π·exp(η²)·erfc(η)`, monotone error, algebraic identity.
- CI workflow adds a dedicated SP-limit step and installs scipy.

## Verification Status
- pytest: **50 passed, 1 skipped** (`cd /app/Fakeon && pytest`).
- ruff: clean.
- `lake build`: deferred (Mathlib cache).

## Open Axioms / Pending sorry's
- Lean: `causalProp_im`, `imaginary_limit_delta` in `Distributions.lean` (both with explicit tactic roadmap and named Mathlib lemmas: `Complex.div_im`, `tendsto_integral_of_dominated_convergence`, `integral_one_div_one_add_sq`).
- Axioms: `fakeon_spectral_density_zero`, `g_tree_im_zero`, `causal_prop_im_proportional`, `rg_flow_1d_reduction`.

## Data Dependencies
- A5, A6, c0..c4, c6, c7.
- Real RG trajectory loader.

## Prioritized Backlog
- **P0** — Close `causalProp_im` (one-liner with Mathlib's `Complex.div_im`) and `imaginary_limit_delta` (DominatedConvergence path, ~40 lines).
- **P0** — Wire boundary-vector loaders; discharge `fakeon_spectral_density_zero` in `FakeonUnitarity.lean`.
- **P1** — `Analysis/PrincipalValue.lean`, `Geometry/PicardLefschetzPV.lean`, `Geometry/GlobalPVClosure.lean`.
- **P2** — `FakeonLSZ` (flat + curved), `SiegelThetaPV`, higher-genus.
