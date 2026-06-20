@echo off
echo ================================================
echo  Trading Middleware - Starting Dev Server
echo ================================================
echo.

:: Activate venv
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause & exit /b 1
)

:: Start Docker services if not running
echo [1/3] Ensuring PostgreSQL and Redis are running...
docker-compose up -d postgres redis >nul 2>&1
timeout /t 3 /nobreak >nul

:: Start FastAPI
echo [2/3] Starting FastAPI backend...
echo.
echo  API:      http://localhost:8000
echo  Docs:     http://localhost:8000/docs
echo  Redoc:    http://localhost:8000/redoc
echo.
echo  Press Ctrl+C to stop
echo ================================================
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
