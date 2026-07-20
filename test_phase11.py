"""
Phase 11: Advanced Features - Test Suite
Tests for lead notes, tags, custom fields, and scoring
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def test_phase11():
    print("=" * 60)
    print("PHASE 11: ADVANCED FEATURES - TEST SUITE")
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
    
    # Step 2: Create Tags
    print("Step 2: Create Tags")
    tags_to_create = [
        {"name": "Hot Lead", "color": "#dc3545", "description": "High priority lead"},
        {"name": "Cold Lead", "color": "#6c757d", "description": "Low priority lead"},
        {"name": "Follow Up", "color": "#ffc107", "description": "Needs follow up"}
    ]
    
    created_tags = []
    for tag_data in tags_to_create:
        response = requests.post(
            f"{API_BASE}/admin/advanced/tags",
            headers=headers,
            json=tag_data
        )
        if response.status_code == 200:
            created_tags.append(response.json())
            print(f"✅ Created tag: {tag_data['name']}")
        elif response.status_code == 400:
            print(f"⚠️  Tag already exists: {tag_data['name']}")
        else:
            print(f"❌ Failed to create tag: {tag_data['name']} - {response.status_code}")
    print()
    
    # Step 3: Get All Tags
    print("Step 3: Get All Tags")
    response = requests.get(f"{API_BASE}/admin/advanced/tags", headers=headers)
    assert response.status_code == 200, f"Get tags failed: {response.status_code}"
    tags = response.json()
    print(f"✅ Retrieved {len(tags)} tags")
    print()
    
    # Step 4: Create Custom Fields
    print("Step 4: Create Custom Fields")
    fields_to_create = [
        {"name": "company_name", "label": "Company Name", "field_type": "text"},
        {"name": "company_size", "label": "Company Size", "field_type": "select", "options": ["1-10", "11-50", "51-200", "201+"]},
        {"name": "budget", "label": "Budget", "field_type": "number"},
        {"name": "interested", "label": "Interested", "field_type": "boolean"}
    ]
    
    created_fields = []
    for field_data in fields_to_create:
        response = requests.post(
            f"{API_BASE}/admin/advanced/custom-fields",
            headers=headers,
            json=field_data
        )
        if response.status_code == 200:
            created_fields.append(response.json())
            print(f"✅ Created custom field: {field_data['label']}")
        elif response.status_code == 400:
            print(f"⚠️  Custom field already exists: {field_data['label']}")
        else:
            print(f"❌ Failed to create custom field: {field_data['label']} - {response.status_code}")
    print()
    
    # Step 5: Get All Custom Fields
    print("Step 5: Get All Custom Fields")
    response = requests.get(f"{API_BASE}/admin/advanced/custom-fields", headers=headers)
    assert response.status_code == 200, f"Get custom fields failed: {response.status_code}"
    fields = response.json()
    print(f"✅ Retrieved {len(fields)} custom fields")
    print()
    
    # Step 6: Get a Lead for Testing
    print("Step 6: Get a Lead for Testing")
    response = requests.get(f"{API_BASE}/admin/leads?limit=1", headers=headers)
    assert response.status_code == 200, f"Get leads failed: {response.status_code}"
    leads = response.json()
    
    if len(leads) == 0:
        print("⚠️  No leads found. Skipping lead-specific tests.")
        test_lead_id = None
    else:
        test_lead_id = leads[0]["id"]
        print(f"✅ Using lead: {test_lead_id}")
    print()
    
    # Step 7: Add Note to Lead (if lead exists)
    if test_lead_id:
        print("Step 7: Add Note to Lead")
        response = requests.post(
            f"{API_BASE}/admin/advanced/notes",
            headers=headers,
            json={
                "asset_id": test_lead_id,
                "note": "This is a test note for Phase 11",
                "is_internal": True,
                "is_pinned": False
            }
        )
        assert response.status_code == 200, f"Create note failed: {response.status_code}"
        note = response.json()
        print(f"✅ Created note: {note['id']}")
        print()
        
        # Step 8: Get Notes for Lead
        print("Step 8: Get Notes for Lead")
        response = requests.get(f"{API_BASE}/admin/advanced/notes/{test_lead_id}", headers=headers)
        assert response.status_code == 200, f"Get notes failed: {response.status_code}"
        notes = response.json()
        print(f"✅ Retrieved {len(notes)} notes for lead")
        print()
        
        # Step 9: Calculate Lead Score
        print("Step 9: Calculate Lead Score")
        response = requests.post(
            f"{API_BASE}/admin/advanced/scoring/calculate/{test_lead_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Calculate score failed: {response.status_code}"
        score = response.json()
        print(f"✅ Lead score calculated: {score['score']} (Grade: {score['grade']})")
        print(f"   Score breakdown: {score['score_breakdown']}")
        print()
        
        # Step 10: Get Lead Score
        print("Step 10: Get Lead Score")
        response = requests.get(f"{API_BASE}/admin/advanced/scoring/{test_lead_id}", headers=headers)
        assert response.status_code == 200, f"Get score failed: {response.status_code}"
        print("✅ Retrieved lead score")
        print()
    
    # Step 11: Get Scoring Stats
    print("Step 11: Get Scoring Stats")
    response = requests.get(f"{API_BASE}/admin/advanced/scoring/stats/overview", headers=headers)
    assert response.status_code == 200, f"Get scoring stats failed: {response.status_code}"
    stats = response.json()
    print(f"✅ Scoring stats:")
    print(f"   - Total scored leads: {stats['total_scored_leads']}")
    print(f"   - Average score: {stats['average_score']}")
    print(f"   - Grade distribution: {stats['grade_distribution']}")
    print()
    
    # Step 12: Test Advanced Features UI
    print("Step 12: Test Advanced Features UI")
    response = requests.get("http://127.0.0.1/admin-advanced.html")
    assert response.status_code == 200, f"Advanced UI not accessible: {response.status_code}"
    print("✅ Advanced features UI accessible")
    print()
    
    print("=" * 60)
    print("✅ ALL PHASE 11 TESTS COMPLETED!")
    print("=" * 60)
    print()
    print("🚀 ADVANCED FEATURES:")
    print(f"   ✅ Tags created: {len(tags)}")
    print(f"   ✅ Custom fields created: {len(fields)}")
    if test_lead_id:
        print(f"   ✅ Notes functionality working")
        print(f"   ✅ Lead scoring working")
    print(f"   ✅ Advanced features UI accessible")
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_phase11()

