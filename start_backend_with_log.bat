@echo off
cd /d "C:\Users\surface pro 7\Desktop\npk_90percent"
echo Demarrage backend avec logs > "C:\Users\surface pro 7\Desktop\npk_90percent\backend\runtime_full.log"
python debug_backend.py 2>&1 | tee "C:\Users\surface pro 7\Desktop\npk_90percent\backend\runtime_full.log"
echo Backend arrete
pause
