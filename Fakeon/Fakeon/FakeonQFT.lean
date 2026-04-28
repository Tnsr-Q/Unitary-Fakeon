/-
  Fakeon/FakeonQFT.lean

  Top-level entry point.  Re-exports the algebra / analysis / geometry /
  QFT modules so that `import Fakeon.FakeonQFT` brings the whole stack
  into scope.
-/

import Fakeon.Algebra.MassiveDE
import Fakeon.Algebra.ChenCollapse
import Fakeon.Analysis.Distributions
import Fakeon.Analysis.DispersiveReality
import Fakeon.Geometry.FlatConnection
import Fakeon.Geometry.WedgeVanishing
import Fakeon.Geometry.PicardLefschetzPV
import Fakeon.Geometry.HyperellipticPV
import Fakeon.Geometry.GlobalPVClosure
import Fakeon.Geometry.GeneralGenusPV
import Fakeon.QFT.Assumptions
import Fakeon.QFT.FakeonUnitarity
import Fakeon.QFT.FakeonLSZ
import Fakeon.QFT.FakeonCurvedLSZ
import Fakeon.Experimental.SiegelThetaPV

namespace Fakeon
end Fakeon
