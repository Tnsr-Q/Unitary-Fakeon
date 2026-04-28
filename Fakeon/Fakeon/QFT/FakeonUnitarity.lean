/-
  Fakeon/QFT/FakeonUnitarity.lean

  Perturbative unitarity closure on the physical Hilbert space `H_phys`.

  Proof architecture (assumption-tagged, "Advanced Candidate Framework"):

    H = H_phys ⊕ H_fakeon
       └────────┘   └────────┘
       projector       fakeon
       P_phys = P†   spectrally-zero (S.1)

    S = I + i T,   modified Cutkosky restricted to physical cuts.

    Chain of inferences:
      (a) chen_series_real     ⇒  fakeon sector amplitude is real;
      (b) fakeon_spectral_cut_zero (S.1) ⇒ Disc_total = Disc_physical;
      (c) physical_optical_theorem   ⇒  2 Im (P T P) = (P T P)† (P T P);
      (d) bootstrap_unitarity_bound (S.2) ⇒ ‖S_l‖ ≤ 1;
      (e) algebraic cancellation in S† S    ⇒  P_phys S† S P_phys = P_phys.

  This file scaffolds (a)..(e) with explicit hypotheses and named axioms.
  The substantive Mathlib work (matrix conjugate-transpose / "imaginary
  part of a matrix" / `Matrix.adjoint`) is parked behind `sorry` with
  inline tactic notes.

  Imports
  -------
    * Fakeon.Algebra.ChenCollapse        — chen_series_real, c_vec
    * Fakeon.Analysis.Distributions      — causalProp, dispersive integral
    * Fakeon.Analysis.DispersiveReality  — im_eq_zero, fakeon spectral axiom
    * Fakeon.Geometry.FlatConnection     — M
-/

import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.Analysis.Complex.Basic
import Mathlib.Data.Matrix.Basic
import Fakeon.Algebra.ChenCollapse
import Fakeon.Analysis.Distributions
import Fakeon.Analysis.DispersiveReality
import Fakeon.Geometry.FlatConnection

open Complex Matrix

namespace Fakeon.QFT.FakeonUnitarity

/-! ## Hilbert-space decomposition -/

variable {N : ℕ}

/-- Orthogonal projector onto `H_phys`.  Self-adjointness and idempotency
    are captured by `P_phys_properties` below. -/
variable (P_phys : Matrix (Fin N) (Fin N) ℂ)

/-- **P_phys is a self-adjoint idempotent.** -/
axiom P_phys_properties :
    P_phys * P_phys = P_phys ∧ P_phys.conjTranspose = P_phys

/-! ## S-matrix at loop order `L` -/

/-- `T_L` ≔ amputated `L`-loop scattering operator.  Concrete form is
    supplied by the Bootstrap / Chen-series module; we keep it opaque
    here to keep the file self-contained. -/
noncomputable def T_matrix (_L : ℕ) : Matrix (Fin N) (Fin N) ℂ := 0

/-- `S_L = 1 + i · T_L`. -/
noncomputable def S_matrix (L : ℕ) : Matrix (Fin N) (Fin N) ℂ :=
  (1 : Matrix (Fin N) (Fin N) ℂ) + Complex.I • T_matrix (N := N) L

/-! ## Physics axioms (S.1 – S.3 from the S-matrix analysis) -/

/-- **S.1**  Fakeon-mediated cuts have vanishing discontinuity.
    Stated abstractly via opaque predicates `IsFakeonCut` and the
    discontinuity functional `discCut`; both are placeholders for the
    eventual `Fakeon/QFT/Cutkosky.lean`. -/
axiom IsFakeonCut : Type
axiom discCut : IsFakeonCut → Matrix (Fin N) (Fin N) ℂ → Matrix (Fin N) (Fin N) ℂ
axiom fakeon_spectral_cut_zero (L : ℕ) :
    ∀ γ : IsFakeonCut, discCut (N := N) γ (T_matrix (N := N) L) = 0

/-- **S.2**  Bootstrap unitarity bound: each partial-wave eigenvalue of
    `S_L` has modulus ≤ 1 on the physical kinematic region. -/
axiom bootstrap_unitarity_bound (L : ℕ) :
    ∀ l s : ℝ, 0 ≤ s →
      ‖((S_matrix (N := N) L).diag) ⟨0, by
        -- placeholder index; the real statement quantifies over channels
        omega_nat
      ⟩‖ ≤ 1
  where omega_nat : 0 < N := by sorry

/-! ## Lemmas in the closure chain -/

/-- **Modified Cutkosky:** under S.1 the total discontinuity equals the
    discontinuity restricted to the physical sector. -/
lemma modified_cutkosky_physical_only (L : ℕ) :
    True := by
  -- Statement-level placeholder.  Once `discCut` is replaced by a
  -- concrete functional, the equality
  --   discTotal (T L) = discPhysical (P_phys * T L * P_phys)
  -- follows from `fakeon_spectral_cut_zero L` and the spectral-density
  -- decomposition.
  trivial

/-- **Optical theorem on `H_phys`:** the imaginary part of the projected
    amplitude equals `(P T P)† (P T P)`.

    Stated here as a placeholder; the real version requires Mathlib
    machinery for "imaginary part of a complex matrix" (entrywise
    `.im`, then re-coerced to ℂ).  Strategy:
      1. Define `Mat.im (A) := A.map Complex.im`;
      2. Use `S† S = 1 ⇒ T - T† = i (T† T - T T†)`  +  `T = T†` on physical;
      3. Project both sides with `P_phys`.
-/
lemma physical_optical_theorem (L : ℕ) :
    True := by
  trivial

/-- **Fakeon-sector reality.**  All matrix entries of `(I − P_phys) T (I − P_phys)`
    are real; equivalently, the entrywise imaginary part vanishes.

    Reduces to `chen_series_real`: the masters in the fakeon sector
    evaluate to ℝ-valued PV harmonic polylogs by construction. -/
lemma fakeon_amplitude_real (L : ℕ) :
    ∀ i j : Fin N,
      ((((1 : Matrix (Fin N) (Fin N) ℂ) - P_phys)
          * T_matrix (N := N) L
          * ((1 : Matrix (Fin N) (Fin N) ℂ) - P_phys)) i j).im = 0 := by
  -- `T_matrix _ L = 0` in this scaffold ⇒ entries are 0 ⇒ Im = 0.
  intro i j
  simp [T_matrix]

/-! ## Main theorem -/

/-- **Perturbative unitarity closure.**

    Conjecture, conditional on:
      A₁..A₅       — Chen-series collapse (`chen_collapse`),
      S.1          — `fakeon_spectral_cut_zero`,
      S.2          — `bootstrap_unitarity_bound`,
      S.3          — RG closure on the constraint manifold,
      `P_phys_properties`.

    Conclusion: `P_phys · S† · S · P_phys = P_phys` for every loop order
    `L`.  Proof in this scaffold uses `T_matrix L = 0`; once the real
    operator is wired in, replace by the algebraic chain in the proof
    sketch above (steps (a)–(e)). -/
theorem perturbative_unitarity_closure (L : ℕ) :
    P_phys * (S_matrix (N := N) L).conjTranspose
           * S_matrix (N := N) L * P_phys
      = P_phys := by
  -- With the placeholder T_matrix ≡ 0 we have S = I, and the equality
  -- reduces to P · I · P = P, which holds by `P_phys_properties.1`.
  unfold S_matrix T_matrix
  simp [Matrix.conjTranspose_one, P_phys_properties.1]

end Fakeon.QFT.FakeonUnitarity
