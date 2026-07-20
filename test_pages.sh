#!/bin/bash

echo "Testing Admin Pages API Endpoints"
echo "=================================="

# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/admin/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@leadex.com","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "✓ Token obtained: ${TOKEN:0:50}..."

# Test clients endpoint
echo ""
echo "Testing /api/admin/clients/"
CLIENTS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/clients/)
CLIENT_COUNT=$(echo $CLIENTS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Clients endpoint: $CLIENT_COUNT clients returned"

# Test leads endpoint
echo ""
echo "Testing /api/admin/leads/"
LEADS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/leads/)
LEAD_COUNT=$(echo $LEADS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Leads endpoint: $LEAD_COUNT leads returned"

# Show sample data
echo ""
echo "Sample Client:"
echo $CLIENTS | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data[0] if data else {}, indent=2))"

echo ""
echo "Sample Lead:"
echo $LEADS | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data[0] if data else {}, indent=2))"
