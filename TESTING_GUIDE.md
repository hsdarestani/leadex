# 🧪 Leadex Testing Guide

## 📋 Table of Contents
1. [Browser Testing](#browser-testing)
2. [API Testing with cURL](#api-testing-with-curl)
3. [Database Verification](#database-verification)
4. [Testing Scenarios](#testing-scenarios)

---

## 🌐 Browser Testing

### **Access URLs:**

**Server IP:** `213.21.235.48`

1. **Test Form (Lead Submission):**
   ```
   http://213.21.235.48/
   ```
   - Beautiful form interface
   - Submit leads with mobile, name, email
   - reCAPTCHA protected (test mode)
   - Real-time feedback

2. **Dashboard (Monitoring):**
   ```
   http://213.21.235.48/dashboard.html
   ```
   - View client statistics
   - Monitor credit balances
   - Track lead distribution
   - Auto-refreshes every 10 seconds

---

## 🔧 API Testing with cURL

### **1. Submit a Single Lead**

```bash
curl -X POST http://213.21.235.48/api/landing/default \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "+971501234567",
    "name": "John Doe",
    "email": "john@example.com",
    "recaptcha_token": "test_token"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Thank you! Your information has been submitted successfully.",
  "lead_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

### **2. Submit 10 Leads (Trigger Distribution)**

```bash
# Submit 10 leads to trigger batch distribution
for i in {1..10}; do
  curl -X POST http://213.21.235.48/api/landing/default \
    -H "Content-Type: application/json" \
    -d "{
      \"mobile\": \"+97150123456$i\",
      \"name\": \"Test User $i\",
      \"email\": \"test$i@example.com\",
      \"recaptcha_token\": \"test_token\"
    }"
  echo ""
  sleep 1
done
```

**What Happens:**
- First 9 leads: Added to batch queue (status: PENDING)
- 10th lead: Triggers distribution
- Distribution engine:
  - Client A (30%) gets 3 leads
  - Client B (20%) gets 2 leads
  - Client C (50%) gets 5 leads
- Credits deducted from each client

---

### **3. Test Duplicate Detection**

```bash
# Submit the same mobile twice
curl -X POST http://213.21.235.48/api/landing/default \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "+971501111111",
    "name": "Duplicate Test",
    "recaptcha_token": "test_token"
  }'

# Wait a second and submit again
sleep 2

curl -X POST http://213.21.235.48/api/landing/default \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "+971501111111",
    "name": "Duplicate Test 2",
    "recaptcha_token": "test_token"
  }'
```

**Expected:** Second submission should be rejected (duplicate within 20 days)

---

### **4. Test Rate Limiting**

```bash
# Submit 6 leads from same IP rapidly
for i in {1..6}; do
  curl -X POST http://213.21.235.48/api/landing/default \
    -H "Content-Type: application/json" \
    -d "{
      \"mobile\": \"+97150999999$i\",
      \"recaptcha_token\": \"test_token\"
    }"
  echo ""
done
```

**Expected:** 6th request should be rate limited (5 per hour per IP)

---

## 💾 Database Verification

### **Check Current System Status**

```bash
cd /root/leadex-project
source venv/bin/activate
python << 'EOF'
from app.core.database import SessionLocal
from app.models import Client, Asset, Delivery, StoredLead, BatchQueue
from sqlalchemy import func

db = SessionLocal()

print("=" * 70)
print("LEADEX SYSTEM STATUS")
print("=" * 70)

# Clients
print("\n📊 CLIENTS:")
clients = db.query(Client).all()
for client in clients:
    print(f"  {client.name}:")
    print(f"    Percentage: {client.percentage}%")
    print(f"    Credits: {client.credits_balance}")
    print(f"    Status: {client.status}")
    
    # Count leads assigned to this client
    assigned = db.query(Delivery).filter(Delivery.client_id == client.id).count()
    print(f"    Leads Assigned: {assigned}")
    print()

# Leads
print("\n📝 LEADS:")
total_leads = db.query(Asset).count()
print(f"  Total Leads: {total_leads}")

by_status = db.query(Asset.status, func.count(Asset.id)).group_by(Asset.status).all()
for status, count in by_status:
    print(f"  {status}: {count}")

