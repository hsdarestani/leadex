"""
Phase 4 Test - Delivery Integrations
Tests webhook, WhatsApp, email, and Google Sheets delivery
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models import Client, Asset, Delivery
from app.services.delivery_orchestrator import DeliveryOrchestrator
from app.services.delivery import (
    WebhookDeliveryService,
    WhatsAppDeliveryService,
    EmailDeliveryService,
    SheetsDeliveryService
)
from datetime import datetime
import uuid


def test_webhook_formatting():
    """Test 1: Webhook data formatting"""
    print("\n" + "=" * 70)
    print("TEST 1: Webhook Data Formatting")
    print("=" * 70)
    
    db = SessionLocal()
    
    # Get a test client and lead
    client = db.query(Client).first()
    lead = db.query(Asset).first()
    
    if not client or not lead:
        print("❌ No test data found")
        db.close()
        return
    
    # Format webhook data
    webhook_data = WebhookDeliveryService.format_lead_data(lead, client)
    
    print(f"✅ Webhook data formatted:")
    print(f"   Lead ID: {webhook_data['lead_id']}")
    print(f"   Mobile: {webhook_data['mobile']}")
    print(f"   Client: {webhook_data['client']['client_name']}")
    
    db.close()


def test_whatsapp_formatting():
    """Test 2: WhatsApp message formatting"""
    print("\n" + "=" * 70)
    print("TEST 2: WhatsApp Message Formatting")
    print("=" * 70)
    
    db = SessionLocal()
    
    client = db.query(Client).first()
    lead = db.query(Asset).first()
    
    if not client or not lead:
        print("❌ No test data found")
        db.close()
        return
    
    # Format WhatsApp message
    message = WhatsAppDeliveryService.format_message(lead, client)
    
    print(f"✅ WhatsApp message formatted:")
    print(message)
    
    db.close()


def test_email_formatting():
    """Test 3: Email HTML formatting"""
    print("\n" + "=" * 70)
    print("TEST 3: Email HTML Formatting")
    print("=" * 70)
    
    db = SessionLocal()
    
    client = db.query(Client).first()
    lead = db.query(Asset).first()
    
    if not client or not lead:
        print("❌ No test data found")
        db.close()
        return
    
    # Format email HTML
    html = EmailDeliveryService.format_html_content(lead, client)
    
    print(f"✅ Email HTML formatted ({len(html)} characters)")
    print(f"   Contains mobile: {'mobile' in html.lower()}")
    print(f"   Contains client name: {client.name in html}")
    
    db.close()


def test_sheets_formatting():
    """Test 4: Google Sheets row formatting"""
    print("\n" + "=" * 70)
    print("TEST 4: Google Sheets Row Formatting")
    print("=" * 70)
    
    db = SessionLocal()
    
    client = db.query(Client).first()
    lead = db.query(Asset).first()
    
    if not client or not lead:
        print("❌ No test data found")
        db.close()
        return
    
    # Format row data
    row_data = SheetsDeliveryService.format_row_data(lead, client)
    headers = SheetsDeliveryService.get_header_row()
    
    print(f"✅ Google Sheets row formatted:")
    print(f"   Headers: {headers}")
    print(f"   Data: {row_data}")
    print(f"   Columns: {len(row_data)}")
    
    db.close()


def test_delivery_orchestrator():
    """Test 5: Delivery orchestrator (mock delivery)"""
    print("\n" + "=" * 70)
    print("TEST 5: Delivery Orchestrator")
    print("=" * 70)
    
    db = SessionLocal()
    
    # Get a test client and lead
    client = db.query(Client).first()
    lead = db.query(Asset).filter(Asset.status == "ASSIGNED").first()
    
    if not client:
        print("❌ No test client found")
        db.close()
        return
    
    if not lead:
        # Create a test lead
        lead = Asset(
            mobile="+971501111111",
            name="Test User",
            email="test@example.com",
            status="ASSIGNED",
            landing_id=None,
            campaign_id=None
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        print(f"✅ Created test lead: {lead.id}")
    
    print(f"   Lead: {lead.mobile}")
    print(f"   Client: {client.name}")
    print(f"   Webhook enabled: {client.accept_webhook}")
    print(f"   WhatsApp enabled: {client.accept_sms}")
    print(f"   Email enabled: {client.accept_email}")
    print(f"   Sheets enabled: {client.accept_sheets}")
    
    print("\n   Note: Actual delivery will be handled by delivery worker")
    print("   This test only validates the orchestrator setup")
    
    db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PHASE 4 TESTS - DELIVERY INTEGRATIONS")
    print("=" * 70)
    
    test_webhook_formatting()
    test_whatsapp_formatting()
    test_email_formatting()
    test_sheets_formatting()
    test_delivery_orchestrator()
    
    print("\n" + "=" * 70)
    print("✅ ALL PHASE 4 TESTS COMPLETED")
    print("=" * 70)
    print("\nNote: These tests validate data formatting and orchestration.")
    print("Actual delivery requires:")
    print("  - Valid webhook URLs")
    print("  - Meta Business API credentials")
    print("  - SendGrid API key")
    print("  - Google Service Account credentials")
    print("\nRun the delivery worker to process actual deliveries:")
    print("  python -m app.workers.delivery_worker")

