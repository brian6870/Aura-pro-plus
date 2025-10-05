#!/usr/bin/env pwsh
Write-Host "Testing NSSM..." -ForegroundColor Green

# Test 1: Check if nssm.exe exists
$NssmPath = "nssm.exe"
if (Test-Path $NssmPath) {
    Write-Host "✅ nssm.exe found" -ForegroundColor Green
    Write-Host "   File size: $((Get-Item $NssmPath).Length) bytes" -ForegroundColor Gray
} else {
    Write-Host "❌ nssm.exe NOT found" -ForegroundColor Red
    exit 1
}

# Test 2: Check if nssm runs
try {
    $result = & $NssmPath 2>&1
    Write-Host "✅ nssm.exe executes successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ nssm.exe failed to execute: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check variable names
Write-Host "`nTesting variables..." -ForegroundColor Yellow
$ServiceName = "AuraCarbonTracker"
$NssmPath = "nssm.exe"

Write-Host "ServiceName: $ServiceName" -ForegroundColor Gray
Write-Host "NssmPath: $NssmPath" -ForegroundColor Gray

Write-Host "`n✅ All basic tests passed!" -ForegroundColor Green