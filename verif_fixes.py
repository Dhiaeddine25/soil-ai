"""Final verification of all fixes"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, re
from pathlib import Path

print('=== FINAL VERIFICATION ===\n')

# 1. Check .env
env_file = Path('frontend/.env')
if env_file.exists():
    content = env_file.read_text(encoding='utf-8').strip()
    print('[1] frontend/.env:')
    print(f'    {content}')
    assert content == 'NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000', '.env content is CORRECT'
    print('    -> OK')
else:
    print('ERROR: .env missing!')

env_local = Path('frontend/.env.local')
if env_local.exists():
    content2 = env_local.read_text(encoding='utf-8').strip()
    print(f'\n[2] frontend/.env.local: {content2} -> OK')
else:
    print('ERROR: .env.local missing!')

print(f'\n[3] Backend status:')
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)
    print(f'    /health -> {r.status} OK')
except Exception as e:
    print(f'    BAD: {e}')

print(f'\n[4] JS Bundle API_BASE verification:')
try:
    r = urllib.request.urlopen('http://localhost:3000/parcels', timeout=10)
    html = r.read().decode('utf-8', errors='replace')
    scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
    
    found = False
    for src in scripts:
        if 'page.js' in src or 'parcels' in src:
            r2 = urllib.request.urlopen(f'http://localhost:3000{src}', timeout=10)
            js = r2.read().decode('utf-8', errors='replace')
            if 'http://127.0.0.1:8000' in js:
                idx = js.find('http://127.0.0.1:8000')
                ctx = js[max(0,idx-30):idx+60]
                print(f'    Bundle: {src}')
                print(f'    Context: ...{ctx}...')
                found = True
                break
    
    if not found:
        print('    Not found in page.js - trying main bundle')
        for src in scripts:
            r2 = urllib.request.urlopen(f'http://localhost:3000{src}', timeout=10)
            js = r2.read().decode('utf-8', errors='replace')
            if '127.0.0.1:8000' in js:
                idx = js.find('127.0.0.1:8000')
                ctx = js[max(0,idx-30):idx+60]
                print(f'    Found in {src}: ...{ctx}...')
                found = True
                break
        if not found:
            print('    WARNING: API_BASE not found in any bundle')
except Exception as e:
    print(f'    ERROR: {e}')

print('\n[5] .gitignore check:')
gi = Path('.gitignore').read_text(encoding='utf-8')
if 'frontend/.env*' in gi:
    print('    .gitignore protects frontend/.env* -> OK')
else:
    print('    WARNING: .gitignore missing frontend/.env*')

print('\n[6] Backend next.config.mjs:')
nc = Path('frontend/next.config.mjs').read_text(encoding='utf-8')
print(f'    output: standalone={"output: standalone" in nc}')
print(f'    cache = false on dev={"config.cache = false" in nc}')

print('\n=== VERIFICATION COMPLETE ===')
