# Fakeon — Theoretical Context

This repository formalises a proof programme for the **massive fakeon**
two-loop crossed-box system with a Principal-Value (PV) prescription.

## The physical object

Fakeons are purely virtual degrees of freedom whose contribution to
amplitudes is defined by a PV projection that removes the absorptive part
at physical thresholds.  At two loops the crossed-box topology with one
massive internal line produces a 6-master canonical differential equation
in the variables `z = -t/s` and `y = m²/s`, with the alphabet

```
A = { z, z - 1, z + y, z - y - 1 }
```

## The verification programme

1. **Algebra** — Encode the 6×6 residue matrices and the ζ₅ boundary in
   Lean (`Fakeon/Algebra/MassiveDE.lean`) and prove Chen-series collapse.
2. **Geometry** — Prove that the PV contour is stable under
   Picard–Lefschetz monodromy and extends to hyperelliptic / Siegel
   covers.
3. **QFT** — Derive fakeon unitarity and LSZ (flat + curved) from the
   above algebraic/geometric foundations.
4. **Numerics** — Cross-validate the symbolic masters against direct
   numeric contour integration.

## Scope of the current pass

The first pass provides:

- The authoritative 6×6 matrices A1..A4 and boundary c5 in Lean.
- A structural + mock DE-consistency pytest suite.
- A ready-to-run HyperInt configuration with PV projection rules.
- Placeholders for every other file in the published tree so the
  directory layout is stable for subsequent expansions.
