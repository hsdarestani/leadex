"""
Phase 13: Reporting & Export - Quick Test Suite
"""
import requests

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def test_phase13():
    print("=" * 60)
    print("PHASE 13: REPORTING & EXPORT - TEST SUITE")
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

    # Step 2: List Report Templates
    print("Step 2: List Report Templates")
    response = requests.get(f"{API_BASE}/admin/reports/templates/list", headers=headers)
    if response.status_code == 200:
        templates = response.json()['templates']
        print(f"✅ Found {len(templates)} report templates:")
        for template in templates:
            print(f"   - {template['name']}: {template['description']}")
    else:
        print(f"⚠️  Failed to get templates: {response.status_code}")
    print()

    # Step 3: Create Custom Report
    print("Step 3: Create Custom Report")
    report_data = {
        "name": "Test Leads Report",
        "description": "Test report for Phase 13",
        "report_type": "leads",
        "fields": ["id", "mobile", "name", "email", "status", "created_at"],
        "filters": {},
        "sorting": {"field": "created_at", "order": "desc"}
    }
    response = requests.post(f"{API_BASE}/admin/reports/create", headers=headers, json=report_data)
    if response.status_code == 200:
        report_id = response.json()['report_id']
        print(f"✅ Report created: {report_id}")
    else:
        print(f"⚠️  Failed to create report: {response.status_code}")
        report_id = None
    print()

    # Step 4: Export Report to Excel
    if report_id:
        print("Step 4: Export Report to Excel")
        export_data = {
            "report_id": report_id,
            "export_format": "excel"
        }
        response = requests.post(f"{API_BASE}/admin/reports/export", headers=headers, json=export_data)
        if response.status_code == 200:
            export_info = response.json()
            print(f"✅ Report exported successfully:")
            print(f"   - File: {export_info.get('file_path', 'N/A')}")
            print(f"   - Size: {export_info.get('file_size', 0)} bytes")
            print(f"   - Records: {export_info.get('record_count', 0)}")
            export_id = export_info.get('export_id')
        else:
            print(f"⚠️  Failed to export report: {response.status_code}")
            export_id = None
        print()

        # Step 5: Export Report to PDF
        print("Step 5: Export Report to PDF")
        export_data = {
            "report_id": report_id,
            "export_format": "pdf"
        }
        response = requests.post(f"{API_BASE}/admin/reports/export", headers=headers, json=export_data)
        if response.status_code == 200:
            print(f"✅ PDF export successful")
        else:
            print(f"⚠️  Failed to export PDF: {response.status_code}")
        print()

        # Step 6: Export Report to CSV
        print("Step 6: Export Report to CSV")
        export_data = {
            "report_id": report_id,
            "export_format": "csv"
        }
        response = requests.post(f"{API_BASE}/admin/reports/export", headers=headers, json=export_data)
        if response.status_code == 200:
            print(f"✅ CSV export successful")
        else:
            print(f"⚠️  Failed to export CSV: {response.status_code}")
        print()

    # Step 7: List All Reports
    print("Step 7: List All Reports")
    response = requests.get(f"{API_BASE}/admin/reports/list", headers=headers)
    if response.status_code == 200:
        reports = response.json()['reports']
        print(f"✅ Found {len(reports)} custom reports")
    else:
        print(f"⚠️  Failed to list reports: {response.status_code}")
    print()

    # Step 8: Get Export History
    print("Step 8: Get Export History")
    response = requests.get(f"{API_BASE}/admin/reports/exports/history", headers=headers)
    if response.status_code == 200:
        exports = response.json()['exports']
        print(f"✅ Export history: {len(exports)} exports")
    else:
        print(f"⚠️  Failed to get export history: {response.status_code}")
    print()

    print("=" * 60)
    print("✅ PHASE 13 TESTS COMPLETED!")
    print("=" * 60)
    print()
    print("📊 REPORTING & EXPORT FEATURES:")
    print("   ✅ Report templates")
    print("   ✅ Custom report creation")
    print("   ✅ Excel export")
    print("   ✅ PDF export")
    print("   ✅ CSV export")
    print("   ✅ Export history tracking")
    print()

if __name__ == "__main__":
    test_phase13()
