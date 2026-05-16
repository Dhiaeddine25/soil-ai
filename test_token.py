#!/usr/bin/env python3
import requests
BASE = "http://localhost:8000"

# 1. Register
r = requests.post(f"{BASE}/auth/register", json={
    "email": "ps_test@example.com",
    "password": "ps_test12345",
    "full_name": "PS Test"
}, timeout=5)
token = r.json()['access_token'] if r.status_code in (200,201) else None
print(f"Register: {r.status_code}, token: {token[:20] if token else 'none'}")

# 2. GET /parcels avec header Authorization (comme navigateur)
if token:
    r2 = requests.get(f"{BASE}/parcels", headers={
        "Authorization": f"Bearer {token}"
    }, timeout=5)
    print(f"GET /parcels: {r2.status_code}, body: {r2.text[:200]}")
