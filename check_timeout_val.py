"""Explicitly verify REQUEST_TIMEOUT_MS = 30000 in the compiled JS"""
import urllib.request, re

BASE = 'http://localhost:3000'
r = urllib.request.urlopen(f'{BASE}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)

for src in scripts:
    try:
        fr = urllib.request.urlopen(f'{BASE}{src}', timeout=10)
        js = fr.read().decode('utf-8', errors='replace')
        
        if 'REQUEST_TIMEOUT_MS' in js:
            # Find the exact return value
            # Pattern: return 30000; {break /}
            idx = js.find('REQUEST_TIMEOUT_MS')
            # Get surrounding context: the variable definition
            # Look for 30000 near REQUEST_TIMEOUT_MS
            chunk = js[max(0,idx-50):idx+200]
            if '30000' in chunk:
                print(f'[{src}]')
                print(f'  FOUND 30000 in REQUEST_TIMEOUT_MS definition')
                print(f'  Context: {chunk}')
            elif re.search(r'\b\d+\b', chunk):
                val = re.findall(r'\b\d+\b', chunk)[-1]
                print(f'[{src}]')
                print(f'  VALUE: {val}')
            else:
                print(f'[{src}]')
                print(f'  REQUEST_TIMEOUT_MS found but value unclear')
    except Exception as e:
        print(f'Error on {src}: {e}')
