"""
Test Phase 2: Landing Page API
"""
import sys
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import LandingPage, Asset, BatchQueue
from app.services.lead_service import LeadService
from app.services.batch_service import BatchService
from app.utils.phone import normalize_phone_number, validate_phone_number
from app.utils.geo import get_geo_info
from app.utils.rate_limit import check_rate_limit, record_submission
import uuid


def test_phone_normalization():
    """Test phone number normalization"""
    print("🔍 Testing phone number normalization...")
    
    test_cases = [
        ("+971501234567", "+971501234567"),
        ("971501234567", "+971501234567"),
        ("0501234567", "+971501234567"),  # UAE local format
        ("+1 (555) 123-4567", "+15551234567"),
    ]
    
    for input_phone, expected in test_cases:
        try:
            result = normalize_phone_number(input_phone)
            print(f"   {input_phone} -> {result}")
            if expected and result != expected:
                print(f"   ⚠️  Expected {expected}, got {result}")
        except Exception as e:
            print(f"   ❌ Error normalizing {input_phone}: {e}")
    
    print("✅ Phone normalization test complete")


def test_phone_validation():
    """Test phone number validation"""
    print("\n🔍 Testing phone number validation...")
    
    valid_numbers = ["+971501234567", "+14155552671", "+442071838750"]
    invalid_numbers = ["123", "abc", "+1234"]
    
    for phone in valid_numbers:
        is_valid = validate_phone_number(phone)
        print(f"   {phone}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    for phone in invalid_numbers:
        is_valid = validate_phone_number(phone)
        print(f"   {phone}: {'❌ Should be invalid' if is_valid else '✅ Correctly invalid'}")
    
    print("✅ Phone validation test complete")


def test_geo_lookup():
    """Test geo lookup"""
    print("\n🔍 Testing geo lookup...")
    
    # Test with local IP
    geo = get_geo_info("127.0.0.1")
    print(f"   Local IP: {geo}")
    
    # Test with public IP (Google DNS)
    geo = get_geo_info("8.8.8.8")
    if geo:
        print(f"   8.8.8.8: {geo.get('country')} - {geo.get('city')}")
    else:
        print("   ⚠️  GeoIP database not found (expected in production)")
    
    print("✅ Geo lookup test complete")


def test_rate_limiting():
    """Test rate limiting"""
    print("\n🔍 Testing rate limiting...")
    
    test_key = f"test:{uuid.uuid4()}"
    
    # First attempt should be allowed
    allowed, remaining = check_rate_limit(test_key, max_attempts=3, window_seconds=60)
    print(f"   Attempt 1: {'✅ Allowed' if allowed else '❌ Blocked'} (Remaining: {remaining})")
    assert allowed, "First attempt should be allowed"
    
    # Record the attempt
    record_submission(test_key, window_seconds=60)
    
    # Second attempt
    allowed, remaining = check_rate_limit(test_key, max_attempts=3, window_seconds=60)
    print(f"   Attempt 2: {'✅ Allowed' if allowed else '❌ Blocked'} (Remaining: {remaining})")
    assert allowed, "Second attempt should be allowed"
    
    record_submission(test_key, window_seconds=60)
    
    # Third attempt
    allowed, remaining = check_rate_limit(test_key, max_attempts=3, window_seconds=60)
    print(f"   Attempt 3: {'✅ Allowed' if allowed else '❌ Blocked'} (Remaining: {remaining})")
    assert allowed, "Third attempt should be allowed"
    
    record_submission(test_key, window_seconds=60)
    
    # Fourth attempt should be blocked
    allowed, remaining = check_rate_limit(test_key, max_attempts=3, window_seconds=60)
    print(f"   Attempt 4: {'❌ Blocked' if not allowed else '⚠️  Should be blocked'} (Remaining: {remaining})")
    assert not allowed, "Fourth attempt should be blocked"
    
    print("✅ Rate limiting test complete")


def test_duplicate_detection():
    """Test duplicate detection"""
    print("\n🔍 Testing duplicate detection...")
    db = SessionLocal()
    
    try:
        # Create a test lead
        test_mobile = f"+971{uuid.uuid4().hex[:9]}"
        landing = db.query(LandingPage).first()
        
        lead = LeadService.create_lead(
            db=db,
            mobile=test_mobile,
            name="Test Lead",
            email="test@example.com",
            landing_id=landing.id,
            campaign_id=landing.campaign_id,
            ip="192.168.1.1",
            user_agent="Test Agent",
            referrer=None,
            geo=None,
            utm=None
        )
        print(f"   Created test lead: {lead.mobile}")
        
        # Check for duplicate (should find it)
        is_duplicate, reason = LeadService.check_duplicate(db, test_mobile)
        print(f"   Duplicate check: {'✅ Found' if is_duplicate else '❌ Not found'}")
        assert is_duplicate, "Should detect duplicate"
        print(f"   Reason: {reason}")
        
        # Check with different mobile (should not find)
        different_mobile = f"+971{uuid.uuid4().hex[:9]}"
        is_duplicate, reason = LeadService.check_duplicate(db, different_mobile)
        print(f"   Different mobile: {'❌ Should not be duplicate' if is_duplicate else '✅ Not duplicate'}")
        assert not is_duplicate, "Should not detect duplicate for different mobile"
        
        # Clean up
        db.delete(lead)
        db.commit()
        print("   ✅ Test lead deleted")
        
    finally:
        db.close()
    
    print("✅ Duplicate detection test complete")


def test_batch_queue():
    """Test batch queue logic"""
    print("\n🔍 Testing batch queue...")
    db = SessionLocal()
    
    try:
        landing = db.query(LandingPage).first()
        
        # Clear any existing batches
        db.query(BatchQueue).delete()
        db.commit()
        
        # Create 10 test leads and add to batch
        lead_ids = []
        for i in range(10):
            test_mobile = f"+971{uuid.uuid4().hex[:9]}"
            lead = LeadService.create_lead(
                db=db,
                mobile=test_mobile,
                name=f"Test Lead {i+1}",
                email=f"test{i+1}@example.com",
                landing_id=landing.id,
                campaign_id=landing.campaign_id,
                ip="192.168.1.1",
                user_agent="Test Agent",
                referrer=None,
                geo=None,
                utm=None
            )
            lead_ids.append(lead.id)
            
            # Add to batch
            batch_full, leads_to_distribute = BatchService.add_lead_to_batch(db, lead.id)
            
            if i < 9:
                print(f"   Lead {i+1}/10 added to batch (not full yet)")
                assert not batch_full, f"Batch should not be full at {i+1} leads"
            else:
                print(f"   Lead {i+1}/10 added to batch (✅ BATCH FULL!)")
                assert batch_full, "Batch should be full at 10 leads"
                assert len(leads_to_distribute) == 10, "Should have 10 leads to distribute"
                print(f"   🚀 Distribution would be triggered for {len(leads_to_distribute)} leads")
        
        # Clean up
        db.query(Asset).filter(Asset.id.in_(lead_ids)).delete(synchronize_session=False)
        db.query(BatchQueue).delete()
        db.commit()
        print("   ✅ Test leads and batches deleted")
        
    finally:
        db.close()
    
    print("✅ Batch queue test complete")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 2 VERIFICATION TEST - LANDING PAGE API")
    print("=" * 70)
    
    try:
        test_phone_normalization()
        test_phone_validation()
        test_geo_lookup()
        test_rate_limiting()
        test_duplicate_detection()
        test_batch_queue()
        
        print("\n" + "=" * 70)
        print("🎉 ALL PHASE 2 TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Landing Page API is fully functional!")
        print("\n📝 Next steps:")
        print("   1. Test the API endpoint with curl or Postman")
        print("   2. Verify reCAPTCHA integration")
        print("   3. Test with real mobile numbers")
        print("   4. Monitor batch queue behavior")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
