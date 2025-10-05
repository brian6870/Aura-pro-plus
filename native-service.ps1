#!/usr/bin/env pwsh

$ServiceName = "AuraCarbonTracker"
$PythonPath = "$PWD\venv\Scripts\python.exe"
$ScriptPath = "$PWD\run.py"

Write-Host "Creating Windows Service using native PowerShell..." -ForegroundColor Green

# Check admin rights
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: Please run as Administrator" -ForegroundColor Red
    exit 1
}

Write-Host "Service Name: $ServiceName" -ForegroundColor Gray
Write-Host "Python Path: $PythonPath" -ForegroundColor Gray
Write-Host "Script Path: $ScriptPath" -ForegroundColor Gray

# Validate paths
Write-Host "Validating paths..." -ForegroundColor Yellow
if (-not (Test-Path $PythonPath)) {
    Write-Host "ERROR: Python not found at: $PythonPath" -ForegroundColor Red
    exit 1
}
Write-Host "Python executable found" -ForegroundColor Green

if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: run.py not found at: $ScriptPath" -ForegroundColor Red
    exit 1
}
Write-Host "run.py found" -ForegroundColor Green

# Make sure environment file exists
if (-not (Test-Path ".env.production")) {
    Write-Host "ERROR: .env.production not found. Run setup-environment.ps1 first" -ForegroundColor Red
    exit 1
}
Write-Host "Environment configuration found" -ForegroundColor Green

# Remove existing service
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing service..." -ForegroundColor Yellow
    try {
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq 'Running') {
            Write-Host "Stopping service..." -ForegroundColor Gray
            Stop-Service -Name $ServiceName -Force -ErrorAction Stop
            Start-Sleep -Seconds 3
        }
        sc.exe delete $ServiceName
        Start-Sleep -Seconds 2
        Write-Host "Existing service removed" -ForegroundColor Green
    } catch {
        Write-Host "Could not remove existing service: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Create service using native PowerShell cmdlet
Write-Host "Creating new service..." -ForegroundColor Yellow
try {
    # Use a wrapper script that sets environment variables
    $WrapperScript = @"
@echo off
cd /d "$PWD"
set FLASK_ENV=production
if exist ".env.production" (
    for /f "usebackq tokens=1,2 delims==" %%i in (".env.production") do (
        if not "%%i"=="" if not "%%i"=="#*" set "%%i=%%j"
    )
)
"$PythonPath" "$ScriptPath"
"@
    
    $WrapperPath = "$PWD\service-wrapper.bat"
    $WrapperScript | Out-File -FilePath $WrapperPath -Encoding ASCII
    
    New-Service -Name $ServiceName -BinaryPathName $WrapperPath -DisplayName "Aura Carbon Tracker" -Description "Carbon footprint tracking application" -StartupType Manual -ErrorAction Stop
    
    Write-Host "Service created successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to create service: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Set environment variables in registry for the service
Write-Host "Setting environment variables..." -ForegroundColor Yellow
try {
    # Read .env.production and set each variable
    if (Test-Path ".env.production") {
        Get-Content ".env.production" | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [System.Environment]::SetEnvironmentVariable($key, $value, "Machine")
                Write-Host "Set: $key" -ForegroundColor Gray
            }
        }
    }
    Write-Host "Environment variables configured" -ForegroundColor Green
} catch {
    Write-Host "Could not set environment variables: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Try to start service with detailed error handling
Write-Host "Starting service..." -ForegroundColor Green
try {
    Start-Service -Name $ServiceName -ErrorAction Stop
    Write-Host "Service start command sent successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to start service: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This is common with Python applications. Let's check the service configuration..." -ForegroundColor Yellow
}

# Check service status and provide diagnostics
Write-Host "Checking service status..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "Service Status: $($service.Status)" -ForegroundColor Green
    Write-Host "Start Type: $($service.StartType)" -ForegroundColor Gray
    
    if ($service.Status -ne 'Running') {
        Write-Host "Service is not running. Common causes:" -ForegroundColor Yellow
        Write-Host "1. Python path issues" -ForegroundColor Gray
        Write-Host "2. Missing Python dependencies" -ForegroundColor Gray
        Write-Host "3. Application startup errors" -ForegroundColor Gray
        Write-Host "4. Working directory issues" -ForegroundColor Gray
        
        Write-Host "Troubleshooting steps:" -ForegroundColor Cyan
        Write-Host "Check event logs: Get-EventLog -LogName Application -Source Python -Newest 10" -ForegroundColor Gray
        Write-Host "Test manually: $PythonPath $ScriptPath" -ForegroundColor Gray
    } else {
        Write-Host "SUCCESS: Service is running!" -ForegroundColor Green
        Write-Host "Application should be available at: http://localhost:5000" -ForegroundColor Cyan
    }
} else {
    Write-Host "Service was not created" -ForegroundColor Red
}

# Display management commands
Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "Check status:    Get-Service -Name $ServiceName" -ForegroundColor Gray
Write-Host "Start service:   Start-Service -Name $ServiceName" -ForegroundColor Gray
Write-Host "Stop service:    Stop-Service -Name $ServiceName" -ForegroundColor Gray
Write-Host "Remove service:  sc.exe delete $ServiceName" -ForegroundColor Gray
Write-Host "Check logs:      Get-EventLog -LogName Application -Source Python -Newest 10" -ForegroundColor Gray

Write-Host "Service creation process completed!" -ForegroundColor Green