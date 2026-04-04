@echo off
REM Joseph Flowershop - Quick Start Script for Windows

echo.
echo ============================================
echo   Joseph Flowershop Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Step 1: Create virtual environment
echo [1/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo     ✓ Virtual environment created
) else (
    echo     ✓ Virtual environment already exists
)

REM Step 2: Activate virtual environment and install dependencies
echo [2/5] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r flowershop\requirements.txt >nul 2>&1
echo     ✓ Dependencies installed

REM Step 3: Navigate to project directory
cd flowershop

REM Step 4: Run migrations
echo [3/5] Setting up database...
python manage.py migrate >nul 2>&1
echo     ✓ Database created

REM Step 5: Load initial data
echo [4/5] Loading flower data...
python manage.py init_data
echo.

REM Step 6: Summary
echo [5/5] Setup complete!
echo.
echo ============================================
echo   Next Steps:
echo ============================================
echo.
echo 1. Create admin account:
echo    python manage.py createsuperuser
echo.
echo 2. Start development server:
echo    python manage.py runserver
echo.
echo 3. Open in browser:
echo    - Home: http://127.0.0.1:8000/
echo    - Admin: http://127.0.0.1:8000/admin/
echo.
echo For detailed setup instructions, see: ..\SETUP.md
echo.
pause
