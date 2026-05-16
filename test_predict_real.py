#!/usr/bin/env python3
"""Test analyse avec endpoint /predict (real)"""
import requests
import os
import time

BASE = "http://127.0.0.1:8000"

# 1. Register
print("1. Register...")
r = requests.post(f"{BASE}/auth/register", json={
    "email": "6566676869707172737475767778798081828384858687888990979899100101102103104105106107108109110111112113114115116117118119120121122@example.com",
    "password": "test12345678",
    "full_name": "Analyze Test"
}, timeout=10)
print(f"   Status: {r.status_code}")
if r.status_code in (200,201):
    token = r.json()['access_token']
    user_id = r.json()['user']['id'] if 'user' in r.json() else 'unknown'
    print(f"   Token OK, user_id: {user_id}")
else:
    print(f"   Erreur: {r.text[:200]}")
    exit(1)

# 2. Trouver image
img_path = r"C:\Users\surface pro 7\Desktop\npk_90percent\backend\data\analysis_images\0108b5f3-fffa-416c-8bbb-f27bc517dd11.webp"
if not os.path.exists(img_path):
    print(f"   Image non trouvée: {img_path}")
    exit(1)

print(f"\n2. Test POST /predict (real ML) avec image...")
print(f"   Image: {os.path.basename(img_path)}")
print(f"   Début: {time.strftime('%H:%M:%S')}")

start = time.time()
try:
    with open(img_path, 'rb') as f:
        files = {'image': (os.path.basename(img_path), f, 'image/webp')}
        data = {'parcel_id': 'test-parcel-001'}
        headers = {'Authorization': f'Bearer {token}'}
        r2 = requests.post(f"{BASE}/predict", files=files, data=data, headers=headers, timeout=60)
    elapsed = time.time() - start
    print(f"   Temps: {elapsed:.2f}s")
    print(f"   Status: {r2.status_code}")
    if r2.status_code == 200:
        resp = r2.json()
        print(f"   analysis_id: {resp.get('analysis_id')}")
        print(f"   status: {resp.get('status')}")
        print(f"   score: {resp.get('score')}")
        print(f"   confidence: {resp.get('confidence')}")
        print(f"   prediction: {resp.get('prediction')}")
        print("   SUCCESS!")
    else:
        print(f"   Erreur: {r2.text[:500]}")
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"   TIMEOUT après {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"   Erreur après {elapsed:.2f}s: {str(e)[:300]}")
