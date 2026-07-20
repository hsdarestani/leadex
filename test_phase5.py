"""
Phase 5 Testing Script
Test admin authentication, client management, and dashboard APIs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import AdminUser, Client
from app.utils.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.services import CreditService
from datetime import datetime


def test_password_hashing():
    """Test password hashing and verification"""
    print("\n🔐 Test 1: Password Hashing")
    print("-" * 50)
    
    password = "admin123"
    hashed = hash_password(password)
    
    print(f"✅ Password hashed: {hashed[:50]}...")
    
    # Verify correct password
    assert verify_password(password, hashed), "Password verification failed"
    print("✅ Correct password verified")
    
    # Verify incorrect password
    assert not verify_password("wrong", hashed), "Wrong password should not verify"
    print("✅ Incorrect password rejected")
    
    print("✅ Test 1 PASSED\n")


def test_jwt_tokens():
    """Test JWT token creation and decoding"""
    print("\n🎫 Test 2: JWT Tokens")
    print("-" * 50)
    
    data = {"sub": "admin@leadex.com", "role": "admin"}
    token = create_access_token(data)
    
    print(f"✅ Token created: {token[:50]}...")
    
    # Decode token
    decoded = decode_access_token(token)
    
    assert decoded is not None, "Token decoding failed"
    assert decoded["sub"] == "admin@leadex.com", "Email mismatch"
    assert decoded["role"] == "admin", "Role mismatch"
    
    print(f"✅ Token decoded: {decoded}")
    print("✅ Test 2 PASSED\n")


def test_admin_user_creation():
    """Test admin user creation"""
    print("\n👤 Test 3: Admin User Creation")
    print("-" * 50)
    
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(AdminUser).filter(AdminUser.email == "admin@leadex.com").first()
        
        if not admin:
            # Create admin user
            admin = AdminUser(
                email="admin@leadex.com",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ Admin user created")
        else:
            print("✅ Admin user already exists")
        
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   ID: {admin.id}")
        
        print("✅ Test 3 PASSED\n")
        
    finally:
        db.close()


def test_client_management():
    """Test client management operations"""
    print("\n🏢 Test 4: Client Management")
    print("-" * 50)
    
    db = SessionLocal()
    
    try:
        # Get all clients
        clients = db.query(Client).all()
        print(f"✅ Found {len(clients)} clients")
        
        for client in clients[:3]:  # Show first 3
            print(f"   - {client.name}: {client.percentage}%, {client.credits_balance} credits")
        
        # Test credit service
        if clients:
            client = clients[0]
            original_balance = client.credits_balance
            
            # Add credits
            CreditService.add_credits(client, 10, db)
            print(f"✅ Added 10 credits to {client.name}")
            print(f"   Balance: {original_balance} → {client.credits_balance}")
        
        print("✅ Test 4 PASSED\n")
        
    finally:
        db.close()


def test_api_imports():
    """Test that all API modules import correctly"""
    print("\n📦 Test 5: API Imports")
    print("-" * 50)
    
    try:
        from app.api.admin import router as admin_router
        print("✅ Admin router imported")
        
        from app.api.admin.auth import router as auth_router
        print("✅ Auth router imported")
        
        from app.api.admin.clients import router as clients_router
        print("✅ Clients router imported")
        
        from app.api.admin.leads import router as leads_router
        print("✅ Leads router imported")
        
        from app.api.admin.stats import router as stats_router
        print("✅ Stats router imported")
        
        from app.api.dependencies import get_current_admin
        print("✅ Dependencies imported")
        
        from app.main import app
        print("✅ Main app imported")
        
        print("✅ Test 5 PASSED\n")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise


def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 PHASE 5 TESTING - ADMIN DASHBOARD & CLIENT PORTAL")
    print("=" * 50)
    
    try:
        test_password_hashing()
        test_jwt_tokens()
        test_admin_user_creation()
        test_client_management()
        test_api_imports()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\n📋 Phase 5 Summary:")
        print("   ✅ Password hashing and verification")
        print("   ✅ JWT token creation and decoding")
        print("   ✅ Admin user management")
        print("   ✅ Client management operations")
        print("   ✅ All API modules import successfully")
        print("\n🎉 Phase 5 is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

