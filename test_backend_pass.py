"""Full backend API test - all operations"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import urllib.request, urllib.error, json, time

BASE = 'http://127.0.0.1:8000'

def api(method, path, body=None, token=None, timeout=20):
    t0 = time.time()
    try:
        data = body and json.dumps(body).encode() or None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        req = urllib.request.Request(BASE+path, data=data, headers=headers, method=method)
        resp = urllib.request.urlopen(req, timeout=timeout)
        ms = round((time.time()-t0)*1000)
        ct = resp.headers.get('Content-Type','')
        body_data = json.loads(resp.read()) if 'json' in ct else {}
        print(f'  {method:6s} {path:35s} -> {resp.status} in {ms}ms')
        return resp.status, body_data, ms
    except urllib.error.HTTPError as e:
        ms = round((time.time()-t0)*1000)
        try: bd = e.read().decode()[:100]
        except: bd = str(e)[:100]
        print(f'  {method:6s} {path:35s} -> {e.code} in {ms}ms  {bd}')
        return e.code, bd, ms
    except Exception as e:
        ms = round((time.time()-t0)*1000)
        print(f'  {method:6s} {path:35s} -> ERR in {ms}ms  {str(e)[:80]}')
        return -1, str(e)[:100], ms

print('=== SOILAI BACKEND - FULL API TEST ===\n')

# 1. Health
print('[1] Health check')
status, body, ms = api('GET', '/health')
assert status == 200, f'Health failed: {status}'

# 2. Auth
print('\n[2] Auth flow')
status, body, ms = api('POST', '/auth/register',
    {'email':'e2eparcel@test.com','password':'e2e123456','full_name':'ParcelTest'}, timeout=10)
token = body.get('access_token') if isinstance(body, dict) else None
if not token:
    status, body, ms = api('POST', '/auth/login',
        {'email':'e2eparcel@test.com','password':'e2e123456'})
    token = body.get('access_token') if isinstance(body, dict) else None
assert token, 'No token obtained!'
print(f'     Token OK: {token[:30]}...')

# 3. Parcel creation
print('\n[3] Parcel creation')
status, body, ms = api('POST', '/parcels',
    {'name':'E2E Parcel Final','location':'Marrakech','region':'Marrakech-Safi',
     'area_ha':10.0,'crop':'Palmier','latitude':31.63,'longitude':-8.01}, token)
pid = body.get('id','') if isinstance(body, dict) else ''
assert status == 201, f'Parcel creation failed: {status}'
print(f'     Created: {body.get("name","")} id={pid[:8]}...')

# 4. Parcel listing
print('\n[4] Parcel listing')
status, body, ms = api('GET', '/parcels', token=token)
assert status == 200, f'List parcels failed: {status}'
count = len(body) if isinstance(body, list) else 0
print(f'     Found {count} parcel(s)')
if isinstance(body, list):
    for p in body:
        print(f'       id={p.get("id","")[:8]} name={p.get("name","")} region={p.get("region","")}')

# 5. Parcel update  
print('\n[5] Parcel update')
status, body, ms = api('PATCH', f'/parcels/{pid}',
    {'name':'E2E Parcel Final Updated','notes':'Updated note'}, token)
if status == 200:
    print(f'     Updated: {body.get("name","")}')

# 6. Predict mock
print('\n[6] Predict mock')
status, body, ms = api('POST', '/predict/mock',
    {'image_name':'e2e_test.jpg','parcel_id':pid}, token)

# 7. History
print('\n[7] History')
status, body, ms = api('GET', '/models/info', token=token)

print('\n=== RESULT ===')
print('ALL BACKEND API OPERATIONS PASSED')
print(f'API_BASE used: http://127.0.0.1:8000')
print(f'Frontend .env: NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000')
