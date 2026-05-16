"""Check that requestJSON in bundles no longer has the broken try/catch around fetch"""
import urllib.request, re

BASE = 'http://localhost:3000'
r = urllib.request.urlopen(f'{BASE}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

for src in scripts:
    try:
        r2 = urllib.request.urlopen(f'{BASE}{src}', timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        
        # Find requestJSON and fetchWithTimeout usage patterns
        idx = 0
        while True:
            idx = js.find('requestJSON', idx)
            if idx == -1:
                break
            # Check the context: does requestJSON use try/catch 
            snippet = js[max(0,idx-50):idx+200]
            if 'fetchWithTimeout' in snippet:
                print(f'BUNDLE: {src}')
                print(f'  Context around requestJSON+fetchWithTimeout:')
                print(f'  {snippet[:200]}')
                print()
            idx += 1
    except Exception as e:
        print(f'Error on {src}: {e}')
