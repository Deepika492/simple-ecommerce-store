@echo off
setlocal enabledelayedexpansion
title Simple E-Commerce Store (AuraStore) - Full-Stack Application

echo ==============================================================================
echo             AuraStore - Full-Stack E-Commerce Web Application
echo ==============================================================================
echo.

:: Step 1: Detect Project Root & Navigate to Backend
cd /d "%~dp0backend"
if errorlevel 1 (
    echo [ERROR] Failed to locate backend directory. Please run this script from the project root.
    pause
    exit /b 1
)

:: Step 2: Ensure Virtual Environment Exists
if not exist "venv\Scripts\activate.bat" (
    echo [*] Python virtual environment not detected.
    echo [*] Creating virtual environment in backend\venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python not found or failed to create virtual environment.
        echo [INFO] Please ensure Python 3.8+ is installed and added to your system PATH.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
)

:: Step 3: Activate Virtual Environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Step 4: Set Development Environment Variable (if not set)
if "%DJANGO_SECRET_KEY%"=="" (
    set "DJANGO_SECRET_KEY=development-secret-key-aura-store-2026"
)

:: Step 5: Install / Verify Dependencies
echo.
echo [1/4] Checking and installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

:: Step 6: Database Migrations
echo.
echo [2/4] Applying database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Database migrations failed.
    pause
    exit /b 1
)

:: Step 7: Safe & Idempotent Database Seeding
echo.
echo [3/4] Seeding demo categories, products, and test accounts...
python manage.py seed_data
if errorlevel 1 (
    echo [ERROR] Database seeding failed.
    pause
    exit /b 1
)

:: Step 8: Start Django Server & Open Browser
echo.
echo [4/4] Starting Django Server at http://127.0.0.1:8000/
echo.
echo ==============================================================================
echo  AuraStore is now running successfully!
echo.
echo  Website URL:       http://127.0.0.1:8000/
echo.
echo  Demo Accounts (Development Testing):
echo   - Customer Demo:  username: customer   password: Customer@123
echo   - Admin Demo:     username: admin      password: Admin@123
echo.
echo  Press Ctrl+C in this terminal window to stop the server.
echo ==============================================================================
echo.

start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000

pause
