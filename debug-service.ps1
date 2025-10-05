#!/usr/bin/env pwsh

$ServiceName = "AuraCarbonTracker"

Write-Host "🔧 Debugging Service Issues..." -ForegroundColor Cyan

# Check service status
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "Service Status: $($service.Status)" -ForegroundColor $(if($service.Status -eq 'Running'){'Green'}else{'Yellow'})
} else {
    Write-Host "❌ Service not found" -ForegroundColor Red
    exit 1
}

# Check event logs for Python errors
Write-Host "`n📋 Checking event logs..." -ForegroundColor Yellow
try {
    $events = Get-EventLog -LogName Application -Source "Python" -Newest 5 -ErrorAction SilentlyContinue
    if ($events) {
        Write-Host "Recent Python events found:" -ForegroundColor Green
        $events | Format-Table TimeGenerated, EntryType, Message -AutoSize
    } else {
        Write-Host "No recent Python events found" -ForegroundColor Gray
    }
} catch {
    Write-Host "No Python events found in log" -ForegroundColor Gray
}

# Check service configuration
Write-Host "`n⚙️ Checking service configuration..." -ForegroundColor Yellow
try {
    $serviceInfo = Get-WmiObject -Class Win32_Service -Filter "Name='$ServiceName'"
    Write-Host "Path: $($serviceInfo.PathName)" -ForegroundColor Gray
    Write-Host "Start Mode: $($serviceInfo.StartMode)" -ForegroundColor Gray
    Write-Host "State: $($serviceInfo.State)" -ForegroundColor Gray
} catch {
    Write-Host "Could not retrieve service details" -ForegroundColor Red
}

# Test manual execution
Write-Host "`n🧪 Testing manual execution..." -ForegroundColor Yellow
$PythonPath = "$PWD\venv\Scripts\python.exe"
$ScriptPath = "$PWD\run.py"

if (Test-Path $PythonPath) {
    Write-Host "Running: `"$PythonPath`" `"$ScriptPath`"" -ForegroundColor Gray
    try {
        Start-Process -FilePath $PythonPath -ArgumentList $ScriptPath -NoNewWindow -Wait
        Write-Host "✅ Manual execution completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Manual execution failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n💡 Solution if service won't start:" -ForegroundColor Cyan
Write-Host "1. Check Python dependencies: .\venv\Scripts\pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "2. Test manually: .\venv\Scripts\python.exe run.py" -ForegroundColor Gray
Write-Host "3. Check port 5000 is available" -ForegroundColor Gray
Write-Host "4. Run service with log output to see errors" -ForegroundColor Gray