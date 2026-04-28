# Fakeon Verification Stack — PRD

## Original Problem Statement
Build the environment and lean files to verify the massive Fakeon canonical
DE system (6×6, alphabet {z, z-1, z+y, z-y-1}), with a numeric DE consistency
test and HyperInt configuration.  Prepare for more expansions after approval.

## Architecture
- **Lean 4 + Mathlib** — formal algebra / geometry / QFT modules under `Fakeon/`.
- **Python (numpy, pytest)** — `fakeon_numeric/` package + `tests/` regression suite.
- **Maple / HyperInt + Mathematica / DiffExp** — symbolic engines under `symbolic/`.
- Layout frozen to the user-provided tree (`Fakeon/` root with inner `Fakeon/`, `fakeon_numeric/`, `scripts/`, `tests/`, `symbolic/`, `docs/`).

## Implemented (2026-01)
- Authoritative 6×6 residue matrices A1..A4 and ζ₅ boundary vector c5 in `Fakeon/Algebra/MassiveDE.lean`.
- `massive_pv_reality` lemma scaffolded (trivial ℝ version; full ℂ version pending Geometry modules).
- `tests/test_massive_de_consistency.py` — 5 tests: shape, integer entries, sparsity, trivial first row, mock DE consistency. All passing.
- `tests/test_numeric_imports.py` — 7 parametrised import smoke tests for `fakeon_numeric`.
- `tests/test_fakeon_pv.py` — placeholder, passing.
- HyperInt config `symbolic/hyperint/crossedbox_massive_PV.maple` with PV projection rules.
- Lake project files (`lakefile.lean`, `lake-manifest.json`, `lean-toolchain`) — Mathlib fetch deferred (opt-in).
- `docs/INVENTORY.md` and `docs/SOURCE_MAP.md` cross-referencing Lean ↔ Numeric ↔ Symbolic.
- Placeholders for all other files in the published layout (Lean stubs, numeric stubs, scripts, DiffExp config).

## Verification Status
- pytest: **13/13 passing** locally (`cd /app/Fakeon && pytest`).
- ruff: clean on all Python modules.
- `lake build`: deferred (not run in preview container; requires Mathlib cache).

## Prioritized Backlog (P0 → P2)
- **P0** — fill in `Algebra/ChenCollapse.lean` and upgrade `massive_pv_reality` to a non-trivial ℂ-valued statement.
- **P0** — replace `_load_master_vector` with a real HPL evaluator (extract from HyperInt dump via `scripts/extract_cvec.py`).
- **P1** — populate `Geometry/PicardLefschetzPV.lean` and `Geometry/GlobalPVClosure.lean`.
- **P1** — implement `fakeon_numeric.validation.validate_masters` comparing symbolic vs. direct numeric contour integration.
- **P2** — QFT chain (`FakeonUnitarity` → `FakeonLSZ` → `FakeonCurvedLSZ`).
- **P2** — Experimental `SiegelThetaPV` and hyperelliptic / general-genus closure.

## Next Tasks
1. Run `lake exe cache get && lake build` locally to confirm the Lean files elaborate against Mathlib.
2. Export weight-5 HPL expressions from HyperInt and wire them into the numeric test.
3. Begin formalisation of Chen-series collapse.
