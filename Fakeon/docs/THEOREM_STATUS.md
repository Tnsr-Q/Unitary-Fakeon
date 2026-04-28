# Theorem ↔ Status Map

Cross-reference between physical claims (S-matrix extension document),
their Lean home, their status tag, and the Python verification hook.
Status vocabulary: `PROVED` · `VERIFIED` · `CALCULATED` · `DEMONSTRATED`
· `PENDING`.

| Document claim                                 | Lean axiom / theorem                                        | Status        | Verification hook                              |
|------------------------------------------------|-------------------------------------------------------------|---------------|------------------------------------------------|
| `ρ_GF^{(1)}(μ²) = 0` (fakeon projection)       | `QFT/Assumptions.lean::S1_dispersive_flow`                  | DEMONSTRATED  | `tests/test_s_matrix_extension::verify_spectral_density` |
| `\|S_l(s)\| ≤ 1`, `η_l(s)` ansatz              | `QFT/Assumptions.lean::S2_bootstrap_inelasticity`           | DEMONSTRATED  | `verify_inelasticity_profile`                  |
| Froissart–Martin bound                         | `QFT/FakeonUnitarity.lean::physical_optical_theorem`        | VERIFIED      | `check_froissart_bound`                        |
| 1-loop / 2-loop `β_{f₂}` (MS̄)                  | `QFT/Assumptions.lean::S3_beta_closure`                     | CALCULATED    | `verify_beta_closure`                          |
| Perturbative unitarity closure                 | `QFT/FakeonUnitarity.lean::perturbative_unitarity_closure`  | DEMONSTRATED  | `tests/test_unitarity_closure`                 |
| Chen-series PV reality                         | `Algebra/ChenCollapse.lean::chen_series_real`               | DEMONSTRATED  | `tests/test_chen_integration`                  |
| Sokhotski–Plemelj distributional limit         | `Analysis/Distributions.lean::imaginary_limit_delta`        | PENDING       | `tests/test_distribution_limits`               |
| Wedge vanishing on 1D RG flow                  | `Geometry/WedgeVanishing.lean::wedge_vanishes_on_rg_flow`   | DEMONSTRATED  | `tests/test_wedge_vanishing`                   |
| 2D flat connection (massive DE)                | `Geometry/FlatConnection.lean::flat_connection`             | VERIFIED      | `tests/test_massive_flatness`                  |
| Dispersive `im_eq_zero`                        | `Analysis/DispersiveReality.lean::im_eq_zero`               | DEMONSTRATED  | `tests/test_dispersive_reality`                |

## Certificate registry

The Lean module `Fakeon/QFT/Assumptions.lean` exposes named
`SMatrixCertificate` values for downstream theorems to carry alongside
their statement.  Currently registered:

| Lean term                  | Status        | Bundles                               |
|----------------------------|---------------|---------------------------------------|
| `smatrix_unitarity_cert`   | DEMONSTRATED  | A1..A5 + S.1..S.3                     |
| `spectral_density_cert`    | DEMONSTRATED  | S.1                                   |
| `froissart_cert`           | VERIFIED      | A1, A2, S.2                           |
| `beta_closure_cert`        | CALCULATED    | A3, A4, S.3                           |

## Promotion rules

A claim moves from one status to a stronger one only when **all** of the
following are true:

| Promotion           | Required evidence                                            |
|---------------------|--------------------------------------------------------------|
| PENDING → DEMONSTRATED | Constructive Lean term with no upstream `sorry` and a passing pytest hook. |
| DEMONSTRATED → VERIFIED | A grid-resolved numerical check that exercises the kinematic envelope of interest. |
| VERIFIED → CALCULATED  | A closed-form analytic expression matching the numeric verifier on its grid to ≤ 1e-10. |
| CALCULATED → PROVED    | A Lean proof carrying no axioms outside `Fakeon.QFT.Assumptions` and no `sorry`. |
