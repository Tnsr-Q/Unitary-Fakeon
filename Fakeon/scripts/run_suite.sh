#!/usr/bin/env bash
# scripts/run_suite.sh — local dry-run of the QÜFT verification pipeline.
#
# Replays the CI pipeline end-to-end (minus Lean `lake build`) against the
# live tree, verifying the same artefacts GitHub Actions would produce.
#
# Usage:
#   bash scripts/run_suite.sh                  # no flags, analytic fallback
#   bash scripts/run_suite.sh --hyperint FILE  # extract c_vectors.json first
#   bash scripts/run_suite.sh --require-verified
set -euo pipefail

HYPERINT_INPUT=""
REQUIRE_VERIFIED=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --hyperint) HYPERINT_INPUT="$2"; shift 2 ;;
        --require-verified) REQUIRE_VERIFIED=1; shift ;;
        -h|--help)
            sed -n '2,12p' "$0"; exit 0 ;;
        *) echo "unknown flag: $1" >&2; exit 2 ;;
    esac
done

REPO="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$REPO"

echo "== [1/6] ruff lint =="
ruff check fakeon_numeric tests scripts

if [[ -n "$HYPERINT_INPUT" ]]; then
    echo "== [2/6] HyperInt boundary-vector extraction =="
    python scripts/extract_cvec.py --input "$HYPERINT_INPUT"
else
    echo "== [2/6] HyperInt extraction skipped (analytic fallback active) =="
fi

echo "== [3/6] pytest =="
python -m pytest --junitxml=logs/pytest-junit.xml

echo "== [4/6] status-matrix audit =="
python -m fakeon_numeric.status_tracker --root . --strict --out logs/status_matrix.json
python scripts/audit_status.py --out docs/STATUS.md

echo "== [5/6] Merkle anchor =="
python scripts/anchor_status.py build
python scripts/anchor_status.py verify

echo "== [6/6] FakeonCertificate =="
ARGS=()
if [[ "$REQUIRE_VERIFIED" -eq 1 ]]; then ARGS+=(--require-verified); fi
python scripts/assemble_certificate.py "${ARGS[@]}"

echo "done — artefacts:"
echo "  logs/status_matrix.json"
echo "  logs/anchor.json"
echo "  logs/FakeonCertificate.json"
echo "  logs/pytest-junit.xml"
echo "  docs/STATUS.md"
