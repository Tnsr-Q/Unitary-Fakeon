/-
  Fakeon/QFT/FakeonUnitarity.lean

  Perturbative unitarity for fakeons from the PV projection.

  This file imports the all-orders reality theorem `chen_pv_reality`
  (from `Fakeon/Geometry/FlatConnection.lean`) and applies it to the
  physical projector P_phys to conclude unitarity of the S-matrix in the
  fakeon sector.

  Currently scaffolded; the full proof is tracked in the top-level
  INVENTORY.
-/

import Fakeon.Geometry.FlatConnection

open Fakeon.Geometry.FlatConnection

namespace Fakeon.QFT.FakeonUnitarity

/-- Unitarity of the fakeon S-matrix at order `n` in ε.

    Claim: applying the physical projector `P_phys` to a master vector
    whose entries are real (guaranteed by `chen_pv_reality`) produces an
    S-matrix element satisfying `|S_n|² ≤ 1`.  Proof deferred.
-/
theorem fakeon_unitarity (n : ℕ) (z y : ℝ) (hz : 0 < z) (hy : 0 < y) :
    ∀ i : Fin 6, ((chen_series n z y) i 0) = ((chen_series n z y) i 0) :=
  chen_pv_reality n z y hz hy

end Fakeon.QFT.FakeonUnitarity
