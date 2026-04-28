# INVENTORY.md

File-by-file index of the Fakeon verification repository.  ✅ = fully
populated, 🟡 = authoritative content present but proofs pending,
⬜ = placeholder.

## Lean sources (`Fakeon/Fakeon/`)

| File                                   | Status | Purpose                              |
|----------------------------------------|--------|--------------------------------------|
| `Algebra/MassiveDE.lean`               | 🟡     | 6×6 matrices, c5, PV reality lemma   |
| `Algebra/ChenCollapse.lean`            | ⬜     | Chen series collapse                 |
| `Geometry/PicardLefschetzPV.lean`      | ⬜     | PL stability of PV contour           |
| `Geometry/HyperellipticPV.lean`        | ⬜     | Hyperelliptic PV extension           |
| `Geometry/GlobalPVClosure.lean`        | ⬜     | Global monodromy closure             |
| `Geometry/GeneralGenusPV.lean`         | ⬜     | Arbitrary-genus closure              |
| `QFT/FakeonUnitarity.lean`             | ⬜     | Perturbative unitarity               |
| `QFT/FakeonLSZ.lean`                   | ⬜     | Flat-space LSZ for fakeons           |
| `QFT/FakeonCurvedLSZ.lean`             | ⬜     | Curved-space LSZ                     |
| `Experimental/SiegelThetaPV.lean`      | ⬜     | PV on Siegel theta                   |
| `FakeonQFT.lean`                       | ✅     | Top-level re-exports                 |

## Numeric package (`fakeon_numeric/`)

| Module                                  | Status |
|-----------------------------------------|--------|
| `validation.py`                         | ⬜     |
| `partial_wave.py`                       | ⬜     |
| `omega_quadrature.py`                   | ⬜     |
| `radial_interpolator.py`                | ⬜     |
| `siegel_theta.py`                       | ⬜     |
| `schwarzschild_radial_solver.py`        | ⬜     |

## Tests (`tests/`)

| File                                   | Status |
|----------------------------------------|--------|
| `test_massive_de_consistency.py`       | ✅ (structural + mock DE) |
| `test_fakeon_pv.py`                    | ⬜     |
| `test_numeric_imports.py`              | ✅     |

## Scripts (`scripts/`)

| File                           | Status |
|--------------------------------|--------|
| `fakeon_validation_ci.py`      | ✅     |
| `extract_cvec.py`              | ⬜     |

## Symbolic (`symbolic/`)

| File                                        | Status |
|---------------------------------------------|--------|
| `hyperint/crossedbox_PV.maple`              | ⬜     |
| `hyperint/crossedbox_massive_PV.maple`      | ✅     |
| `diffexp/system_2D.m`                       | ⬜     |
