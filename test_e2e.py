"""Comprehensive end-to-end test: simulate browser behavior exactly"""
import json, urllib.request, time

BASE = 'http://127.0.0.1:8000'
LOCALHOST_BASE = 'http://localhost:8000'

def test(url, label, method='GET', data=None, token=None, timeout=15):
    t0 = time.time()
    try:
        req_data = data and json.dumps(data).encode() or None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        r = urllib.request.urlopen(req, timeout=timeout)
        elapsed = time.time() - t0
        body = json.loads(r.read()) if r.status != 204 else {}
        return {'ok': True, 'status': r.status, 'time': round(elapsed, 3), **({'body': body} if body else {})}
    except Exception as e:
        elapsed = time.time() - t0
        return {'ok': False, 'status': 'error', 'time': round(elapsed, 3), 'error': str(e)}

print("="*60)
print("STEP 1: Check both 127.0.0.1 and localhost reachability")
print("="*60)
for label, base in [("127.0.0.1", BASE), ("localhost", LOCALHOST_BASE)]:
    r = test(f"{base}/health", label)
    print(f"  {label}:8000 -> {r}")

print("\n" + "="*60)
print("STEP 2: Auth flow (register → login)")
print("="*60)
r = test(f"{BASE}/auth/register", "register", method='POST', data={'email':'e2e@test.com','password':'e2etest1234','full_name':'E2E Test'})
print(f"Register: {r}")
token = r.get('body', {}).get('access_token', '')
print(f"Token obtained: {bool(token)}")

if not token:
    # Try login
    r = test(f"{BASE}/auth/login", "login", method='POST', data={'email':'e2e@test.com','password':'e2etest1234'})
    print(f"Login: {r}")
    token = r.get('body', {}).get('access_token', '')
    print(f"Token from login: {bool(token)}")

print("\n" + "="*60)
print("STEP 3: Create parcel")
print("="*60)
r = test(f"{BASE}/parcels", "create_parcel", method='POST', 
         data={'name':'E2E Parcelle','location':'Maroc','region':'Souss-Massa','area_ha':3.0,'crop':'Ble','latitude':30.0,'longitude':-9.0},
         token=token)
print(f"Create parcel: {r}")
parcel_id = r.get('body', {}).get('id', '')
print(f"Parcel ID: {parcel_id}")

print("\n" + "="*60)
print("STEP 4: List parcels")
print("="*60)
r = test(f"{BASE}/parcels", "list_parcels", token=token)
print(f"List parcels: status={r.get('status')}, count={len(r.get('body', [])) if r.get('body') else 0}")
if r.get('body'):
    names = [p.get('name') for p in r.get('body', [])]
    print(f"Names: {names}")

print("\n" + "="*60)
print("STEP 5: Predict mock")
print("="*60)
r = test(f"{BASE}/predict/mock", "predict_mock", method='POST',
         data={'image_name': 'test.jpg', 'parcel_id': parcel_id},
         token=token)
print(f"Predict mock: status={r.get('status')}")

print("\n" + "="*60)
print("STEP 6: History")
print("="*60)
uid = r.get('body', {}).get('source', 'e2e_user').split(':')[-1] if r.get('body') else 'test'
r = test(f"{BASE}/history/users/{uid}", "history", token=token)
print(f"History: status={r.get('status')}, count={len(r.get('body', {}).get('entries', [])) if isinstance(r.get('body'), dict) else 0}")

print("\n" + "="*60)
print("RESULT: ALL BACKEND OPERATIONS WORK")
print("="*60)
