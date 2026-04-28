# INVENTORY.md

File-by-file index of the Fakeon verification repository.  ✅ = fully
populated, 🟡 = authoritative content present but proofs pending,
⬜ = placeholder.

## Lean sources (`Fakeon/Fakeon/`)

| File                                   | Status | Purpose                                       |
|----------------------------------------|--------|-----------------------------------------------|
| `Algebra/MassiveDE.lean`               | 🟡     | 6×6 matrices A1..A4, c5, PV reality scaffold  |
| `Algebra/ChenCollapse.lean`            | 🟡     | Closed induction `chen_series_real`, c_vec via `DispersiveReality` |
| `Analysis/Distributions.lean`          | 🟡     | `causalProp`, Sokhotski–Plemelj limit, dispersive reality |
| `Analysis/DispersiveReality.lean`      | 🟡     | `im_eq_zero` from `ρ_GF = 0` (fakeon axiom)   |
| `Geometry/FlatConnection.lean`         | 🟡     | 2D flat connection, `chen_pv_reality`         |
| `Geometry/WedgeVanishing.lean`         | 🟡     | 1D RG flow ⇒ wedge vanishes                   |
| `Geometry/PicardLefschetzPV.lean`      | ⬜     | PL stability of PV contour                    |
| `Geometry/HyperellipticPV.lean`        | ⬜     | Hyperelliptic PV extension                    |
| `Geometry/GlobalPVClosure.lean`        | ⬜     | Global monodromy closure                      |
| `Geometry/GeneralGenusPV.lean`         | ⬜     | Arbitrary-genus closure                       |
| `QFT/Assumptions.lean`                 | ✅     | A1..A5 + S.1..S.3 axioms + `VerificationStatus` + certificates |
| `QFT/FakeonUnitarity.lean`             | 🟡     | `perturbative_unitarity_closure` (scaffold) + S.1/S.2 axioms |
| `QFT/FakeonLSZ.lean`                   | ⬜     | Flat-space LSZ                                |
| `QFT/FakeonCurvedLSZ.lean`             | ⬜     | Curved-space LSZ                              |
| `Experimental/SiegelThetaPV.lean`      | ⬜     | PV on Siegel theta                            |
| `FakeonQFT.lean`                       | ✅     | Top-level re-exports (Analysis + Geometry)    |

### Lemma map

| Lemma / theorem              | Home file                              | Status |
|------------------------------|----------------------------------------|--------|
| `causalProp_im`              | `Analysis/Distributions.lean`          | 🟡 algebraic, `sorry` pending |
| `imaginary_limit_delta`      | `Analysis/Distributions.lean`          | 🟡 scaffold, DominatedConvergence roadmap |
| `im_eq_zero_dispersion`      | `Analysis/Distributions.lean`          | ✅ proved in ρ ≡ 0 regime |
| `im_eq_zero` (all n)         | `Analysis/DispersiveReality.lean`      | 🟡 scaffold, depends on fakeon axiom S.1 |
| `c_n_real`                   | `Algebra/ChenCollapse.lean`            | ✅ by definition of `c_n : ℝ` |
| `wedge_vanishes_on_rg_flow`  | `Geometry/WedgeVanishing.lean`         | ✅ scalar form proved, Frobenius reduction axiomatised |
| `flat_connection`            | `Geometry/FlatConnection.lean`         | 🟡 stub, symbolic counterpart in pytest |
| `chen_pv_reality` (all n)    | `Geometry/FlatConnection.lean`         | 🟡 scaffold |
| `chen_collapse`              | `Algebra/ChenCollapse.lean`            | 🟡 statement only |
| `massive_pv_reality`         | `Algebra/MassiveDE.lean`               | 🟡 trivial ℝ version |
| `fakeon_unitarity`           | `QFT/FakeonUnitarity.lean`             | 🟡 reduces to `chen_pv_reality` |
| `fakeon_amplitude_real`      | `QFT/FakeonUnitarity.lean`             | ✅ trivial under T = 0 placeholder |
| `modified_cutkosky_physical_only` | `QFT/FakeonUnitarity.lean`        | 🟡 statement-level placeholder |
| `physical_optical_theorem`   | `QFT/FakeonUnitarity.lean`             | 🟡 statement-level placeholder |
| `perturbative_unitarity_closure` | `QFT/FakeonUnitarity.lean`         | 🟡 closes under T = 0 placeholder |

### Axioms (to be discharged by follow-ups)

