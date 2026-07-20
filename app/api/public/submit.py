"""
Public lead submission endpoint (simplified, no auth required)
"""
import os
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from app.services.lead_service import LeadService
from app.services.batch_service import BatchService
from app.utils.geo import get_geo_info
from app.utils.phone import normalize_phone_number


router = APIRouter()


class PublicLeadSubmit(BaseModel):
    """Simplified schema for public lead submission"""
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    mobile: str = Field(..., description="Mobile number")
    email: Optional[str] = Field(None, description="Email address (optional)")

    # NEW
    consent: bool = Field(..., description="User consent checkbox must be true")
    captcha_token: str = Field(..., min_length=10, description="Cloudflare Turnstile token")

    @field_validator('consent')
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Consent is required")
        return v

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v:
            raise ValueError("Mobile number is required")
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        if not re.match(r'^\+?\d{8,15}$', cleaned):
            raise ValueError("Invalid mobile number format (8-15 digits required)")
        return cleaned

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")
        return v.lower()


class PublicLeadResponse(BaseModel):
    """Response for public lead submission"""
    success: bool
    message: str
    lead_id: Optional[str] = None


@router.post("/submit-lead", response_model=PublicLeadResponse)
async def submit_public_lead(
    lead_data: PublicLeadSubmit,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for lead submission (no auth required)

    This is a simplified version without:
    - reCAPTCHA verification
    - Landing page association
    - Rate limiting (basic only)
    - UTM tracking

    Use this for simple lead capture forms.
    """
    try:
        # Get client IP
        client_ip = request.client.host
        # Verify Turnstile (server-side)
        ok = await verify_turnstile(lead_data.captcha_token, client_ip)
        if not ok:
            raise HTTPException(status_code=400, detail="Captcha verification failed")
        if request.headers.get("X-Forwarded-For"):
            client_ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()

        # Get user agent
        user_agent = request.headers.get("User-Agent", "")

        # Get referrer
        referrer = request.headers.get("Referer")

        # Normalize phone number
        try:
            normalized_mobile = normalize_phone_number(lead_data.mobile)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid mobile number: {str(e)}")

        # Check for duplicates (20-day window)
        is_duplicate, duplicate_reason = LeadService.check_duplicate(db, normalized_mobile)
        if is_duplicate:
            # Silent success - don't reveal duplicate
            return PublicLeadResponse(
                success=True,
                message="Thank you! Your information has been submitted successfully.",
                lead_id=None
            )

        # Get geo information
        geo_info = get_geo_info(client_ip)

        # Create lead (no campaign or landing page association)
        lead = LeadService.create_lead(
            db=db,
            mobile=normalized_mobile,
            name=lead_data.name,
            email=lead_data.email,
            landing_id=None,
            campaign_id=None,
            ip=client_ip,
            user_agent=user_agent,
            referrer=referrer,
            geo=geo_info,
            utm=None
        )

        # Add to batch queue
        batch_full, lead_ids_to_distribute = BatchService.add_lead_to_batch(db, lead.id)

        # If batch is full, trigger distribution
        if batch_full:
            BatchService.trigger_distribution(db, lead_ids_to_distribute)

        # Return success response
        return PublicLeadResponse(
            success=True,
            message="Thank you! Your information has been submitted successfully.",
            lead_id=str(lead.id)
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error submitting public lead: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your submission")
TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET_KEY", "0x4AAAAAACd7VpPq3HHuS2IXeO_KNVjHn4s").strip()

async def verify_turnstile(token: str, remoteip: str) -> bool:
    """
    Server-side verification for Cloudflare Turnstile
    https://challenges.cloudflare.com/turnstile/v0/siteverify
    """
    if not TURNSTILE_SECRET:
        # اگر secret ست نشده، بهتر است fail کنیم (نه bypass)
        return False

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": TURNSTILE_SECRET,
        "response": token,
        "remoteip": remoteip
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, data=data)
            resp.raise_for_status()
            result = resp.json()
            return bool(result.get("success", False))
    except Exception:
        return False

