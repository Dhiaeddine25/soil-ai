#!/usr/bin/env python3
"""Test 1: Health et models info"""
import requests
print("=== Test 1: Backend health ===")
r = requests.get("http://127.0.0.1:8000/health", timeout=5)
print(f"Health: {r.status_code} {r.text}")

print("\n=== Test 2: Models info ===")
r2 = requests.get("http://127.0.0.1:8000/models/info", timeout=5)
print(f"Models: {r2.status_code}")
if r2.status_code == 200:
    print(r2.text[:300])
