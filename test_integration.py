#!/usr/bin/env python3
import requests
BASE = "http://127.0.0.1:8000"
r = requests.get(f"{BASE}/health", timeout=3)
print(f"Backend health: {r.status_code} {r.text}")
r2 = requests.post(f"{BASE}/auth/register", json={"email":"webtest@ex.com","password":"web123456","full_name":"Web Test"}, timeout=3)
print(f"Register: {r2.status_code}")
if r2.status_code == 200:
    token = r2.json()['access_token']
    r3 = requests.get(f"{BASE}/parcels", headers={"Authorization": f"Bearer {token}"}, timeout=3)
    print(f"Parcels: {r3.status_code}")
    r4 = requests.post(f"{BASE}/parcels", json={"name":"Web Parcel","area_ha":1.0}, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    print(f"Create: {r4.status_code} {r4.text[:150]}")
else:
    print(f"Register error: {r2.text[:200]}")
