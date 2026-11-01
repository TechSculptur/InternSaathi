# ==============================================================================
# Full Verification Suite for Internship Saathi (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host " Running Full Verification Suite for Internship Saathi" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# 1. Backend Pytest
Write-Host "[1/4] Running Backend Pytest Suite..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    & "$PythonExe" -m pytest -v
} finally {
    Pop-Location
}

# 2. Integration Smoke Test
Write-Host "`n[2/4] Running End-to-End Integration Smoke Test..." -ForegroundColor Yellow
Push-Location $ProjectRoot
try {
    & "$PythonExe" (Join-Path $ScriptDir "smoke_test.py")
} finally {
    Pop-Location
}

# 3. Frontend Vitest
Write-Host "[3/4] Running Frontend Vitest Suite..." -ForegroundColor Yellow
Push-Location $FrontendDir
try {
    npm run test
} finally {
    Pop-Location
}

# 4. Frontend Production Build Check
Write-Host "`n[4/4] Checking Frontend Production Build (Vite & TypeScript)..." -ForegroundColor Yellow
Push-Location $FrontendDir
try {
    npm run build
} finally {
    Pop-Location
}

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " ALL CHECKS PASSED: Application is healthy and ready!" -ForegroundColor Green
Write-Host "========================================================`n" -ForegroundColor Green
