@echo off
echo ========================================
echo  Interviewly Phase 2 Setup
echo ========================================
echo.

echo [1/2] Installing Backend Dependencies...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/Updating Python packages...
pip install -r requirements.txt

echo.
echo [2/2] Checking Environment Configuration...
cd ..

if not exist backend\.env (
    echo WARNING: No .env file found!
    echo.
    echo Please create backend\.env with your API keys:
    echo.
    echo OPENAI_API_KEY=sk-...
    echo ELEVENLABS_API_KEY=...
    echo DEEPGRAM_API_KEY=...
    echo.
    echo See MIGRATION_TO_PHASE2.md for details.
    echo.
    pause
) else (
    echo ✓ .env file found
)

echo.
echo ========================================
echo  Phase 2 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Configure API keys in backend\.env
echo    See MIGRATION_TO_PHASE2.md for help
echo.
echo 2. Start backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 3. Start frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open http://localhost:3000
echo.
echo ========================================
pause

