"""Verify api.ts changes are reflected in JS bundle"""
import urllib.request, re

BASE = 'http://localhost:3000'

r = urllib.request.urlopen(f'{BASE}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

print('Checking bundles for api.ts changes:')

for src in scripts:
    try:
        r2 = urllib.request.urlopen(f'{BASE}{src}', timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        
        if 'REQUEST_TIMEOUT_MS' in js and '30000' in js:
            idx = js.find('REQUEST_TIMEOUT_MS')
            ctx = js[max(0,idx-10):idx+40]
            print(f'\n{BASE}{src}:')
            print(f'  export const REQUEST_TIMEOUT_MS = 30000: FOUND')
            print(f'  Context: ...{ctx}...')
            
    except Exception as e:
        print(f'Error on {src}: {e}')

# Also verify .env in bundles
print('\n--- VERIFYING API_BASE IN BUNDLES ---')
for src in scripts:
    try:
        r2 = urllib.request.urlopen(f'{BASE}{src}', timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        if '127.0.0.1:8000' in js:
            idx = js.find('127.0.0.1:8000')
            ctx = js[max(0,idx-30):idx+60]
            print(f'{src}: API_BASE=127.0.0.1:8000 [OK]')
    except Exception as e:
        print(f'Error: {e}')
