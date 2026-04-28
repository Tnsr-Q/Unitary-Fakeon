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

### Lightning Submodule Breakdown (`Fakeon/fakeon_numeric/lightning/`)

The `lightning` folder is an opt-in training instrumentation package for PyTorch Lightning that layers Hessian-spectrum probing, PL-condition checking, and adaptive learning-rate control on top of distributed training pipelines.

**Package-level structure**
- `__init__.py`: exports callback variants and keeps this namespace opt-in so torch/lightning dependencies do not leak into the core verification stack.
- `spectral/`: reusable spectral estimation primitives (robust Lanczos/power methods).
- `Mesh/`: mesh/topology/scheme utilities for geometry-aware or discretization-aware experiments.
- `Dicovery/`: theory-space discovery helpers (note: folder name appears intentionally/legacy-spelled as `Dicovery`).

**Core callback families**
- `hessian_pl_callback.py` (`HessianPLCallback`): baseline and most certification-aligned callback; uses stochastic Lanczos HVP estimation, PL ratio checks, and LR adaptation bounded by smoothness constraints and certified constants.
- `distributed_hessian_pl.py` / `checkpointed_hessian_pl.py`: distributed + activation-checkpointed variants with optional persisted callback state and all-reduce/all-gather aggregation paths.
- `zero3_hessian_pl.py`: ZeRO-3/FSDP parameter-gather-aware callback with robust spectral estimation and optional dynamic tolerance ledger coupling.
- `zero3_compressed_hessian_pl.py`: communication/computation pressure reduction variant (compressed state paths) for ZeRO-3 workloads.
- `fp8_zero3_hessian_pl.py`: FP8-aware ZeRO-3 pathway that attempts lower-precision acceleration where hardware/runtime supports it.
- `zeroinfinity_fp8_hessian_pl.py`: ZeRO-Infinity + FP8 monitoring path that also tracks NVMe I/O side effects.
- `zeroinfinity_cpu_fallback_pl.py`: resilience-oriented ZeRO-Infinity branch that can shift execution toward CPU fallback when storage/runtime health gates fail.

**Shared technical themes across callbacks**
- Hessian-vector product construction with double-backprop for curvature monitoring.
- Lanczos tridiagonal spectrum approximations to estimate `(mu, L)` and condition number.
- PL-condition checking via `0.5*||grad||^2 / (loss-loss*)` style ratios.
- Adaptive LR updates based on spectral bounds, clipped by stability envelopes.
- Distributed reductions (`all_reduce`, `all_gather`, `broadcast`, optional barriers) to keep optimizer decisions synchronized.
- Optional activation checkpointing to reduce memory at the cost of extra recomputation.

**Runtime adaptation helpers**
- `precision_controller.py`: runtime precision negotiation utility (FP8/BF16/FP32 fallbacks), telemetry emission, and quantize/dequantize error tracking for mixed-precision observability.
- `spectral/robust_estimator.py`: safety-factored and EMA-smoothed global spectral estimator plus bounded LR heuristic (`compute_adaptive_lr`).

**Operational notes for maintainers**
- This folder contains multiple evolutionary callback implementations that overlap in scope; some are targeted to specific infra profiles (plain DDP vs ZeRO-3 vs ZeRO-Infinity).
- Several modules import from `src.*` paths (e.g., orbax/spectral/tolerance helpers), so portability depends on the expected runtime package layout.
- Because this package is explicitly opt-in, breakages here should not block the torch-free verification core, but callback-level tests are still recommended whenever these files change.
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
