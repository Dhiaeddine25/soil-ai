#!/usr/bin/env python3
"""Test preflight CORS complet (simulation navigateur)"""
import requests

BASE = "http://localhost:8000"

# Simuler une requête OPTIONS preflight pour GET /parcels
print("Test OPTIONS (preflight) pour GET /parcels")
r = requests.options(f"{BASE}/parcels", headers={
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "authorization, content-type"
}, timeout=5)
print(f"Status: {r.status_code}")
print("Headers CORS retournés:")
for k,v in r.headers.items():
    if 'access' in k.lower() or 'cors' in k.lower():
        print(f"  {k}: {v}")

print()

# Simuler POST /parcels preflight
print("Test OPTIONS pour POST /parcels")
r2 = requests.options(f"{BASE}/parcels", headers={
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization, content-type"
}, timeout=5)
print(f"Status: {r2.status_code}")
for k,v in r2.headers.items():
    if 'access' in k.lower() or 'cors' in k.lower():
        print(f"  {k}: {v}")
