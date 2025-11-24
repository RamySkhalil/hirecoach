@echo off
echo ========================================
echo  Starting LiveKit Interview System
echo ========================================
echo.

echo This will open 3 terminal windows:
echo   1. Backend API Server
echo   2. LiveKit Agent Worker (Voice AI)
echo   3. Frontend Dev Server
echo.
echo Press any key to continue...
pause > nul

echo.
echo [1/3] Starting Backend API Server...
start "Backend Server" cmd /k "cd backend && .\.venv\Scripts\python -m uvicorn app.main:app --reload"

timeout /t 3 > nul

echo [2/3] Starting LiveKit Agent Worker...
start "LiveKit Agent" cmd /k "cd backend && .\.venv\Scripts\python livekit_agent.py start"

timeout /t 3 > nul

echo [3/3] Starting Frontend Dev Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo Three terminal windows should now be open:
echo   1. Backend Server (port 8000)
echo   2. LiveKit Agent (handling voice)
echo   3. Frontend (port 3000)
echo.
echo Open: http://localhost:3000
echo.
echo To stop: Close each terminal window or press Ctrl+C
echo ========================================
pause

