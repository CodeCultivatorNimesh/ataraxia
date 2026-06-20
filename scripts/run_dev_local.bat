@echo off
setlocal

cd /d "%~dp0.."

set "VENV_DIR=.venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at %VENV_DIR%\Scripts\activate.bat
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"

start "Trading Middleware Backend" cmd /k "cd /d "%~dp0.." && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "Trading Middleware Frontend" cmd /k "cd /d "%~dp0..\frontend" && npm run dev"

echo.
echo Backend started at: http://127.0.0.1:8000
echo Frontend started at: http://localhost:3000
echo.
echo Both processes were launched in separate windows.
