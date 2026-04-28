# 🔷 Status Matrix: Quadratic Relativity / QFT-Engine

*Epistemic tagging of all lemmas, formal proofs, computational modules,
and physical predictions.  Status levels follow `STATUS_LEVELS` from
`S-matrix analysis.txt`.*

| Status Level | Definition |
|--------------|------------|
| `PROVED` | Formal theorem with explicit assumptions (Lean / axiom-explicit) |
| `VERIFIED` | Numerically confirmed within stated bounds (CI / ledger-pass) |
| `CALCULATED` | Analytical derivation complete (symbolic / perturbative) |
| `DEMONSTRATED` | Constructive framework, not full existence proof |
| `PENDING` | Open problem; testable predictions defined, awaiting experiment |
| `METADATA` | Bookkeeping artefact (assumption tag, certificate registry) |

The machine-readable counterpart of every row below lives in
`docs/status_components.json`.  CI loads that file on every run and
fails the build whenever a row's claimed status cannot be reproduced
(see `fakeon_numeric/status_tracker.py`).

> **Note on this document vs. the JSON registry.**  This table is the
> *target* state of the verification programme.  The live repository
> state is the JSON file, which may downgrade individual rows (e.g. a
> `PROVED` claim downgrades to `PENDING` until the Lean module exists).
> The promotion rules in `docs/THEOREM_STATUS.md` govern when a JSON
> row may be raised to its target status.

---

## 📐 1. Theoretical Lemmas & Supplementary Results

| Component | Status | Verification Method | Assumption Dependencies | Basis / Evidence |
|-----------|--------|---------------------|-------------------------|------------------|
| **L1: SM Coupling** | `PROVED` | Lean + Symbolic BRST | A₁, A₃ | Palatini variational principle; fakeon projector rank unchanged |
| **L2: Mass Generation** | `VERIFIED` | 2-Loop RGE + Thermal Solver | A₂, A₄ | Copositivity λ_H, λ_S > 0; Picard–Lindelöf uniqueness |
| **L3: Anomaly Freedom** | `CALCULATED` | `brst_checker.py` (sym) | A₃ | Gauge–gravity anomalies cancel; s² = 0 preserved under PV contour |
| **L4: IR Fixed-Point** | `VERIFIED` | Lyapunov + Hessian PL | A₄, A₅ | μ ≈ 2.4 × 10⁻²; exponential convergence on 𝒲^{cs} |
| **L5: Observational Closure** | `DEMONSTRATED` | Constraint monotonicity + flat IR floor | A₅ | Single f₂* ≃ 10⁻⁸ satisfies UV / IR / SM targets simultaneously |
| **S.1: Lorentzian Spectral Flow** | `DEMONSTRATED` | Dispersive integral ansatz | A₁, S.1 | G_k(p) modulates spectral weights without violating iε |
| **S.2: Inelastic Dual Bootstrap** | `DEMONSTRATED` | η_ℓ(s) profile + crossing loss | A₂, S.2 | \|S_ℓ(s)\| ≤ 1; Froissart–Martin σ_tot ≤ C ln²(s/s₀) |
| **S.3: β-Function Closure** | `CALCULATED` | MS-scheme perturbative derivation | A₄ | β^(1)_{f₂} = −133 / (20 (4π)²) · f₂³; 2-loop gravitational + SM cross-terms |

---

## 🧮 2. Lean Formalizations

| Module / Theorem | Status | Verification Method | Assumption Dependencies | Basis / Evidence |
|------------------|--------|---------------------|-------------------------|------------------|
| `Fakeon/Analysis/DispersiveReality.lean → im_eq_zero` | `DEMONSTRATED` | Inductive dispersive limit | S.1 | ρ_GF^{(1)}(μ²) = 0; Sokhotski–Plemelj projection |
| `Fakeon/Algebra/ChenCollapse.lean → chen_series_real` | `DEMONSTRATED` | Weight-n induction + PV kernels | A₁, A₄ | Rational M_k + real d ln \|α_k\| + real c_n |
| `Fakeon/Geometry/WedgeVanishing.lean → wedge_vanishes_on_rg_flow` | `DEMONSTRATED` | 1D manifold reduction | A₄, A₅ | Non-commuting constraints ⇒ d ln α_i ∧ d ln α_j = 0 |
| `Fakeon/QFT/FakeonUnitarity.lean → perturbative_unitarity_closure` | `DEMONSTRATED` | Modified Cutkosky + Chen reality | A₁–A₅, S.1, S.2 | P_phys S† S P_phys = P_phys (conditional on axioms) |
| `Fakeon/QFT/InelasticBootstrap.lean → loss_zero_implies_unitarity` | `DEMONSTRATED` | Loss-zero ⇒ ‖S_ℓ‖ ≤ 1 + bridge to optical inequality | A₂, S.2, S.3 | Im T_ℓ ≥ ‖T_ℓ‖² from S = 1 + 2 i T |
| `Fakeon/QFT/Assumptions.lean → smatrix_unitarity_cert` | `METADATA` | Axiom tagging + status bundle | — | Explicit dependency graph for downstream theorems |

---

## 💻 3. Computational Modules & CI Tests

