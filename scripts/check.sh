#!/usr/bin/env bash
# ==============================================================================
# Full Verification Suite for Internship Saathi (macOS / Linux / Bash)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"

echo -e "\n========================================================"
echo " Running Full Verification Suite for Internship Saathi"
echo -e "========================================================\n"

# 1. Backend Pytest
echo "[1/4] Running Backend Pytest Suite..."
(
    cd "$BACKEND_DIR"
    "$PYTHON_BIN" -m pytest -v
)

# 2. Integration Smoke Test
echo -e "\n[2/4] Running End-to-End Integration Smoke Test..."
(
    cd "$PROJECT_ROOT"
    "$PYTHON_BIN" "$SCRIPT_DIR/smoke_test.py"
)

# 3. Frontend Vitest
echo -e "\n[3/4] Running Frontend Vitest Suite..."
(
    cd "$FRONTEND_DIR"
    npm run test
)

# 4. Frontend Production Build Check
echo -e "\n[4/4] Checking Frontend Production Build (Vite & TypeScript)..."
(
    cd "$FRONTEND_DIR"
    npm run build
)

echo -e "\n========================================================"
echo " ALL CHECKS PASSED: Application is healthy and ready!"
echo -e "========================================================\n"
