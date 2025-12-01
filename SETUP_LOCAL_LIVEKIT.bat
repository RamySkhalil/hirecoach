@echo off
echo ============================================================
echo Setting up Local LiveKit Server
echo ============================================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Docker found! Starting LiveKit server...
    echo.
    echo Press Ctrl+C to stop the server when done
    echo.
    docker run --rm -p 7880:7880 -p 7881:7881 -e LIVEKIT_DEV_MODE=1 livekit/livekit-server --dev
) else (
    echo Docker not found!
    echo.
    echo Please install Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Or download LiveKit server directly:
    echo https://github.com/livekit/livekit/releases
    echo.
    pause
)

