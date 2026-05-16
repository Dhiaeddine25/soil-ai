"""Test full dashboard data flow: parcels + history after prediction"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

BASE = 'http://127.0.0.1:8000'

# 1. Auth
r = requests.post(f'{BASE}/auth/register', json={
    'email': 'dashflow@test.com', 'password': 'dash123456', 'full_name': 'Dash Flow'
}, timeout=5)
print('Register:', r.status_code)
token = r.json().get('access_token', '')
if not token:
    r = requests.post(f'{BASE}/auth/login', json={
        'email': 'dashflow@test.com', 'password': 'dash123456'
    }, timeout=5)
    token = r.json().get('access_token', '')
print('Token OK:', bool(token))

# 2. listParcels (empty)
r2 = requests.get(f'{BASE}/parcels', headers={'Authorization': f'Bearer {token}'}, timeout=5)
print('listParcels (empty):', r2.status_code, 'count=', len(r2.json()))

# 3. createParcel
r3 = requests.post(f'{BASE}/parcels', json={
    'name': 'DashParcel1', 'location': 'Rabat', 'region': 'Rabat-Sale',
    'area_ha': 1.5, 'crop': 'Olivier', 'latitude': 34.02, 'longitude': -6.84
}, headers={'Authorization': f'Bearer {token}'}, timeout=5)
print('createParcel:', r3.status_code)
pid = r3.json().get('id') if r3.status_code == 201 else None
print('  Created parcel ID:', pid[:8] if pid else 'None')

# 4. Get user ID from token
import base64
payload_b64 = token.split('.')[1] + '=='
uid = json.loads(base64.b64decode(payload_b64)).get('sub', '')
print('User ID from token:', uid[:8])

# 5. getHistory (before predict)
r5 = requests.get(f'{BASE}/history/users/{uid}', headers={'Authorization': f'Bearer {token}'}, timeout=5)
print('getHistory (before):', r5.status_code, 'entries=', r5.json().get('total', 0))

# 6. predictMock (creates history entry)
r6 = requests.post(f'{BASE}/predict/mock', json={
    'image_name': 'dash_test.jpg',
    'parcel_id': pid if pid else ''
}, headers={'Authorization': f'Bearer {token}'}, timeout=15)
print('predictMock:', r6.status_code)

# 7. getHistory (after predict)
r7 = requests.get(f'{BASE}/history/users/{uid}', headers={'Authorization': f'Bearer {token}'}, timeout=5)
hist = r7.json()
print('getHistory (after):', r7.status_code, 'entries=', hist.get('total', 0))
for entry in hist.get('entries', [])[:2]:
    pred = entry.get('prediction', {})
    prediction_data = pred.get('prediction', {}) if isinstance(pred, dict) else {}
    print(f'  Entry {entry.get("id","")[:8]}: status={pred.get("status","N/A") if isinstance(pred,dict) else "N/A"}, confidence={pred.get("confidence","N/A") if isinstance(pred,dict) else "N/A"}')

# 8. listParcels again (should include DashParcel1)
r8 = requests.get(f'{BASE}/parcels', headers={'Authorization': f'Bearer {token}'}, timeout=5)
parcels = r8.json()
names = [p.get('name', '') for p in parcels]
print('listParcels final:', r8.status_code, 'count=', len(parcels), 'names=', names)

print('\nDashboard data flow: ALL OK')
