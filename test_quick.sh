#!/bin/bash
cd /root/leadex-project
source venv/bin/activate

TOKEN=$(python3 -c "
import requests
r = requests.post('http://localhost:8000/api/admin/auth/login',
    json={'email': 'admin@leadex.com', 'password': 'admin123'})
print(r.json()['access_token'])
")

echo "Testing delete..."
python3 -c "
import requests
r = requests.delete('http://localhost:8000/api/admin/clients/309673a3-a93c-4677-8336-6e1f66404877',
    headers={'Authorization': 'Bearer $TOKEN'})
print('Status:', r.status_code)
print('Response:', r.text if r.text else '(empty)')
"
