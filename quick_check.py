#!/usr/bin/env python3
import requests, sys, time
for i in range(10):
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        print(f"Health: {r.status_code} {r.text}")
        if r.status_code == 200:
            print("BACKEND OK")
            sys.exit(0)
    except Exception as e:
        print(f"Essai {i+1}: {e}")
        time.sleep(1)
print("BACKEND NON DISPONIBLE")
sys.exit(1)
