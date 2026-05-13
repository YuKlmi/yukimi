@echo off
title Course System Launcher
setlocal enabledelayedexpansion

echo ============================================
echo     Course System - One Click Launch
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

:: 1. Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python ready

:: 2. Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    ) else if exist "C:\Program Files (x86)\nodejs\node.exe" (
        set "PATH=C:\Program Files (x86)\nodejs;%PATH%"
    ) else (
        echo [ERROR] Node.js not found. Please install Node.js.
        pause
        exit /b 1
    )
)
echo [OK] Node.js ready

:: 3. Check project files
if not exist "%BACKEND_DIR%\app.py" (
    echo [ERROR] Missing: %BACKEND_DIR%\app.py
    pause
    exit /b 1
)
if not exist "%FRONTEND_DIR%\package.json" (
    echo [ERROR] Missing: %FRONTEND_DIR%\package.json
    pause
    exit /b 1
)
echo [OK] Project files verified

:: 4. Auto-install frontend dependencies
if not exist "%FRONTEND_DIR%\node_modules" (
    echo.
    echo [..] Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] npm install failed. Please run manually: npm install
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
)

:: 5. Start backend
echo.
echo [1/3] Starting backend...
start "course-system-backend" "%SCRIPT_DIR%run_backend.bat"

:: 6. Wait for backend
echo       Waiting for backend...
ping -n 5 127.0.0.1 >nul

:: 7. Start frontend
echo [2/3] Starting frontend...
start "course-system-frontend" "%SCRIPT_DIR%run_frontend.bat"

:: 8. Wait for frontend
ping -n 3 127.0.0.1 >nul

:: 9. Open browser
echo [3/3] Opening browser...
start "" http://localhost:5173

echo.
echo ============================================
echo  Launch complete!
echo  Backend : http://localhost:5000
echo  Frontend: http://localhost:5173
echo.
echo  Close each window to stop service
echo ============================================
echo.
pause
