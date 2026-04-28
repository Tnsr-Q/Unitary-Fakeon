# Lean Proof-Patch Review — 2026-04-29

_Referee-grade review of user-proposed discharges for the four open
`sorry`s in the Lean stack.  No Lean toolchain is installed in this
container (handoff: `lake build: deferred`), so "Compile Status: OK"
claims are unverified; the review is therefore restricted to static
analysis (Mathlib4 lemma-name correctness, Lean 4 syntax / type
checking by inspection, and mathematical soundness)._

## Summary

| # | Target `sorry` | Verdict | Outcome |
|---|----------------|---------|---------|
| 1 | `Distributions.causalProp_im` | **Plausible, unverified** | Park — re-try when `lake build` is wired |
| 2 | `Distributions.imaginary_limit_delta` | **Reject** | Type error + fabricated Mathlib names |
| 3 | `FakeonUnitarity.bootstrap_unitarity_bound` | **Reject as proposed** | Wrong object (per-channel vs. matrix-level); real proof already in-file as `loss_zero_implies_unitarity` |
| 4 | `InelasticBootstrap.optical_inequality_from_bound` | **Reject** | Sign error in `‖S‖²` expansion, coefficient error in the claimed identity, adds two axioms, re-introduces a statement rejected in Pass 11 |

All four Lean files left **unchanged** pending a Lean-equipped environment.

---

## Patch 1 — `causalProp_im`

**Current scaffold (`Fakeon/Analysis/Distributions.lean:44–51`)**:

```lean
lemma causalProp_im (η x : ℝ) :
    (causalProp η x).im = -η / (x ^ 2 + η ^ 2) := by
  unfold causalProp
  sorry
```

**Proposed tactic**:

```lean
simp [causalProp, Complex.div_im, Complex.ofReal_re, Complex.ofReal_im]
<;> ring_nf
<;> field_simp [add_comm, add_left_comm, add_assoc]
```

### Static analysis
- The algebra is right: with `a = 1 = ⟨1,0⟩` and `b = x + iη = ⟨x, η⟩`, `Complex.div_im` gives `(0·x − 1·η)/(x² + η²) = −η/(x² + η²)`. ✓
- `<;>` after `simp` is dead code if `simp` already closes the goal; harmless either way.
- `field_simp` without a non-zero hypothesis `x² + η² ≠ 0` is the weak point. In Mathlib 4, `field_simp` typically discharges positivity side-conditions via `positivity`, but only after the goal is already in `a/b = c/d` form. If `ring_nf` leaves the goal in mixed additive form, `field_simp` will either do nothing or fail.
- A safer discharge is:
  ```lean
  simp only [causalProp, Complex.div_im, Complex.one_im, Complex.one_re,
             Complex.add_re, Complex.add_im, Complex.mul_re, Complex.mul_im,
             Complex.I_re, Complex.I_im, Complex.ofReal_re, Complex.ofReal_im,
             Complex.normSq_apply]
  ring
  ```
  which does not depend on `field_simp` at all.

