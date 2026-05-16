#!/usr/bin/env python3
"""Lance le backend avec logs dans fichier et stdout"""
import logging
import sys
import os

# Config path
backend_root = r"C:\Users\surface pro 7\Desktop\npk_90percent\backend"
sys.path.insert(0, backend_root)

log_path = r"C:\Users\surface pro 7\Desktop\npk_90percent\backend\uvicorn_debug.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, mode='w'),
    ],
)

import uvicorn
from app.main import app

print(f"Backend demarre depuis: {backend_root}")
print(f"Logs: {log_path}")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=False,
    )
