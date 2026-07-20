"""
Test Phase 9: Lead Import & Bulk Operations
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000/api"
ADMIN_API = f"{API_BASE}/admin"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)

def print_result(success, message):
    status = "✅" if success else "❌"
    print(f"{status} {message}")

# Step 1: Admin Login
print_step(1, "Admin Login")
login_response = requests.post(
    f"{ADMIN_API}/auth/login",
    json={"email": "admin@leadex.com", "password": "admin123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print_result(True, "Admin login successful")
else:
    print_result(False, f"Admin login failed: {login_response.status_code}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Upload CSV File
print_step(2, "Upload CSV File")
with open('test_leads.csv', 'rb') as f:
    files = {'file': ('test_leads.csv', f, 'text/csv')}
    data = {
        'source': 'test_import',
        'skip_duplicates': 'true'
    }
    upload_response = requests.post(
        f"{ADMIN_API}/imports/upload",
        headers=headers,
        files=files,
        data=data
    )

if upload_response.status_code == 200:
    import_result = upload_response.json()
    print_result(True, f"Upload CSV: {upload_response.status_code}")
    print(f"   - Import ID: {import_result['id']}")
    print(f"   - Status: {import_result['status']}")
    print(f"   - Total Rows: {import_result['total_rows']}")
    print(f"   - Successful: {import_result['successful_imports']}")
    print(f"   - Failed: {import_result['failed_imports']}")
    print(f"   - Duplicates: {import_result['duplicate_skipped']}")
    print(f"   - Success Rate: {import_result['success_rate']:.2f}%")
    import_id = import_result['id']
else:
    print_result(False, f"Upload failed: {upload_response.status_code}")
    print(upload_response.text)
    import_id = None

# Step 3: Get Import History
print_step(3, "Get Import History")
history_response = requests.get(
    f"{ADMIN_API}/imports/history?limit=10",
    headers=headers
)

if history_response.status_code == 200:
    history = history_response.json()
    print_result(True, f"Get import history: {history_response.status_code}")
    print(f"   - Total imports: {len(history)}")
else:
    print_result(False, f"Get history failed: {history_response.status_code}")

# Step 4: Get Import Details
if import_id:
    print_step(4, "Get Import Details")
    details_response = requests.get(
        f"{ADMIN_API}/imports/history/{import_id}",
        headers=headers
    )

    if details_response.status_code == 200:
        details = details_response.json()
        print_result(True, f"Get import details: {details_response.status_code}")
        print(f"   - Filename: {details['filename']}")
        print(f"   - Status: {details['status']}")
        print(f"   - Processing Time: {details['processing_time_seconds']}s")
    else:
        print_result(False, f"Get details failed: {details_response.status_code}")

# Step 5: Get Import Statistics
print_step(5, "Get Import Statistics")
stats_response = requests.get(
    f"{ADMIN_API}/imports/stats",
    headers=headers
)

if stats_response.status_code == 200:
    stats = stats_response.json()
    print_result(True, f"Get import stats: {stats_response.status_code}")
    print(f"   - Total Imports: {stats['total_imports']}")
    print(f"   - Completed: {stats['completed_imports']}")
    print(f"   - Failed: {stats['failed_imports']}")
    print(f"   - Total Leads Imported: {stats['total_leads_imported']}")
    print(f"   - Average Success Rate: {stats['average_success_rate']}%")
else:
    print_result(False, f"Get stats failed: {stats_response.status_code}")

# Step 6: Get Leads to Test Bulk Update
print_step(6, "Get Leads for Bulk Update")
leads_response = requests.get(
    f"{ADMIN_API}/leads?limit=3",
    headers=headers
)

if leads_response.status_code == 200:
    leads = leads_response.json()
    print_result(True, f"Get leads: {leads_response.status_code}")
    print(f"   - Total leads: {len(leads)}")
    lead_ids = [lead['id'] for lead in leads[:2]]  # Get first 2 leads
else:
    print_result(False, f"Get leads failed: {leads_response.status_code}")
    lead_ids = []

# Step 7: Bulk Update Leads
if lead_ids:
    print_step(7, "Bulk Update Leads")
    bulk_update_response = requests.post(
        f"{ADMIN_API}/imports/bulk-update",
        headers=headers,
        json={
            "lead_ids": lead_ids,
            "status": "ASSIGNED"
        }
    )

    if bulk_update_response.status_code == 200:
        bulk_result = bulk_update_response.json()
        print_result(True, f"Bulk update: {bulk_update_response.status_code}")
        print(f"   - Updated: {bulk_result['updated_count']}")
        print(f"   - Failed: {bulk_result['failed_count']}")
    else:
        print_result(False, f"Bulk update failed: {bulk_update_response.status_code}")

# Step 8: Test UI Accessibility
print_step(8, "Test UI Accessibility")
ui_response = requests.get("http://213.21.235.48/admin-imports.html")

if ui_response.status_code == 200:
    print_result(True, f"Import UI accessible: {ui_response.status_code}")
else:
    print_result(False, f"Import UI not accessible: {ui_response.status_code}")

print("\n" + "="*60)
print("✅ ALL PHASE 9 TESTS COMPLETED!")
print("="*60)

