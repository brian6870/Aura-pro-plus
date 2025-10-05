#!/usr/bin/env pwsh

Write-Host "Starting Aura Production Deployment (Native Service)..." -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: Please run as Administrator" -ForegroundColor Red
    exit 1
}

# Check prerequisites
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "run.py")) {
    Write-Host "ERROR: run.py not found" -ForegroundColor Red
    exit 1
}

# Setup environment first
Write-Host "Setting up environment variables..." -ForegroundColor Yellow
.\setup-environment.ps1

# Test the application manually first
Write-Host "Testing application manually..." -ForegroundColor Yellow
try {
    # Set environment variables for current session
    $env:FLASK_ENV = "production"
    
    if (Test-Path ".env.production") {
        Get-Content ".env.production" | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    
    Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList "run.py" -PassThru -NoNewWindow -Wait
    Write-Host "✅ Application test completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Application test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Run the native service installation
Write-Host "Installing Windows Service..." -ForegroundColor Yellow
.\native-service.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Deployment completed!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Deployment failed" -ForegroundColor Red
    exit 1
}