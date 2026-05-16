#!/usr/bin/env python3
"""Test direct: GET /parcels avec token via request (simule navigateur)"""
import requests

BASE = "http://localhost:8000"

# 1. Register
r = requests.post(f"{BASE}/auth/register", json={
    "email": "frontend_test@example.com",
    "password": "frontend12345",
    "full_name": "Frontend Test"
}, timeout=5)
print(f"Register: {r.status_code}")
if r.status_code in (200,201):
    token = r.json()['access_token']
    print(f"Token: {token[:30]}...")

    # 2. GET /parcels AVEC Authorization header
    print("\nGET /parcels avec Bearer token...")
    r2 = requests.get(f"{BASE}/parcels", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, timeout=5)
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text}")

    # 3. POST /parcels AVEC token
    print("\nPOST /parcels avec token...")
    parcel = {
        "name": "TestFrontendParcel",
        "location": "Test location",
        "region": "Test",
        "area_ha": 1.0,
        "crop": "Test",
        "notes": "Test",
        "latitude": 0.0,
        "longitude": 0.0
    }
    r3 = requests.post(f"{BASE}/parcels", json=parcel, headers={
        "Authorization": f"Bearer {token}"
    }, timeout=5)
    print(f"Status: {r3.status_code}")
    print(f"Response: {r3.text[:300]}")

else:
    print(f"Register failed: {r.text}")
