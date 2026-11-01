#!/usr/bin/env bash
# ==============================================================================
# Setup Script for Internship Saathi (macOS / Linux / Bash)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "\n=== Setting up Internship Saathi ==="
echo "Project Root: $PROJECT_ROOT"

# 1. Ensure Environment Files Exist Without Overwriting
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "Creating backend .env from .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
else
    echo "Backend .env already exists. Preserving existing file."
fi

if [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo "Creating frontend .env from .env.example..."
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
else
    echo "Frontend .env already exists. Preserving existing file."
fi

# 2. Python Virtual Environment Setup
VENV_DIR="$BACKEND_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Creating isolated virtual environment in $VENV_DIR..."
    if command -v python3.12 &>/dev/null; then
        python3.12 -m venv "$VENV_DIR"
    elif command -v python3 &>/dev/null; then
        python3 -m venv "$VENV_DIR"
    else
        echo "Error: Python 3 not found." >&2
        exit 1
    fi
fi

# 3. Install Backend Dependencies
echo "Installing backend dependencies..."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r "$BACKEND_DIR/requirements-dev.txt"

# 4. Migrations & Seed
echo "Applying database migrations..."
(
    cd "$BACKEND_DIR"
    "$PYTHON_BIN" -m alembic upgrade head
    echo "Seeding database..."
    "$PYTHON_BIN" seed.py
)

# 5. Frontend Dependencies
echo "Installing frontend dependencies..."
(
    cd "$FRONTEND_DIR"
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
)

echo -e "\nSetup completed successfully!"
echo "Start backend with:  ./scripts/run-backend.sh"
echo -e "Start frontend with: ./scripts/run-frontend.sh\n"
