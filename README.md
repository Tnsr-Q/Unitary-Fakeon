# Unitary-Fakeon Repository Guide (Development-Only)

This repository contains multiple active codebases that evolve together during development:

- `Fakeon/`: formal Lean proofs, numeric Python modules, symbolic assets, and verification tooling.
- `frontend/`: React/Tailwind UI workspace.
- `backend/`: lightweight Python service stub.
- `memory/`: product and planning notes.

This README intentionally focuses on **development orientation**, not end-user installation.

---

## Top-Level Layout

```text
.
├── README.md
├── backend/
├── frontend/
├── Fakeon/
├── memory/
├── tests/
└── test_result.md
```

---

## Development Guardrails

When adding or refactoring runtime behavior, follow these repository rules:

- Do not add transport before policy/replay/run closure.
- Do not publish plugin-originating events without PolicyEngine admission.
- Do not write raw JSON strings where `serde_json::Value` is expected.
- Do not manually format browser JSON.
- Do not use non-cryptographic hashes for provenance.
- Do not let station-kernel absorb reusable logic.
- Do not make browser or GPUI projections authoritative.
- Do not panic on expected runtime denials; emit evidence events.
- Every new runtime decision should be replayable.
- Every new crate needs unit tests.

Future sidecars may use `local`, `wasm`, `subprocess`, `websocket`, `grpc`, `connectrpc`, `pyro5`, and `ffi`, but must always stay behind:
`PluginRegistry`, `StationSupervisor`, `SchemaRegistry`, `PolicyEngine`, `JsonlReplayLog`, `ArtifactLedger`, and `RunManifest`.

---

## Repository Workstreams

### 1) `Fakeon/` (formal + numeric + symbolic + status)

Key areas:

- `Fakeon/Fakeon/`: Lean modules for algebra, analysis, geometry, QFT, optimization, and experiments.
- `Fakeon/fakeon_numeric/`: Python numeric modules (distribution checks, cutkosky, regime detection, PL certification, status tracking, and optional lightning callbacks).
- `Fakeon/tests/`: verification tests across symbolic, numeric, and status/CI workflows.
- `Fakeon/scripts/`: automation (`audit_status.py`, `anchor_status.py`, certificate assembly, extractors, CI helpers).
- `Fakeon/docs/`: status matrix, theorem/proof status, source maps, and review artifacts.
- `Fakeon/logs/`: generated outputs (anchors, status JSON, certificates, junit report).

Use `Fakeon/docs/INVENTORY.md` as the detailed development inventory.

### 2) `frontend/` (UI)

- React app with Tailwind/PostCSS and CRACO.
- Health-check plugin under `frontend/plugins/health-check/`.
- UI components and utilities under `frontend/src/`.

### 3) `backend/` (service stub)

- `backend/server.py`.
- `backend/requirements.txt`.

### 4) `memory/` (planning)

- `memory/PRD.md` for planning/product notes.

---

## Development Workflow (Quick Reference)

- Keep changes scoped to a single workstream whenever possible.
- Prefer updating docs/status outputs when logic changes.
- Run targeted tests first, then broader suites.
- Treat generated artifacts in `Fakeon/logs/` and status docs as part of development evidence.

Typical commands used during development:

```bash
# Python tests (Fakeon workspace)
cd Fakeon && pytest

# Status/doc refresh helpers
cd Fakeon && python scripts/audit_status.py
cd Fakeon && python scripts/anchor_status.py --verify
```

---

## Where to Update Docs During Development

- Repository map and cross-project orientation: `README.md` (this file).
- Deep file/module inventory for Fakeon: `Fakeon/docs/INVENTORY.md`.
- Verification and theorem state snapshots: `Fakeon/docs/STATUS.md`, `Fakeon/docs/THEOREM_STATUS.md`.
