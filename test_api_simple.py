#!/usr/bin/env python3
"""Test API SoilAI - Backend FastAPI"""
import requests
import sys

BASE = "http://localhost:8000"
tests = []

def test(path, method="get", expected=200):
    url = f"{BASE}{path}"
    try:
        r = requests.get(url, timeout=5) if method=="get" else requests.post(url, json=data, timeout=5)
        status = "OK" if r.status_code == expected else "UNEXPECTED"
        tests.append((path, r.status_code, expected, status))
        print(f"  {method.upper()} {path} -> {r.status_code} (expected {expected}) [{status}]")
        if r.status_code == expected:
            return True
        print(f"    Body: {r.text[:200]}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  {method.upper()} {path} -> CONNECTION REFUSED")
        tests.append((path, "CONN", expected, "FAIL"))
        return False
    except Exception as e:
        print(f"  {method.upper()} {path} -> ERROR: {str(e)[:100]}")
        tests.append((path, "ERR", expected, "FAIL"))
        return False

print("Testing SoilAI Backend API")
print("-" * 50)

# Routes publiques
print("\nPublic routes:")
test("/", expected=200)
test("/health", expected=200)
test("/docs", expected=200)
test("/openapi.json", expected=200)

# Routes protégées (doivent retourner 401 sans token)
print("\nProtected routes (should return 401):")
test("/parcels", expected=401)
test("/history/users/test", expected=401)
test("/predict", expected=401)

# Résumé
print("\n" + "-" * 50)
passed = sum(1 for _,code,exp,_ in tests if code == exp)
total = len(tests)
print(f"Result: {passed}/{total} tests passed")
if passed == total:
    print("SUCCESS: API is responding correctly")
    sys.exit(0)
else:
    print("ISSUES DETECTED - check failures above")
    sys.exit(1)
