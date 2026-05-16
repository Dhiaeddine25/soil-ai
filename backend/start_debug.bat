@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Demarrage Backend SoilAI
echo ========================================
cd /d "C:\Users\surface pro 7\Desktop\npk_90percent\backend"
echo PYTHONPATH=%CD%
set PYTHONPATH=%CD%
echo.
echo Lancement uvicorn...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level debug
echo.
echo Backend arrete avec code: %ERRORLEVEL%
pause
