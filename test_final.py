"""Complete e2e test simulating browser behavior"""
import json, urllib.request, time

BASE = 'http://127.0.0.1:8000'

def req(url, method='GET', data=None, token=None, timeout=15):
    t0 = time.time()
    try:
        req_data = json.dumps(data).encode() if data else None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        r = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        resp = urllib.request.urlopen(r, timeout=timeout)
        elapsed = time.time() - t0
        body = {}
        ct = resp.headers.get('Content-Type', '')
        if 'json' in ct:
            body = json.loads(resp.read())
        else:
            body = {'raw': resp.read().decode()[:200]}
        return {'ok': True, 'code': resp.status, 'ms': round(elapsed*1000), 'body': body}
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        body = {}
        try:
            body = json.loads(e.read())
        except:
            body = {'text': str(e)}
        return {'ok': False, 'code': e.code, 'ms': round(elapsed*1000), 'body': body}
    except Exception as e:
        elapsed = time.time() - t0
        return {'ok': False, 'code': 'ERR', 'ms': round(elapsed*1000), 'error': str(e)[:120]}

print('--- STEP 1: Health ---')
r = req(BASE + '/health')
print(r['code'], r['ms'], 'ms', r.get('body'))

print('\n--- STEP 2: Register ---')
r = req(BASE + '/auth/register', method='POST', data={
    'email': 'finaltest@test.com',
    'password': 'finaltest1234',
    'full_name': 'Final Test'
})
print(r['code'], r['ms'], 'ms', r.get('body', {}).get('access_token', '')[:30] if 'body' in r else '')

token = r.get('body', {}).get('access_token', '')
if not token:
    print('  -> Trying login')
    r2 = req(BASE + '/auth/login', method='POST', data={
        'email': 'finaltest@test.com',
        'password': 'finaltest1234'
    })
    print(r2.get('code'), r2.get('ms'), 'ms', r2.get('body', {}).get('access_token', '')[:30])
    token = r2.get('body', {}).get('access_token', '')

print('\n--- STEP 3: Create Parcel ---')
r = req(BASE + '/parcels', method='POST', data={
    'name': 'Ma Parcelle Finale',
    'location': 'Marrakech-Safi, Maroc',
    'region': 'Marrakech-Safi',
    'area_ha': 5.0,
    'crop': 'Bled Doukkala',
    'notes': 'Parcelle de test automatique',
    'latitude': 31.63,
    'longitude': -8.01
}, token=token)
print(r['code'], r['ms'], 'ms')
if r.get('body'):
    print('  id:', r['body'].get('id'))
    print('  name:', r['body'].get('name'))

pid = r.get('body', {}).get('id', '') if r['ok'] else ''

print('\n--- STEP 4: List Parcels ---')
r = req(BASE + '/parcels', token=token)
print(r['code'], r['ms'], 'ms')
if r.get('body') and isinstance(r['body'], list):
    print('  count:', len(r['body']))
    for p in r['body']:
        print('   -', p.get('name'), '|', p.get('region'), '|', p.get('crop'))

print('\n--- STEP 5: Predict Mock ---')
r = req(BASE + '/predict/mock', method='POST', data={
    'image_name': 'test_soil.jpg',
    'parcel_id': pid
}, token=token)
print(r['code'], r['ms'], 'ms')
if r.get('body'):
    print('  status:', r['body'].get('status'))
    print('  model:', r['body'].get('model_name'))

print('\n--- STEP 6: History ---')
uid = 'e2e_user'
if r.get('body') and pid:
    r_hist = req(BASE + '/history/users/' + uid, token=token, timeout=10)
    print(r_hist.get('code'), r_hist.get('ms'), 'ms')
else:
    print('Skip (no pid)')

print('\n=== ALL TESTS COMPLETE ===')
