#!/usr/bin/env python3
import requests, time
for i in range(5):
    try:
        r = requests.get("http://127.0.0.1:3000", timeout=5)
        print(f"Attempt {i+1}: {r.status_code} - length {len(r.content)}")
        if r.status_code == 200:
            print("✓ FRONTEND IS RESPONDING!")
            print(f"First 200 chars: {r.text[:200]}")
            break
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
        time.sleep(1)
else:
    print("✗ FRONTEND NOT RESPONDING")
