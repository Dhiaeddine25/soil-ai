# MONITOR_STARTUP.PS1 - Monitor backend and frontend startup progress
# Usage: .\monitor_startup.ps1

$ROOT = "c:\Users\surface pro 7\Desktop\npk_90percent"

Write-Host "`n===== MONITORING SERVICE STARTUP =====" -ForegroundColor Cyan
Write-Host "Watch for these messages:`n" -ForegroundColor Cyan

Write-Host "BACKEND (FastAPI):" -ForegroundColor Yellow
Write-Host '  Expected: "Uvicorn running on http://127.0.0.1:8000"' -ForegroundColor Gray
Write-Host "  ETA: 8-10 minutes (models loading...)" -ForegroundColor Gray
Write-Host ""

Write-Host "FRONTEND (Next.js):" -ForegroundColor Yellow
Write-Host '  Expected: "localhost:3000 ready"' -ForegroundColor Gray
Write-Host "  ETA: 1-2 minutes" -ForegroundColor Gray
Write-Host ""

Write-Host "===== PORT STATUS =====" -ForegroundColor Cyan

$checkInterval = 10  # Check every 10 seconds
$maxChecks = 60      # Check for 10 minutes
$checkCount = 0

while ($checkCount -lt $maxChecks) {
    $checkCount++
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    # Check port 3000
    $port3000 = netstat -ano 2>$null | Select-String ":3000\s" | Select-String "LISTENING"
    $status3000 = if ($port3000) { "[ONLINE]" } else { "[STARTING]" }
    
    # Check port 8000
    $port8000 = netstat -ano 2>$null | Select-String ":8000\s" | Select-String "LISTENING"
    $status8000 = if ($port8000) { "[ONLINE]" } else { "[STARTING]" }
    
    Write-Host "[$timestamp] Port 3000 (Frontend) ... $status3000" -ForegroundColor $(if ($port3000) { "Green" } else { "Yellow" })
    Write-Host "[$timestamp] Port 8000 (Backend)  ... $status8000" -ForegroundColor $(if ($port8000) { "Green" } else { "Yellow" })
    
    # If both are online, we're done!
    if ($port3000 -and $port8000) {
        Write-Host "`n===== SUCCESS =====" -ForegroundColor Green
        Write-Host "[OK] Both services are now running!" -ForegroundColor Green
        Write-Host "[OK] Frontend  : http://localhost:3000" -ForegroundColor Green
        Write-Host "[OK] Backend   : http://localhost:8000/docs" -ForegroundColor Green
        break
    }
    
    if ($checkCount -lt $maxChecks) {
        Start-Sleep -Seconds $checkInterval
    }
}

if ($port3000 -and $port8000) {
    Write-Host "`n===== TEST CONNECTIVITY =====" -ForegroundColor Cyan
    Write-Host "Run these commands in PowerShell to verify:" -ForegroundColor Gray
    Write-Host '  curl http://127.0.0.1:3000' -ForegroundColor Gray
    Write-Host '  curl http://127.0.0.1:8000/docs' -ForegroundColor Gray
}
else {
    Write-Host "`n===== WAITING FOR SERVICES =====" -ForegroundColor Yellow
    Write-Host "Services are still starting." -ForegroundColor Yellow
    Write-Host "Check the backend and frontend terminal windows for startup messages." -ForegroundColor Yellow
}
