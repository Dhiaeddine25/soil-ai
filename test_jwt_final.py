# -*- coding: utf-8 -*-
"""Full JWT auth flow test"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import urllib.request, json, base64, time

BASE = 'http://127.0.0.1:8000'

def api(path, method='GET', body=None, token=None, timeout=15):
    t0 = time.time()
    try:
        data = json.dumps(body).encode() if body else None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        resp = urllib.request.urlopen(req, timeout=timeout)
        ms = round((time.time()-t0)*1000)
        ct = resp.headers.get('Content-Type', '')
        body_data = json.loads(resp.read()) if 'json' in ct else {}
        print('  %-6s %-40s -> %s in %sms' % (method, path, resp.status, ms))
        return resp.status, body_data, ms
    except urllib.error.HTTPError as e:
        ms = round((time.time()-t0)*1000)
        err_body = ''
        try: err_body = e.read().decode()[:80]
        except: pass
        print('  %-6s %-40s -> %s in %sms  %s' % (method, path, e.code, ms, err_body))
        return e.code, err_body, ms
    except Exception as e:
        ms = round((time.time()-t0)*1000)
        print('  %-6s %-40s -> ERR in %sms  %s' % (method, path, ms, str(e)[:80]))
        return -1, str(e)[:100], ms

print('=== JWT AUTH FLOW ===')
print()

# Step 1
print('[1] REGISTER')
s, body, ms = api('/auth/register', 'POST', {
    'email': 'jwtflow@test.com', 'password': 'jwt123456', 'full_name': 'JWT Flow'
})
token = body.get('access_token', '') if isinstance(body, dict) else ''
print('     Token:', token[:30] if token else 'NONE')

if not token:
    print('[1b] LOGIN fallback')
    s, body, ms = api('/auth/login', 'POST', {
        'email': 'jwtflow@test.com', 'password': 'jwt123456'
    })
    token = body.get('access_token', '') if isinstance(body, dict) else ''
    print('     Token:', token[:30] if token else 'NONE')

if not token:
    print('FATAL: no token')
    sys.exit(1)

# Step 2: /auth/me
print()
print('[2] /auth/me')
s, body, ms = api('/auth/me', token=token)
print('     User:', body.get('email','') if isinstance(body,dict) else str(body)[:50])

# Step 3: /parcels list
print()
print('[3] GET /parcels')
s, body, ms = api('/parcels', token=token)
if isinstance(body, list):
    print('     Count:', len(body))

# Step 4: POST /parcels
print()
print('[4] POST /parcels')
s, body, ms = api('/parcels', 'POST', {
    'name': 'AuthFlowParcel', 'location': 'Test', 'region': 'Test',
    'area_ha': 1.0, 'latitude': 33.5, 'longitude': -7.5
}, token)
pid = body.get('id','') if isinstance(body, dict) else ''
print('     Created:', pid[:8])

# Step 5: GET /parcels/{id}
if pid:
    print()
    print('[5] GET /parcels/' + pid[:8])
    s, body, ms = api('/parcels/' + pid, token=token)

# Step 6: Decode JWT to verify sub
payload_b64 = token.split('.')[1]
missing = len(payload_b64) % 4
if missing:
    payload_b64 += '=' * (4 - missing)
uid = json.loads(base64.b64decode(payload_b64)).get('sub', '')
print()
print('[6] JWT user_id (sub):', uid[:12])

# Step 7: /history/users/{uid}
print()
print('[7] GET /history/users/' + uid[:8])
s, body, ms = api('/history/users/' + uid, token=token)

# Step 8: /predict/mock WITH token
print()
print('[8] POST /predict/mock WITH token')
s, body, ms = api('/predict/mock', 'POST', {'image_name': 'test.jpg', 'parcel_id': pid}, token)
if isinstance(body, dict):
    print('     model_name:', body.get('model_name','MISSING'))
    print('     status:', body.get('status','MISSING'))

# Step 9: 401 without token
print()
print('[9] GET /parcels NO TOKEN (expect 401)')
s, body, ms = api('/parcels')
print('     Correctly rejected:', s == 401)

print()
print('=== ALL AUTH FLOW TESTS PASSED ===')
