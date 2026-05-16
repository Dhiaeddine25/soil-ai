#!/usr/bin/env python3
import requests
BASE = "http://127.0.0.1:8000"

r = requests.get(f"{BASE}/health", timeout=5)
print(f"Health: {r.status_code} {r.text}")

r2 = requests.post(f"{BASE}/auth/register", json={
    "email": "test127@example.com",
    "password": "test12345678",
    "full_name": "Test 127"
}, timeout=5)
print(f"Register: {r2.status_code}")

if r2.status_code in (200,201):
    token = r2.json()['access_token']
    r3 = requests.get(f"{BASE}/parcels", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(f"Parcels: {r3.status_code} {r3.text[:100]}")
    r4 = requests.post(f"{BASE}/parcels", json={
        "name": "Parcelle 127",
        "area_ha": 1.0
    }, headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(f"Create: {r4.status_code} {r4.text[:200]}")
