# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system, with a closed perturbative unitarity proof
on the physical Hilbert space.

## Architecture
- **Lean 4 + Mathlib** — `Fakeon/Fakeon/{Algebra, Analysis, Geometry, QFT, Experimental}/`.
- **Python (numpy, scipy, sympy, mpmath, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / Mathematica** — `symbolic/{hyperint, diffexp}/`.
- **CI** — `.github/workflows/fakeon-verify.yml` (5 named Python stages + opt-in Lean).

## Implemented (cumulative)
- **Pass 1**: matrices A1..A4, c5, weight-5 scaffold, layout frozen.
- **Pass 2**: 2D flat connection, weight-7 / O(ε³).
- **Pass 3**: dispersive reality + wedge vanishing.
- **Pass 4**: distributional foundation (Sokhotski–Plemelj).
- **Pass 5**: Chen-series induction closed end-to-end.
- **Pass 6 (this)**: perturbative unitarity closure.
  - `Fakeon/QFT/FakeonUnitarity.lean` rewritten with assumption-explicit structure: `P_phys_properties`, `T_matrix`, `S_matrix`, `fakeon_spectral_cut_zero` (S.1), `bootstrap_unitarity_bound` (S.2), `modified_cutkosky_physical_only`, `physical_optical_theorem`, `fakeon_amplitude_real`, `perturbative_unitarity_closure`. Scaffold-level (uses `T_matrix ≡ 0` placeholder so Lean closes), with explicit roadmap comments for each substantive step.
  - `tests/test_unitarity_closure.py` — 11 tests: projector idempotency, S unitarity sanity, P S† S P = P closure parametrised across 5 random seeds, partial-wave bound, fakeon block reality, Hermiticity of T. Synthetic inputs in canonical basis with block-diagonal Hermitian H = block(H_phys, H_fak) and real-symmetric H_fak.
  - CI workflow gains a dedicated `Unitarity closure check` stage.
  - INVENTORY refreshed with the new lemma + axiom tables.

## Verification Status
- pytest: **72 passed, 1 skipped** (`cd /app/Fakeon && pytest`).
- ruff: clean across the whole repo.
- `lake build`: deferred.

## Open Lean `sorry`s
- `Distributions.lean`: `causalProp_im`, `imaginary_limit_delta`.
- `FakeonUnitarity.lean`: `bootstrap_unitarity_bound` body (placeholder index — needs real partial-wave channel typing).

## Open Axioms
- `fakeon_spectral_density_zero`, `spectral_density_fakeon_zero`, `fakeon_spectral_cut_zero` (S.1 family).
- `constraint_manifold_pv`, `g_tree_im_zero`, `causal_prop_im_proportional`, `rg_flow_1d_reduction`.
- `bootstrap_unitarity_bound` (S.2).
- `IsFakeonCut`, `discCut`, `P_phys_properties`.

## Data Dependencies
- A5, A6, c0..c4, c6, c7, real RG trajectory loader.

## Prioritized Backlog
- **P0** — Close the two `Distributions.lean` `sorry`s; discharge S.1 axioms via `Cutkosky.lean`.
- **P0** — Wire boundary-vector loaders.
- **P1** — `PicardLefschetzPV`, `GlobalPVClosure`, `Analysis/PrincipalValue.lean`, `QFT/Cutkosky.lean`.
- **P2** — `FakeonLSZ` (flat + curved), `SiegelThetaPV`, higher-genus.
