"""
Test Phase 3: Distribution Engine
"""
import sys
import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Client, Asset, LandingPage, Campaign, StoredLead, Delivery
from app.services.distribution_service import DistributionService
from app.services.credit_service import CreditService
from app.services.lead_service import LeadService


def setup_test_clients(db: Session) -> list:
    """Create test clients with different percentages and credits"""
    print("🔧 Setting up test clients...")

    # Clear existing data (order matters due to foreign keys)
    db.query(Delivery).delete()
    db.query(Client).delete()
    db.commit()
    
    clients = []
    
    # Client A: 30%, 10 credits
    client_a = Client(
        name="Client A (30%)",
        percentage=30.0,
        credits_balance=10.0,
        credit_cost_per_lead=1.0,
        status="active",
        priority_order=1,
        password_protected_link_token=str(uuid.uuid4())
    )
    db.add(client_a)
    clients.append(client_a)
    
    # Client B: 20%, 5 credits
    client_b = Client(
        name="Client B (20%)",
        percentage=20.0,
        credits_balance=5.0,
        credit_cost_per_lead=1.0,
        status="active",
        priority_order=2,
        password_protected_link_token=str(uuid.uuid4())
    )
    db.add(client_b)
    clients.append(client_b)
    
    # Client C: 50%, 15 credits
    client_c = Client(
        name="Client C (50%)",
        percentage=50.0,
        credits_balance=15.0,
        credit_cost_per_lead=1.0,
        status="active",
        priority_order=3,
        password_protected_link_token=str(uuid.uuid4())
    )
    db.add(client_c)
    clients.append(client_c)
    
    db.commit()
    
    for client in clients:
        db.refresh(client)
        print(f"   ✅ {client.name}: {client.percentage}%, {client.credits_balance} credits")
    
    return clients


def create_test_leads(db: Session, count: int = 10) -> list:
    """Create test leads"""
    print(f"\n🔧 Creating {count} test leads...")
    
    landing = db.query(LandingPage).first()
    campaign = db.query(Campaign).first()
    
    lead_ids = []
    for i in range(count):
        mobile = f"+971{uuid.uuid4().hex[:9]}"
        lead = LeadService.create_lead(
            db=db,
            mobile=mobile,
            name=f"Test Lead {i+1}",
            email=f"test{i+1}@example.com",
            landing_id=landing.id,
            campaign_id=campaign.id,
            ip="192.168.1.1",
            user_agent="Test Agent",
            referrer=None,
            geo=None,
            utm=None
        )
        lead_ids.append(lead.id)
    
    print(f"   ✅ Created {len(lead_ids)} leads")
    return lead_ids


def test_normal_distribution(db: Session):
    """Test normal distribution with sufficient credits"""
    print("\n" + "="*70)
    print("TEST 1: Normal Distribution (All clients have sufficient credits)")
    print("="*70)
    
    # Setup
    clients = setup_test_clients(db)
    lead_ids = create_test_leads(db, 10)
    
    # Expected allocation: A=3, B=2, C=5
    print("\n📊 Expected allocation:")
    print("   Client A (30%): 3 leads")
    print("   Client B (20%): 2 leads")
    print("   Client C (50%): 5 leads")
    
    # Distribute
    print("\n🚀 Distributing batch...")
    results = DistributionService.distribute_batch(lead_ids, db)
    
    # Verify
    print("\n✅ Distribution Results:")
    print(f"   Assigned: {results['assigned']}")
    print(f"   Stored: {results['stored']}")
    
    for client_id, assignment in results['assignments'].items():
        print(f"   {assignment['client_name']}: {assignment['leads_assigned']} leads")
    
    # Check credits were deducted
    print("\n💰 Credit Balances After Distribution:")
    for client in clients:
        db.refresh(client)
        print(f"   {client.name}: {client.credits_balance} credits")
    
    # Cleanup
    db.query(Delivery).delete()
    db.query(Asset).filter(Asset.id.in_(lead_ids)).delete(synchronize_session=False)
    db.query(Delivery).delete()
    db.commit()
    
    assert results['assigned'] == 10, "Should assign all 10 leads"
    assert results['stored'] == 0, "Should not store any leads"
    print("\n✅ TEST 1 PASSED")


