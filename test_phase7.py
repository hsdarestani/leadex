"""
Test Phase 7: Advanced Analytics & Reporting
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_analytics_endpoints():
    """Test all analytics endpoints"""
    
    print("=" * 80)
    print("PHASE 7: ADVANCED ANALYTICS & REPORTING - TEST SUITE")
    print("=" * 80)
    print()
    
    # Login as admin
    print("1. Admin Login...")
    login_response = requests.post(
        f"{BASE_URL}/api/admin/auth/login",
        json={"email": "admin@leadex.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful")
    print()
    
    # Test 1: Overview Metrics
    print("2. Testing Overview Metrics...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/overview", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Overview Metrics: {response.status_code}")
        print(f"   - Total Leads: {data['total_leads']}")
        print(f"   - Active Clients: {data['active_clients']}")
        print(f"   - Delivery Success Rate: {data['delivery_success_rate']}%")
    else:
        print(f"❌ Overview Metrics failed: {response.status_code}")
        return False
    print()
    
    # Test 2: Time Series Data
    print("3. Testing Time Series Data...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/time-series?days=7", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Time Series Data: {response.status_code}")
        print(f"   - Data Points: {len(data)}")
    else:
        print(f"❌ Time Series Data failed: {response.status_code}")
        return False
    print()
    
    # Test 3: Client Performance
    print("4. Testing Client Performance...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/client-performance?limit=5", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Client Performance: {response.status_code}")
        print(f"   - Clients Analyzed: {len(data)}")
    else:
        print(f"❌ Client Performance failed: {response.status_code}")
        return False
    print()
    
    # Test 4: Delivery Methods
    print("5. Testing Delivery Methods Stats...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/delivery-methods", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Delivery Methods: {response.status_code}")
        print(f"   - Methods: {len(data)}")
    else:
        print(f"❌ Delivery Methods failed: {response.status_code}")
        return False
    print()
    
    # Test 5: Lead Sources
    print("6. Testing Lead Sources...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/lead-sources", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Lead Sources: {response.status_code}")
        print(f"   - Sources: {len(data)}")
    else:
        print(f"❌ Lead Sources failed: {response.status_code}")
        return False
    print()
    
    # Test 6: Conversion Funnel
    print("7. Testing Conversion Funnel...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/conversion-funnel", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Conversion Funnel: {response.status_code}")
        print(f"   - Total Leads: {data['total_leads']}")
        print(f"   - Assigned: {data['assigned_leads']}")
        print(f"   - Assignment Rate: {data['assignment_rate']}%")
    else:
        print(f"❌ Conversion Funnel failed: {response.status_code}")
        return False
    print()
    
    # Test 7: Hourly Distribution
    print("8. Testing Hourly Distribution...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/hourly-distribution?days=7", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Hourly Distribution: {response.status_code}")
        print(f"   - Hours: {len(data)}")
    else:
        print(f"❌ Hourly Distribution failed: {response.status_code}")
        return False
    print()
    
    # Test 8: Revenue Metrics
    print("9. Testing Revenue Metrics...")
    response = requests.get(f"{BASE_URL}/api/admin/analytics/revenue", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Revenue Metrics: {response.status_code}")
        print(f"   - Total Credits Used: {data['total_credits_used']}")
        print(f"   - Total Credits Available: {data['total_credits_available']}")
    else:
        print(f"❌ Revenue Metrics failed: {response.status_code}")
        return False
    print()
    
    print("=" * 80)
    print("✅ ALL PHASE 7 TESTS PASSED!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_analytics_endpoints()
    exit(0 if success else 1)

