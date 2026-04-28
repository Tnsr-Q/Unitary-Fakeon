# Unitary-Fakeon Repository Guide (Development-Oriented)

This repository is a **multi-part workspace** that combines:

- a formalization-heavy **`Fakeon/` research and verification project** (Lean + Python + symbolic assets),
- a separate **`frontend/` React UI codebase**,
- a lightweight **`backend/` Python service stub**,
- and top-level notes/artifacts used for planning and reporting.

The purpose of this README is to help contributors quickly understand **what is in the repo** and **how it is organized**.

---

## Top-Level Layout

```text
.
├── README.md                 # This development-facing repo map
├── memory/                   # Product/planning notes
├── backend/                  # Python backend service stub
├── frontend/                 # React/Tailwind frontend project
├── Fakeon/                   # Main formal + numeric + symbolic project
├── tests/                    # Top-level Python test package marker
└── test_result.md            # Captured test/report artifact
```

---

## `Fakeon/` (Core Research + Verification Workspace)

`Fakeon/` is the largest and most structured part of the repository. It mixes:

1. **Formal Lean developments**,
2. **Python numeric/validation modules**,
3. **Symbolic computation inputs**,
4. **Status dashboards and generated logs**,
5. **Automation scripts and tests**.

### `Fakeon/` high-level tree

```text
Fakeon/
├── README.md
├── FAKEON-readme.md
├── pytest.ini
├── lean-toolchain
├── lakefile.lean
├── lake-manifest.json
├── Fakeon/                  # Lean source tree
├── fakeon_numeric/          # Python numeric library
├── tests/                   # Python test suite
├── scripts/                 # CI/status/certificate tooling
├── docs/                    # Status docs, inventories, reviews
├── logs/                    # Generated logs/certificates/matrices
└── symbolic/                # Symbolic computation assets
```

### Lean source tree: `Fakeon/Fakeon/`

The Lean modules are grouped by topic:

- `Algebra/`
- `Analysis/`
- `Geometry/`
- `QFT/`
- `Optimization/`
- `Experimental/`

Entry/aggregation module:

- `Fakeon/Fakeon/FakeonQFT.lean`

### Python numeric library: `Fakeon/fakeon_numeric/`

This package contains numerical routines and helpers, including:

- quadrature and interpolation,
- partial-wave and PL certification logic,
- solver/status tracking modules,
- distribution/cutkosky-related numerics,
- optional Lightning callbacks under `lightning/`.

### Tests: `Fakeon/tests/`

The suite is composed of focused `pytest` modules that mirror theorem/numeric domains (unitarity closure, cutkosky, wedge vanishing, PL certification, status/audit checks, etc.).

### Scripts: `Fakeon/scripts/`

Automation and reporting scripts include:

- status anchoring and auditing,
- certificate assembly,
- CI validation entrypoints,
- utility extractors.

### Docs and status assets: `Fakeon/docs/` + `Fakeon/logs/`

- `docs/` holds inventories, source maps, status matrices, and review notes.
- `logs/` holds machine-produced artifacts such as certificates and status outputs.

### Symbolics: `Fakeon/symbolic/`

Contains symbolic-analysis inputs and notes split by method families:

- `hyperint/`
- `diffexp/`

---

## `frontend/` (UI Project)

`frontend/` is a React application with Tailwind/PostCSS toolchain and component-heavy UI structure.

```text
frontend/
├── package.json
├── craco.config.js
├── tailwind.config.js
├── postcss.config.js
├── components.json
├── public/
├── src/
│   ├── App.js / App.css / index.js / index.css
│   ├── components/ui/      # Large shadcn-style UI component set
│   ├── hooks/              # Shared hooks (e.g., toast handling)
│   └── lib/                # Utility helpers
└── plugins/health-check/   # Health-check webpack plugin/helpers
```

---

## `backend/` (Service Stub)

`backend/` currently contains:

- `server.py` — backend entry module,
- `requirements.txt` — Python dependency manifest for backend scope.

---

## Other Top-Level Artifacts

- `memory/PRD.md` — product/planning reference.
- `tests/__init__.py` — top-level Python tests package marker.
- `test_result.md` — stored test output/report artifact.

---

## Contributor Orientation Notes

When making development changes, treat this repository as **multiple adjacent projects** with different concerns:

- **Formal proof/code track** under `Fakeon/Fakeon/` (Lean),
- **Numeric/test tooling track** under `Fakeon/fakeon_numeric/`, `Fakeon/tests/`, and `Fakeon/scripts/`,
- **UI track** under `frontend/`,
- **Backend service track** under `backend/`.

Favor keeping changes scoped to the relevant subtree and preserving the existing domain separation reflected in the directory structure.