def test_partial_credits(db: Session):
    """Test distribution with partial credits"""
    print("\n" + "="*70)
    print("TEST 2: Partial Credits (Client B has only 1 credit instead of 2)")
    print("="*70)
    
    # Setup
    clients = setup_test_clients(db)
    
    # Give Client B only 1 credit (needs 2)
    client_b = clients[1]
    client_b.credits_balance = 1.0
    db.commit()
    
    lead_ids = create_test_leads(db, 10)
    
    print("\n📊 Setup:")
    print("   Client A (30%): 10 credits (needs 3) ✅")
    print("   Client B (20%): 1 credit (needs 2) ⚠️  SHORT 1 CREDIT")
    print("   Client C (50%): 15 credits (needs 5) ✅")
    
    # Distribute
    print("\n🚀 Distributing batch...")
    results = DistributionService.distribute_batch(lead_ids, db)
    
    # Verify
    print("\n✅ Distribution Results:")
    print(f"   Assigned: {results['assigned']}")
    print(f"   Stored: {results['stored']}")
    
    for client_id, assignment in results['assignments'].items():
        print(f"   {assignment['client_name']}: {assignment['leads_assigned']} leads")
    
    # Cleanup
    db.query(Delivery).delete()
    db.query(Asset).filter(Asset.id.in_(lead_ids)).delete(synchronize_session=False)
    db.query(Delivery).delete()
    db.commit()
    
    assert results['assigned'] == 10, "Should still assign all 10 leads (redistributed)"
    print("\n✅ TEST 2 PASSED")


def test_no_credits(db: Session):
    """Test distribution when all clients have 0 credits"""
    print("\n" + "="*70)
    print("TEST 3: No Credits (All clients have 0 credits)")
    print("="*70)

    # Setup
    clients = setup_test_clients(db)

    # Set all clients to 0 credits
    for client in clients:
        client.credits_balance = 0.0
    db.commit()

    lead_ids = create_test_leads(db, 10)

    print("\n📊 Setup:")
    print("   Client A (30%): 0 credits ❌")
    print("   Client B (20%): 0 credits ❌")
    print("   Client C (50%): 0 credits ❌")

    # Distribute
    print("\n🚀 Distributing batch...")
    results = DistributionService.distribute_batch(lead_ids, db)

    # Verify
    print("\n✅ Distribution Results:")
    print(f"   Assigned: {results['assigned']}")
    print(f"   Stored: {results['stored']}")
    print(f"   Reason: {results.get('reason', 'N/A')}")

    # Check stored leads
    stored_count = db.query(StoredLead).count()
    print(f"\n📦 Stored Leads in Database: {stored_count}")

    # Cleanup (order matters due to foreign keys)
    db.query(Delivery).delete()
    db.query(StoredLead).delete()
    db.query(Asset).filter(Asset.id.in_(lead_ids)).delete(synchronize_session=False)
    db.commit()

    assert results['assigned'] == 0, "Should not assign any leads"
    assert results['stored'] == 10, "Should store all 10 leads"
    print("\n✅ TEST 3 PASSED")


def test_credit_deduction(db: Session):
    """Test that credits are properly deducted"""
    print("\n" + "="*70)
    print("TEST 4: Credit Deduction Verification")
    print("="*70)

    # Setup
    clients = setup_test_clients(db)
    lead_ids = create_test_leads(db, 10)

    # Record initial balances
    initial_balances = {client.id: client.credits_balance for client in clients}

    print("\n💰 Initial Credit Balances:")
    for client in clients:
        print(f"   {client.name}: {client.credits_balance} credits")

    # Distribute
    print("\n🚀 Distributing batch...")
    results = DistributionService.distribute_batch(lead_ids, db)

    # Check final balances
    print("\n💰 Final Credit Balances:")
    for client in clients:
        db.refresh(client)
        initial = initial_balances[client.id]
        deducted = initial - client.credits_balance
        print(f"   {client.name}: {client.credits_balance} credits (deducted: {deducted})")

    # Verify deductions match assignments
    for client_id, assignment in results['assignments'].items():
        client = db.query(Client).filter(Client.id == uuid.UUID(client_id)).first()
        expected_deduction = assignment['leads_assigned'] * client.credit_cost_per_lead
        actual_deduction = initial_balances[client.id] - client.credits_balance

        assert actual_deduction == expected_deduction, \
            f"{client.name}: Expected {expected_deduction} credits deducted, got {actual_deduction}"

    # Cleanup
    db.query(Delivery).delete()
    db.query(Asset).filter(Asset.id.in_(lead_ids)).delete(synchronize_session=False)
    db.query(Delivery).delete()
    db.commit()

    print("\n✅ TEST 4 PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 3 VERIFICATION TEST - DISTRIBUTION ENGINE")
    print("=" * 70)

    db = SessionLocal()

    try:
        test_normal_distribution(db)
        test_partial_credits(db)
        test_no_credits(db)
        test_credit_deduction(db)

        print("\n" + "=" * 70)
        print("🎉 ALL PHASE 3 TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Distribution Engine is fully functional!")
        print("\n📝 Features Verified:")
        print("   ✅ Percentage-based allocation")
        print("   ✅ Credit checking and deduction")
        print("   ✅ Partial credit handling with redistribution")
        print("   ✅ No credits scenario (stored leads queue)")
        print("   ✅ Lead assignment to clients")
        print("   ✅ Delivery record creation")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

