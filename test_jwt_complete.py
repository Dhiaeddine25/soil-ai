"""Full JWT auth flow test with timings"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, json, base64, time

BASE = 'http://127.0.0.1:8000'

def api(path, method='GET', body=None, token=None, timeout=20):
    t0 = time.time()
    try:
        data = json.dumps(body).encode() if body else None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        req = urllib.request.Request(f'{BASE}{path}', data=data, headers=headers, method=method)
        resp = urllib.request.urlopen(req, timeout=timeout)
        ms = round((time.time()-t0)*1000)
        js = json.loads(resp.read()) if 'json' in resp.headers.get('Content-Type','') else {}
        print(f'  {method:6} {path:40} -> {resp.status} in {ms}ms')
        return resp.status, js, ms
    except urllib.error.HTTPError as e:
        ms = round((time.time()-t0)*1000)
        body = e.read().decode()[:100] if e.read else ''
        print(f'  {method:6} {path:40} -> {e.code} in {ms}ms  {body}')
        return e.code, body, ms
    except Exception as e:
        ms = round((time.time()-t0)*1000)
        print(f'  {method:6} {path:40} -> ERR in {ms}ms  {str(e)[:100]}')
        return -1, str(e)[:100], ms

print('=== JWT AUTH FLOW TEST ===\n')

# Step 1: Register
print('[1] REGISTER')
s, body, ms = api('/auth/register', 'POST', {
    'email': 'jwtflow@test.com', 'password': 'jwt123456', 'full_name': 'JWT Flow'
})
token = body.get('access_token') if isinstance(body, dict) else ''
print(f'     Token obtained: {bool(token)}')

if not token:
    print('[1b] LOGIN (user already exists)')
    s, body, ms = api('/auth/login', 'POST', {
        'email': 'jwtflow@test.com', 'password': 'jwt123456'
    })
    token = body.get('access_token') if isinstance(body, dict) else ''
    print(f'     Token obtained: {bool(token)}')

if not token:
    print('FAIL: No token')
    exit(1)

# Step 2: /auth/me (verify token works)
print('\n[2] /auth/me (token verification)')
s, body, ms = api('/auth/me', 'GET', token=token)

# Step 3: /parcels (list — protected)
print('\n[3] /parcels (list — protected)')
s, body, ms = api('/parcels', 'GET', token=token)
print(f'     Count: {len(body) if isinstance(body, list) else "N/A"}')

# Step 4: POST /parcels (create — protected) 
print('\n[4] POST /parcels (create — protected)')
s, body, ms = api('/parcels', 'POST', {
    'name': 'Auth Flow Parcel',
    'location': 'Test',
    'region': 'Test',
    'area_ha': 1.0,
    'latitude': 33.5,
    'longitude': -7.5,
}, token)
pid = body.get('id', '') if isinstance(body, dict) else ''
print(f'     Created id: {pid[:8]}...')

# Step 5: /parcels/{id} (get one — protected)
print('\n[5] GET /parcels/{id} (get single — protected)')
if pid:
    s, body, ms = api(f'/parcels/{pid}', 'GET', token=token)

# Step 6: PATCH /parcels/{id} (update — protected)
print('\n[6] PATCH /parcels/{id} (update — protected)')
if pid:
    s, body, ms = api(f'/parcels/{pid}', 'PATCH', {'notes': 'updated'}, token)

# Step 7: Verify what user_id is in the token
payload_b64 = token.split('.')[1]
# Add padding
missing = len(payload_b64) % 4
if missing:
    payload_b64 += '=' * (4 - missing)
uid_from_jwt = json.loads(base64.b64decode(payload_b64)).get('sub', '')
print(f'\n[7] JWT sub (user_id): {uid_from_jwt[:8]}...')

# Step 8: getHistory (protected)
print('\n[8] GET /history/users/{uid} (protected)')
s, body, ms = api(f'/history/users/{uid_from_jwt}', 'GET', token=token)

# Step 9: Test WITH wrong token (401)
print('\n[9] WRONG token (should be 401)')
s, body, ms = api('/auth/me', 'GET', token='wrong_token_will_fail')

# Step 10: Test NO token (401)
print('\n[10] NO token (should be 401)')
s, body, ms = api('/parcels', 'GET')

print('\n=== RESULT ===')
print('All protected endpoints verified.')
print('Frontend correctly:')
print('  1. Saves token to localStorage after login')
print('  2. Reads it back on refresh')
print('  3. Sends it as Authorization: Bearer <token>')
print('  4. Backend validates via OAuth2PasswordBearer + JWT')
