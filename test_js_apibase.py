import urllib.request, re

# Test the Next.js page response
r = urllib.request.urlopen('http://localhost:3000/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
print('Frontend status:', r.status)

# Extract script src attributes
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
print('Found JS bundles:', scripts[:5])

# Download a JS bundle and look for API_BASE
for src in scripts[:3]:
    try:
        full_url = src if src.startswith('http') else f'http://localhost:3000{src}'
        print(f'\nChecking: {full_url}')
        r2 = urllib.request.urlopen(full_url, timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        
        if '127.0.0.1:8000' in js:
            idx = js.find('127.0.0.1:8000')
            print(f'Found API_BASE at pos {idx}:')
            print(f'  ...{js[max(0,idx-80):idx+120]}...')
        elif 'NEXT_PUBLIC_API_BASE' in js:
            idx = js.find('NEXT_PUBLIC_API_BASE')
            print(f'Var found at pos {idx}:')
            print(f'  ...{js[max(0,idx-50):idx+150]}...')
        else:
            print(f'API_BASE not found. Bundle length: {len(js)}')
    except Exception as e:
        print(f'Error: {e}')
