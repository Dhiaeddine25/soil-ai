# ============================================================================
# FIX_PORTS.PS1 - Diagnostiquer et corriger les connexions ERR_CONNECTION_REFUSED
# ============================================================================

param(
    [switch]$SkipStart = $false,
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
)

$ErrorActionPreference = "Continue"
$ROOT = "c:\Users\surface pro 7\Desktop\npk_90percent"
$FRONTEND = "$ROOT\frontend"
$BACKEND = "$ROOT"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ETAPE 1: Verifier l'etat des ports" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Check-Port {
    param([int]$Port)
    $netstat = netstat -ano 2>$null
    $match = $netstat | Select-String ":$Port\s" | Select-String "LISTENING"
    
    if ($match) {
        $line = $match[0].ToString()
        $pid = [regex]::Match($line, '(\d+)$').Groups[1].Value
        Write-Host "[OK] Port $Port : EN ECOUTE (PID: $pid)" -ForegroundColor Green
        return $pid
    }
    else {
        Write-Host "[FAIL] Port $Port : AUCUN SERVICE (ERR_CONNECTION_REFUSED)" -ForegroundColor Red
        return $null
    }
}

$pid3000 = Check-Port 3000
$pid8000 = Check-Port 8000

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ETAPE 2: Tuer les processus residuels" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Kill-Process-Safe {
    param([int]$ProcessId, [string]$Name)
    if ($ProcessId) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            Write-Host "[OK] Processus $Name (PID: $ProcessId) tue avec succes" -ForegroundColor Green
        }
        catch {
            Write-Host "[WARN] Impossible de tuer le processus $Name (PID: $ProcessId)" -ForegroundColor Yellow
        }
    }
}

if ($pid3000) { Kill-Process-Safe $pid3000 "Frontend (port 3000)" }
if ($pid8000) { Kill-Process-Safe $pid8000 "Backend (port 8000)" }

Write-Host "`nRecherche des processus Node.js et Python residuels..." -ForegroundColor Yellow
$nodeProcs = Get-Process -Name node -ErrorAction SilentlyContinue
$pythonProcs = Get-Process -Name python -ErrorAction SilentlyContinue

if ($nodeProcs) {
    Write-Host "Tuer les processus Node.js residuels..." -ForegroundColor Yellow
    $nodeProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Processus Node.js tues" -ForegroundColor Green
}

if ($pythonProcs) {
    Write-Host "Tuer les processus Python residuels..." -ForegroundColor Yellow
    $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Processus Python tues" -ForegroundColor Green
}

Write-Host "`nAttendre 2 secondes que les ports se liberent..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ETAPE 3: Verifier l'etat des ports (apres nettoyage)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$pid3000_after = Check-Port 3000
$pid8000_after = Check-Port 8000

if ($SkipStart) {
    Write-Host "`n[OK] Diagnostic complet. Services non redemarres (SkipStart)." -ForegroundColor Cyan
    exit 0
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ETAPE 4: Redemarrer les services" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$pythonExe = "$ROOT\.venv\Scripts\python.exe"

if (!(Test-Path $pythonExe)) {
    Write-Host "[FAIL] Python n'existe pas a $pythonExe" -ForegroundColor Red
    Write-Host "   Verifiez que le venv est active correctement." -ForegroundColor Red
    exit 1
}

$npmCheck = Get-Command npm -ErrorAction SilentlyContinue
if (!$npmCheck) {
    Write-Host "[FAIL] npm n'est pas disponible" -ForegroundColor Red
    Write-Host "   Verifiez que Node.js est installe et dans le PATH." -ForegroundColor Red
    exit 1
}

if (!$FrontendOnly) {
    Write-Host "`n--> Demarrage du BACKEND (FastAPI sur port 8000)..." -ForegroundColor Cyan
    Write-Host "    Commande: python run_backend.py" -ForegroundColor Gray
    Write-Host "    (Cela prendra 8-10 minutes pour charger les modeles ML)" -ForegroundColor Gray
    
    $backendProc = Start-Process -FilePath $pythonExe `
        -ArgumentList "run_backend.py" `
        -WorkingDirectory $BACKEND `
        -NoNewWindow -PassThru
    
    Write-Host "[OK] Backend lance (PID: $($backendProc.Id))" -ForegroundColor Green
}

if (!$BackendOnly) {
    Write-Host "`n--> Demarrage du FRONTEND (Next.js sur port 3000)..." -ForegroundColor Cyan
    Write-Host "    Commande: npm run dev" -ForegroundColor Gray
    
    $frontendProc = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit -Command `"cd '$FRONTEND'; npm run dev`"" `
        -WorkingDirectory $FRONTEND `
        -PassThru
    
    Write-Host "[OK] Frontend lance (PID: $($frontendProc.Id))" -ForegroundColor Green
    Write-Host "    Une nouvelle fenetre PowerShell a ete ouverte pour le frontend." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ETAPE 5: Instructions d'attente" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host @"
1. BACKEND (FastAPI):
   - Attendez le message: "Uvicorn running on http://127.0.0.1:8000"
   - Cela prendra ~8-10 minutes (chargement de tous les modeles ML)
   - Verifiez ensuite: http://localhost:8000/docs

2. FRONTEND (Next.js):
   - Attendez le message: "localhost:3000 ready"
   - Une fois affiche, testez: http://localhost:3000

3. VERIFICATION:
   Executez dans un nouveau terminal PowerShell:
   
   netstat -ano | Select-String ":3000" | Out-String
   netstat -ano | Select-String ":8000" | Out-String
   
   Vous devriez voir deux lignes "LISTENING".

"@ -ForegroundColor Yellow

Write-Host "[OK] Services en cours de demarrage..." -ForegroundColor Green
