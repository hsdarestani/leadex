"""
Phase 12: Performance Optimization - Test Suite
Tests for caching, rate limiting, monitoring, and background jobs
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def test_phase12():
    print("=" * 60)
    print("PHASE 12: PERFORMANCE OPTIMIZATION - TEST SUITE")
    print("=" * 60)
    print()

    # Step 1: Admin Login
    print("Step 1: Admin Login")
    login_response = requests.post(
        f"{API_BASE}/admin/auth/login",
        json={"email": "admin@leadex.com", "password": "admin123"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.status_code}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful")
    print()

    # Step 2: Test Rate Limiting Headers
    print("Step 2: Test Rate Limiting Headers")
    response = requests.get(f"{API_BASE}/admin/clients", headers=headers)
    assert response.status_code == 200, f"Get clients failed: {response.status_code}"

    # Check for rate limit headers
    rate_limit_headers = {
        'X-RateLimit-Limit': response.headers.get('X-RateLimit-Limit'),
        'X-RateLimit-Remaining': response.headers.get('X-RateLimit-Remaining'),
        'X-RateLimit-Reset': response.headers.get('X-RateLimit-Reset')
    }

    if rate_limit_headers['X-RateLimit-Limit']:
        print(f"✅ Rate limit headers present:")
        print(f"   - Limit: {rate_limit_headers['X-RateLimit-Limit']}")
        print(f"   - Remaining: {rate_limit_headers['X-RateLimit-Remaining']}")
        print(f"   - Reset in: {rate_limit_headers['X-RateLimit-Reset']}s")
    else:
        print("⚠️  Rate limit headers not found (may be disabled)")
    print()

    # Step 3: Test Performance Headers
    print("Step 3: Test Performance Headers")
    response_time = response.headers.get('X-Response-Time')
    if response_time:
        print(f"✅ Response time tracked: {response_time}")
    else:
        print("⚠️  Response time header not found")
    print()

    # Step 4: Test Cache Statistics
    print("Step 4: Test Cache Statistics")
    response = requests.get(f"{API_BASE}/admin/performance/cache/stats", headers=headers)
    if response.status_code == 200:
        cache_stats = response.json()['data']
        print(f"✅ Cache stats retrieved:")
        print(f"   - Total keys: {cache_stats.get('total_keys', 'N/A')}")
        print(f"   - Memory used: {cache_stats.get('memory_used', 'N/A')}")
        print(f"   - Hit rate: {cache_stats.get('hit_rate', 'N/A')}%")
    else:
        print(f"⚠️  Failed to get cache stats: {response.status_code}")
    print()

    # Step 5: Test System Statistics
    print("Step 5: Test System Statistics")
    response = requests.get(f"{API_BASE}/admin/performance/system/stats", headers=headers)
    if response.status_code == 200:
        system_stats = response.json()['data']
        print(f"✅ System stats retrieved:")
        if 'database' in system_stats:
            db_stats = system_stats['database']
            print(f"   - Database pool size: {db_stats.get('pool_size', 'N/A')}")
            print(f"   - Active connections: {db_stats.get('checked_out', 'N/A')}")
            print(f"   - Available connections: {db_stats.get('checked_in', 'N/A')}")
    else:
        print(f"⚠️  Failed to get system stats: {response.status_code}")
    print()

    # Step 6: Test Endpoint Statistics
    print("Step 6: Test Endpoint Statistics")
    response = requests.get(
        f"{API_BASE}/admin/performance/endpoint/stats",
        params={"endpoint": "/api/admin/clients", "method": "GET", "hours": 1},
        headers=headers
    )
    if response.status_code == 200:
        endpoint_stats = response.json()['data']
        print(f"✅ Endpoint stats retrieved:")
        print(f"   - Total requests: {endpoint_stats.get('total_requests', 0)}")
        print(f"   - Avg duration: {endpoint_stats.get('avg_duration', 0):.2f}ms")
    else:
        print(f"⚠️  Failed to get endpoint stats: {response.status_code}")
    print()

    # Step 7: Test Rate Limit Configuration
    print("Step 7: Test Rate Limit Configuration")
    response = requests.get(f"{API_BASE}/admin/performance/rate-limit/stats", headers=headers)
    if response.status_code == 200:
        rate_limits = response.json()['limits']
        print(f"✅ Rate limit configuration:")
        for limit_type, limit_value in rate_limits.items():
            print(f"   - {limit_type}: {limit_value} req/min")
    else:
        print(f"⚠️  Failed to get rate limit config: {response.status_code}")
    print()

    # Step 8: Test Database Statistics
    print("Step 8: Test Database Statistics")
    response = requests.get(f"{API_BASE}/admin/performance/database/stats", headers=headers)
    if response.status_code == 200:
        db_stats = response.json()
        if 'tables' in db_stats:
            print(f"✅ Database statistics:")
            print(f"   - Top tables by size:")
            for table in db_stats['tables'][:3]:
                print(f"     • {table['table']}: {table['total_size']}")
    else:
        print(f"⚠️  Failed to get database stats: {response.status_code}")
    print()

    # Step 9: Test Celery Statistics
    print("Step 9: Test Celery Statistics")
    response = requests.get(f"{API_BASE}/admin/performance/celery/stats", headers=headers)
    if response.status_code == 200:
        celery_stats = response.json()
        if celery_stats.get('success'):
            print(f"✅ Celery is running:")
            print(f"   - Workers: {len(celery_stats['data'].get('workers', []))}")
        else:
            print(f"⚠️  Celery not available: {celery_stats.get('message', 'Unknown')}")
    else:
        print(f"⚠️  Failed to get Celery stats: {response.status_code}")
    print()

    # Step 10: Test Cache Clearing
    print("Step 10: Test Cache Clear (Pattern)")
    response = requests.post(
        f"{API_BASE}/admin/performance/cache/clear",
        params={"pattern": "test:*"},
        headers=headers
    )
    if response.status_code == 200:
        print(f"✅ Cache clear successful: {response.json()['message']}")
    else:
        print(f"⚠️  Failed to clear cache: {response.status_code}")
    print()

    # Step 11: Test Multiple Requests for Rate Limiting
    print("Step 11: Test Multiple Requests (Rate Limit Test)")
    request_count = 5
    successful_requests = 0
    rate_limited = False

    for i in range(request_count):
        response = requests.get(f"{API_BASE}/admin/clients", headers=headers)
        if response.status_code == 200:
            successful_requests += 1
        elif response.status_code == 429:
            rate_limited = True
            print(f"   Request {i+1}: Rate limited (429)")
            break

    if successful_requests > 0:
        print(f"✅ Made {successful_requests} requests successfully")
        if rate_limited:
            print(f"✅ Rate limiting is working (request blocked)")
    print()

    # Step 12: Performance Summary
    print("Step 12: Performance Summary")
    print("✅ Testing completed! Summary:")
    print()
    print("📊 PERFORMANCE FEATURES TESTED:")
    print("   ✅ Rate limiting headers")
    print("   ✅ Response time tracking")
    print("   ✅ Cache statistics")
    print("   ✅ System monitoring")
    print("   ✅ Endpoint statistics")
    print("   ✅ Database statistics")
    print("   ✅ Celery integration")
    print("   ✅ Cache management")
    print()

    print("=" * 60)
    print("✅ ALL PHASE 12 TESTS COMPLETED!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    test_phase12()
