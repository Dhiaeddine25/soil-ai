#!/usr/bin/env python3
"""Test imports backend pas à pas"""
import sys
import os
backend_root = r"C:\Users\surface pro 7\Desktop\npk_90percent\backend"
sys.path.insert(0, backend_root)

print("=== Test 1: Import config ===")
try:
    from app.core.config import get_settings
    settings = get_settings()
    print(f"Settings OK: {settings.project_name}")
except Exception as e:
    print(f"ERREUR config: {e}")
    sys.exit(1)

print("\n=== Test 2: Import DB ===")
try:
    from app.db.session import SessionLocal
    print("DB session OK")
except Exception as e:
    print(f"ERREUR DB: {e}")
    sys.exit(1)

print("\n=== Test 3: Import modèles ===")
try:
    from app.models.analysis import Analysis
    from app.models.parcel import Parcel
    from app.models.user import User
    print("Modèles OK")
except Exception as e:
    print(f"ERREUR modèles: {e}")
    sys.exit(1)

print("\n=== Test 4: Import services ===")
try:
    from app.services.ml_prediction_service import MLPredictionService
    print("MLPredictionService importé")
except Exception as e:
    print(f"ERREUR ML service: {e}")
    sys.exit(1)

print("\n=== Test 5: Créer instance MLPredictionService ===")
try:
    service = MLPredictionService(settings)
    print("Instance créée")
except Exception as e:
    print(f"ERREUR création instance: {e}")
    sys.exit(1)

print("\n=== Test 6: Charger modèles (rapide, sans prédiction) ===")
try:
    models = service.load_models()
    print(f"Modèles chargés: {[(k, len(v)) for k,v in models.items()]}")
except Exception as e:
    print(f"ERREUR chargement modèles: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\n=== Test 7: Import FastAPI app ===")
try:
    from app.main import app
    print("FastAPI app importé OK")
except Exception as e:
    print(f"ERREUR import app: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\n=== Tous les tests PASSED ===")
