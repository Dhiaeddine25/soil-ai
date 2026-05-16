@echo off
setlocal enabledelayedexpansion
cd /d "C:\Users\surface pro 7\Desktop\npk_90percent\backend"
set PYTHONPATH=C:\Users\surface pro 7\Desktop\npk_90percent\backend
python "C:\Users\surface pro 7\Desktop\npk_90percent\test_complete_pipeline.py"
echo exit code: %ERRORLEVEL%