@echo off
chcp 65001 >nul
echo Starting Aura Production Deployment (Native Service)...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if we're in the right directory
if not exist "run.py" (
    echo ERROR: Must run from application root directory
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Run: python -m venv venv
    pause
    exit /b 1
)

:: Setup environment first
echo Setting up environment...
powershell -ExecutionPolicy Bypass -File "setup-environment.ps1"

:: Run the deployment script
echo Starting deployment with PowerShell...
powershell -ExecutionPolicy Bypass -File "deploy-prod.ps1"

:: Check if deployment was successful
if errorlevel 1 (
    echo ERROR: Deployment failed
    pause
    exit /b 1
)

echo SUCCESS: Deployment completed successfully!
echo Check application at: http://localhost:5000
pause