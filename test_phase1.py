"""
Quick test to verify Phase 1 is working correctly
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import AdminUser, Campaign, LandingPage, Client
from app.core.security import verify_password, get_password_hash, generate_token
import uuid


def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    db = SessionLocal()
    try:
        # Query admin user
        admin = db.query(AdminUser).filter(AdminUser.email == "admin@leadex.com").first()
        assert admin is not None, "Admin user not found"
        print(f"✅ Admin user found: {admin.email}")
        
        # Verify password
        assert verify_password("admin123", admin.password), "Password verification failed"
        print("✅ Password verification works")
        
        # Query campaign
        campaign = db.query(Campaign).filter(Campaign.name == "Default Campaign").first()
        assert campaign is not None, "Campaign not found"
        print(f"✅ Campaign found: {campaign.name}")
        
        # Query landing page
        landing = db.query(LandingPage).filter(LandingPage.slug == "default").first()
        assert landing is not None, "Landing page not found"
        print(f"✅ Landing page found: {landing.slug}")
        
        print("\n✅ All database queries successful!")
        
    finally:
        db.close()


def test_create_client():
    """Test creating a client"""
    print("\n🔍 Testing client creation...")
    db = SessionLocal()
    try:
        # Create a test client
        token = generate_token()
        client = Client(
            id=uuid.uuid4(),
            name="Test Client",
            phone_number="+971501234567",
            email="test@example.com",
            percentage=30.0,
            credits_balance=100.0,
            accept_webhook=True,
            webhook_url="https://example.com/webhook",
            status="active",
            password_protected_link_token=token,
            client_password=get_password_hash("client123")
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
        print(f"✅ Client created: {client.name} (ID: {client.id})")
        print(f"   - Percentage: {client.percentage}%")
        print(f"   - Credits: {client.credits_balance}")
        print(f"   - Token: {client.password_protected_link_token[:20]}...")
        
        # Clean up
        db.delete(client)
        db.commit()
        print("✅ Test client deleted (cleanup)")
        
    finally:
        db.close()


def test_security_functions():
    """Test security functions"""
    print("\n🔍 Testing security functions...")
    
    # Test password hashing
    password = "test123"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed: {hashed[:30]}...")
    
    # Test password verification
    assert verify_password(password, hashed), "Password verification failed"
    print("✅ Password verification works")
    
    # Test wrong password
    assert not verify_password("wrong", hashed), "Wrong password should fail"
    print("✅ Wrong password correctly rejected")
    
    # Test token generation
    token = generate_token()
    print(f"✅ Token generated: {token[:30]}...")
    assert len(token) > 20, "Token too short"
    print("✅ Token length valid")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 VERIFICATION TEST")
    print("=" * 60)
    
    try:
        test_database_connection()
        test_create_client()
        test_security_functions()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Phase 1 is fully functional and ready for Phase 2!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
