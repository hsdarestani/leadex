#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/admin/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@leadex.com","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:50}..."

# List clients first
echo ""
echo "Current clients:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/clients/ | \
  python3 -c "import sys, json; data=json.load(sys.stdin); [print(f'{c[\"name\"]}: {c[\"id\"]}') for c in data]"

# Try to delete API Test Client
CLIENT_ID="309673a3-a93c-4677-8336-6e1f66404877"
echo ""
echo "Attempting to delete: $CLIENT_ID"
RESPONSE=$(curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  -w "\n%{http_code}" \
  "http://localhost:8000/api/admin/clients/$CLIENT_ID")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

echo "HTTP Status: $HTTP_CODE"
echo "Response: $BODY"

if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Delete successful"
else
    echo "✗ Delete failed"
fi
