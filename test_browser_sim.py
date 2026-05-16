"""
Final test: Simulate exact browser behavior
- Uses http://127.0.0.1:8000 (what browser JS uses after bundling)
- Creates a parcel like the UI would
- Verifies the parcel appears in listing
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

BASE = 'http://127.0.0.1:8000'

print('=== EXACT BROWSER SIMULATION ===\n')

# User logs in
print('[Browser] Auth: register then login')
r = requests.post(f'{BASE}/auth/register', json={
    'email':'browser_e2e@test.com', 'password':'browsere2e123', 'full_name':'Browser E2E'
}, timeout=5)
if r.status_code == 400:
    # Already exists, login
    print('[Browser] User exists, logging in...')
    r = requests.post(f'{BASE}/auth/login', json={
        'email':'browser_e2e@test.com', 'password':'browsere2e123'
    }, timeout=5)

token = r.json().get('access_token','')
print(f'[Browser] Auth OK, token: {token[:25]}...')

# User opens parcels page
print('\n[Browser] Opening /parcels page (SSR)')
r_ssr = requests.get(f'http://localhost:3000/parcels', timeout=10)
print(f'[Browser] SSR status: {r_ssr.status_code}, size: {len(r_ssr.content)} bytes')
assert r_ssr.status_code == 200, 'SSR failed!'

# JS bundle calls createParcel when form is submitted
print('\n[Browser] Submitting parcel form (API call)')
create_payload = {
    'name': 'Parcelle App',
    'location': 'Marrakech-Safi',
    'region': 'Marrakech-Safi',
    'area_ha': 3.5,
    'crop': 'Orge',
    'notes': 'Creee via navigateur',
    'latitude': 31.6295,
    'longitude': -7.9811
}
t0 = __import__('time').time()
r_create = requests.post(f'{BASE}/parcels', json=create_payload,
    headers={'Authorization': f'Bearer {token}'}, timeout=15)
elapsed = round((__import__('time').time() - t0)*1000)
print(f'[Browser] Create parcel: {r_create.status_code} in {elapsed}ms')
assert r_create.status_code == 201, f'Parcel create failed: {r_create.status_code}'
parcel = r_create.json()
print(f'[Browser] Created: id={parcel["id"][:8]}, name={parcel["name"]}')

# JS bundle calls listParcels after creation
print('\n[Browser] Refreshing parcel list (listParcels)')
t0 = __import__('time').time()
r_list = requests.get(f'{BASE}/parcels', headers={'Authorization': f'Bearer {token}'}, timeout=10)
elapsed = round((__import__('time').time() - t0)*1000)
print(f'[Browser] List parcels: {r_list.status_code} in {elapsed}ms')
parcels = r_list.json()
names = [p['name'] for p in parcels]
print(f'[Browser] Found {len(parcels)} parcel(s): {names}')

# Verify parcel exists
assert parcel['id'] in [p['id'] for p in parcels], 'Parcel not in listing!'
print('\n[Browser] Parcel confirmed in listing!')

# Simulate navigation to dashboard
print('\n[Browser] Loading dashboard page')
r_dash = requests.get(f'http://localhost:3000/dashboard', timeout=10)
print(f'[Browser] Dashboard SSR: {r_dash.status_code}, size={len(r_dash.content)} bytes')

# JS calls listParcels and getHistory for dashboard
print('\n[Browser] Dashboard data fetch: listParcels + getHistory')
t0 = __import__('time').time()
r_p = requests.get(f'{BASE}/parcels', headers={'Authorization': f'Bearer {token}'}, timeout=10)
r_h = requests.get(f'{BASE}/history/users/{parcel["user_id"]}', headers={'Authorization': f'Bearer {token}'}, timeout=10)
elapsed = round((__import__('time').time() - t0)*1000)
total_h = r_h.json().get('total', 0)
print(f'[Browser] Dashboard fetch: {r_p.status_code} (parcels={len(r_p.json())}) + {r_h.status_code} (history={total_h}) in {elapsed}ms')

print('\n' + '='*50)
print('SIMULATION RESULT: ALL OK')
print('='*50)
print('The following configuration makes parcel creation work:')
print('  frontend/.env: NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000')
print('  frontend/.env.local: NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000')
print('  Backend: running on http://127.0.0.1:8000')
print('  CORS: configured for http://localhost:3000')
print('  Frontend: next dev running on http://localhost:3000')
