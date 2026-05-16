#!/usr/bin/env python3
"""Test temps réel de l'endpoint /predict avec une image"""
import requests
import time
import os

BASE = "http://127.0.0.1:8000"

# 1. Register pour obtenir token
print("1. Register...")
r = requests.post(f"{BASE}/auth/register", json={
    "email": "timeout_test@example.com",
    "password": "test12345678",
    "full_name": "Timeout Test"
}, timeout=10)
print(f"   Status: {r.status_code}")
if r.status_code in (200,201):
    token = r.json()['access_token']
    print(f"   Token ok")
else:
    print(f"   Error: {r.text[:200]}")
    exit(1)

# 2. Trouver une image de test
test_images = [
    "C:/Users/surface pro 7/Desktop/npk_90percent/backend/data/analysis_images/0108b5f3-fffa-416c-8bbb-f27bc517dd11.webp",
    "C:/Users/surface pro 7/Desktop/npk_90percent/backend/data/analysis_images/237ac136-5f50-4bb6-8bf0-03a04437d7b5.jpg",
]
test_image = next((p for p in test_images if os.path.exists(p)), None)
if not test_image:
    print("   Erreur: pas d'image de test trouvée")
    exit(1)

print(f"2. Test PREDICT avec image: {os.path.basename(test_image)}")
print("   Début du test à:", time.strftime("%H:%M:%S"))

start = time.time()
try:
    with open(test_image, 'rb') as f:
        files = {'image': (os.path.basename(test_image), f, 'image/jpeg')}
        data = {'parcel_id': 'test-parcel-123'}
        headers = {'Authorization': f'Bearer {token}'}
        r2 = requests.post(f"{BASE}/predict", files=files, data=data, headers=headers, timeout=60)
    elapsed = time.time() - start
    print(f"   Temps écoulé: {elapsed:.2f}s")
    print(f"   Status: {r2.status_code}")
    if r2.status_code == 200:
        resp = r2.json()
        print(f"   Analysis ID: {resp.get('analysis_id')}")
        print(f"   Status: {resp.get('status')}")
        print(f"   Score: {resp.get('score')}")
        print(f"   Confidence: {resp.get('confidence')}")
        print("   SUCCESS!")
    else:
        print(f"   Error: {r2.text[:500]}")
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"   TIMEOUT après {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"   Erreur après {elapsed:.2f}s: {e}")

print("\n3. Vérifions que l'analyse est dans l'historique...")
r3 = requests.get(f"{BASE}/history/users/{r.json()['id'] if r.status_code in (200,201) else 'unknown'}", headers={'Authorization': f'Bearer {token}'}, timeout=10)
print(f"   Status historique: {r3.status_code}")
