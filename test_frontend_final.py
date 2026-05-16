#!/usr/bin/env python3
import requests, time
for i in range(3):
    try:
        r = requests.get("http://127.0.0.1:3000", timeout=5)
        print(f"Try {i+1}: {r.status_code} - {len(r.content)} bytes")
        if r.status_code == 200:
            print("FRONTEND OK!")
            print(r.text[:200])
            break
    except Exception as e:
        print(f"Try {i+1}: {e}")
        time.sleep(1)
