# ==============================================================================
# Setup Script for Internship Saathi (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "`n=== Setting up Internship Saathi ===" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot"

# 1. Ensure Environment Files Exist Without Overwriting
$BackendEnv = Join-Path $BackendDir ".env"
$BackendEnvExample = Join-Path $BackendDir ".env.example"
if (-not (Test-Path $BackendEnv)) {
    Write-Host "Creating backend .env from .env.example..." -ForegroundColor Yellow
    Copy-Item $BackendEnvExample $BackendEnv
} else {
    Write-Host "Backend .env already exists. Preserving existing file." -ForegroundColor Green
}

$FrontendEnv = Join-Path $FrontendDir ".env"
$FrontendEnvExample = Join-Path $FrontendDir ".env.example"
if (-not (Test-Path $FrontendEnv)) {
    Write-Host "Creating frontend .env from .env.example..." -ForegroundColor Yellow
    Copy-Item $FrontendEnvExample $FrontendEnv
} else {
    Write-Host "Frontend .env already exists. Preserving existing file." -ForegroundColor Green
}

# 2. Python Virtual Environment Setup
$VenvDir = Join-Path $BackendDir ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Creating isolated Python virtual environment in $VenvDir..." -ForegroundColor Yellow
    $CreatedVenv = $false

    # Prefer Python 3.12 when installed, but fall back to the active Python.
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        & py -3.12 -m venv "$VenvDir"
        if (Test-Path $PythonExe) { $CreatedVenv = $true }
    }

    if (-not $CreatedVenv -and (Get-Command "python" -ErrorAction SilentlyContinue)) {
        if (Test-Path $VenvDir) { Remove-Item $VenvDir -Recurse -Force }
        & python -m venv "$VenvDir"
        if (Test-Path $PythonExe) { $CreatedVenv = $true }
    }

    if (-not $CreatedVenv) {
        Write-Error "Could not create a Python virtual environment. Install Python 3.11 or 3.12 and ensure it is available on PATH."
        exit 1
    }
}

Write-Host "Using Python interpreter: $PythonExe" -ForegroundColor Green

# 3. Install Backend Dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& "$PythonExe" -m pip install --upgrade pip
& "$PythonExe" -m pip install -r (Join-Path $BackendDir "requirements-dev.txt")

# 4. Run Migrations and Seed Data
Write-Host "Applying database migrations..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    & "$PythonExe" -m alembic upgrade head
    Write-Host "Seeding database with taxonomy and sample internships..." -ForegroundColor Yellow
    & "$PythonExe" seed.py
} finally {
    Pop-Location
}

# 5. Install Frontend Dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $FrontendDir
try {
    if (Test-Path (Join-Path $FrontendDir "package-lock.json")) {
        npm ci
    } else {
        npm install
    }
} finally {
    Pop-Location
}

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "Start backend with:  .\scripts\run-backend.ps1" -ForegroundColor Cyan
Write-Host "Start frontend with: .\scripts\run-frontend.ps1`n" -ForegroundColor Cyan
