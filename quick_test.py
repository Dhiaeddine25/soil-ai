#!/usr/bin/env python3
import requests, time
print("Test backend API...")
tests = [
    ("/health", "GET"),
    ("/models/info", "GET"),
]
for path, method in tests:
    try:
        r = requests.get(f"http://127.0.0.1:8000{path}", timeout=5)
        print(f"{method} {path}: {r.status_code}")
    except Exception as e:
        print(f"{method} {path}: ERREUR - {e}")
