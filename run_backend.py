#!/usr/bin/env python3
"""Lanceur backend avec logs"""
import logging
import sys
import os

# Ajout du backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration logging
log_file = 'C:/Users/surface pro 7/Desktop/npk_90percent/backend/server_debug.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode='w'),
    ],
)

import uvicorn
from app.main import app

print("=== Démarrage serveur FastAPI ===")
print(f"Logs seront écrits dans: {log_file}")
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8000,
    log_level="debug",
    reload=False,
)
