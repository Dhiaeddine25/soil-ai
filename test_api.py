#!/usr/bin/env python3
"""Test complet de l'API SoilAI"""

import requests
import json
import sys

BASE = "http://localhost:8000"

def test_endpoint(path, method="get", expected=200, auth=None, data=None):
    url = f"{BASE}{path}"
    try:
        if method.lower() == "get":
            r = requests.get(url, timeout=5)
        elif method.lower() == "post":
            r = requests.post(url, json=data, timeout=5)
        else:
            print(f"  Méthode non supportée: {method}")
            return False
        
        print(f"  {method.upper()} {path} → {r.status_code} (attendu {expected})")
        if r.status_code != expected:
            print(f"    ⚠ Statut inattendu!")
            print(f"    Body: {r.text[:200]}")
        else:
            print(f"    ✓ OK")
        return r.status_code == expected
    except requests.exceptions.ConnectionError:
        print(f"  ✗ {method.upper()} {path} → CONNECTION REFUSED")
        return False
    except Exception as e:
        print(f"  ✗ {method.upper()} {path} → ERREUR: {e}")
        return False

print("="*60)
print("TEST API SOILAI - Backend FastAPI")
print("="*60)

all_ok = True

# 1. Test racine
print("\n[1] Routes publiques")
all_ok &= test_endpoint("/", expected=200)

# 2. Health
all_ok &= test_endpoint("/health", expected=200)

# 3. Documentation
all_ok &= test_endpoint("/docs", expected=200)

# 4. Parcels sans auth → doit retourner 401
print("\n[2] Routes protégées (doivent retourner 401 sans token)")
all_ok &= test_endpoint("/parcels", expected=401)

# 5. Models info (probablement public)
all_ok &= test_endpoint("/models/info", expected=200)

# 6. History (protected)
all_ok &= test_endpoint("/history/users/test123", expected=401)

print("\n" + "="*60)
if all_ok:
    print("✓ Tous les tests de connexion sont OK!")
    print("Remarque: Les endpoints 401 sont attendus sans auth.")
else:
    print("✗ Certains tests ont échoué - vérifiez le backend")
print("="*60)
