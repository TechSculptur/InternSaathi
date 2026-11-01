#!/usr/bin/env bash
# ==============================================================================
# Run Backend Server (macOS / Linux / Bash)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Virtual environment not found at $PYTHON_BIN. Please run ./scripts/setup.sh first." >&2
    exit 1
fi

echo -e "\nStarting Internship Saathi Backend on http://127.0.0.1:8000 ..."
echo "Interactive API documentation available at: http://127.0.0.1:8000/docs"
echo -e "Press Ctrl+C to stop.\n"

cd "$BACKEND_DIR"
exec "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
