from app.api.admin.leads import normalize_lead_status


def test_missing_status_is_pending():
    assert normalize_lead_status(None) == "pending"
    assert normalize_lead_status("") == "pending"


def test_legacy_new_status_is_pending():
    assert normalize_lead_status("NEW") == "pending"
    assert normalize_lead_status(" new ") == "pending"


def test_valid_statuses_are_lowercase():
    assert normalize_lead_status("ASSIGNED") == "assigned"
    assert normalize_lead_status("Delivered") == "delivered"
    assert normalize_lead_status("failed") == "failed"
