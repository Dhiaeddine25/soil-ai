#!/usr/bin/env python3
import requests, time
for i in range(5):
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        print(f"Attempt {i+1}: {r.status_code} {r.text}")
        break
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
        time.sleep(1)