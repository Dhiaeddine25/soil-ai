# Commandes Manuelles pour Corriger ERR_CONNECTION_REFUSED

## Diagnostic Rapide

```powershell
# Vérifier si quelque chose écoute sur les ports 3000 et 8000
netstat -ano | Select-String ":3000" | Out-String
netstat -ano | Select-String ":8000" | Out-String

# Si aucune ligne → rien ne tourne (ERR_CONNECTION_REFUSED expliqué)
# Si une ligne "LISTENING" → le service tourne mais peut-être inaccessible (pare-feu?)
```

## Option 1 : Utiliser le Script Automatisé (RECOMMANDÉ)

```powershell
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
.\fix_ports.ps1
```

## Option 2 : Commandes Manuelles Étape par Étape

### A. Tuer les Processus Résiduels

```powershell
# Tuer tous les Node.js
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force

# Tuer tous les Python
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Attendre la libération des ports
Start-Sleep -Seconds 2
```

### B. Démarrer le Backend (FastAPI + Uvicorn)

**Terminal 1 - Backend (prend 8-10 minutes):**

```powershell
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
python run_backend.py
```

✅ Attendez le message:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

⏳ **Temps d'attente estimé:**

- TensorFlow initialization: ~30s
- Chargement EfficientNetV2L (8 modèles): ~60s
- Chargement MobileNetV2 (8 modèles): ~60s
- Chargement DenseNet201 (8 modèles): ~60s
- Warmup des modèles: ~250s
- **Total: ~8-10 minutes**

### C. Démarrer le Frontend (Next.js)

**Terminal 2 - Frontend (prend 1-2 minutes):**

```powershell
cd "C:\Users\surface pro 7\Desktop\npk_90percent\frontend"
npm run dev
```

✅ Attendez le message:

```
  ▲ Next.js 14.x.x
  - Local: http://localhost:3000
```

## Vérification de la Connectivité

### Après que les deux services disent "ready":

```powershell
# 1. Vérifier que les ports écoutent
netstat -ano | Select-String ":3000" | Out-String
netstat -ano | Select-String ":8000" | Out-String

# Résultat attendu: deux lignes avec "LISTENING"

# 2. Tester avec curl (PowerShell)
curl http://127.0.0.1:3000
curl http://127.0.0.1:8000/docs

# 3. Tester dans le navigateur
# - Frontend: http://localhost:3000
# - Backend Docs: http://localhost:8000/docs
```

## Dépannage Avancé

### Si le Backend Ne Démarre Pas (erreur immédiate)

```powershell
# 1. Vérifier le venv
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
."\.venv\Scripts\Activate.ps1"  # Activer le venv

# 2. Vérifier l'installation des dépendances
pip list | Select-String "fastapi\|uvicorn\|tensorflow"

# 3. Si des packages manquent:
pip install -r requirements.txt

# 4. Relancer le backend
python run_backend.py
```

### Si le Frontend Ne Démarre Pas

```powershell
# 1. Vérifier Node.js et npm
node --version
npm --version

# 2. Réinstaller les dépendances du frontend
cd "C:\Users\surface pro 7\Desktop\npk_90percent\frontend"
rm -r node_modules package-lock.json
npm install

# 3. Relancer
npm run dev
```

### Si le Pare-Feu Windows Bloque (rare pour localhost)

```powershell
# Créer une règle de pare-feu pour Node.js
New-NetFirewallRule -DisplayName "Allow Node.js 3000" `
    -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3000

# Créer une règle pour Python/Uvicorn
New-NetFirewallRule -DisplayName "Allow Python 8000" `
    -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000
```

## Cas Spéciaux

### Redémarrer UNIQUEMENT le Backend

```powershell
.\fix_ports.ps1 -BackendOnly
```

### Redémarrer UNIQUEMENT le Frontend

```powershell
.\fix_ports.ps1 -FrontendOnly
```

### Seulement Diagnostiquer (sans redémarrer)

```powershell
.\fix_ports.ps1 -SkipStart
```

---

**Besoin d'aide?** Exécutez la commande de diagnostic et partagez la sortie.
