# Commands to run the servers

## Backend (Terminal 1)
```bash
cd C:\Users\surface pro 7\Desktop\npk_90percent
python run_backend.py
```

## Frontend (Terminal 2)
```bash
cd C:\Users\surface pro 7\Desktop\npk_90percent\frontend
npm run dev
```

## After startup (wait for models to load ~2-3 minutes)
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Kill processes if needed
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```