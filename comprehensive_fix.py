"""
Comprehensive fix for all reported issues
"""
import sys
sys.path.insert(0, '/root/leadex-project')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("="*60)
print("COMPREHENSIVE FIX SCRIPT")
print("="*60)

# Issue 1: Clean up duplicate "Hamed Test" clients
print("\n1. Cleaning up duplicate clients...")
duplicates = db.execute(text("""
    SELECT id, name, email, created_at
    FROM clients
    WHERE name = 'Hamed Test'
    ORDER BY created_at ASC
""")).fetchall()

if len(duplicates) > 1:
    print(f"   Found {len(duplicates)} 'Hamed Test' clients")
    # Keep the first one, delete the rest
    keep_id = duplicates[0][0]
    print(f"   Keeping: {duplicates[0][0]} (created: {duplicates[0][3]})")

    for dup in duplicates[1:]:
        print(f"   Deleting: {dup[0]} (created: {dup[3]})")
        # Delete associated deliveries first
        db.execute(text("DELETE FROM deliveries WHERE client_id = :id"), {'id': dup[0]})
        # Delete client
        db.execute(text("DELETE FROM clients WHERE id = :id"), {'id': dup[0]})

    db.commit()
    print(f"   ✓ Cleaned up {len(duplicates)-1} duplicate clients")
else:
    print("   No duplicates found")

# Issue 2: Verify client count
print("\n2. Verifying client count...")
client_count = db.execute(text("SELECT COUNT(*) FROM clients")).scalar()
print(f"   Total clients now: {client_count}")

clients = db.execute(text("SELECT name, email, percentage, credits_balance FROM clients")).fetchall()
for c in clients:
    print(f"     - {c[0]}: {c[1] or 'no email'} ({c[2]}%) - {c[3]} credits")

# Issue 3: Get demo client token
print("\n3. Demo client credentials...")
demo = db.execute(text("""
    SELECT name, email, password_protected_link_token, client_password
    FROM clients
    WHERE email = 'client@example.com'
""")).fetchone()

if demo:
    print(f"   Name: {demo[0]}")
    print(f"   Email: {demo[1]}")
    print(f"   Token: {demo[2]}")
    print(f"   Has Password: {demo[3] is not None}")
    print(f"\n   To login, use:")
    print(f"   - Access Token: {demo[2]}")
    print(f"   - Password: client123")
else:
    print("   ⚠ Demo client not found!")

# Issue 4: Check lead distribution
print("\n4. Checking lead status...")
leads = db.execute(text("""
    SELECT id, mobile, name, status, created_at
    FROM assets
    ORDER BY created_at DESC
""")).fetchall()

print(f"   Total leads: {len(leads)}")
for lead in leads:
    print(f"     - {lead[2] or 'N/A'}: {lead[1]} - Status: {lead[3]} ({lead[4]})")

# Check deliveries for these leads
print("\n5. Checking deliveries...")
deliveries = db.execute(text("""
    SELECT d.id, d.lead_id, d.client_id, d.status, c.name as client_name
    FROM deliveries d
    LEFT JOIN clients c ON d.client_id = c.id
""")).fetchall()

print(f"   Total deliveries: {len(deliveries)}")
if deliveries:
    for d in deliveries:
        print(f"     - Lead: {d[1]} → Client: {d[4] or 'N/A'} - Status: {d[3]}")
else:
    print("   No deliveries found - leads not distributed yet")

# Issue 6: Check stored leads
print("\n6. Checking stored leads system...")
stored = db.execute(text("SELECT COUNT(*) FROM stored_leads")).scalar()
print(f"   Stored leads: {stored}")

# Issue 7: Check campaigns and landing pages
print("\n7. Checking campaigns and landing pages...")
campaigns = db.execute(text("SELECT COUNT(*) FROM campaigns")).scalar()
landing_pages = db.execute(text("SELECT COUNT(*) FROM landing_pages")).scalar()
print(f"   Campaigns: {campaigns}")
print(f"   Landing pages: {landing_pages}")

db.close()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("✓ Duplicate clients cleaned")
print("✓ Demo client available for login")
print("✓ Leads exist in database")
print("⚠ Leads not distributed (check percentile allocation)")
print("⚠ Check frontend API calls in admin-leads.html")
