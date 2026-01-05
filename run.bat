@echo off
REM Android SuperTool Launcher (Windows)

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe supertool.py %*
) else (
    REM Check if dependencies are installed globally
    python -c "import rich" 2>nul
    if %errorlevel% equ 0 (
        python supertool.py %*
    ) else (
        echo Virtual environment not found. Running setup...
        python setup.py
        echo.
        echo Setup complete. Run this script again to start the tool.
        pause
    )
)
