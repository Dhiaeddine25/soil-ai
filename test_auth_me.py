#!/usr/bin/env python3
"""Test auth/me avec token"""
import requests

BASE = "http://localhost:8000"

# Register pour obtenir un token
print("Register...")
r = requests.post(f"{BASE}/auth/register", json={
    "email": "test_auth@example.com",
    "password": "test12345678",
    "full_name": "Test Auth"
}, timeout=5)
print(f"Register status: {r.status_code}")
if r.status_code in (200,201):
    token = r.json()['access_token']
    print(f"Token: {token[:30]}...")

    # Test /auth/me
    print("\nTest GET /auth/me avec token...")
    r2 = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(f"Status: {r2.status_code}")
    print(f"Body: {r2.text}")

    # Test /parcels avec même token
    print("\nTest GET /parcels avec même token...")
    r3 = requests.get(f"{BASE}/parcels", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(f"Status: {r3.status_code}")
    print(f"Body: {r3.text[:200]}")
else:
    print(f"Register failed: {r.text}")
