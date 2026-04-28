#!/usr/bin/env python3
"""
scripts/anchor_status.py

Reproducibility anchor for the Fakeon status matrix.

Builds a deterministic SHA-256 Merkle tree over the per-component audit
checksums in `logs/status_matrix.json`, emits a single Merkle root plus
the full manifest (every leaf, every intermediate hash, every level), and
provides O(log n) inclusion proofs so a reviewer can verify a specific
component's claim from the published root alone.

Output document
---------------
The anchor JSON has the shape:

    {
      "schema_version": 1,
      "generated_at": "<ISO-8601 UTC>",
      "input": "<path to status_matrix.json>",
      "input_sha256": "<hex>",
      "leaves": [
        {"component": "...", "leaf_hash": "<hex>", "row_digest": {...}},
        ...
      ],
      "levels": [["<hex>", ...], ...],   # bottom-up, level 0 == leaves
      "merkle_root": "<hex>",
      "n_components": 27
    }

Subcommands
-----------
* `build`  — read status_matrix.json, write anchor.json (default).
* `verify` — read both files, recompute, fail non-zero on mismatch.
* `proof`  — emit inclusion proof for a single component.

Determinism
-----------
* Components sorted by name (lexicographic, byte-level).
* Leaf hash:
      sha256(  component_name
            || 0x00 || status
            || 0x00 || sorted_deps_csv
            || 0x00 || audit_checksum  )
* Tree node:  sha256(left || right).  Last leaf is duplicated when the
  count is odd (Bitcoin-style padding).
* All bytes are UTF-8 encoded; no JSON re-serialisation in the digest
  path, so cross-platform reproduction needs only Python's `hashlib`.

The construction is intentionally vanilla so a reviewer with `sha256sum`
and 30 lines of any language can reproduce the root from the published
JSON inputs.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SEP = b"\x00"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utf8(*parts: str) -> bytes:
    return SEP.join(p.encode("utf-8") for p in parts)


def _row_digest(component: str, row: dict[str, Any]) -> dict[str, Any]:
    """Canonical digest of a single matrix row.  Stable under JSON ordering."""
    deps = sorted(row.get("dependencies", []))
    return {
        "component": component,
        "status": row.get("status", ""),
        "dependencies": deps,
        "audit_checksum": row.get("audit_checksum", ""),
    }


def _leaf_hash(component: str, row: dict[str, Any]) -> str:
    deps_csv = ",".join(sorted(row.get("dependencies", [])))
    return _sha256_hex(_utf8(
        component,
        str(row.get("status", "")),
        deps_csv,
        str(row.get("audit_checksum", "")),
    ))


def _merkle_levels(leaves: list[str]) -> list[list[str]]:
    """Build the tree bottom-up; level 0 is the leaf list."""
    if not leaves:
        return [[]]
    levels: list[list[str]] = [list(leaves)]
    cur = list(leaves)
    while len(cur) > 1:
        if len(cur) % 2 == 1:
            cur.append(cur[-1])  # duplicate-last padding
        nxt = []
        for i in range(0, len(cur), 2):
            left_b = bytes.fromhex(cur[i])
            right_b = bytes.fromhex(cur[i + 1])
            nxt.append(_sha256_hex(left_b + right_b))
        levels.append(nxt)
        cur = nxt
    return levels


def _merkle_proof(levels: list[list[str]], leaf_index: int) -> list[dict[str, str]]:
    """Sibling chain from the leaf up to the root."""
    proof: list[dict[str, str]] = []
    idx = leaf_index
    for level in levels[:-1]:  # skip the root level
        # Pad if needed (mirrors `_merkle_levels`).
        if len(level) % 2 == 1:
            level = level + [level[-1]]
        sibling_idx = idx + 1 if idx % 2 == 0 else idx - 1
        side = "right" if idx % 2 == 0 else "left"
        proof.append({"side": side, "hash": level[sibling_idx]})
        idx //= 2
    return proof


def _verify_proof(leaf: str, proof: list[dict[str, str]], root: str) -> bool:
    h = leaf
    for step in proof:
        sib = step["hash"]
        if step["side"] == "right":
            h = _sha256_hex(bytes.fromhex(h) + bytes.fromhex(sib))
        else:
            h = _sha256_hex(bytes.fromhex(sib) + bytes.fromhex(h))
    return h == root


# ---------------------------------------------------------------------------
# Anchor data class + builder.
# ---------------------------------------------------------------------------

@dataclass
class Anchor:
    schema_version: int = SCHEMA_VERSION
    generated_at: str = ""
    input: str = ""
    input_sha256: str = ""
    leaves: list[dict[str, Any]] = field(default_factory=list)
    levels: list[list[str]] = field(default_factory=list)
    merkle_root: str = ""
    n_components: int = 0


def build_anchor(matrix_path: Path) -> Anchor:
    raw = matrix_path.read_bytes()
    matrix = json.loads(raw)
    components = sorted(matrix.keys())

    leaves_meta: list[dict[str, Any]] = []
    leaves_hashes: list[str] = []
    for name in components:
        row = matrix[name]
        digest = _row_digest(name, row)
        leaf = _leaf_hash(name, row)
        leaves_meta.append({
            "component": name,
            "leaf_hash": leaf,
            "row_digest": digest,
        })
        leaves_hashes.append(leaf)

    levels = _merkle_levels(leaves_hashes)
    root = levels[-1][0] if leaves_hashes else _sha256_hex(b"")

    return Anchor(
        generated_at=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        input=str(matrix_path),
        input_sha256=_sha256_hex(raw),
        leaves=leaves_meta,
        levels=levels,
        merkle_root=root,
        n_components=len(components),
    )


def anchor_to_dict(a: Anchor) -> dict[str, Any]:
    return {
        "schema_version": a.schema_version,
        "generated_at": a.generated_at,
        "input": a.input,
        "input_sha256": a.input_sha256,
        "leaves": a.leaves,
        "levels": a.levels,
        "merkle_root": a.merkle_root,
        "n_components": a.n_components,
    }


# ---------------------------------------------------------------------------
# Verify / proof commands.
# ---------------------------------------------------------------------------

def cmd_build(args: argparse.Namespace) -> int:
    a = build_anchor(Path(args.input))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(anchor_to_dict(a), indent=2), encoding="utf-8")
    print(f"wrote {out}")
    print(f"merkle_root = {a.merkle_root}")
    print(f"n_components = {a.n_components}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    anchor = json.loads(Path(args.anchor).read_text(encoding="utf-8"))
    matrix_path = Path(args.input or anchor["input"])
    fresh = build_anchor(matrix_path)

    fresh_root = fresh.merkle_root
    expected_root = anchor["merkle_root"]
    fresh_hash = fresh.input_sha256
    expected_hash = anchor["input_sha256"]

    print(f"input          : {matrix_path}")
    print(f"input_sha256   : expected {expected_hash}")
    print(f"                 actual   {fresh_hash}")
    print(f"merkle_root    : expected {expected_root}")
    print(f"                 actual   {fresh_root}")

    ok = (fresh_root == expected_root) and (fresh_hash == expected_hash)
    if not ok:
        print("ANCHOR VERIFICATION FAILED", file=sys.stderr)
        return 1
    print("ANCHOR VERIFIED")
    return 0


def cmd_proof(args: argparse.Namespace) -> int:
    a = build_anchor(Path(args.input))
    names = [leaf["component"] for leaf in a.leaves]
    if args.component not in names:
        print(f"unknown component: {args.component}", file=sys.stderr)
        print(f"available: {names}", file=sys.stderr)
        return 2
    idx = names.index(args.component)
    leaf = a.leaves[idx]["leaf_hash"]
    proof = _merkle_proof(a.levels, idx)
    out = {
        "component": args.component,
        "leaf_hash": leaf,
        "merkle_proof": proof,
        "merkle_root": a.merkle_root,
        "verified": _verify_proof(leaf, proof, a.merkle_root),
    }
    print(json.dumps(out, indent=2))
    return 0


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("build", help="Build the Merkle anchor from a status_matrix.json.")
    pb.add_argument("--input", default="logs/status_matrix.json",
                    help="Path to the status_matrix.json (default: logs/status_matrix.json)")
    pb.add_argument("--out", default="logs/anchor.json",
                    help="Where to write the anchor (default: logs/anchor.json)")
    pb.set_defaults(func=cmd_build)

    pv = sub.add_parser("verify", help="Verify an existing anchor against the live matrix.")
    pv.add_argument("--anchor", default="logs/anchor.json")
    pv.add_argument("--input", default=None,
                    help="Override the matrix path recorded in the anchor.")
    pv.set_defaults(func=cmd_verify)

    pp = sub.add_parser("proof", help="Emit a Merkle inclusion proof for one component.")
    pp.add_argument("--input", default="logs/status_matrix.json")
    pp.add_argument("--component", required=True,
                    help="Exact component name as it appears in the matrix.")
    pp.set_defaults(func=cmd_proof)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
