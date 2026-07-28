# WortWeaver PowerShell Launcher for Windows
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         WortWeaver PowerShell Launcher for Windows     " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Detect Python command
$pyCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py -3"
}

if (-not $pyCmd) {
    Write-Host "[ERROR] Python is not installed or not in system PATH." -ForegroundColor Red
    Write-Host "Please download Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Be sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Using Python: $pyCmd" -ForegroundColor Green

# Create venv if missing
if (-not (Test-Path "venv")) {
    Write-Host "[1/3] Creating virtual environment (venv)..." -ForegroundColor Yellow
    Invoke-Expression "$pyCmd -m venv venv"
}

# Activate venv
Write-Host "[2/3] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "[WARNING] Activate.ps1 not found, continuing with Python..." -ForegroundColor Yellow
}

# Install requirements
Write-Host "[3/3] Checking dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt --disable-pip-version-check

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " Launching WortWeaver on http://127.0.0.1:5000          " -ForegroundColor Green
Write-Host " Press Ctrl+C in this window to stop the server         " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

python run_app.py

Read-Host -Prompt "Press Enter to exit"
