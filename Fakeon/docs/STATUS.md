# Fakeon Verification — Status

_Generated 2026-04-28T10:36:46+00:00 from `/app/Fakeon`._
_Auto-discovered:_ Lean modules, Python modules, pytest files, .github/workflows.

## Headline

- **Content-bearing theorems / lemmas:** 26 / 29 (89.7 %)
- **Open `sorry`s:** 4
- **Open axioms:** 53
- **pytest:** 198 passed · 0 failed · 1 skipped · 0 errors

## Lean modules

| File | axiom | theorem | lemma | def | sorry | content-bearing |
|------|------:|--------:|------:|----:|------:|----------------:|
| `/app/Fakeon/Fakeon/Algebra/ChenCollapse.lean` | 2 | 3 | 1 | 5 | 0 | 4 / 4 |
| `/app/Fakeon/Fakeon/Algebra/MassiveDE.lean` | 0 | 0 | 1 | 10 | 0 | 1 / 1 |
| `/app/Fakeon/Fakeon/Analysis/DispersiveReality.lean` | 6 | 1 | 0 | 2 | 0 | 1 / 1 |
| `/app/Fakeon/Fakeon/Analysis/Distributions.lean` | 0 | 2 | 1 | 3 | 2 | 1 / 3 |
| `/app/Fakeon/Fakeon/Experimental/SiegelThetaPV.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/FakeonQFT.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/Geometry/FlatConnection.lean` | 0 | 1 | 1 | 4 | 0 | 2 / 2 |
| `/app/Fakeon/Fakeon/Geometry/GeneralGenusPV.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/Geometry/GlobalPVClosure.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/Geometry/HyperellipticPV.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/Geometry/PicardLefschetzPV.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/Geometry/WedgeVanishing.lean` | 1 | 0 | 1 | 1 | 0 | 1 / 1 |
| `/app/Fakeon/Fakeon/Optimization/PLCertification.lean` | 10 | 0 | 3 | 5 | 0 | 3 / 3 |
| `/app/Fakeon/Fakeon/QFT/Assumptions.lean` | 13 | 0 | 0 | 4 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/QFT/Cutkosky.lean` | 13 | 2 | 1 | 6 | 0 | 3 / 3 |
| `/app/Fakeon/Fakeon/QFT/FakeonCurvedLSZ.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/QFT/FakeonLSZ.lean` | 0 | 0 | 0 | 0 | 0 | 0 / 0 |
| `/app/Fakeon/Fakeon/QFT/FakeonUnitarity.lean` | 5 | 1 | 3 | 2 | 1 | 4 / 4 |
| `/app/Fakeon/Fakeon/QFT/InelasticBootstrap.lean` | 0 | 0 | 5 | 4 | 1 | 4 / 5 |
| `/app/Fakeon/Fakeon/QFT/ReggeVirtualization.lean` | 3 | 1 | 1 | 2 | 0 | 2 / 2 |

## Python modules

| File | lines | def | class |
|------|------:|----:|------:|
| `/app/Fakeon/fakeon_numeric/__init__.py` | 21 | 0 | 0 |
| `/app/Fakeon/fakeon_numeric/boundary_vectors.py` | 115 | 4 | 0 |
| `/app/Fakeon/fakeon_numeric/cutkosky.py` | 175 | 7 | 0 |
| `/app/Fakeon/fakeon_numeric/distributions.py` | 53 | 3 | 0 |
| `/app/Fakeon/fakeon_numeric/omega_quadrature.py` | 11 | 1 | 0 |
| `/app/Fakeon/fakeon_numeric/partial_wave.py` | 11 | 1 | 0 |
| `/app/Fakeon/fakeon_numeric/pl_certification.py` | 150 | 5 | 2 |
| `/app/Fakeon/fakeon_numeric/radial_interpolator.py` | 11 | 1 | 0 |
| `/app/Fakeon/fakeon_numeric/regge_solver.py` | 88 | 5 | 1 |
| `/app/Fakeon/fakeon_numeric/regime.py` | 47 | 1 | 1 |
| `/app/Fakeon/fakeon_numeric/schwarzschild_radial_solver.py` | 13 | 1 | 0 |
| `/app/Fakeon/fakeon_numeric/siegel_theta.py` | 11 | 1 | 0 |
| `/app/Fakeon/fakeon_numeric/status_tracker.py` | 255 | 10 | 1 |
| `/app/Fakeon/fakeon_numeric/tolerance_ledger.py` | 80 | 7 | 2 |
| `/app/Fakeon/fakeon_numeric/validation.py` | 49 | 4 | 0 |
| `/app/Fakeon/scripts/anchor_status.py` | 302 | 13 | 1 |
| `/app/Fakeon/scripts/assemble_certificate.py` | 273 | 10 | 0 |
| `/app/Fakeon/scripts/audit_status.py` | 511 | 12 | 5 |
| `/app/Fakeon/scripts/extract_cvec.py` | 187 | 7 | 0 |
| `/app/Fakeon/scripts/fakeon_validation_ci.py` | 23 | 1 | 0 |

## Tests

| File | collected |
|------|----------:|
| `tests/test_anchor_status.py` | 10 |
| `tests/test_assemble_certificate.py` | 6 |
| `tests/test_audit_status.py` | 5 |
| `tests/test_bootstrap_optical.py` | 10 |
| `tests/test_chen_integration.py` | 10 |
| `tests/test_cutkosky.py` | 42 |
| `tests/test_dispersive_reality.py` | 7 |
| `tests/test_distribution_limits.py` | 8 |
| `tests/test_extract_cvec.py` | 8 |
| `tests/test_fakeon_pv.py` | 1 |
| `tests/test_massive_de_consistency.py` | 5 |
| `tests/test_massive_flatness.py` | 19 |
| `tests/test_numeric_imports.py` | 13 |
| `tests/test_pl_certification.py` | 10 |
| `tests/test_regge_virtualization.py` | 10 |
| `tests/test_s_matrix_extension.py` | 9 |
| `tests/test_status_tracker.py` | 10 |
| `tests/test_unitarity_closure.py` | 11 |
| `tests/test_wedge_vanishing.py` | 5 |

## CI stages

| Workflow | Job | Step |
|----------|-----|------|
| `fakeon-verify.yml` | `python` | Install deps |
| `fakeon-verify.yml` | `python` | Lint |
| `fakeon-verify.yml` | `python` | Dispersive reality check |
| `fakeon-verify.yml` | `python` | Sokhotski–Plemelj limit check |
| `fakeon-verify.yml` | `python` | Chen integration check |
| `fakeon-verify.yml` | `python` | Unitarity closure check |
| `fakeon-verify.yml` | `python` | S-matrix extension validation (S.1–S.3) |
| `fakeon-verify.yml` | `python` | Bootstrap-optical bridge check |
| `fakeon-verify.yml` | `python` | Regge virtualization certificate |
| `fakeon-verify.yml` | `python` | PL certification (Hessian spectrum) |
| `fakeon-verify.yml` | `python` | Status matrix audit |
| `fakeon-verify.yml` | `python` | Reproducibility anchor |
| `fakeon-verify.yml` | `python` | Wedge vanishing check |
| `fakeon-verify.yml` | `python` | Flatness check |
| `fakeon-verify.yml` | `python` | Full regression |
| `fakeon-verify.yml` | `python` | Audit + status report |
| `fakeon-verify.yml` | `lean` | Lake build |
| `quft-verify.yml` | `numeric` | Install Python dependencies |
| `quft-verify.yml` | `numeric` | Ruff lint |
| `quft-verify.yml` | `numeric` | HyperInt / DiffExp extraction (optional) |
| `quft-verify.yml` | `numeric` | Boundary-vector reality gate |
| `quft-verify.yml` | `numeric` | Pytest (full suite with JUnit XML) |
| `quft-verify.yml` | `numeric` | Upload pytest artefacts |
| `quft-verify.yml` | `numeric` | Status-matrix audit |
| `quft-verify.yml` | `numeric` | Merkle reproducibility anchor |
| `quft-verify.yml` | `numeric` | Assemble FakeonCertificate |
| `quft-verify.yml` | `numeric` | Upload certification artefacts |
| `quft-verify.yml` | `numeric` | Step summary |
| `quft-verify.yml` | `lean` | lake exe cache get (Mathlib olean cache) |
| `quft-verify.yml` | `lean` | lake build |

