import Lake
open Lake DSL

package «Fakeon» where
  -- Lean options for the package as a whole.
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩,
    ⟨`autoImplicit, false⟩
  ]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "master"

@[default_target]
lean_lib «Fakeon» where
  -- Source root is the inner `Fakeon/` directory.
  srcDir := "."
  roots := #[`Fakeon.FakeonQFT]
