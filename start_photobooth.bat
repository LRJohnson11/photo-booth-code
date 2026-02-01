@echo off
REM Photo Booth Startup Script (Windows)
REM This script sets up and runs the photo booth application

setlocal enabledelayedexpansion

REM Load configuration
if exist config.env (
    for /f "tokens=1,2 delims==" %%a in (config.env) do (
        if "%%a"=="PYTHON_VERSION" set PYTHON_VERSION=%%b
        if "%%a"=="VENV_DIR" set VENV_DIR=%%b
    )
) else (
    echo Warning: config.env not found. Using defaults.
    set PYTHON_VERSION=3.13.9
    set VENV_DIR=venv
)

cd /d "%~dp0"

echo ==================================================
echo Photo Booth Application - Startup
echo ==================================================
echo.

REM Ask user which mode to run
echo Select email sending mode:
echo 1. Gmail API (100 emails/day unverified, requires OAuth setup)
echo 2. SMTP (500 emails/day, simpler setup with app password)
echo.
set /p mode_choice="Enter your choice (1 or 2): "

if "%mode_choice%"=="1" (
    set SCRIPT_TO_RUN=photo_booth.py
    set MODE_NAME=Gmail API
) else if "%mode_choice%"=="2" (
    set SCRIPT_TO_RUN=photo_booth_smtp.py
    set MODE_NAME=SMTP
) else (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
echo Starting in %MODE_NAME% mode...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

REM Get installed Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set INSTALLED_VERSION=%%i
echo Installed Python version: %INSTALLED_VERSION%
echo Configured Python version: %PYTHON_VERSION%
echo.

REM Try to find the specific Python version
set PYTHON_CMD=python

REM Check if specific version exists (e.g., py -3.13)
py -%PYTHON_VERSION% --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -%PYTHON_VERSION%
    echo Using: py -%PYTHON_VERSION%
) else (
    echo Note: Exact version %PYTHON_VERSION% not found via py launcher
    echo Using default python command
    echo If you need a specific version, install it and it will be auto-detected
)

echo.

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)

echo.

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install/update requirements
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ==================================================
echo Starting Photo Booth Application (%MODE_NAME%)...
echo ==================================================
echo.

REM Run the application
python %SCRIPT_TO_RUN%

REM Deactivate on exit
deactivate

pause
