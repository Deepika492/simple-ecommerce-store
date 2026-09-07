@echo off
title Simple E-Commerce Store - CodeAlpha
echo ========================================================
echo       Starting Simple E-Commerce Store (Full-Stack)
echo ========================================================
echo.

cd /d "%~dp0backend"

if "%DJANGO_SECRET_KEY%"=="" (
    set "DJANGO_SECRET_KEY=development-secret-key-aura-store-2026"
)

echo [1/3] Checking dependencies...
python -m pip install -r requirements.txt

echo.
echo [2/3] Applying migrations and seeding database...
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data

echo.
echo [3/3] Starting Django Server at http://127.0.0.1:8000/
echo.
echo --------------------------------------------------------
echo Customer Demo:  username: customer   password: Customer@123
echo Admin Demo:     username: admin      password: Admin@123
echo --------------------------------------------------------
echo.
start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000

pause