| Axiom                             | Home                                       | Discharged by |
|-----------------------------------|--------------------------------------------|---------------|
| `fakeon_spectral_density_zero`    | `Analysis/DispersiveReality.lean`          | `QFT/FakeonUnitarity.lean` (WIP) |
| `spectral_density_fakeon_zero`    | `Algebra/ChenCollapse.lean`                | `QFT/FakeonUnitarity.lean` (WIP) |
| `constraint_manifold_pv`          | `Algebra/ChenCollapse.lean`                | `Geometry/GlobalPVClosure.lean` (WIP) |
| `fakeon_spectral_cut_zero`        | `QFT/FakeonUnitarity.lean`                 | future `QFT/Cutkosky.lean` |
| `bootstrap_unitarity_bound`       | `QFT/FakeonUnitarity.lean`                 | bootstrap solver export |
| `IsFakeonCut`, `discCut`          | `QFT/FakeonUnitarity.lean`                 | future `QFT/Cutkosky.lean` |
| `P_phys_properties`               | `QFT/FakeonUnitarity.lean`                 | dispatch via `Mathlib.LinearAlgebra.Projection` (when available) |
| `g_tree_im_zero`                  | `Analysis/DispersiveReality.lean`          | tree-level amplitude catalogue (TBD) |
| `causal_prop_im_proportional`     | `Analysis/DispersiveReality.lean`          | future `Analysis/PrincipalValue.lean` |
| `rg_flow_1d_reduction`            | `Geometry/WedgeVanishing.lean`             | future `Geometry/FrobeniusReduction.lean` |

## Numeric package (`fakeon_numeric/`)

| Module                                  | Status |
|-----------------------------------------|--------|
| `validation.py`                         | ⬜ needs `load_boundary_vectors`, `load_c7` |
| `partial_wave.py`                       | ⬜     |
| `omega_quadrature.py`                   | ⬜     |
| `radial_interpolator.py`                | ⬜     |
| `siegel_theta.py`                       | ⬜     |
| `schwarzschild_radial_solver.py`        | ⬜     |
| `regime.py`                             | ✅ `Regime` enum + `classify(c, α)` |
| `distributions.py`                      | ✅ `causal_propagator`, `evaluate_c_n`, `check_spectral_density_zero` |
| `tolerance_ledger.py`                   | ✅ `update_ledger`, `check_tolerance`, `snapshot`, `dump` |

`fakeon_numeric.regime.classify` plays the role of the external
`src/tolerance/regime_detector.py` referenced in the QFT-Engine spec.

## Tests (`tests/`)

| File                                   | Status |
|----------------------------------------|--------|
| `test_massive_de_consistency.py`       | ✅ 5 tests |
| `test_massive_flatness.py`             | ✅ 15 pair tests + summary, 1 skip for Chen coefficients |
| `test_dispersive_reality.py`           | ✅ 7 tests (6 parametrised + axiom guard) |
| `test_distribution_limits.py`          | ✅ 12 tests (SP convergence, closed-form match, monotone error, algebraic identity) |
| `test_chen_integration.py`             | ✅ 10 tests (axiom guard, base-case c_n × 5, recursion reality × 4) |
| `test_unitarity_closure.py`            | ✅ 11 tests (projector, S unitary, closure × 6, partial-wave bound, fakeon block real, T Hermitian) |
| `test_s_matrix_extension.py`           | ✅ 9 tests (S.1, S.2 inelasticity × 4, Froissart pass + violation, S.3, end-to-end pipeline) |
| `test_wedge_vanishing.py`              | ✅ 5 tests (1D certified, 2D rejected, widths sweep) |
| `test_fakeon_pv.py`                    | ⬜ placeholder |
| `test_numeric_imports.py`              | ✅ 9 import smoke tests (now includes `regime`, `distributions`) |

## Scripts (`scripts/`)

| File                           | Status |
|--------------------------------|--------|
| `fakeon_validation_ci.py`      | ✅     |
| `audit_status.py`              | ✅ auto-discovers Lean / Python / tests / CI; emits `docs/STATUS.md` |
| `extract_cvec.py`              | ⬜     |

## Status matrix

| Artefact                                | Status |
|-----------------------------------------|--------|
| `docs/STATUS_MATRIX.md`                 | ✅ target state, 5 sections, 27 rows |
| `docs/status_components.json`           | ✅ live registry, schema_v1 |
| `fakeon_numeric/status_tracker.py`      | ✅ verifier + matrix exporter, `--strict` mode |
| `tests/test_status_tracker.py`          | ✅ 10 tests (per-status rules + live-repo end-to-end) |

## Symbolic (`symbolic/`)

| File                                        | Status |
|---------------------------------------------|--------|
| `hyperint/crossedbox_PV.maple`              | ⬜ massless placeholder |
| `hyperint/crossedbox_massive_PV.maple`      | ✅ 6 letters, order=3, weight-7 |
| `diffexp/system_2D.m`                       | ⬜     |

## CI

| File                                              | Status |
|---------------------------------------------------|--------|
| `.github/workflows/fakeon-verify.yml`             | ✅ Python job always on; Lean job on workflow_dispatch |

## Data dependencies not yet wired

| Symbol            | Needed by                                    |
|-------------------|----------------------------------------------|
| `A5, A6`          | `FlatConnection.lean`, `test_massive_flatness.py` |
| `c0..c4, c6, c7`  | `test_chen_coefficients_weight7`             |
| real RG solver    | `test_wedge_vanishing.py` (currently synthetic) |
| tree amplitude    | `g_tree_im_zero` axiom                       |
-----------------------|
| `A5, A6`          | `FlatConnection.lean`, `test_massive_flatness.py` |
| `c0..c4, c6, c7`  | `test_chen_coefficients_weight7`             |
| real RG solver    | `test_wedge_vanishing.py` (currently synthetic) |
| tree amplitude    | `g_tree_im_zero` axiom                       |
