# Fakeon

Formal + numeric verification stack for the **massive Fakeon** canonical
differential-equation system with Principal-Value (PV) projection.

## Layout

```
Fakeon/                     # Lean sources (Mathlib-based)
  Algebra/                  # Canonical DE, Chen series collapse
  Geometry/                 # PV geometry (Picard–Lefschetz, Siegel, …)
  QFT/                      # Unitarity & LSZ for fakeons
  Experimental/             # Work in progress
fakeon_numeric/             # Python numerics package
scripts/                    # CI and extraction helpers
tests/                      # pytest regression suite
symbolic/                   # HyperInt / DiffExp symbolic configs
docs/                       # Theory / numeric / symbolic notes
```

## Quick start

```bash
# Python tests
cd /app/Fakeon && pytest

# Lean build (requires Mathlib cache; not run in the preview container)
#   lake exe cache get
#   lake build
```

## Current verification status

| Component                         | Status         |
|-----------------------------------|----------------|
| 6×6 massive matrices A1..A4       | Authoritative  |
| Boundary vector c5 (ζ₅ sector)    | Authoritative  |
| PV reality lemma (Lean)           | Scaffolded (`sorry`) |
| DE consistency (numeric)          | Passing (mock) |
| HyperInt config                   | Ready to run   |

See `FAKEON-readme.md` for the full theoretical context and
`docs/INVENTORY.md` for a file-by-file index.
