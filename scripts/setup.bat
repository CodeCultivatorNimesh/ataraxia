@echo off
echo ================================================
echo  Trading Middleware - Windows Setup
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)
echo [OK] Python found

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install from https://nodejs.org
    pause & exit /b 1
)
echo [OK] Node.js found

:: Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker not found. Install from https://docker.com
    echo           Docker is needed to run PostgreSQL and Redis automatically.
    echo           Alternatively install them manually.
)

:: Create virtual environment
echo.
echo [1/5] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [2/5] Installing Python dependencies...
pip install -r requirements.txt --quiet

:: Copy .env
echo [3/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo [INFO] .env file created. Edit it and add your API keys before running.
) else (
    echo [INFO] .env already exists, skipping.
)

:: Start Docker services
echo [4/5] Starting PostgreSQL and Redis via Docker...
docker-compose up -d postgres redis
if errorlevel 1 (
    echo [WARNING] Docker start failed. Make sure Docker Desktop is running.
)

:: Wait for DB
echo [5/5] Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Edit .env and add your Alpaca + Binance keys
echo  2. Run: scripts\run_dev.bat
echo  3. Open: http://localhost:8000/docs
echo ================================================
pause
