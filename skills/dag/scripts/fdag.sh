#!/usr/bin/env bash
# fdag.sh - Shell wrapper for the Formal-Agentic DAG Engine CLI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(which python3 || echo "python3")"

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/fdag.py" "$@"
