@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Campaign Analyzer - Startup Script
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.x from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python detected.
echo.

REM Install dependencies
echo [2/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [2/4] Dependencies installed successfully.
echo.

REM Start Flask backend in a new window
echo [3/4] Starting Flask backend on http://127.0.0.1:5000 ...
start "Campaign Analyzer Backend" cmd /k "python -m backend.app"
echo [3/4] Backend started in a new window.
echo.

REM Wait a moment for the server to initialize
timeout /t 3 /nobreak >nul

REM Open frontend in default browser
echo [4/4] Opening frontend in default web browser...
start "" "frontend/index.html"
echo [4/4] Frontend opened.
echo.

echo ============================================
echo   Campaign Analyzer is running!
echo   - Backend: http://127.0.0.1:5000
echo   - Frontend: frontend/index.html
echo ============================================
echo.
echo Press any key to exit this window (backend will keep running).
pause >nul
endlocal
