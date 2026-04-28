import Mathlib.Data.Finset.Basic
import Mathlib.Data.Real.Basic

namespace Fakeon

/-- Explicit physical pairing for finite-dimensional real coefficient vectors. -/
def physical_pairing {n : ℕ} (v w : Fin n → ℝ) : ℝ :=
  Finset.univ.sum fun i => v i * w i

/-- Weighted pairing for Fisher / Gauss-Newton style quadratic forms. -/
def weighted_pairing {n : ℕ} (W : Fin n → ℝ) (v w : Fin n → ℝ) : ℝ :=
  Finset.univ.sum fun i => W i * v i * w i

end Fakeon
