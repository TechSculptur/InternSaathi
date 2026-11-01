# ==============================================================================
# Run Frontend Dev Server (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectRoot "frontend"

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Error "Frontend dependencies not installed. Please run .\scripts\setup.ps1 first."
    exit 1
}

Write-Host "`nStarting Internship Saathi Frontend on http://127.0.0.1:5173 ..." -ForegroundColor Green
Write-Host "Make sure the backend is also running on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Yellow

Push-Location $FrontendDir
try {
    npm run dev
} finally {
    Pop-Location
}
