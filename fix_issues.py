"""
Fix multiple issues:
1. Create demo client with known credentials
2. Check leads in database
3. Check client creation issues
"""
import sys
sys.path.insert(0, '/root/leadex-project')

from app.core.database import SessionLocal, engine
from sqlalchemy import text
from app.core.security import get_password_hash
import uuid

db = SessionLocal()

print("=" * 60)
print("FIXING ISSUES")
print("=" * 60)

# Issue 1: Create/Update demo client with email/password
print("\n1. Checking demo client...")
result = db.execute(text("SELECT * FROM clients WHERE email = 'client@example.com'")).fetchone()

if result:
    print(f"   Client exists: {result[1]} (ID: {result[0]})")
    print(f"   Token: {result[18]}")
    print(f"   Has password: {result[19] is not None}")
else:
    print("   Creating demo client...")
    token = str(uuid.uuid4())
    hashed_pw = get_password_hash('client123')

    db.execute(text("""
        INSERT INTO clients (
            id, name, email, phone_number, percentage, credits_balance,
            password_protected_link_token, client_password, status,
            accept_webhook, accept_email, accept_sms, accept_sheets,
            credit_cost_per_lead, priority_order, weight,
            created_at, updated_at
        ) VALUES (
            :id, :name, :email, :phone, :percentage, :credits,
            :token, :password, :status,
            :webhook, :email_flag, :sms, :sheets,
            :cost, :priority, :weight,
            NOW(), NOW()
        )
    """), {
        'id': str(uuid.uuid4()),
        'name': 'Demo Client',
        'email': 'client@example.com',
        'phone': '+971501234567',
        'percentage': 50.0,
        'credits': 1000.0,
        'token': token,
        'password': hashed_pw,
        'status': 'active',
        'webhook': True,
        'email_flag': True,
        'sms': True,
        'sheets': False,
        'cost': 1.0,
        'priority': 1,
        'weight': 1
    })
    db.commit()
    print(f"   ✓ Client created with token: {token}")
    print(f"   ✓ Email: client@example.com")
    print(f"   ✓ Password: client123")

# Issue 2: Check leads
print("\n2. Checking leads...")
leads_count = db.execute(text("SELECT COUNT(*) FROM assets")).scalar()
print(f"   Total leads in database: {leads_count}")

if leads_count > 0:
    recent_leads = db.execute(text("""
        SELECT id, mobile, name, email, created_at
        FROM assets
        ORDER BY created_at DESC
        LIMIT 5
    """)).fetchall()

    print("   Recent leads:")
    for lead in recent_leads:
        print(f"     - {lead[2] or 'N/A'}: {lead[1]} ({lead[4]})")

# Issue 3: Check clients
print("\n3. Checking all clients...")
clients = db.execute(text("SELECT id, name, email, percentage, credits_balance, status FROM clients")).fetchall()
print(f"   Total clients: {len(clients)}")
for client in clients:
    print(f"     - {client[1]}: {client[2] or 'no email'} ({client[3]}%) - {client[4]} credits - {client[5]}")

# Issue 4: Check for duplicate "Hamed Test" clients
print("\n4. Checking for duplicate clients...")
duplicates = db.execute(text("""
    SELECT name, COUNT(*) as count
    FROM clients
    GROUP BY name
    HAVING COUNT(*) > 1
""")).fetchall()

if duplicates:
    print("   ⚠ Duplicate clients found:")
    for dup in duplicates:
        print(f"     - {dup[0]}: {dup[1]} instances")
        # Get all instances
        instances = db.execute(text("SELECT id, email, created_at FROM clients WHERE name = :name"), {'name': dup[0]}).fetchall()
        for inst in instances:
            print(f"       • ID: {inst[0]}, Email: {inst[1] or 'none'}, Created: {inst[2]}")
else:
    print("   No duplicates found")

# Issue 5: Check stored leads
print("\n5. Checking stored leads (waiting for credits)...")
stored_count = db.execute(text("SELECT COUNT(*) FROM stored_leads")).scalar()
print(f"   Stored leads: {stored_count}")

if stored_count > 0:
    stored = db.execute(text("""
        SELECT sl.id, a.mobile, a.name, sl.reason, sl.created_at
        FROM stored_leads sl
        JOIN assets a ON sl.lead_id = a.id
        ORDER BY sl.created_at DESC
        LIMIT 5
    """)).fetchall()

    print("   Recent stored leads:")
    for s in stored:
        print(f"     - {s[2] or 'N/A'}: {s[1]} - Reason: {s[3]} ({s[4]})")

db.close()

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)
print("1. Use token from database for client login")
print("2. Check admin-leads.html API endpoint")
print("3. Clean up duplicate 'Hamed Test' clients")
print("4. Review stored_leads logic for credit management")
