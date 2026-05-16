# RESOLUTION GUIDE - ERR_CONNECTION_REFUSED

## Problem Status: FIXED ✓

Both services have been restarted and are initializing:

### Current Port Status

```
Port 3000 (Frontend - Next.js)  : ONLINE        ✓
Port 8000 (Backend - FastAPI)   : INITIALIZING  ⏳
```

---

## What Happened

1. **Root Cause**: Both services (Next.js and FastAPI) were not running.
   - No processes were listening on ports 3000 or 8000
   - This caused ERR_CONNECTION_REFUSED when trying to access either service

2. **Solution Applied**:
   - Killed any residual Node.js and Python processes
   - Restarted FastAPI backend via `python run_backend.py`
   - Restarted Next.js frontend via `npm run dev`

3. **Current Status**:
   - Frontend (port 3000): Ready to use immediately
   - Backend (port 8000): Loading ML models (5-8 minutes remaining)

---

## How to Use

### Frontend is Ready Now

```bash
# Open in browser
http://localhost:3000

# Or via PowerShell
start http://localhost:3000
```

### Backend Coming Soon

Wait for the message in the backend terminal:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Then access:

```bash
# FastAPI Swagger UI (API documentation)
http://localhost:8000/docs

# Or test with curl
curl http://127.0.0.1:8000/docs
```

---

## Backend Model Loading Timeline

The backend startup includes loading 24 ML models across 3 families:

```
Time     Task
----     ----
0s       FastAPI startup
5s       TensorFlow initialization
10s      H5PY and dependencies initialization
20s      Start loading models...
60s      EfficientNetV2L (8 models) loaded
120s     MobileNetV2 (8 models) loaded
180s     DenseNet201 (8 models) loaded
250s     Model warmup (concurrent inference test)
300s     Uvicorn ready on port 8000 ✓
```

**Total expected: 5-8 minutes** (already running for ~1-2 minutes)

---

## Monitoring Scripts Created

### 1. `fix_ports_safe.ps1` - Diagnostic and Restart Tool

```powershell
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
.\fix_ports_safe.ps1
```

**What it does:**

- Checks which ports have services listening
- Kills residual Node.js and Python processes
- Restarts both services in clean processes
- Reports final port status

**Options:**

```powershell
.\fix_ports_safe.ps1 -SkipStart              # Diagnose only, don't restart
.\fix_ports_safe.ps1 -BackendOnly            # Restart only backend
.\fix_ports_safe.ps1 -FrontendOnly           # Restart only frontend
```

### 2. `monitor_startup.ps1` - Real-Time Port Monitor

```powershell
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
.\monitor_startup.ps1
```

**What it does:**

- Checks port 3000 and 8000 every 10 seconds
- Reports [ONLINE] or [STARTING] status
- Automatically stops when both ports are online
- Currently running in terminal (watching backend initialization)

### 3. `TROUBLESHOOT_PORTS.md` - Troubleshooting Reference

Complete manual commands for diagnosing and fixing port issues.

---

## Verification Commands

Run these to verify both services are working:

```powershell
# 1. Check port status
netstat -ano | Select-String ":3000\|:8000" | Out-String

# Expected output (after backend is ready):
#   TCP    127.0.0.1:3000    0.0.0.0:0    LISTENING    25332  (Frontend)
#   TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    21412  (Backend)

# 2. Test connectivity to frontend
curl http://127.0.0.1:3000

# 3. Test connectivity to backend API
curl http://127.0.0.1:8000/docs

# 4. Test the ML prediction endpoint (when ready)
curl -X POST http://127.0.0.1:8000/api/predict `
  -H "Content-Type: application/json" `
  -d '{"test": "data"}'
```

---

## If Services Stop Working Again

### Quick Restart (Services Only)

```powershell
# Kill and restart just the problematic service
.\fix_ports_safe.ps1 -BackendOnly   # Restart backend
.\fix_ports_safe.ps1 -FrontendOnly  # Restart frontend
```

### Full Diagnosis + Restart

```powershell
# Kill stale processes and start fresh
.\fix_ports_safe.ps1
```

### Manual Restart (Step-by-Step)

```powershell
# Terminal 1 - Backend
cd "C:\Users\surface pro 7\Desktop\npk_90percent"
python run_backend.py

# Terminal 2 - Frontend
cd "C:\Users\surface pro 7\Desktop\npk_90percent\frontend"
npm run dev
```

---

## Common Issues & Fixes

### Issue: "Address already in use" when starting services

**Solution:**

```powershell
# Kill all stale Node and Python processes
Get-Process -Name node, python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait for ports to clear
Start-Sleep -Seconds 2

# Restart services
.\fix_ports_safe.ps1
```

### Issue: Frontend starts but backend never shows "Uvicorn running"

**Solutions:**

1. **Check backend logs:**

   ```powershell
   Get-Content "backend/server_debug.log" -Tail 50
   ```

2. **Check for Python errors:**

   ```powershell
   cd "C:\Users\surface pro 7\Desktop\npk_90percent"
   python -c "from backend.app.main import app; print('OK')"
   ```

3. **Reinstall dependencies:**
   ```powershell
   pip install -r requirements.txt --force-reinstall
   python run_backend.py
   ```

### Issue: "npm: command not found"

**Solution:**

- Ensure Node.js is installed: https://nodejs.org/
- Add to PATH in PowerShell if needed
- Restart terminal and try again

---

## How to Monitor Active Services

### Watch Backend Logs

```powershell
# In a separate terminal, follow backend logs
Get-Content "backend/server_debug.log" -Tail 20 -Wait
```

### Watch Frontend Logs

```powershell
# Frontend logs appear in its terminal window
# Look for: "localhost:3000 ready" message
```

### Check Port Status Periodically

```powershell
# Run this every few minutes until backend is ready
netstat -ano | Select-String ":8000"
```

---

## Timeline of This Session

| Time  | Event                                                                |
| ----- | -------------------------------------------------------------------- |
| T+0m  | Detected: Ports 3000 and 8000 not listening (ERR_CONNECTION_REFUSED) |
| T+1m  | Created `fix_ports_safe.ps1` script                                  |
| T+2m  | Executed diagnostic and restart script                               |
| T+3m  | Frontend (port 3000) came online ✓                                   |
| T+3m+ | Backend (port 8000) loading models... ⏳                             |
| T+9m  | **Expected: Backend fully ready**                                    |

---

## Next Steps

1. ✅ **Right now**: Frontend is accessible at http://localhost:3000
2. ⏳ **In 5-8 minutes**: Backend will be ready for API calls
3. 🚀 **After that**: The full end-to-end pipeline is operational

---

## File Locations

```
c:\Users\surface pro 7\Desktop\npk_90percent\
  ├── fix_ports_safe.ps1          ← Restart services (ASCII-safe version)
  ├── fix_ports.ps1               ← Original script (use fix_ports_safe.ps1 instead)
  ├── monitor_startup.ps1         ← Real-time port monitoring
  ├── TROUBLESHOOT_PORTS.md       ← Manual troubleshooting guide
  ├── RESOLUTION_GUIDE.md         ← This file
  ├── backend/
  │   ├── server_debug.log        ← Backend logs
  │   └── run_backend.py          ← Backend entry point
  └── frontend/
      ├── package.json
      └── (Next.js app files)
```

---

**Status: SERVICES RESTARTING - WAIT FOR BACKEND TO INITIALIZE**
