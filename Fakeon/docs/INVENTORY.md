# INVENTORY.md (Development)

Development-focused inventory for the `Fakeon/` workspace.

This document tracks where core implementation, verification, and status artifacts live after recent upgrades.

---

## 1) Lean formalization (`Fakeon/Fakeon/`)

### Algebra
- `Algebra/MassiveDE.lean`
- `Algebra/ChenCollapse.lean`
- `Algebra/Pairing.lean`

### Analysis
- `Analysis/Distributions.lean`
- `Analysis/DispersiveReality.lean`

### Geometry
- `Geometry/FlatConnection.lean`
- `Geometry/WedgeVanishing.lean`
- `Geometry/PicardLefschetzPV.lean`
- `Geometry/HyperellipticPV.lean`
- `Geometry/GlobalPVClosure.lean`
- `Geometry/GeneralGenusPV.lean`

### QFT
- `QFT/Assumptions.lean`
- `QFT/FakeonUnitarity.lean`
- `QFT/Cutkosky.lean`
- `QFT/InelasticBootstrap.lean`
- `QFT/ReggeVirtualization.lean`
- `QFT/FakeonLSZ.lean`
- `QFT/FakeonCurvedLSZ.lean`

### Optimization + Experimental
- `Optimization/PLCertification.lean`
- `Experimental/SiegelThetaPV.lean`

### Aggregator
- `FakeonQFT.lean`

---

## 2) Numeric/runtime Python package (`fakeon_numeric/`)

### Core numeric and verification modules
- `__init__.py`
- `validation.py`
- `partial_wave.py`
- `omega_quadrature.py`
- `radial_interpolator.py`
- `siegel_theta.py`
- `schwarzschild_radial_solver.py`
- `boundary_vectors.py`
- `regime.py`
- `distributions.py`
- `cutkosky.py`
- `regge_solver.py`
- `pl_certification.py`
- `tolerance_ledger.py`
- `status_tracker.py`

### Lightning integration modules
- `lightning/hessian_pl_callback.py`
- `lightning/checkpointed_hessian_pl.py`
- `lightning/distributed_hessian_pl.py`
- `lightning/precision_controller.py`
- `lightning/zero3_hessian_pl.py`
- `lightning/zero3_compressed_hessian_pl.py`
- `lightning/fp8_zero3_hessian_pl.py`
- `lightning/zeroinfinity_fp8_hessian_pl.py`
- `lightning/zeroinfinity_cpu_fallback_pl.py`
- `lightning/spectral/robust_estimator.py`
- `lightning/Mesh/topology.py`
- `lightning/Mesh/unified_mesh.py`
- `lightning/Mesh/Schemes.py`
- `lightning/Dicovery/theory_space.py`

---

## 3) Tests (`tests/`)

### Lean/Python verification and regression tests
- `test_massive_de_consistency.py`
- `test_massive_flatness.py`
- `test_dispersive_reality.py`
- `test_distribution_limits.py`
- `test_chen_integration.py`
- `test_cutkosky.py`
- `test_unitarity_closure.py`
- `test_s_matrix_extension.py`
- `test_bootstrap_optical.py`
- `test_regge_virtualization.py`
- `test_pl_certification.py`
- `test_wedge_vanishing.py`
- `test_fakeon_pv.py`
- `test_numeric_imports.py`
- `test_status_tracker.py`

### Tooling/status/certificate tests
- `test_anchor_status.py`
- `test_audit_status.py`
- `test_assemble_certificate.py`
- `test_extract_cvec.py`
- `test_hessian_pl_callback.py`

### Lean-side test artifact
- `test_global_closure.lean`

---

## 4) Scripts (`scripts/`)

- `fakeon_validation_ci.py`
- `audit_status.py`
- `anchor_status.py`
- `assemble_certificate.py`
- `extract_cvec.py`
- `run_suite.sh`

Use these to generate or verify development evidence (status docs, anchors, certificate outputs, CI checks).

---

## 5) Documentation (`docs/`)

### Status and registry artifacts
- `STATUS.md`
- `STATUS.json`
- `STATUS_MATRIX.md`
- `status_components.json`
- `THEOREM_STATUS.md`
- `SOURCE_MAP.md`

### Review artifacts
- `LEAN_PROOF_REVIEW_2026-04-29.md`
- `REFEREE_REVIEW_2026-04-29_A5_A6.md`

### Domain sub-docs
- `numeric/README.md`
- `symbolic/README.md`
- `theory/README.md`

---

## 6) Symbolic assets (`symbolic/`)

### HyperInt
- `hyperint/crossedbox_PV.maple`
- `hyperint/crossedbox_massive_PV.maple`
- `hyperint/README.md`

### Differential equations
- `diffexp/system_2D.m`
- `diffexp/README.md`

---

## 7) Generated logs and outputs (`logs/`)

- `FakeonCertificate.json`
- `anchor.json`
- `status_matrix.json`
- `pytest-junit.xml`

These are generated artifacts and should be treated as development outputs, not hand-authored sources.

---

## 8) Build/test control files

- `pytest.ini`
- `lakefile.lean`
- `lake-manifest.json`
- `lean-toolchain`
- `README.md`
- `FAKEON-readme.md`

