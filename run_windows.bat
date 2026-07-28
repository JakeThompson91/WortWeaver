@echo off
TITLE WortWeaver - Local German-English Spot-Checker
echo ========================================================
echo               WortWeaver Windows Launcher
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to system PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Create Virtual Environment if it doesn't exist
IF NOT EXIST "venv" (
    echo [1/3] Creating virtual environment (venv)...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate Virtual Environment
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install / Update Dependencies
echo [3/3] Checking and installing requirements...
pip install -r requirements.txt --disable-pip-version-check
IF %ERRORLEVEL% NEQ 0 (
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

:: Start application via cross-platform launcher
python run_app.py

pause
