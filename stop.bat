@echo off
setlocal
title Body Metrics — Stop

echo.
echo  ======================================
echo   BODY METRICS — Stopping...
echo  ======================================
echo.

set KILLED=0

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a  ^(port 8000 - backend^)
    taskkill /f /pid %%a >nul 2>&1
    set KILLED=1
)

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a  ^(port 5173 - frontend^)
    taskkill /f /pid %%a >nul 2>&1
    set KILLED=1
)

echo.
if "%KILLED%"=="0" (
    echo   Nothing was running on ports 8000 / 5173.
) else (
    echo   All Body Metrics processes stopped.
)
echo.
pause
endlocal
