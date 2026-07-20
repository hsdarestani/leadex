"""
Create a test client for portal testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Client
from app.utils.auth import hash_password
import uuid

db = SessionLocal()

try:
    # Create a test client
    token = "test-client-token-123"
    password = hash_password("password123")
    
    # Check if client already exists
    existing = db.query(Client).filter(Client.password_protected_link_token == token).first()
    if existing:
        print(f"Client already exists: {existing.name}")
        print(f"Token: {existing.password_protected_link_token}")
        print(f"Client ID: {existing.id}")
    else:
        client = Client(
            name="Demo Client",
            email="demo@example.com",
            phone_number="+1234567890",
            percentage=25.0,
            credits_balance=500.0,
            credit_cost_per_lead=1.0,
            password_protected_link_token=token,
            client_password=password,
            status="active",
            accept_webhook=True,
            webhook_url="https://example.com/webhook"
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        print("✅ Test client created successfully!")
        print(f"Client Name: {client.name}")
        print(f"Client ID: {client.id}")
        print(f"Token: {client.password_protected_link_token}")
        print(f"Password: password123")
        print(f"Credits: {client.credits_balance}")
        print(f"\nLogin URL: http://213.21.235.48/client-login.html")
        print(f"Use token: {token}")
        print(f"Use password: password123")
        
finally:
    db.close()

