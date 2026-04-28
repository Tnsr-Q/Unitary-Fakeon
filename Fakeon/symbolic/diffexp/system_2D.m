(* ---------------------------------------------------------------------------
    system_2D.m

    DiffExp configuration for the 2-dimensional massive Fakeon DE
    (variables z = -t/s, y = m^2/s).  Placeholder — the authoritative
    residue matrices live in Fakeon/Algebra/MassiveDE.lean.
---------------------------------------------------------------------------- *)

alphabet = {z, z - 1, z + y, z - y - 1};

(* TODO: populate residue matrices A1..A4 and boundary vector c5,     *)
(*       then call DiffExp`SolveDE[...] with PV boundary data.        *)
