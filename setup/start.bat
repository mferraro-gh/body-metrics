@echo off
setlocal
title Body Metrics — Starting up

:: Resolve paths relative to this script (setup\ folder)
set "SETUP_DIR=%~dp0"
set "ROOT=%SETUP_DIR%.."
set "BACKEND=%ROOT%\backend"
set "FRONTEND=%ROOT%\frontend"
set "VENV=%BACKEND%\venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "UVICORN=%VENV%\Scripts\uvicorn.exe"

echo ============================================
echo  Body Metrics — Windows Setup ^& Launch
echo ============================================

:: ── Check Python ─────────────────────────────
echo.
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found.
    echo  Please install Python 3.10+ from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Found: %%v

:: ── Check Node ───────────────────────────────
echo.
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Node.js not found.
    echo  Please install Node.js 18+ from https://nodejs.org
    echo.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do echo  Found: Node %%v

:: ── Create venv if missing ───────────────────
echo.
echo [3/5] Setting up Python virtual environment...
if not exist "%PYTHON%" (
    echo  Creating venv...
    python -m venv "%VENV%"
    if not exist "%PYTHON%" (
        echo  ERROR: Could not create virtual environment.
        pause & exit /b 1
    )
)
echo  Done.

:: ── Install backend deps if needed ──────────
echo.
echo [4/5] Checking backend dependencies...
if not exist "%UVICORN%" (
    echo  Installing Python packages — this may take several minutes on first run.
    echo  ^(EasyOCR requires PyTorch, ~2 GB download^)
    echo.
    "%PYTHON%" -m pip install --upgrade pip --quiet
    "%PYTHON%" -m pip install -r "%BACKEND%\requirements.txt"
    if not exist "%UVICORN%" (
        echo  ERROR: Dependency installation failed.
        pause & exit /b 1
    )
)
echo  Done.

:: ── Install frontend deps if needed ─────────
echo.
echo [5/5] Checking frontend dependencies...
if not exist "%FRONTEND%\node_modules" (
    echo  Installing npm packages...
    cd /d "%FRONTEND%"
    npm install
)
echo  Done.

:: ── Launch ───────────────────────────────────
echo.
echo  Launching servers...

start "Body Metrics — Backend" cmd /k ""%UVICORN%" main:app --reload --port 8000 --app-dir "%BACKEND%""
start "Body Metrics — Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev"

echo  Waiting for servers to start...
timeout /t 6 /nobreak >nul

:: Open browser on first available Vite port
for %%P in (5173 5174 5175 5176 5177 5178 5179 5180) do (
    curl -s --max-time 1 http://localhost:%%P >nul 2>&1
    if not errorlevel 1 (
        echo  Opening http://localhost:%%P
        start "" "http://localhost:%%P"
        goto :done
    )
)
echo  Could not detect frontend — open http://localhost:5173 manually.

:done
echo.
echo  Both servers are running in separate windows.
echo  Close those windows to stop the app.
echo.
endlocal
