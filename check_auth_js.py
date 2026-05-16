"""Check JS bundles for auth/Authorization/localStorage patterns"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, re

BASE_DEV = 'http://localhost:3000'
r = urllib.request.urlopen(f'{BASE_DEV}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

for target in ['auth-provider', 'api.ts']:
    src = next((s for s in scripts if target in s), None)
    if not src:
        # Try partial match
        src = next((s for s in scripts if 'auth' in s or 'api' in s), None)
    if src:
        print(f'\n=== Checking: {src} ===')
        r2 = urllib.request.urlopen(f'{BASE_DEV}{src}', timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        
        for kw, label in [
            ('localStorage', 'localStorage'),
            ('getItem', 'getItem'),
            ('setItem', 'setItem'),
            ('Authorization', 'Authorization header'),
            ('Bearer', 'Bearer token'),
            ('soilai_token', 'soilai_token key'),
        ]:
            count = js.count(kw)
            if count > 0:
                # Find first context
                idx = js.find(kw)
                ctx = js[max(0,idx-60):idx+100]
                print(f'  {label}: {count}x -> ...{ctx}...')
            else:
                print(f'  {label}: NOT present')
    else:
        print(f'{target}: not found in scripts')
