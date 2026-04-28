# Referee Review — Proposed A5 / A6 + Weight-7 Activation Plan
_Date: 2026-04-29.  Reviewer: full-stack agent.  Verdict: **REJECT for
merge as proposed**.  No code changes were made to `MassiveDE.lean`,
`test_massive_flatness.py`, or `extract_cvec.py`._

## TL;DR

| Item | Verdict | Why |
|------|---------|-----|
| Proposed A₅, A₆ matrices | **Reject** | 2D flatness fails on 5 of 15 letter-pairs (mechanical counter-example below). |
| 2D HyperInt Maple block | Reject as-written | Mixes Maple and Mathematica syntax (`:>` rule arrow is Mathematica); `c₄` declared as zeros, so the cubic Chen term `M³c₄` is trivially zero and the test never bites; `evalc(Re(...)) assuming z>0, y>0` is not valid Maple syntax. |
| Python `chen_weight7` | Reject as-written | With `c₄` = 0 the cubic term is identically zero, so the residual check is vacuous; `np.load(f"artifacts/A{i+1}.npy")` is hardcoded against artefacts the user does not supply. |
| Lean `massive_2d_flatness` | Reject as-written | Body is `sorry -- Trivial with matrix_decide`; with the proposed matrices the lemma is provably **false** (see commutators below).  Also: the disjunction's wedge predicate `(i < 4 ∧ j < 4 → wedge_vanishes …)` is wrong-direction — the (1,3), (1,4), (2,3), (2,4), (3,4) wedges are *non-zero*, so the condition under `i, j < 4` is empirically false. |
| CI hook in `quft-verify.yml` | Reject as-written | `cp artifacts/A5.npy artifacts/A6.npy Fakeon/Geometry/` deposits numpy files into a Lean directory and calls them "compiled into Lean".  Lean does not load `.npy`. |

## The flatness counter-example

The integrability condition `dΩ + Ω∧Ω = 0` for the canonical 2D
connection `Ω = Σ Aᵢ d ln αᵢ` reduces, on every letter-pair, to

    [Aᵢ, Aⱼ] = 0     OR     d ln αᵢ ∧ d ln αⱼ = 0.

With the user-proposed

```text
A1 = [[ 0,  0,  0,  0,  0,  0],     A5 = [[ 0,  0,  0,  0,  0,  0],
      [ 0, -2,  0,  0,  0,  0],           [ 0, -1,  0,  0,  0,  0],
      [ 0,  0, -2,  0,  0,  0],           [ 0,  0, -1,  0,  0,  0],
      [ 0,  0,  0, -2,  0,  0],           [ 0,  0,  0,  0,  0,  0],
      [ 0,  1,  1,  0, -1,  0],           [ 0,  0,  0,  0,  0,  0],
      [ 0,  0,  0,  0,  0, -2]]           [ 0,  1,  1,  0,  0, -1]]
```

direct sympy computation gives

    [A1, A5] = [[0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0,-1,-1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0]]

with row-4 entries `(-1, -1)` at columns 1 and 2.  The wedge

    d ln α₁ ∧ d ln α₅ = d ln z ∧ d ln y = (1 / (y z)) dz ∧ dy

is non-zero on the physical slice `(z, y) ∈ ℝ²₊`, so the (A₁, A₅)
disjunction is satisfied by neither branch.  **2D flatness fails.**

The full automated scan returns **5 violations / 15 letter pairs**:

| Pair | wedge | [Aᵢ, Aⱼ] non-zero entries |
|------|-------|---------------------------|
| (A1, A5) | `1/(y z)` | row 4: cols 1, 2 → `-1, -1` |
| (A2, A5) | `1/(y (z-1))` | rows 1, 2: col 0 → `2, 2`; row 4: cols 1, 2 → `-2, -2`; row 5: col 0 → `-4` |
| (A2, A6) | `1/((y+1)(z-1))` | row 4: col 3 → `-4` |
| (A4, A5) | `-1/(y(y-z+1))` | row 5: col 3 → `2` |
| (A4, A6) | `-1/((y+1)(y-z+1))` | row 5: col 3 → `-2` |

Reproduce locally:

```bash
cd /app/Fakeon
python - <<'PY'
import numpy as np, sympy as sp
A1 = np.array([[0,0,0,0,0,0],[0,-2,0,0,0,0],[0,0,-2,0,0,0],[0,0,0,-2,0,0],[0,1,1,0,-1,0],[0,0,0,0,0,-2]],dtype=int)
A5 = np.array([[0,0,0,0,0,0],[0,-1,0,0,0,0],[0,0,-1,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,1,1,0,0,-1]],dtype=int)
M1, M5 = sp.Matrix(A1), sp.Matrix(A5)
print(M1*M5 - M5*M1)
PY
```

## What it would take to do this right

1. **Derive A₅, A₆ from the y-evolution of the canonical DE.**  The
   y-direction is *not* a free choice; the residue at `αᵢ = y, y+1`
   is fixed by demanding that the canonical basis remains canonical
   under y-evolution.  Specifically: differentiate the UT basis with
   respect to y, IBP-reduce against the master integrals, and read
   off the residues.  HyperInt or Kira can produce this directly.
   The output should pass the sympy flatness check above with **0**
   violations.

2. **Re-run `tests/test_massive_flatness.py::test_flatness_pairwise`**
   with the new matrices.  Today it parametrises over 15 pairs and
   passes only because A₅ = A₆ = 0 (every commutator is trivially
   zero against the zero stub).  Once non-trivial A₅, A₆ are wired
   in, the test will tell you immediately whether they satisfy the
   flatness disjunction.

3. **Run HyperInt at the (z₀, y₀) = (1/2, 1/3) base point** with the
   *correct* 6-letter alphabet to extract the boundary vectors at
   weights 4, 5, 6, 7 — *all four*, not just c₅ and c₇ with c₄ and
   c₆ as placeholders.  The Chen recursion only closes when **all
   of c₄, c₅, c₆, c₇** are physical.

4. **Drop the `< 1e-10` tolerance**; with HyperInt evaluating
   ζ-values at quad precision, residuals at the matrix-product level
   sit at 1e-14.  But require monotone improvement under η-grid
   refinement so the test catches reduction-system mistakes.

5. **The `.npy` artefacts cannot live in `Fakeon/Geometry/`** — that
   directory is a Lean library root.  Numerical artefacts belong
   under `artifacts/` or `fakeon_numeric/`, with the loader
   (`fakeon_numeric/boundary_vectors.py`) reading them.

## What landed from this review

- **No changes to source.**  `MassiveDE.lean`, `FlatConnection.lean`,
  `test_massive_flatness.py`, and `extract_cvec.py` are untouched.
- This document, recording the counter-example so the next attempt
  starts from a verified failing test rather than an unverified
  claim of completeness.

## Re-activation plan

1. Produce A₅, A₆ via y-evolution of the canonical basis.
2. Run the 5-line sympy flatness scanner above; require 0/15 violations.
3. Append the verified A₅, A₆ to `_A5_num` / `_A6_num` in
   `tests/test_massive_flatness.py` (replacing the zero stubs).
4. Run HyperInt at (1/2, 1/3) with the full 6-letter alphabet to
   produce a real `c_vectors.json` covering weights 4..7.
5. The existing `test_chen_coefficients_weight7` (currently
   skipped pending `c_vectors.json`) will activate automatically.
