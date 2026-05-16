@echo off
cd /d "C:\Users\surface pro 7\Desktop\npk_90percent\backend"
echo [Backend] Demarrage uvicorn sur 127.0.0.1:8000
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
echo [Backend] Arrete avec code: %ERRORLEVEL%
pause
