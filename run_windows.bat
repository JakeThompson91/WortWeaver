@echo off
TITLE WortWeaver - Local German-English Spot-Checker
cd /d "%~dp0"

echo ========================================================
echo               WortWeaver Windows Launcher
echo ========================================================
echo.

set "PY_CMD="
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python is not installed or not added to system PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python command: %PY_CMD%

if not exist "venv" (
    echo [1/3] Creating virtual environment venv...
    %PY_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [2/3] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo [WARNING] venv\Scripts\activate.bat not found. Continuing with Python...
)

echo [3/3] Checking and installing requirements...
pip install -r requirements.txt --disable-pip-version-check
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo  Starting WortWeaver Web App on http://127.0.0.1:5000
echo  Press Ctrl+C in this window to stop the server.
echo ========================================================
echo.

python run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] WortWeaver terminated with error code %ERRORLEVEL%.
)

echo.
pause
