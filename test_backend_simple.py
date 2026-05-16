#!/usr/bin/env python3
import requests, time
print("Test santé backend...")
try:
    r = requests.get("http://127.0.0.1:8000/health", timeout=3)
    print(f"Health: {r.status_code} {r.text}")
except Exception as e:
    print(f"Erreur santé: {e}")

print("\nTest liste modèles...")
try:
    r2 = requests.get("http://127.0.0.1:8000/models/info", timeout=5)
    print(f"Models info: {r2.status_code}")
    if r2.status_code == 200:
        print(r2.text[:300])
except Exception as e:
    print(f"Erreur models: {e}")
