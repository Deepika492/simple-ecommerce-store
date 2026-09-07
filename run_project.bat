@echo off
setlocal enabledelayedexpansion
title Simple E-Commerce Store (AuraStore) - Full-Stack Launcher

echo ==============================================================================
echo             AuraStore - Full-Stack E-Commerce Web Application
echo ==============================================================================
echo.
echo Starting AuraStore...
echo.

:: Step 1: Check Python Installation
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on your system or is not added to your PATH.
    echo.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Step 2: Detect Project Root & Set Directories
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

cd /d "%PROJECT_ROOT%"

:: Step 3: Create Virtual Environment if Missing
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [*] Python virtual environment not detected.
    echo [*] Creating virtual environment in backend\venv...
    python -m venv "%BACKEND_DIR%\venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo Please ensure Python is properly configured on your system.
        echo.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
    echo.
)

:: Step 4: Activate Virtual Environment
echo [*] Activating Python virtual environment...
call "%BACKEND_DIR%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    echo.
    pause
    exit /b 1
)

:: Step 5: Set Development Environment Variable (Safe Local Fallback)
if "%DJANGO_SECRET_KEY%"=="" (
    set "DJANGO_SECRET_KEY=development-secret-key-aura-store-2026"
)

:: Step 6: Install / Verify Dependencies
echo [*] Checking and installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install packages from requirements.txt.
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies verified.
echo.

:: Step 7: Apply Migrations & Seed Data Idempotently
cd /d "%BACKEND_DIR%"

echo [*] Applying database migrations...
python manage.py makemigrations --noinput >nul 2>nul
python manage.py migrate --noinput
if errorlevel 1 (
    echo [ERROR] Database migration failed.
    echo.
    pause
    exit /b 1
)

echo [*] Seeding demo products, categories, and test accounts...
python manage.py seed_data
if errorlevel 1 (
    echo [ERROR] Database seeding failed.
    echo.
    pause
    exit /b 1
)
echo.

:: Step 8: Start Frontend Local Server (Port 5500) in Background Process
echo Starting frontend...
start "AuraStore Frontend Server (Port 5500)" /min cmd /c "cd /d "%FRONTEND_DIR%" && python -m http.server 5500"

:: Step 9: Open Frontend in Default Web Browser
echo Opening AuraStore in browser...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5500/index.html

:: Step 10: Start Backend Django Server (Port 8000) in Main Process
echo Starting backend...
echo.
echo ==============================================================================
echo  AuraStore Full-Stack Application is now running!
echo.
echo  Frontend URL:      http://127.0.0.1:5500/index.html
echo  Backend API URL:   http://127.0.0.1:8000/api/
echo.
echo  Development Demo Accounts:
echo   - Customer Demo:  username: customer   password: Customer@123
echo   - Admin Demo:     username: admin      password: Admin@123
echo.
echo  Both Frontend (Port 5500) and Backend (Port 8000) are active.
echo  Press Ctrl+C in this terminal window to stop the Django backend server.
echo ==============================================================================
echo.

python manage.py runserver 127.0.0.1:8000

pause
