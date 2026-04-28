# SOURCE_MAP.md

Cross-reference between the physical objects, their Lean home, their
numeric home, and their symbolic home.

| Object                               | Lean                                   | Numeric                                           | Symbolic                                         |
|--------------------------------------|----------------------------------------|---------------------------------------------------|--------------------------------------------------|
| 6×6 residue matrices A1..A4          | `Algebra/MassiveDE.lean`               | `tests/test_massive_de_consistency.py`            | `symbolic/hyperint/crossedbox_massive_PV.maple`  |
| Alphabet {z, z-1, z+y, z-y-1}        | `Algebra/MassiveDE.lean`               | `tests/test_massive_de_consistency.py` (`alpha`)  | `symbolic/hyperint/crossedbox_massive_PV.maple`  |
| Boundary vector c5 (ζ₅ sector)       | `Algebra/MassiveDE.lean` (`c5`)        | —                                                 | loaded from Maple dump                           |
| PV projection rules                  | `Geometry/GlobalPVClosure.lean` (TBD)  | `fakeon_numeric/validation.py` (TBD)              | `symbolic/hyperint/crossedbox_massive_PV.maple`  |

Any change to the matrices or the alphabet must be propagated through
all three columns in the same commit.
