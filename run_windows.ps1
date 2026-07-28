# WortWeaver PowerShell Launcher for Windows
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         WortWeaver PowerShell Launcher for Windows     " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] $pythonVersion found." -ForegroundColor Green
} catch {
    Write-Host "[!] Error: Python is not installed or not in system PATH." -ForegroundColor Red
    Write-Host "    Download Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "    Be sure to check 'Add Python to PATH' during setup." -ForegroundColor Yellow
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Create venv if missing
if (-not (Test-Path "venv")) {
    Write-Host "[1/3] Creating virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "[2/3] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install requirements
Write-Host "[3/3] Checking dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt --disable-pip-version-check

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " Launching WortWeaver on http://127.0.0.1:5000          " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

python run_app.py
