#!/bin/bash

echo "🧪 Testing Leadex API Endpoints"
echo "================================"

# Test health endpoint
echo -e "\n1️⃣  Testing health endpoint..."
curl -s http://localhost:8000/health | jq '.'

# Test root endpoint
echo -e "\n2️⃣  Testing root endpoint..."
curl -s http://localhost:8000/ | jq '.'

# Test landing page submission (will fail without valid recaptcha, but tests routing)
echo -e "\n3️⃣  Testing landing page endpoint (POST /api/landing/default)..."
curl -s -X POST http://localhost:8000/api/landing/default \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "+971501234567",
    "name": "Test User",
    "email": "test@example.com",
    "recaptcha_token": "test_token_bypass"
  }' | jq '.'

echo -e "\n✅ API tests complete!"
