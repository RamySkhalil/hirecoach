@echo off
echo ========================================
echo  Interviewly - Quick Start Script
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Setting up Frontend...
cd ..\frontend

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo [3/4] Configuration Check...
cd ..

if not exist backend\.env (
    echo Creating backend .env file...
    copy backend\env.example backend\.env
)

if not exist frontend\.env.local (
    echo Creating frontend .env.local file...
    copy frontend\env.local.example frontend\.env.local
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo 1. Backend (in one terminal):
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 2. Frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo Then open: http://localhost:3000
echo.
echo API Docs: http://localhost:8000/docs
echo ========================================
pause

