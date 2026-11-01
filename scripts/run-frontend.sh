#!/usr/bin/env bash
# ==============================================================================
# Run Frontend Dev Server (macOS / Linux / Bash)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Error: Frontend dependencies not found. Please run ./scripts/setup.sh first." >&2
    exit 1
fi

echo -e "\nStarting Internship Saathi Frontend on http://127.0.0.1:5173 ..."
echo "Make sure the backend is also running on http://127.0.0.1:8000"
echo -e "Press Ctrl+C to stop.\n"

cd "$FRONTEND_DIR"
exec npm run dev
