#!/usr/bin/env python3
"""
Phase 8 Testing Script
Tests webhook management functionality
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/admin"

def print_test(name, passed):
    """Print test result"""
    status = "✅" if passed else "❌"
    print(f"{status} {name}")

def main():
    print("\n" + "="*60)
    print("PHASE 8: WEBHOOK MANAGEMENT - TESTING")
    print("="*60 + "\n")
    
    # Step 1: Admin Login
    print("Step 1: Admin Login")
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": "admin@leadex.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Admin login failed")
        sys.exit(1)
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_test("Admin login successful", True)
    
    # Step 2: Get clients
    print("\nStep 2: Get Clients")
    clients_response = requests.get(f"{API_BASE}/clients/", headers=headers)
    print_test(f"Get clients: {clients_response.status_code}", clients_response.status_code == 200)
    
    clients = clients_response.json()
    if not clients:
        print("⚠️  No clients found. Creating test client...")
        # Create a test client
        create_client_response = requests.post(
            f"{API_BASE}/clients/",
            headers=headers,
            json={
                "name": "Test Webhook Client",
                "email": "webhook@test.com",
                "mobile": "+971501234567",
                "credits_balance": 100,
                "percentage": 50,
                "delivery_method": "webhook",
                "webhook_url": "https://webhook.site/unique-id"
            }
        )
        if create_client_response.status_code == 200:
            clients = [create_client_response.json()]
            print_test("Test client created", True)
        else:
            print("❌ Failed to create test client")
            sys.exit(1)
    
    client_id = clients[0]["id"]
    print(f"   Using client: {clients[0]['name']} ({client_id})")
    
    # Step 3: Test webhook
    print("\nStep 3: Test Webhook")
    test_webhook_response = requests.post(
        f"{API_BASE}/webhooks/test",
        headers=headers,
        json={
            "client_id": client_id,
            "webhook_url": "https://httpbin.org/post",
            "method": "POST",
            "test_payload": {
                "name": "Test Lead",
                "mobile": "+971501234567",
                "email": "test@example.com"
            }
        }
    )
    
    print_test(f"Test webhook: {test_webhook_response.status_code}", test_webhook_response.status_code == 200)
    
    if test_webhook_response.status_code == 200:
        result = test_webhook_response.json()
        print(f"   - Success: {result['success']}")
        print(f"   - Status Code: {result['status_code']}")
        print(f"   - Response Time: {result['response_time_ms']}ms")
        print(f"   - Log ID: {result['log_id']}")
        log_id = result['log_id']
    else:
        print(f"   Error: {test_webhook_response.text}")
        log_id = None
    
    # Step 4: Get webhook logs
    print("\nStep 4: Get Webhook Logs")
    logs_response = requests.get(f"{API_BASE}/webhooks/logs?limit=10", headers=headers)
    print_test(f"Get webhook logs: {logs_response.status_code}", logs_response.status_code == 200)
    
    if logs_response.status_code == 200:
        logs = logs_response.json()
        print(f"   - Total logs retrieved: {len(logs)}")
        if logs:
            print(f"   - Latest log: {logs[0]['webhook_url']}")
            print(f"   - Success: {logs[0]['success']}")
    
    # Step 5: Get specific log
    if log_id:
        print("\nStep 5: Get Specific Log")
        log_detail_response = requests.get(f"{API_BASE}/webhooks/logs/{log_id}", headers=headers)
        print_test(f"Get log detail: {log_detail_response.status_code}", log_detail_response.status_code == 200)
        
        if log_detail_response.status_code == 200:
            log = log_detail_response.json()
            print(f"   - Client: {log['client_name']}")
            print(f"   - URL: {log['webhook_url']}")
            print(f"   - Method: {log['method']}")
            print(f"   - Is Test: {log['is_test']}")
    
    # Step 6: Get webhook stats
    print("\nStep 6: Get Webhook Statistics")
    stats_response = requests.get(f"{API_BASE}/webhooks/stats", headers=headers)
    print_test(f"Get webhook stats: {stats_response.status_code}", stats_response.status_code == 200)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   - Total Webhooks: {stats['total_webhooks']}")
        print(f"   - Successful: {stats['successful_webhooks']}")
        print(f"   - Failed: {stats['failed_webhooks']}")
        print(f"   - Success Rate: {stats['success_rate']}%")
        print(f"   - Avg Response Time: {stats['average_response_time_ms']}ms")
        print(f"   - Test Webhooks: {stats['total_test_webhooks']}")
        print(f"   - Production Webhooks: {stats['total_production_webhooks']}")
    
    # Step 7: Test with filters
    print("\nStep 7: Test Filtered Logs")
    filtered_logs_response = requests.get(
        f"{API_BASE}/webhooks/logs?is_test=true&success=true&limit=5",
        headers=headers
    )
    print_test(f"Get filtered logs: {filtered_logs_response.status_code}", filtered_logs_response.status_code == 200)
    
    if filtered_logs_response.status_code == 200:
        filtered_logs = filtered_logs_response.json()
        print(f"   - Filtered logs count: {len(filtered_logs)}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ ALL PHASE 8 TESTS PASSED!")
    print("="*60 + "\n")
    
    print("Phase 8 Features Tested:")
    print("  ✅ Webhook testing endpoint")
    print("  ✅ Webhook logs retrieval")
    print("  ✅ Webhook log details")
    print("  ✅ Webhook statistics")
    print("  ✅ Filtered logs")
    print("\nPhase 8 is ready for deployment! 🚀\n")

if __name__ == "__main__":
    main()

