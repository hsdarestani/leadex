"""
Phase 6 Tests: Client Portal
Test client authentication, portal access, and lead export
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.models import Client, Asset, Delivery
from app.core.database import SessionLocal
from datetime import datetime, timedelta
import uuid


def test_client_token_generation():
    """Test 1: Client password-protected link token generation"""
    print("\n" + "="*70)
    print("TEST 1: Client Password-Protected Link Token Generation")
    print("="*70)
    
    # Generate a unique token
    token = str(uuid.uuid4())
    print(f"✅ Generated token: {token[:20]}...")
    
    # Hash a password
    password = "client123"
    hashed = hash_password(password)
    print(f"✅ Hashed password: {hashed[:30]}...")
    
    # Verify password
    is_valid = verify_password(password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    assert is_valid, "Password verification failed"
    print("✅ TEST 1 PASSED")
    return True


def test_client_jwt_token():
    """Test 2: Client JWT token creation and validation"""
    print("\n" + "="*70)
    print("TEST 2: Client JWT Token Creation and Validation")
    print("="*70)
    
    client_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    
    # Create JWT token
    jwt_token = create_access_token(
        data={"sub": client_id, "type": "client", "token": token},
        expires_delta=timedelta(days=7)
    )
    print(f"✅ Created JWT token: {jwt_token[:50]}...")
    
    # Decode token
    payload = decode_access_token(jwt_token)
    print(f"✅ Decoded payload: {payload}")
    
    assert payload is not None, "Token decoding failed"
    assert payload.get("sub") == client_id, "Client ID mismatch"
    assert payload.get("type") == "client", "Token type mismatch"
    assert payload.get("token") == token, "Token mismatch"
    
    print("✅ TEST 2 PASSED")
    return True


def test_client_database_operations():
    """Test 3: Client database operations"""
    print("\n" + "="*70)
    print("TEST 3: Client Database Operations")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Create a test client
        token = str(uuid.uuid4())
        password = hash_password("testpass123")
        
        client = Client(
            name="Test Client Portal",
            email="testclient@example.com",
            phone_number="+1234567890",
            percentage=20.0,
            credits_balance=100.0,
            credit_cost_per_lead=1.0,
            password_protected_link_token=token,
            client_password=password,
            status="active"
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        print(f"✅ Created client: {client.name} (ID: {client.id})")
        print(f"✅ Token: {client.password_protected_link_token[:20]}...")
        print(f"✅ Credits: {client.credits_balance}")
        
        # Verify we can find client by token
        found_client = db.query(Client).filter(
            Client.password_protected_link_token == token
        ).first()
        
        assert found_client is not None, "Client not found by token"
        assert found_client.id == client.id, "Client ID mismatch"
        
        print(f"✅ Found client by token: {found_client.name}")
        
        # Verify password
        is_valid = verify_password("testpass123", found_client.client_password)
        assert is_valid, "Password verification failed"
        print("✅ Password verification successful")
        
        # Clean up
        db.delete(client)
        db.commit()
        print("✅ Cleaned up test client")
        
        print("✅ TEST 3 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def test_api_imports():
    """Test 4: API imports"""
    print("\n" + "="*70)
    print("TEST 4: API Imports")
    print("="*70)
    
    try:
        from app.api.client import router
        print("✅ Client router imported")
        
        from app.api.client.auth import router as auth_router
        print("✅ Client auth router imported")
        
        from app.api.client.portal import router as portal_router
        print("✅ Client portal router imported")
        
        from app.api.client.dependencies import get_current_client
        print("✅ Client dependencies imported")
        
        print("✅ TEST 4 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {str(e)}")
        return False


def main():
    """Run all Phase 6 tests"""
    print("\n" + "="*70)
    print("PHASE 6 TESTS: CLIENT PORTAL")
    print("="*70)
    
    tests = [
        test_client_token_generation,
        test_client_jwt_token,
        test_client_database_operations,
        test_api_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

