#!/usr/bin/env python3
import requests, sys
for attempt in range(5):
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        print(f"Attempt {attempt+1}: {r.status_code} {r.text}")
        if r.status_code == 200:
            print("SUCCESS - Backend is UP")
            sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt+1}: {e}")
        import time; time.sleep(1)
print("FAILED - Backend not responding")
sys.exit(1)
