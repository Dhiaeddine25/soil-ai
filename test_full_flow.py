#!/usr/bin/env python3
"""Test registration et création parcelle via API complète"""
import requests
import json
import sys

BASE = "http://localhost:8000"

print("="*60)
print("TEST INSCRIPTION + CREATION PARCELLE")
print("="*60)

# 1. Register
print("\n1. Tentative d'inscription...")
register_data = {
    "email": "test_parcels@example.com",
    "password": "testpassword123",
    "full_name": "Test Parcels User"
}
try:
    r = requests.post(f"{BASE}/auth/register", json=register_data, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code in (200, 201):
        token = r.json().get('access_token')
        print(f"   Token: {token[:20]}...")
    else:
        print(f"   Error: {r.text[:200]}")
        token = None
except Exception as e:
    print(f"   Exception: {e}")
    token = None

# 2. Login (si register a échoué car user existe)
if not token:
    print("\n2. Tentative de login...")
    login_data = {"email": "test_parcels@example.com", "password": "testpassword123"}
    try:
        r = requests.post(f"{BASE}/auth/login", json=login_data, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            token = r.json().get('access_token')
            print(f"   Token: {token[:20]}...")
        else:
            print(f"   Error: {r.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")
        token = None

# 3. GET /parcels (doit fonctionner avec token)
if token:
    print("\n3. GET /parcels avec token...")
    try:
        r = requests.get(f"{BASE}/parcels", headers={"Authorization": f"Bearer {token}"}, timeout=5)
        print(f"   Status: {r.status_code}")
        print(f"   Body: {r.text[:300]}")
    except Exception as e:
        print(f"   Exception: {e}")

    # 4. POST /parcels (création)
    print("\n4. POST /parcels avec token...")
    parcel_data = {
        "name": "Parcelle Test API",
        "location": "Souss-Massa, Morocco",
        "region": "Souss-Massa",
        "area_ha": 2.5,
        "crop": "Tomate",
        "notes": "Test automatique",
        "latitude": 30.034,
        "longitude": -9.553
    }
    try:
        r = requests.post(f"{BASE}/parcels", json=parcel_data, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        print(f"   Status: {r.status_code}")
        print(f"   Body: {r.text[:500]}")
        if r.status_code in (200, 201):
            print("   ✓ PARCELLE CRÉÉE AVEC SUCCÈS!")
        else:
            print(f"   ✗ Erreur création")
    except Exception as e:
        print(f"   Exception: {e}")

print("\n" + "="*60)
