"""Check exactly what the built JS contains for API calls and search for any fetch bug"""
import re, urllib.request

BASE_DEV = 'http://localhost:3000'

# Get the parcels page JS bundle
r = urllib.request.urlopen(f'{BASE_DEV}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

# Find the api.js bundle
api_src = None
for src in scripts:
    if 'api' in src or 'lib' in src or 'page' in src:
        api_src = src
        break

if not api_src:
    # Look for any chunk that might contain api
    for src in scripts:
        print(f'Checking: {src}')
        try:
            r2 = urllib.request.urlopen(f'{BASE_DEV}{src}', timeout=10)
            js = r2.read().decode('utf-8', errors='replace')
            if 'fetch' in js:
                print(f'  -> Contains fetch, length={len(js)}')
                # Find fetch calls
                matches = [(m.start(), js[max(0,m.start()-60):m.start()+120]) for m in re.finditer(r'fetch\(', js)]
                for pos, ctx in matches[:3]:
                    print(f'     fetch at {pos}: ...{ctx}...')
        except Exception as e:
            print(f'  Error: {e}')
else:
    print(f'Using API src: {api_src}')
