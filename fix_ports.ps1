# ============================================================================
# FIX_PORTS.PS1 - Diagnostiquer et corriger les connexions ERR_CONNECTION_REFUSED
# ============================================================================
# Objectif: Tuer les processus résiduels et relancer les services proprement
# Utilisation: .\fix_ports.ps1 (dans PowerShell ISE ou Terminal)
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
Write-Host "  ÉTAPE 1: Vérifier l'état des ports" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Check-Port {
    param([int]$Port)
    $netstat = netstat -ano 2>$null
    $match = $netstat | Select-String ":$Port\s" | Select-String "LISTENING"
    
    if ($match) {
        $line = $match[0].ToString()
        $pid = [regex]::Match($line, '(\d+)$').Groups[1].Value
        Write-Host "✓ Port $Port: EN ÉCOUTE (PID: $pid)" -ForegroundColor Green
        return $pid
    }
    else {
        Write-Host "✗ Port $Port: AUCUN SERVICE (ERR_CONNECTION_REFUSED)" -ForegroundColor Red
        return $null
    }
}

$pid3000 = Check-Port 3000
$pid8000 = Check-Port 8000

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ÉTAPE 2: Tuer les processus résiduels" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Kill-Process-Safe {
    param([int]$ProcessId, [string]$Name)
    if ($ProcessId) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            Write-Host "✓ Processus $Name (PID: $ProcessId) tué avec succès" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ Impossible de tuer le processus $Name (PID: $ProcessId): $_" -ForegroundColor Yellow
        }
    }
}

if ($pid3000) { Kill-Process-Safe $pid3000 "Frontend (port 3000)" }
if ($pid8000) { Kill-Process-Safe $pid8000 "Backend (port 8000)" }

# Tuer tous les node.exe et python.exe résiduels
Write-Host "`nRecherche des processus Node.js et Python résiduels..." -ForegroundColor Yellow
$nodeProcs = Get-Process -Name node -ErrorAction SilentlyContinue
$pythonProcs = Get-Process -Name python -ErrorAction SilentlyContinue

if ($nodeProcs) {
    Write-Host "Tuer les processus Node.js résiduels..." -ForegroundColor Yellow
    $nodeProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Processus Node.js tués" -ForegroundColor Green
}

if ($pythonProcs) {
    Write-Host "Tuer les processus Python résiduels..." -ForegroundColor Yellow
    $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Processus Python tués" -ForegroundColor Green
}

Write-Host "`nAttendre 2 secondes que les ports se libèrent..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ÉTAPE 3: Vérifier l'état des ports (après nettoyage)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$pid3000_after = Check-Port 3000
$pid8000_after = Check-Port 8000

if ($SkipStart) {
    Write-Host "`n✓ Diagnostic complet. (--SkipStart utilisé: services non redémarrés)" -ForegroundColor Cyan
    exit 0
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ÉTAPE 4: Redémarrer les services" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Variables de services
$pythonExe = "$ROOT\.venv\Scripts\python.exe"
$nvmOrNpm = "npm"

# Vérifier que les outils existent
if (!(Test-Path $pythonExe)) {
    Write-Host "✗ ERREUR: Python n'existe pas à $pythonExe" -ForegroundColor Red
    Write-Host "   Vérifiez que le venv est activé correctement." -ForegroundColor Red
    exit 1
}

$npmCheck = Get-Command npm -ErrorAction SilentlyContinue
if (!$npmCheck) {
    Write-Host "✗ ERREUR: npm n'est pas disponible" -ForegroundColor Red
    Write-Host "   Vérifiez que Node.js est installé et dans le PATH." -ForegroundColor Red
    exit 1
}

# Redémarrer les services

if (!$FrontendOnly) {
    Write-Host "`n→ Démarrage du BACKEND (FastAPI sur port 8000)..." -ForegroundColor Cyan
    Write-Host "   Commande: python run_backend.py" -ForegroundColor Gray
    Write-Host "   (Cela prendra 8-10 minutes pour charger les modèles ML)" -ForegroundColor Gray
    
    $backendProc = Start-Process -FilePath $pythonExe `
        -ArgumentList "run_backend.py" `
        -WorkingDirectory $BACKEND `
        -NoNewWindow -PassThru
    
    Write-Host "✓ Backend lancé (PID: $($backendProc.Id))" -ForegroundColor Green
    Write-Host "  Rendez-vous dans le terminal PowerShell original pour suivre la progression..." -ForegroundColor Yellow
}

if (!$BackendOnly) {
    Write-Host "`n→ Démarrage du FRONTEND (Next.js sur port 3000)..." -ForegroundColor Cyan
    Write-Host "   Commande: npm run dev" -ForegroundColor Gray
    
    $frontendProc = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit -Command `"cd '$FRONTEND'; npm run dev`"" `
        -WorkingDirectory $FRONTEND `
        -PassThru
    
    Write-Host "✓ Frontend lancé (PID: $($frontendProc.Id))" -ForegroundColor Green
    Write-Host "  Une nouvelle fenêtre PowerShell a été ouverte pour le frontend." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ÉTAPE 5: Instructions d'attente" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host @"
1. BACKEND (FastAPI):
   - Attendez le message: "Uvicorn running on http://127.0.0.1:8000"
   - Cela prendra ~8-10 minutes (chargement de tous les modèles ML)
   - Vérifiez ensuite: http://localhost:8000/docs

2. FRONTEND (Next.js):
   - Attendez le message: "localhost:3000 ready"
   - Une fois affiché, testez: http://localhost:3000

3. VÉRIFICATION:
   Exécutez dans un nouveau terminal PowerShell:
   
   netstat -ano | Select-String ":3000" | Out-String
   netstat -ano | Select-String ":8000" | Out-String
   
   Vous devriez voir deux lignes "LISTENING".

"@ -ForegroundColor Yellow

Write-Host "✓ Services en cours de démarrage..." -ForegroundColor Green
