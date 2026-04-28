# INVENTORY.md

File-by-file index of the Fakeon verification repository.  ✅ = fully
populated, 🟡 = authoritative content present but proofs pending,
⬜ = placeholder.

## Lean sources (`Fakeon/Fakeon/`)

| File                                   | Status | Purpose                                       |
|----------------------------------------|--------|-----------------------------------------------|
| `Algebra/MassiveDE.lean`               | 🟡     | 6×6 matrices A1..A4, c5, PV reality scaffold  |
| `Algebra/ChenCollapse.lean`            | 🟡     | Chen recursion + collapse theorem (stub)      |
| `Geometry/FlatConnection.lean`         | 🟡     | 2D flat connection, `flat_connection`, `chen_pv_reality` |
| `Geometry/PicardLefschetzPV.lean`      | ⬜     | PL stability of PV contour                    |
| `Geometry/HyperellipticPV.lean`        | ⬜     | Hyperelliptic PV extension                    |
| `Geometry/GlobalPVClosure.lean`        | ⬜     | Global monodromy closure                      |
| `Geometry/GeneralGenusPV.lean`         | ⬜     | Arbitrary-genus closure                       |
| `QFT/FakeonUnitarity.lean`             | 🟡     | Unitarity, wired to `chen_pv_reality`         |
| `QFT/FakeonLSZ.lean`                   | ⬜     | Flat-space LSZ for fakeons                    |
| `QFT/FakeonCurvedLSZ.lean`             | ⬜     | Curved-space LSZ                              |
| `Experimental/SiegelThetaPV.lean`      | ⬜     | PV on Siegel theta                            |
| `FakeonQFT.lean`                       | ✅     | Top-level re-exports (now imports FlatConnection) |

### Lemma map (2D connection)

| Lemma / theorem           | Home file                              | Status |
|---------------------------|----------------------------------------|--------|
| `flat_connection`         | `Geometry/FlatConnection.lean`         | 🟡 stub, symbolic counterpart in pytest |
| `chen_step`               | `Algebra/ChenCollapse.lean`            | 🟡 signature only |
| `chen_series`             | `Algebra/ChenCollapse.lean` + `Geometry/FlatConnection.lean` | 🟡 signature only |
| `chen_collapse`           | `Algebra/ChenCollapse.lean`            | 🟡 statement only |
| `chen_pv_reality` (all n) | `Geometry/FlatConnection.lean`         | 🟡 stub |
| `massive_pv_reality`      | `Algebra/MassiveDE.lean`               | 🟡 trivial ℝ version |
| `fakeon_unitarity`        | `QFT/FakeonUnitarity.lean`             | 🟡 reduces to `chen_pv_reality` |

## Numeric package (`fakeon_numeric/`)

| Module                                  | Status |
|-----------------------------------------|--------|
| `validation.py`                         | ⬜ (needs `load_boundary_vectors`, `load_c7`) |
| `partial_wave.py`                       | ⬜     |
| `omega_quadrature.py`                   | ⬜     |
| `radial_interpolator.py`                | ⬜     |
| `siegel_theta.py`                       | ⬜     |
| `schwarzschild_radial_solver.py`        | ⬜     |

## Tests (`tests/`)

| File                                   | Status |
|----------------------------------------|--------|
| `test_massive_de_consistency.py`       | ✅ structural + mock DE (5 tests) |
| `test_massive_flatness.py`             | ✅ symbolic flatness (15 pair tests + summary); weight-7 Chen check auto-skips until data is wired |
| `test_fakeon_pv.py`                    | ⬜ placeholder |
| `test_numeric_imports.py`              | ✅ 7 import smoke tests |

## Scripts (`scripts/`)

| File                           | Status |
|--------------------------------|--------|
| `fakeon_validation_ci.py`      | ✅     |
| `extract_cvec.py`              | ⬜ will parse HyperInt `massive_masters_w7.m` into `load_c*` |

## Symbolic (`symbolic/`)

| File                                        | Status |
|---------------------------------------------|--------|
| `hyperint/crossedbox_PV.maple`              | ⬜ massless placeholder |
| `hyperint/crossedbox_massive_PV.maple`      | ✅ 6 letters, `order = 3`, weight-7 ready |
| `diffexp/system_2D.m`                       | ⬜     |

## Data dependencies not yet wired

| Symbol            | Needed by                                   |
|-------------------|---------------------------------------------|
| `A5, A6`          | `FlatConnection.lean`, `test_massive_flatness.py` |
| `c0, c1, c2, c3`  | `ChenCollapse.lean`                         |
| `c4, c6, c7`      | `test_massive_flatness::test_chen_coefficients_weight7` |
