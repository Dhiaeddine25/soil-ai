"""Test the real predict flow: does /predict require Bearer token?"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json, io
from PIL import Image

BASE = 'http://127.0.0.1:8000'

# 1. Register
r = requests.post(f'{BASE}/auth/register', json={
    'email': 'authflow@test.com', 'password': 'authflow1234', 'full_name': 'AuthFlow'
}, timeout=5)
token = r.json().get('access_token', '') if r.status_code == 200 else ''
if not token:
    r = requests.post(f'{BASE}/auth/login', json={
        'email': 'authflow@test.com', 'password': 'authflow1234'
    }, timeout=5)
    token = r.json().get('access_token', '')

print(f'Token: {token[:30]}...')

# 2. Prepare test image
img = Image.new('RGB', (100, 100), color=(80, 65, 40))
buf = io.BytesIO()
img.save(buf, format='JPEG')
img_bytes = buf.getvalue()
print(f'Image: {len(img_bytes)} bytes')

# 3. POST /predict WITHOUT token
buf.seek(0)
r_no_token = requests.post(f'{BASE}/predict', files={
    'image': ('test.jpg', buf, 'image/jpeg')
}, timeout=30)
print(f'\n/predict WITHOUT token: status={r_no_token.status_code}')
if r_no_token.status_code == 401:
    print('  -> TOKEN REQUIRED (protected endpoint)')
else:
    print(f'  -> OPEN endpoint or error: {r_no_token.text[:200]}')

# 4. POST /predict WITH token
buf.seek(0)
r_with_token = requests.post(f'{BASE}/predict', files={
    'image': ('test.jpg', buf, 'image/jpeg')
}, headers={'Authorization': f'Bearer {token}'}, timeout=30)
print(f'\n/predict WITH token: status={r_with_token.status_code}')
resp = r_with_token.json()
print(f'  model_name: {resp.get("model_name", "MISSING")}')
print(f'  status: {resp.get("status", "MISSING")}')
print(f'  confidence: {resp.get("confidence", "MISSING")}')
print(f'  can_trust_result: {resp.get("can_trust_result", "MISSING")}')

# 5. POST /predict/mock WITH token (requires token)
r_mock = requests.post(f'{BASE}/predict/mock', json={
    'image_name': 'test.jpg', 'parcel_id': ''
}, headers={'Authorization': f'Bearer {token}'}, timeout=15)
print(f'\n/predict/mock WITH token: status={r_mock.status_code}')

# 6. POST /predict/mock WITHOUT token
r_mock_no = requests.post(f'{BASE}/predict/mock', json={
    'image_name': 'test.jpg', 'parcel_id': ''
}, timeout=15)
print(f'/predict/mock WITHOUT token: status={r_mock_no.status_code}')
if r_mock_no.status_code in (401, 403):
    print('  -> TOKEN REQUIRED (good)')

print('\n=== AUTH FLOW SUMMARY ===')
print(f'Frontend stores token as: localStorage key = "soilai_token"')
print(f'Frontend sends as: Authorization: Bearer <token> (confirmed in JS bundle)')
print(f'Backend expects: OAuth2PasswordBearer(tokenUrl="/auth/login")')
print(f'/predict protected: {r_no_token.status_code == 401}')
print(f'/predict/mock protected: {r_mock_no.status_code in (401, 403)}')
print(f'All auth operations work correctly with token: {r_with_token.status_code == 200}')
