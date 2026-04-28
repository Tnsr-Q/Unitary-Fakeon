"""scripts/extract_cvec.py — extract boundary vectors c4..c7 from a
HyperInt/DiffExp master dump.

Parses a Mathematica-formatted ``Master[i] = a + b*eps + c*eps^2 + ...``
file produced by ``symbolic/hyperint/crossedbox_massive_PV.maple`` (or
the DiffExp twin) evaluated at the PV base point (z0, y0) = (1/2, 1/3),
extracts the ε^n coefficient for n ∈ {4, 5, 6, 7}, and writes
``fakeon_numeric/c_vectors.json`` — the single source of truth consumed
by :mod:`fakeon_numeric.boundary_vectors`.

Usage
-----
    python scripts/extract_cvec.py --input PV_CrossedBox_Masters.m
    python scripts/extract_cvec.py --input artifacts/masters.m \
        --out fakeon_numeric/c_vectors.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
from mpmath import mp, pi, zeta

mp.dps = 40

_DEFAULT_OUT = Path(__file__).resolve().parent.parent / "fakeon_numeric" / "c_vectors.json"


def _mma_to_python(expr: str) -> str:
    """Translate a Mathematica scalar expression into a Python expression
    using ``mp.pi`` and ``zeta``.

    Handles:
      * ``Pi``, ``Pi^n`` → ``mp.pi``, ``mp.pi**n``
      * ``Zeta[n]``      → ``zeta(n)``
      * ``^``            → ``**``
      * whitespace
    """
    s = expr.strip()
    s = s.replace(" ", "")
    # Zeta[n] → zeta(n)
    s = re.sub(r"Zeta\[(\d+)\]", r"zeta(\1)", s)
    # Pi^n → mp.pi**n  (do before bare Pi)
    s = re.sub(r"Pi\^(\d+)", r"(mp.pi**\1)", s)
    s = s.replace("Pi", "mp.pi")
    # Mathematica ^ → Python **
    s = s.replace("^", "**")
    return s


def _safe_eval(expr: str) -> float:
    """Evaluate a Mathematica scalar expression as a real float.

    Uses mpmath ``pi`` and ``zeta`` in a restricted namespace.  Falls
    back to 0.0 on any parse error (logged to stderr).
    """
    py = _mma_to_python(expr)
    try:
        val = eval(py, {"__builtins__": {}}, {"mp": mp, "zeta": zeta, "pi": pi})
        return float(val)
    except Exception as exc:  # pragma: no cover - best-effort parser
        print(f"[extract_cvec] parse fail '{expr[:60]}...' → {exc}", file=sys.stderr)
        return 0.0


_MASTER_SPLIT = re.compile(r"Master\s*\[\s*(\d+)\s*\]\s*=\s*", re.IGNORECASE)
_EPS_TERM = re.compile(
    r"""
    (?P<coeff> [^,;+\-]*? )   # coefficient chunk (non-greedy)
    \*?\s*eps\s*\^\s*(?P<n>\d+)
    """,
    re.VERBOSE,
)


def _split_masters(text: str) -> List[str]:
    """Split a dump into per-master blocks keyed by index (1-based)."""
    parts = _MASTER_SPLIT.split(text)
    # parts = [preamble, idx1, body1, idx2, body2, ...]
    blocks: Dict[int, str] = {}
    for i in range(1, len(parts) - 1, 2):
        idx = int(parts[i])
        blocks[idx] = parts[i + 1]
    if not blocks:
        return []
    return [blocks.get(i, "") for i in range(1, max(blocks) + 1)]


def _extract_eps_coeff(block: str, n: int) -> float:
    """Pull the coefficient of ε^n from a master block.

    We look for either ``<coeff>*eps^n`` or ``eps^n`` with an explicit
    leading sign; the matched coefficient chunk is handed to
    :func:`_safe_eval`.
    """
    # Normalise exponent notation
    b = block.replace("Epsilon", "eps").replace("EPS", "eps")
    # Patterns covering (a)*eps^n, a*eps^n, +eps^n, -eps^n
    patterns = [
        rf"\(([^()]*)\)\s*\*\s*eps\s*\^\s*{n}\b",
        rf"([+\-]?\s*[^+\-;,]*?)\s*\*\s*eps\s*\^\s*{n}\b",
        rf"([+\-])\s*eps\s*\^\s*{n}\b",
    ]
    for pat in patterns:
        m = re.search(pat, b)
        if m:
            coeff_str = m.group(1).strip()
            if coeff_str in ("+", ""):
                return 1.0
            if coeff_str == "-":
                return -1.0
            return _safe_eval(coeff_str)
    return 0.0


def parse_mathematica_dump(filepath: Path) -> Dict[str, np.ndarray]:
    """Return {"4": c4, "5": c5, "6": c6, "7": c7} from a Mathematica dump."""
    text = filepath.read_text()
    blocks = _split_masters(text)
    if not blocks:
        raise ValueError(
            f"{filepath} contains no `Master[i] = ...` entries."
        )

    coeffs: Dict[str, List[float]] = {str(n): [] for n in (4, 5, 6, 7)}
    for block in blocks[:6]:  # 6 masters
        for n in (4, 5, 6, 7):
            coeffs[str(n)].append(_extract_eps_coeff(block, n))

    # Pad to 6 entries if the dump was short.
    for n in coeffs:
        while len(coeffs[n]) < 6:
            coeffs[n].append(0.0)
        coeffs[n] = coeffs[n][:6]

    return {k: np.asarray(v, dtype=float) for k, v in coeffs.items()}


def save_vectors(coeffs: Dict[str, np.ndarray], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v.tolist() for k, v in coeffs.items()}
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"[extract_cvec] wrote {out_path}")
    for w in ("4", "5", "6", "7"):
        preview = ", ".join(f"{x:+.4e}" for x in coeffs[w][:3])
        print(f"    c{w} = [{preview}, ...]")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--input",
        required=True,
        help="Path to Mathematica .m master dump (HyperInt/DiffExp output).",
    )
    parser.add_argument(
        "--out",
        default=str(_DEFAULT_OUT),
        help=f"Output JSON path (default: {_DEFAULT_OUT}).",
    )
    parser.add_argument(
        "--format",
        choices=["mathematica"],
        default="mathematica",
        help="Input format (only `mathematica` is currently supported).",
    )
    args = parser.parse_args(argv)

    src = Path(args.input)
    if not src.exists():
        print(f"[extract_cvec] input not found: {src}", file=sys.stderr)
        return 2

    coeffs = parse_mathematica_dump(src)
    save_vectors(coeffs, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
