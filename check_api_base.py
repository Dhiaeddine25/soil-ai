"""Check ALL bundles for API_BASE content"""
import urllib.request, re, json

BASE = 'http://localhost:3000'

# Get parcels page
r = urllib.request.urlopen(f'{BASE}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

print('Bundles found:')
for src in scripts:
    try:
        fr = urllib.request.urlopen(f'{BASE}{src}', timeout=10)
        js = fr.read().decode('utf-8', errors='replace')
        if 'API_BASE' in js:
            # Extract next_env/NEXT_PUBLIC context
            idx = js.find('API_BASE')
            ctx = js[max(0,idx-100):idx+100]
            print(f'\n[BUNDLE: {src}]')
            print(ctx)
        elif 'fetch(' in js and ('parcels' in js.lower() or 'request' in js.lower()):
            print(f'[BUNDLE contains fetch+parcels: {src}]')
    except Exception as e:
        print(f'Error loading {src}: {e}')
