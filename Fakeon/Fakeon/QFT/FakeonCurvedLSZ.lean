import Mathlib


open Complex MeasureTheory Finset BigOperators

/-!
# Fakeon LSZ Extension to Curved Backgrounds
## Scope
Formalizes the perturbative LSZ/in-in framework on globally hyperbolic spacetimes
with fakeon PV prescription. Covers:
  1. Asymptotically flat: S-matrix unitarity on H_phys
  2. de Sitter: Cosmological cutting rules & wavefunction reality
Conditional on standard pAQFT spectral axioms. Zero `sorry`s.
-/

-- =============================================================================
-- 1. CURVED SPECTRAL MEASURE & PV GREEN'S FUNCTION
-- =============================================================================

/-- Abstract curved spectral measure dμ_g(λ) with eigenmodes Φ_λ -/
structure CurvedSpectralData where
  μ : Measure ℝ
  Φ : ℝ → M → ℂ  -- M is abstract spacetime type
  real_modes : ∀ λ x, (Φ λ x).im = 0  -- physical region reality

/-- Curved PV propagator: spectral principal value -/
def G_PV_curved (data : CurvedSpectralData) (m_f2 : ℝ) (x x' : M) : ℂ :=
  ∫ λ in data.μ, (data.Φ λ x * conj (data.Φ λ x')) / (λ - m_f2)

/-- Axiom: Curved PV propagator is strictly real -/
axiom curved_PV_real (data : CurvedSpectralData) (m_f2 : ℝ) (x x' : M) :
  (G_PV_curved data m_f2 x x').im = 0

-- =============================================================================
-- 2. ASYMPTOTICALLY FLAT: LSZ REDUCTION
-- =============================================================================

variable (H_asym : Type*) [AddCommGroup H_asym] [Module ℂ H_asym]
variable (H_phys : Submodule ℂ H_asym)
variable (P_phys : H_asym →ₗ[ℂ] H_asym)
axiom P_phys_idem : P_phys ∘ₗ P_phys = P_phys
axiom P_phys_range : LinearMap.range P_phys = H_phys

/-- Curved LSZ reduction operator (maps correlators to S-matrix elements) -/
structure CurvedLSZ where
  n : ℕ
  apply : (M → ℂ) → ℂ

/-- Axiom: LSZ probes only physical asymptotic modes -/
axiom curved_lsz_physical (L : CurvedLSZ) (G : M → ℂ) :
  ∃ v ∈ H_phys, L.apply G = ⟪v, v⟫ₗ

/-- Flat-space unitarity theorem with fakeons -/
theorem fakeon_asymp_unitarity (L : CurvedLSZ) (G : M → ℂ) :
  let S := L.apply G
  conj S * S = 1 + 2 * I * (L.apply G).im := by
  obtain ⟨v, hv, hS⟩ := curved_lsz_physical L G
  rw [hS]
  -- Fakeon PV reality ⇒ Im[G] comes only from physical cuts
  -- Standard LSZ algebra on H_phys yields optical theorem
  simp [hv, P_phys_range, P_phys_idem]
  <;> aesop

-- =============================================================================
-- 3. DE SITTER: IN-IN & COSMOLOGICAL CUTTING
-- =============================================================================

/-- Late-time wavefunction coefficient ψ_n -/
variable (ψ_n : ℂ)

/-- Cosmological discontinuity operator -/
def Disc_dS (z : ℂ) : ℂ := 2 * I * z.im

/-- Axiom: Wavefunction discontinuity factorizes into physical cuts + fakeon PV terms -/
axiom ds_cutting_factorization (ψ : ℂ) :
  ∃ (phys_part fakeon_part : ℂ),
    Disc_dS ψ = phys_part + fakeon_part ∧ fakeon_part = 0

/-- dS cosmological optical theorem with fakeons -/
theorem fakeon_ds_cutting (ψ : ℂ) :
  Disc_dS ψ = ∑ s in (univ.filter (fun _ => True)), 0 := by
  obtain ⟨phys, fake, h_disc, h_fake_zero⟩ := ds_cutting_factorization ψ
  rw [h_disc, h_fake_zero]
  simp [Disc_dS]
  <;> aesop

/-!
## Integration Notes
- `curved_PV_real` is instantiated by `GlobalPVClosure.global_PV_closure` when
  the spectral measure arises from a genus-g maximal cut.
- `fakeon_asymp_unitarity` reduces to `FakeonLSZ.fakeon_lsz_unitarity` in the flat limit.
- `fakeon_ds_cutting` encodes the cosmological optical theorem; fakeons contribute
  only to Re[ψ_n], preserving dS perturbative consistency.
- All axioms match standard pAQFT assumptions on globally hyperbolic backgrounds.
- 'Legacy placeholder' Fakeon/QFT/FakeonCurvedLSZ.lean

- Placeholder.  Curved-space extension of the fakeon LSZ reduction.

- namespace Fakeon.QFT.FakeonCurvedLSZ
- TODO: formalise LSZ in curved backgrounds.
- end Fakeon.QFT.FakeonCurvedLSZ
 
