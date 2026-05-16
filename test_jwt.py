# -*- coding: utf-8 -*-
"""JWT auth flow test"""
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

print('[1] REGISTER')
s, body, ms = api('/auth/register', 'POST', {
    'email': 'jwtflow@test.com', 'password': 'jwt123456', 'full_name': 'JWT Flow'
})
token = body.get('access_token', '') if isinstance(body, dict) else ''
print('     Token:', token[:30] if token else 'NONE')

if not token:
    print('[1b] LOGIN')
    s, body, ms = api('/auth/login', 'POST', {
        'email': 'jwtflow@test.com', 'password': 'jwt123456'
    })
    token = body.get('access_token', '') if isinstance(body, dict) else ''
    print('     Token:', token[:30] if token else 'NONE')

if not token:
    print('FATAL: no token')
    exit(1)

print()
print('[2] /auth/me')
s, body, ms = api('/auth/me', token=token)
if isinstance(body, dict):
    print('     email:', body.get('email'))

print()
print('[3] GET /parcels')
s, body, ms = api('/parcels', token=token)
if isinstance(body, list):
    print('     count:', len(body))

print()
print('[4] POST /parcels')
s, body, ms = api('/parcels', 'POST', {
    'name': 'AuthFlowParcel', 'location': 'Test', 'region': 'Test',
    'area_ha': 1.0, 'latitude': 33.5, 'longitude': -7.5
}, token)
pid = body.get('id', '') if isinstance(body, dict) else ''
print('     Created:', pid[:8])

if pid:
    print()
    print('[5] GET /parcels/' + pid[:8])
    s, body, ms = api('/parcels/' + pid, token=token)

print()
print('[6] WRONG token (expect 401)')
s, body, ms = api('/auth/me', token='fake_wrong_token')

print()
print('[7] NO token (expect 401)')
s, body, ms = api('/parcels')

print()
print('=== AUTH FLOW OK ===')
