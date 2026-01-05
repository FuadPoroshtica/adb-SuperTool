@echo off
REM ============================================================================
REM  Android SuperTool - Windows Launcher
REM  Double-click to run
REM ============================================================================

title Android SuperTool - Mobile Shop Edition

echo.
echo ===============================================================
echo          ANDROID SUPERTOOL - Mobile Shop Edition
echo ===============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check/create virtual environment
if not exist "venv" (
    echo.
    echo [...] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created

    REM Install dependencies
    echo [...] Installing dependencies...
    venv\Scripts\pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
)

REM Run the tool
echo.
echo Starting Android SuperTool...
echo.

venv\Scripts\python.exe supertool.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Program exited with an error.
    pause
)
