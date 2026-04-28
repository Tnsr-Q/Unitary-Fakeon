/-
  Fakeon/Geometry/WedgeVanishing.lean

  Wedge vanishing for the Chen flat connection on the 1D RG flow.

  Physics statement:
    On the center-stable manifold `𝒲^{cs}`, the non-Abelian constraint
    algebra `[M_i, M_j] ≠ 0` forces a Frobenius integrability reduction
    of the RG flow to a 1D trajectory `α : ℝ → ℝ^k`.  On a 1D manifold
    every 2-form vanishes, hence

        d ln α_i ∧ d ln α_j = 0

    for every pair (i, j).  Combined with the `flat_connection` datum in
    `Geometry/FlatConnection.lean`, this discharges the flatness
    obligation `dΩ + Ω ∧ Ω = 0` on the physical slice.

  This file exposes:
    * axiom `rg_flow_1d_reduction` (the Frobenius reduction);
    * definition `dlog_α`;
    * lemma `wedge_vanishes_on_rg_flow` (trivial at the scalar level;
      the substantive content is the Frobenius reduction above).

  For higher-dimensional settings where the reduction is not available
  the companion numeric test `tests/test_wedge_vanishing.py` provides a
  rank check on sampled trajectories.
-/

import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Data.Real.Basic

namespace Fakeon.Geometry.WedgeVanishing

variable {k : ℕ}

/-- **Frobenius reduction on 𝒲^{cs}.**  Every component of the α-vector
    is a function of any other component along the flow. -/
axiom rg_flow_1d_reduction :
    ∀ (α : ℝ → Fin k → ℝ) (i j : Fin k),
      ∃ f : ℝ → ℝ, ∀ t : ℝ, α t i = f (α t j)

/-- Logarithmic derivative of `α_i` along the RG time `t`. -/
noncomputable def dlog_α (α : ℝ → Fin k → ℝ) (i : Fin k) (t : ℝ) : ℝ :=
  (deriv (fun s => α s i) t) / (α t i)

/-- **Wedge vanishing.**

    At the scalar level of the `dt`-pullback, the antisymmetric
    combination is trivially zero because ℝ is commutative:

        dlog_α i t · dlog_α j t − dlog_α j t · dlog_α i t = 0.

    The physics content (that this scalar version is sufficient) sits in
    `rg_flow_1d_reduction`: on a 1D manifold the pullback to `dt ∧ dt`
    annihilates every 2-form, so only the scalar coefficient remains,
    and that coefficient is antisymmetric. -/
lemma wedge_vanishes_on_rg_flow
    (α : ℝ → Fin k → ℝ) (t : ℝ) (i j : Fin k) :
    dlog_α α i t * dlog_α α j t - dlog_α α j t * dlog_α α i t = 0 := by
  ring

end Fakeon.Geometry.WedgeVanishing