| Module / Test File | Status | Verification Method | Assumption Dependencies | Basis / Evidence |
|--------------------|--------|---------------------|-------------------------|------------------|
| `tests/test_dispersive_reality.py` | `VERIFIED` | Parametric Im[c_n] across n=0..5 | S.1 | All entries pass `\|Im\| < 1e-14` under ρ_GF ≡ 0 |
| `tests/test_distribution_limits.py` | `VERIFIED` | Sokhotski–Plemelj quadrature | S.1 | I(η) ↔ −π · exp(η²) · erfc(η) match to 1e-7 |
| `tests/test_chen_integration.py` | `VERIFIED` | Recursive Chen reality (weight 1..4) | A₁, A₄, S.1 | Chen step preserves \|Im\| < 1e-12 |
| `tests/test_unitarity_closure.py` | `VERIFIED` | P S† S P − P residual sweep | A₁..A₅, S.1, S.2 | Block-diagonal Hermitian H, residual < 1e-10 |
| `tests/test_s_matrix_extension.py` | `VERIFIED` | S.1/S.2/S.3 hooks + ledger | S.1, S.2, S.3 | Spectral-density, Froissart, β-closure all pass |
| `tests/test_massive_flatness.py` | `VERIFIED` | Symbolic wedge / commutator pair sweep | A₁ | 15 pairs satisfy flatness disjunction |
| `tests/test_wedge_vanishing.py` | `VERIFIED` | Rank ≤ 1 on synthetic 1D RG curve | A₄, A₅ | True positive + true negative sanity |
| `SIQGRGESolver` | `PENDING` | RK45, rtol=1e-8, atol=1e-10 | A₄ | Awaiting wiring (registry placeholder) |
| `DiscretizedBootstrapSolver` | `PENDING` | L-BFGS-B, unitarity / crossing loss | S.2 | Awaiting wiring |
| `JAXHessianEstimator` | `PENDING` | Lanczos, k-step HVP | A₄, A₅ | Awaiting wiring |
| `ReggeExtendedBootstrap` | `PENDING` | Newton–Raphson pole tracking | S.2 | Awaiting wiring |

---

## 🌌 4. Physics Outputs & Certificates

| Component | Status | Verification Method | Assumption Dependencies | Basis / Evidence |
|-----------|--------|---------------------|-------------------------|------------------|
| Convergence root f₂* ≃ 10⁻⁸ | `PENDING` | Monotonic UV selectors + PL descent | L1–L4 | Awaiting numerical run |
| PL constant μ ≈ 2.4 × 10⁻² | `PENDING` | Hessian GN spectrum (500 perturbations) | A₄, A₅ | Awaiting Hessian estimator |
| Lyapunov decay rate γ ≈ 0.082 | `PENDING` | λ_min / λ_max ratio + PPO clipping | A₄ | Awaiting optimizer integration |
| Fakeon virtualization certificate | `PENDING` | Regge pole extraction Re α(M₂²) < 0 | S.2 | Awaiting Regge bootstrap |
| Vacuum metastability S_E ≈ 8.2 × 10³ | `PENDING` | Thin-wall bounce action | A₂ | Awaiting bounce integrator |
| Froissart–Martin saturation | `VERIFIED` | Bootstrap asymptotic extrapolation | S.2 | σ_tot ≤ 0.25 ln²(s/s₀) enforced + violation case rejected |

---

## 🔭 5. Experimental Predictions

| Prediction | Status | Verification Method | Assumption Dependencies | Basis / Evidence |
|------------|--------|---------------------|-------------------------|------------------|
| Top mass m_t = 173.1 ± 0.3 GeV | `PENDING` | Collider measurement (ATLAS/CMS) | L2, S.3 | 2-loop SM cross-term β^(2,SM)_{f₂} precision shift |
| SGWB double peak (Δf = 9 Hz) | `PENDING` | LISA / DECIGO spectral analysis | S.1, L5 | Fakeon threshold resonance + reheating coupling imprint |
| PBH abundance f_PBH ≈ 1 | `PENDING` | Microlensing / GW merger rates | 𝒞_DM, 𝒞_infl | Inflationary fluctuation spectrum tuned by f₂* |
| Echo spacing signature | `PENDING` | LIGO / Virgo / KAGRA ringdown residuals | 𝒞_echo, S.2 | Regge pole interference in post-merger waveform |

---

## ⚙️ Implementation & CI Integration

### Status tracker

`fakeon_numeric/status_tracker.py` consumes `docs/status_components.json`
and verifies, per row, that the claimed status is reproducible:

| Status        | CI verification rule                                                             |
|---------------|----------------------------------------------------------------------------------|
| `PROVED`      | Lean source file exists **and** contains no `sorry`                              |
| `VERIFIED`    | Tolerance ledger has a `passed=True` entry for the registered ledger key        |
| `CALCULATED`  | Lean source file exists (closed-form result lives in code, not as a `sorry`)    |
| `DEMONSTRATED`| Lean source file exists (no completeness claim — passes by definition)          |
| `PENDING`     | Always passes (placeholder)                                                      |
| `METADATA`    | Always passes (bookkeeping)                                                      |

`PROVED` rows that still contain a `sorry` are **silently downgraded**
to `DEMONSTRATED` in the audit output, and the build fails.  This is
the promotion-rules guardrail from `docs/THEOREM_STATUS.md`.

### CI hook

`.github/workflows/fakeon-verify.yml` runs the tracker as a named stage
that emits `logs/status_matrix.json`, asserts `all(ci_verified)`, and
attaches both `STATUS_MATRIX.md` and `status_matrix.json` to the build.
