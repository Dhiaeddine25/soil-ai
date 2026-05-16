"""Find the exact API_BASE value in the bundles"""
import urllib.request, json, re

BASE = 'http://localhost:3000'

bundles_to_check = [
    '/_next/static/chunks/app/parcels/page.js',
    '/_next/static/chunks/app/layout.js',
    '/_next/static/chunks/main-app.js?v=1778838701318',
]

for path in bundles_to_check:
    try:
        r = urllib.request.urlopen(f'{BASE}{path}', timeout=10)
        js = r.read().decode('utf-8', errors='replace')
        
        # Find API_BASE definitions
        matches = []
        start = 0
        while True:
            pos = js.find('NEXT_PUBLIC_API_BASE_URL', start)
            if pos == -1:
                break
            start = pos + 1
            matches.append(pos)
        
        if matches:
            for pos in matches[:3]:
                ctx = js[max(0, pos-30):pos+120]
                print(f'[{path}] pos {pos}:')
                print(ctx)
                print()
        else:
            print(f'[{path}]: No NEXT_PUBLIC_API_BASE_URL found')
            
    except Exception as e:
        print(f'Error loading {path}: {e}')
