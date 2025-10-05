#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install Aura as a Windows Service
.DESCRIPTION
    This script installs the Aura Carbon Tracker application as a Windows Service using NSSM.
#>

$ServiceName = "AuraCarbonTracker"
$AppDir = $PWD.Path
$VenvPython = "venv\Scripts\python.exe"
$NssmPath = "nssm.exe"

Write-Host "Starting Aura Windows Service Installation..." -ForegroundColor Cyan
Write-Host "Service Name: $ServiceName" -ForegroundColor Gray

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: Please run this script as Administrator" -ForegroundColor Red
    exit 1
}
Write-Host "Running with administrator privileges" -ForegroundColor Green

# Validate prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check if nssm.exe exists
if (-not (Test-Path $NssmPath)) {
    Write-Host "ERROR: NSSM not found at: $NssmPath" -ForegroundColor Red
    Write-Host "Download from: https://nssm.cc/download" -ForegroundColor Yellow
    exit 1
}
Write-Host "NSSM found: $NssmPath" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: Virtual environment not found at: $VenvPython" -ForegroundColor Red
    Write-Host "Create virtual environment with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}
Write-Host "Virtual environment found: $VenvPython" -ForegroundColor Green

# Check if run.py exists
if (-not (Test-Path "run.py")) {
    Write-Host "ERROR: run.py not found in current directory" -ForegroundColor Red
    exit 1
}
Write-Host "Application entry point found: run.py" -ForegroundColor Green

# Service management section
Write-Host "Managing Windows Service..." -ForegroundColor Yellow

# Check if service already exists and remove it
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Service '$ServiceName' already exists" -ForegroundColor Yellow
    Write-Host "Stopping and removing existing service..." -ForegroundColor Gray
    
    $existingService = Get-Service -Name $ServiceName
    if ($existingService.Status -eq 'Running') {
        Write-Host "Stopping service..." -ForegroundColor Gray
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    Write-Host "Removing service..." -ForegroundColor Gray
    & $NssmPath remove $ServiceName confirm
    Start-Sleep -Seconds 2
}

# Install and configure service
Write-Host "Installing new service..." -ForegroundColor Yellow

try {
    Write-Host "Installing service with NSSM..." -ForegroundColor Gray
    & $NssmPath install $ServiceName $VenvPython "run.py"
    if ($LASTEXITCODE -ne 0) {
        throw "NSSM install failed with exit code: $LASTEXITCODE"
    }
    
    Write-Host "Configuring service settings..." -ForegroundColor Gray
    & $NssmPath set $ServiceName AppDirectory $AppDir
    & $NssmPath set $ServiceName DisplayName "Aura Carbon Footprint Tracker"
    & $NssmPath set $ServiceName Description "Carbon footprint tracking application"
    & $NssmPath set $ServiceName Start SERVICE_AUTO_START
    & $NssmPath set $ServiceName AppEnvironmentExtra FLASK_ENV=production
    
    Write-Host "Service installed and configured successfully" -ForegroundColor Green
}
catch {
    Write-Host "Failed to install service: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Start service
Write-Host "Starting service..." -ForegroundColor Green
try {
    Start-Service -Name $ServiceName -ErrorAction Stop
    Write-Host "Service start command sent" -ForegroundColor Gray
}
catch {
    Write-Host "Service start command failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Verify service status
Write-Host "Verifying service status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "Service Status: $($service.Status)" -ForegroundColor $(if($service.Status -eq 'Running'){'Green'}else{'Yellow'})
    
    if ($service.Status -eq 'Running') {
        Write-Host "SUCCESS: Service installed and running!" -ForegroundColor Green
        Write-Host "Application should be available at: http://localhost:5000" -ForegroundColor Cyan
    } else {
        Write-Host "Service installed but not running" -ForegroundColor Yellow
        Write-Host "Current status: $($service.Status)" -ForegroundColor Yellow
    }
} else {
    Write-Host "ERROR: Service was not created successfully" -ForegroundColor Red
    exit 1
}

Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "Check status:    Get-Service -Name '$ServiceName'" -ForegroundColor Gray
Write-Host "Start service:   Start-Service -Name '$ServiceName'" -ForegroundColor Gray
Write-Host "Stop service:    Stop-Service -Name '$ServiceName'" -ForegroundColor Gray

Write-Host "Installation process completed!" -ForegroundColor Green