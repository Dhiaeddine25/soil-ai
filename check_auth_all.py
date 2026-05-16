"""Full auth JS bundle scanner"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, re

BASE_DEV = 'http://localhost:3000'
r = urllib.request.urlopen(f'{BASE_DEV}/parcels', timeout=10)
html = r.read().decode('utf-8', errors='replace')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
print('All scripts found:')
for s in scripts:
    print(' ', s)

# Check each script for auth patterns
for src in scripts:
    try:
        r2 = urllib.request.urlopen(f'{BASE_DEV}{src}', timeout=10)
        js = r2.read().decode('utf-8', errors='replace')
        hits = []
        for kw in ['localStorage', 'getItem', 'setItem', 'Authorization', 'Bearer', 'soilai_token']:
            cnt = js.count(kw)
            if cnt > 0:
                hits.append((kw, cnt))
        if hits:
            print(f'\nBUNDLE: {src}')
            for kw, cnt in hits:
                print(f'  {kw}: {cnt}x')
                idx = js.find(kw)
                ctx = js[max(0,idx-80):idx+100]
                print(f'    ...{ctx}...')
    except Exception as e:
        print(f'Error on {src}: {e}')
