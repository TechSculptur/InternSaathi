# ==============================================================================
# Run Backend Server (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Error "Virtual environment not found at $PythonExe. Please run .\scripts\setup.ps1 first."
    exit 1
}

Write-Host "`nStarting Internship Saathi Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "Interactive API documentation available at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Yellow

Push-Location $BackendDir
try {
    & "$PythonExe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} finally {
    Pop-Location
}
