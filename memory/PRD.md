# Fakeon Verification Stack — PRD

## Original Problem Statement
Build and iteratively extend the environment + Lean files for the massive
Fakeon canonical DE system (6×6, PV projection), now through O(ε³) /
weight 7 over the full 2D alphabet {z, z-1, z+y, z-y-1, y, y+1}.

## Architecture
- **Lean 4 + Mathlib** — Algebra / Geometry / QFT modules under `Fakeon/Fakeon/`.
- **Python (numpy, sympy, pytest)** — `fakeon_numeric/` + `tests/`.
- **Maple / HyperInt + Mathematica / DiffExp** — `symbolic/`.
- Layout frozen to the user-provided tree.

## Implemented
### Pass 1 (2026-01, weight 5)
- Authoritative 6×6 matrices A1..A4 and ζ₅ boundary c5 in `Algebra/MassiveDE.lean`.
- Structural + mock DE-consistency pytest (5 tests).
- HyperInt config with 4-letter alphabet, PV rules.
- Full scaffold of every layout file; lake project files.

### Pass 2 (2026-01, weight 7 / O(ε³))
- `Geometry/FlatConnection.lean`: 2D alphabet enum, `M : Fin 6 → Matrix`, `flat_connection` lemma, `chen_series`, `chen_pv_reality` theorem (stubs with strategy comments).
- `Algebra/ChenCollapse.lean` upgraded: `chen_step`, `chen_series`, `chen_collapse` theorem.
- `QFT/FakeonUnitarity.lean` wired to `chen_pv_reality`.
- `FakeonQFT.lean` now re-exports `FlatConnection`.
- `tests/test_massive_flatness.py`: 15 parametrised pairwise flatness tests (symbolic, sympy) + summary; weight-7 Chen coefficient cross-check auto-skips pending `c_k` data.
- `symbolic/hyperint/crossedbox_massive_PV.maple`: 6-letter alphabet, PV rules for all z- and y-cuts, `order = 3`.
- `docs/INVENTORY.md` refreshed with Lemma ↔ file map and data-dependency table.

## Verification Status
- pytest: **29 passed, 1 skipped** (`cd /app/Fakeon && pytest`).
- ruff: clean.
- `lake build`: deferred (Mathlib cache not fetched in preview).

## Data Dependencies Not Yet Wired
- `A5, A6` (y-evolution residue matrices) — currently zero stubs.
- `c0, c1, c2, c3` (low-weight boundary vectors).
- `c4, c6, c7` (needed by `test_chen_coefficients_weight7`).

## Prioritized Backlog
- **P0** — Supply A5, A6 authoritative entries; upgrade `flat_connection` from stub to full statement over `ℝ²_{>0}`.
- **P0** — Wire `fakeon_numeric.validation.load_boundary_vectors` + `load_c7` (parse HyperInt `massive_masters_w7.m`) → activate the skipped weight-7 test.
- **P1** — Populate `Geometry/PicardLefschetzPV.lean`, `Geometry/GlobalPVClosure.lean`; promote `chen_pv_reality` to a non-trivial ℂ statement.
- **P2** — `FakeonLSZ.lean`, `FakeonCurvedLSZ.lean`; experimental Siegel theta.

## Next Tasks
1. Receive A5, A6 and the c_k batch; drop into the existing slots.
2. Run `lake exe cache get && lake build` locally.
3. Begin the formal proof of `chen_collapse`.
