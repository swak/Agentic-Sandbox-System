@echo off
REM Agentic Sandbox System - Windows Setup Script
REM This script validates prerequisites and initializes the system

echo ============================================
echo Agentic Sandbox System - Setup (Windows)
echo ============================================
echo.

REM ===================================================================
REM 1. Check Prerequisites
REM ===================================================================

echo Step 1/5: Checking prerequisites...
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)
echo [OK] Docker found

REM Check Docker Compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not available.
    echo Please ensure Docker Desktop is installed and running.
    pause
    exit /b 1
)
echo [OK] Docker Compose found

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker daemon is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker daemon is running

echo.

REM ===================================================================
REM 2. Environment Configuration
REM ===================================================================

echo Step 2/5: Configuring environment...
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env >nul
    echo [OK] Created .env file
    echo.
    echo [IMPORTANT] Please edit .env and add your API keys:
    echo   - OPENAI_API_KEY=your-key-here
    echo   - ANTHROPIC_API_KEY=your-key-here
    echo.
    echo Opening .env in Notepad...
    start notepad .env
    echo.
    pause
) else (
    echo [OK] .env file found
)

echo.

REM ===================================================================
REM 3. Create Directories
REM ===================================================================

echo Step 3/5: Creating directories...
echo.

if not exist configs mkdir configs
if not exist backend\app\api mkdir backend\app\api
if not exist backend\app\models mkdir backend\app\models
if not exist backend\app\services mkdir backend\app\services
if not exist backend\app\schemas mkdir backend\app\schemas
if not exist backend\app\utils mkdir backend\app\utils
if not exist frontend\src\components mkdir frontend\src\components
if not exist frontend\src\pages mkdir frontend\src\pages
if not exist frontend\src\services mkdir frontend\src\services
if not exist frontend\src\context mkdir frontend\src\context
if not exist database mkdir database

echo [OK] Directories created
echo.

REM ===================================================================
REM 4. Build Docker Images
REM ===================================================================

echo Step 4/5: Building Docker images...
echo.

echo This may take several minutes on first run...
docker compose build
if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed. Check the output above for errors.
    pause
    exit /b 1
)

echo [OK] Docker images built successfully
echo.

REM ===================================================================
REM 5. Start Services
REM ===================================================================

echo Step 5/5: Starting services...
echo.

docker compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services. Check Docker Desktop and try again.
    pause
    exit /b 1
)

echo.
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check service health
docker compose ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [WARNING] Some services may not be running properly.
    echo Run 'docker compose logs' to see error details.
) else (
    echo [OK] Services started successfully
)

echo.

REM ===================================================================
REM Setup Complete
REM ===================================================================

echo ============================================
echo [SUCCESS] Setup Complete!
echo ============================================
echo.
echo Your Agentic Sandbox System is now running:
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Useful commands:
echo   docker compose logs -f          # View logs
echo   docker compose ps               # Check status
echo   docker compose down             # Stop services
echo   docker compose restart          # Restart services
echo.
echo Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Click 'Create New Agent'
echo   3. Configure your first agent
echo   4. Start chatting!
echo.
echo For help, see SETUP_WINDOWS.md or README.md
echo.

REM Optionally open browser
set /p OPEN_BROWSER="Open http://localhost:3000 in browser? (Y/N): "
if /i "%OPEN_BROWSER%"=="Y" start http://localhost:3000

pause