### Action
Park. When `lake build` is wired we attempt **both** forms (user's + the `simp only; ring` variant above) and keep whichever closes.  Leave the `sorry` in place for now.

---

## Patch 2 — `imaginary_limit_delta`

**Current scaffold (`Fakeon/Analysis/Distributions.lean:68–74`)**:

```lean
theorem imaginary_limit_delta
    (f : ℝ → ℂ) (_hf_cont : Continuous f) (_hf_comp : HasCompactSupport f) :
    Tendsto
      (fun η : ℝ => ∫ x, f x * ((causalProp η x).im : ℂ))
      (𝓝[>] 0)
      (𝓝 (-(π : ℂ) * f 0)) := by
  sorry
```

### Hard defects in the proposed patch

1. **Type error in the statement copied at the top of the patch**:
   ```lean
   … Tendsto (fun η => …) (𝓝[>] 0) (-π * f 0)
   ```
   The third argument of `Tendsto` must be a `Filter`; this is a bare `ℂ`. The file's actual signature wraps it in `𝓝 (…)`. The patch would not type-check before a single tactic runs.

2. **Fabricated / misnamed Mathlib lemmas**:
   - `MeasureTheory.integrable_one_div_add_sq` — no such lemma in Mathlib4. The closest real one is `MeasureTheory.Integrable` on `fun t => (1 + t^2)⁻¹` via `integrable_one_div_one_add_sq`, and even that name isn't quite stable across versions.
   - `integral_one_div_add_sq` — not a Mathlib4 name; the canonical result `∫ 1/(1+t²) dt = π` is proven via `integral_one_div_one_add_sq` (over ℝ) together with `Real.arctan_neg_one_half_pi` / `Real.arctan_one_half_pi`.
   - `le_norm_sup` — not a Mathlib name. For `BoundedContinuousFunction` one uses `BoundedContinuousFunction.norm_coe_le_norm`; for generic `ℝ → ℂ` with compact support, the sup-norm has to be built via `Continuous.bddAbove_image` + `IsCompact.image` + `Set.iSup_le`.
   - `measurable_cont_comp measurable_id` — not a Mathlib name.
   - `MeasureTheory.tendsto_integral_of_dominated_convergence` — the real name is `MeasureTheory.tendsto_integral_filter_of_dominated_convergence` (and it takes a sequence-style bound, not a per-`η` bound; the version here would need `MeasureTheory.tendsto_integral_of_dominated_convergence` which *does* exist but with a **different signature** expecting a countable filter basis).

3. **`‖f‖∞` is not available** for a raw `f : ℝ → ℂ`. One must either promote `f` to `BoundedContinuousFunction ℝ ℂ` (possible because it is continuous + compactly supported ⇒ bounded) or introduce an explicit `M := ⨆ x, ‖f x‖` and prove `∃ M, ∀ x, ‖f x‖ ≤ M` from `Continuous.bddAbove_range_of_hasCompactSupport`.

4. **`this.const_smul ‖f‖∞`** on an integrability fact `Integrable (fun t => 1/(t²+1))` produces `Integrable (fun t => ‖f‖∞ • (1/(t²+1)))` — with `•`, not `*`, and the subsequent `‖f‖∞ / (t²+1)` in the dominator doesn't match.

5. **`hf_cont.tendsto 0 (by simp)`** — `Continuous.tendsto` takes one argument, not two.

6. **`tendsto_mul_const`** — in Mathlib4 the name is `Tendsto.mul_const`; the composition target used in the patch is backwards.

### Action
Reject. The full Sokhotski–Plemelj proof is a substantive 40+ line DCT argument; it will stay as `sorry` until we have a Lean environment, and we will use Mathlib's actual `integral_one_div_one_add_sq` + `Continuous.bddAbove_range_of_hasCompactSupport` + `MeasureTheory.tendsto_integral_filter_of_dominated_convergence` rather than invented names.

---

## Patch 3 — `bootstrap_unitarity_bound`

**Current state (`Fakeon/QFT/FakeonUnitarity.lean:83–89`)**: declared as an **axiom** over the matrix-level `S_matrix.diag`, with one internal `sorry` in the `where omega_nat : 0 < N := by sorry` index-bound placeholder (not in the conclusion).

### Defects

1. **Wrong target**. The patch proves a statement about a per-channel abstract function `S_partial : ℕ → ℝ → ℂ`, indexed by `(l, s)` over `Finset.product grid_l grid_s`. This is **not** the matrix-level statement declared in `FakeonUnitarity.lean`. Substituting it would require a refactor of the downstream closure chain (steps (a)–(e) in the file preamble) which currently consumes the matrix-diag form.

2. **The per-channel theorem already exists in-tree**, in the right file, correctly proven:
   ```
   Fakeon/QFT/InelasticBootstrap.lean:97–137
     lemma loss_zero_implies_unitarity
       (grid_l) (grid_s) (S) (hloss : total_loss … = 0) :
       ∀ l ∈ grid_l, ∀ s ∈ grid_s, ‖S l s‖ ≤ 1
   ```
   Its last step uses `nlinarith [sq_nonneg (‖S l s‖ - 1), sq_nonneg (‖S l s‖ + 1)]`, which is exactly the idiomatic Mathlib closure for `x² ≤ 1 ∧ 0 ≤ x ⇒ x ≤ 1`. The patch's `le_of_sub_nonpos (by linarith)` **does not** bridge `‖S‖² ≤ 1` to `‖S‖ ≤ 1` — it only bridges `a − b ≤ 0 → a ≤ b`.

3. **Name drift**:
   - `simp [pow_eq_zero, max_eq_zero]` — correct Mathlib names are `pow_eq_zero_iff` and `max_eq_zero_iff` (plus a `0 ≤ a` side condition).
   - `Finset.single_le_sum h_nonneg ⟨hl, hs⟩` — `Finset.single_le_sum` takes `(h : ∀ i ∈ s, 0 ≤ f i) (hi : i ∈ s)` where `i` is the *element*, not a pair. For membership in a `Finset.product` one needs `Finset.mem_product.mpr ⟨hl, hs⟩`.

### Action
Reject the patch as a replacement for the FakeonUnitarity axiom. The right move is:
- Leave the FakeonUnitarity axiom *as-is* (it models a matrix-level theorem, which requires the spectral theorem to lift the per-channel result — a downstream task).
- The in-file `loss_zero_implies_unitarity` already achieves the per-channel content the patch was aiming for.

---

## Patch 4 — `optical_inequality_from_bound`

**Current state (`Fakeon/QFT/InelasticBootstrap.lean:151–164`)**:

```lean
lemma optical_inequality_from_bound
    (Sl Tl : ℂ) (hS : Sl = 1 + 2 * Complex.I * Tl) (hbnd : ‖Sl‖ ≤ 1) :
    Tl.im ≥ ‖Tl‖ ^ 2 := by
  have hSq : ‖Sl‖ ^ 2 = 1 - 4 * Tl.im + 4 * ‖Tl‖ ^ 2 := by
    sorry       -- ← the ONE remaining sorry, a single algebraic identity
  have h1 : ‖Sl‖ ^ 2 ≤ 1 := …
  linarith [hSq]
```

The only open content is the single line `hSq`, a routine algebraic identity over ℂ.

### Defects in the proposed patch

1. **Mathematical error in `h_S_norm`** — claims
   ```
   ‖S_partial l s‖^2 = 1 + 4 (T).im + 4 ‖T‖²
   ```
   The correct identity (as the file's own comment at line 154 records) is
   ```
   ‖1 + 2iT‖² = (1 + 2iT)(1 − 2iT̄)
              = 1 − 2iT̄ + 2iT + 4 TT̄
              = 1 + 2i(T − T̄) + 4|T|²
              = 1 − 4 Im T + 4 |T|².
   ```
   The patch's sign on `Im T` is wrong (+ instead of −).

2. **Coefficient error in the stated identity**. From the correct `‖S‖² = 1 − 4 Im T + 4 ‖T‖²` and `‖S‖² = η²`:
   ```
   η² = 1 − 4 Im T + 4 ‖T‖²
   ⇒ 4 Im T = 1 − η² + 4 ‖T‖²
   ⇒ 2 Im T = (1 − η²)/2 + 2 ‖T‖².
   ```
   The patch's theorem states `2 Im T = ‖T‖² + (1 − η²)/2`, which is missing the factor of 2 on ‖T‖². Off by a factor of 2 in the leading term.

3. **Adds two new axioms** (`partial_wave_normalization`, `inelasticity_match`), both of which are *already available as hypotheses* in the existing signature (`hS : Sl = 1 + 2 * Complex.I * Tl` and the `hbnd` coming from the discretised bootstrap).  This strictly increases the open-axiom count — the opposite of the roadmap direction.

4. **Re-introduces the identity rejected in Pass 11.** The Pass-11 PRD entry explicitly records:

   > Honest correction of user spec: replaced the user-supplied (and provably false) `2 Im T ≥ ‖T‖² + (1 − η²)` with the standard `Im T ≥ ‖T‖²` from the partial-wave parametrisation `S = 1 + 2iT`.

   The patch here re-proposes exactly that shape.

### Correct minimal discharge for the one open line

The only open `sorry` in this theorem is the single-line algebraic identity. The idiomatic Mathlib closure is:

```lean
have hSq : ‖Sl‖ ^ 2 = 1 - 4 * Tl.im + 4 * ‖Tl‖ ^ 2 := by
  subst hS
  rw [sq, Complex.norm_eq_abs, ← Complex.normSq_eq_abs,
      Complex.normSq_apply]
  simp [Complex.mul_re, Complex.mul_im, Complex.I_re, Complex.I_im,
        Complex.ofReal_re, Complex.ofReal_im]
  ring
```

This is a ~6-line, axiom-free, Mathlib-name-accurate candidate.  It is **still unverified** in this container (no `lake`) but is at least syntactically plausible and algebraically correct.

### Action
Reject patch 4 as proposed. When Lean is wired we try the 6-line candidate above; if it doesn't close, iterate.

---

## What lands from this pass

- **No changes to any Lean file.**
- This review document, committed under `docs/LEAN_PROOF_REVIEW_2026-04-29.md`, so the analysis survives and can be re-used when `lake build` is activated.
- The four open `sorry`s remain exactly as before. `audit_status.py` / `anchor_status.py` will continue to track them honestly.

## Re-activation plan (when Lean lands)

1. Stand up `leanprover/lean-action@v1` + `lake exe cache get` (already in `quft-verify.yml` under `workflow_dispatch`).
2. Attempt **Patch 1**'s `simp only [Complex.div_im, …]; ring` variant; if that closes, remove the `sorry`.
3. Attempt the 6-line candidate for `optical_inequality_from_bound`'s internal `hSq`; if it closes, the whole theorem goes green (the rest of the proof is already content-bearing).
4. Sokhotski–Plemelj (`imaginary_limit_delta`) stays `sorry` until `PrincipalValue.lean` is introduced (it's the proper home for the change-of-variables lemma).
5. The matrix-level `bootstrap_unitarity_bound` remains an axiom until the spectral-theorem lift from `loss_zero_implies_unitarity` is formalised in a new `FakeonUnitarity.Spectral` module.