# Batch Queue
print("\n📦 BATCH QUEUE:")
batches = db.query(BatchQueue).all()
if batches:
    for batch in batches:
        print(f"  Batch {batch.id}: {batch.lead_count} leads ({batch.status})")
else:
    print("  No batches in queue")

# Stored Leads
print("\n💾 STORED LEADS:")
stored = db.query(StoredLead).count()
print(f"  Total Stored: {stored}")

if stored > 0:
    by_reason = db.query(StoredLead.reason, func.count(StoredLead.id)).group_by(StoredLead.reason).all()
    for reason, count in by_reason:
        print(f"  {reason}: {count}")

# Deliveries
print("\n📬 DELIVERIES:")
total_deliveries = db.query(Delivery).count()
print(f"  Total Delivery Records: {total_deliveries}")

successful = db.query(Delivery).filter(Delivery.success == True).count()
failed = db.query(Delivery).filter(Delivery.success == False).count()
print(f"  Successful: {successful}")
print(f"  Pending/Failed: {failed}")

print("\n" + "=" * 70)

db.close()
EOF
```

---

## 🧪 Testing Scenarios

### **Scenario 1: Normal Distribution (All Clients Have Credits)**

**Setup:**
- Client A: 30%, 10 credits
- Client B: 20%, 5 credits
- Client C: 50%, 15 credits

**Test:** Submit 10 leads

**Expected Result:**
- Client A gets 3 leads (7 credits remaining)
- Client B gets 2 leads (3 credits remaining)
- Client C gets 5 leads (10 credits remaining)
- All 10 leads assigned
- 0 leads stored

---

### **Scenario 2: Partial Credits**

**Setup:**
```bash
# Give Client B only 1 credit
cd /root/leadex-project && source venv/bin/activate && python << 'EOF'
from app.core.database import SessionLocal
from app.models import Client

db = SessionLocal()
client_b = db.query(Client).filter(Client.name.like("%Client B%")).first()
client_b.credits_balance = 1.0
db.commit()
print(f"Client B credits set to: {client_b.credits_balance}")
db.close()
EOF
```

**Test:** Submit 10 leads

**Expected Result:**
- Client A gets 3 leads
- Client B gets 1 lead (only has 1 credit, short 1)
- Client C gets 6 leads (got the redistributed lead)
- All 10 leads still assigned

---

### **Scenario 3: No Credits (Stored Leads)**

**Setup:**
```bash
# Set all clients to 0 credits
cd /root/leadex-project && source venv/bin/activate && python << 'EOF'
from app.core.database import SessionLocal
from app.models import Client

db = SessionLocal()
clients = db.query(Client).all()
for client in clients:
    client.credits_balance = 0.0
db.commit()
print("All clients set to 0 credits")
db.close()
EOF
```

**Test:** Submit 10 leads

**Expected Result:**
- 0 leads assigned
- 10 leads stored with reason "no_credits"
- Stored leads worker will retry every 1 minute

---

### **Scenario 4: Restore Credits**

```bash
cd /root/leadex-project && source venv/bin/activate && python << 'EOF'
from app.core.database import SessionLocal
from app.models import Client

db = SessionLocal()
clients = db.query(Client).all()
for client in clients:
    if "Client A" in client.name:
        client.credits_balance = 10.0
    elif "Client B" in client.name:
        client.credits_balance = 5.0
    elif "Client C" in client.name:
        client.credits_balance = 15.0
db.commit()
print("Credits restored to default values")
db.close()
EOF
```

---

## 🔍 Monitoring Logs

### **View API Logs:**
```bash
tail -f /root/leadex-project/logs/app.log
```

### **View Nginx Access Logs:**
```bash
tail -f /var/log/nginx/access.log
```

### **View Nginx Error Logs:**
```bash
tail -f /var/log/nginx/error.log
```

---

## 📞 Support

If you encounter any issues:
1. Check the logs
2. Verify database status
3. Ensure API is running: `ps aux | grep uvicorn`
4. Restart API if needed: `supervisorctl restart leadex`

---

**Happy Testing!** 🚀

