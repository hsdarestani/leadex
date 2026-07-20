
"""Test Phase 2: Landing Page API"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import LandingPage, Asset, BatchQueue
from app.services.lead_service import LeadService
from app.services.batch_service import BatchService
from app.utils.phone import normalize_phone_number, validate_phone_number
from app.utils.geo import get_geo_info
from app.utils.rate_limit import check_rate_limit, record_submission
import uuid

print('Testing Phase 2 components...')
print('✅ All imports successful!')
