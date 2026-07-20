"""
Landing page submission endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.lead import LeadSubmitRequest, LeadSubmitResponse
from app.models import LandingPage
from app.services.lead_service import LeadService
from app.services.batch_service import BatchService
from app.utils.captcha import verify_recaptcha
from app.utils.geo import get_geo_info
from app.utils.phone import normalize_phone_number
from app.utils.rate_limit import check_rate_limit, record_submission


router = APIRouter()


@router.post("/{slug}", response_model=LeadSubmitResponse)
async def submit_lead(
    slug: str,
    lead_data: LeadSubmitRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit a lead from landing page
    
    Args:
        slug: Landing page slug
        lead_data: Lead submission data
        request: FastAPI request object
        db: Database session
    
    Returns:
        LeadSubmitResponse with success status and message
    """
    # Get client IP
    client_ip = request.client.host
    if request.headers.get("X-Forwarded-For"):
        client_ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    
    # Get user agent
    user_agent = request.headers.get("User-Agent", "")
    
    # Get referrer
    referrer = request.headers.get("Referer")
    
    # 1. Verify landing page exists
    landing_page = db.query(LandingPage).filter(LandingPage.slug == slug).first()
    if not landing_page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    
    # 2. Verify reCAPTCHA
    captcha_success, captcha_score, captcha_error = await verify_recaptcha(
        lead_data.recaptcha_token,
        client_ip
    )
    
    if not captcha_success:
        raise HTTPException(status_code=400, detail=f"Captcha verification failed: {captcha_error}")
    
    # 3. Rate limiting - IP based (max 5 submissions per hour)
    ip_allowed, ip_remaining = check_rate_limit(f"ip:{client_ip}", max_attempts=5, window_seconds=3600)
    if not ip_allowed:
        raise HTTPException(status_code=429, detail="Too many submissions from this IP. Please try again later.")
    
    # 4. Normalize phone number
    try:
        normalized_mobile = normalize_phone_number(lead_data.mobile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid mobile number: {str(e)}")
    
    # 5. Rate limiting - Mobile based (max 1 submission per day)
    mobile_allowed, mobile_remaining = check_rate_limit(
        f"mobile:{normalized_mobile}",
        max_attempts=1,
        window_seconds=86400  # 24 hours
    )
    if not mobile_allowed:
        raise HTTPException(status_code=429, detail="This mobile number has already been submitted today.")
    
    # 6. Check for duplicates (20-day window)
    is_duplicate, duplicate_reason = LeadService.check_duplicate(db, normalized_mobile)
    if is_duplicate:
        # Silent redirect - return success but don't create lead
        return LeadSubmitResponse(
            success=True,
            message="Thank you! Your information has been submitted successfully.",
            lead_id=None
        )
    
    # 7. Get geo information
    geo_info = get_geo_info(client_ip)
    
    # 8. Build UTM parameters
    utm_params = {}
    if lead_data.utm_source:
        utm_params["utm_source"] = lead_data.utm_source
    if lead_data.utm_medium:
        utm_params["utm_medium"] = lead_data.utm_medium
    if lead_data.utm_campaign:
        utm_params["utm_campaign"] = lead_data.utm_campaign
    if lead_data.utm_term:
        utm_params["utm_term"] = lead_data.utm_term
    if lead_data.utm_content:
        utm_params["utm_content"] = lead_data.utm_content
    
    # 9. Create lead
    lead = LeadService.create_lead(
        db=db,
        mobile=normalized_mobile,
        name=lead_data.name,
        email=lead_data.email,
        landing_id=landing_page.id,
        campaign_id=landing_page.campaign_id,
        ip=client_ip,
        user_agent=user_agent,
        referrer=referrer,
        geo=geo_info,
        utm=utm_params if utm_params else None
    )
    
    # 10. Record rate limit attempts
    record_submission(f"ip:{client_ip}", window_seconds=3600)
    record_submission(f"mobile:{normalized_mobile}", window_seconds=86400)
    
    # 11. Add to batch queue
    batch_full, lead_ids_to_distribute = BatchService.add_lead_to_batch(db, lead.id)
    
    # 12. If batch is full, trigger distribution
    if batch_full:
        BatchService.trigger_distribution(db, lead_ids_to_distribute)
    
    # 13. Return success response
    return LeadSubmitResponse(
        success=True,
        message="Thank you! Your information has been submitted successfully.",
        lead_id=str(lead.id)
    )
