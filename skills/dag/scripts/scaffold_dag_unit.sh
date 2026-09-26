#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/scaffold_dag_unit.py" "$@"
else
    echo "[ERROR] python3 was not found in PATH." >&2
    exit 1
fi
