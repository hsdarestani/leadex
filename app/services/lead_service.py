"""
Lead service for duplicate detection and lead creation
"""
from sqlalchemy.orm import Session
from app.models import Asset
from app.core.config import settings
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid


class LeadService:
    """Service for lead operations"""
    
    @staticmethod
    def check_duplicate(db: Session, mobile: str) -> Tuple[bool, Optional[str]]:
        """
        Check if mobile number is duplicate within dedupe window
        
        Args:
            db: Database session
            mobile: Normalized mobile number
        
        Returns:
            Tuple of (is_duplicate: bool, reason: Optional[str])
        """
        # Calculate dedupe window
        dedupe_window = datetime.utcnow() - timedelta(days=settings.DEDUPE_WINDOW_DAYS)
        
        # Check if mobile exists in the window
        existing_lead = db.query(Asset).filter(
            Asset.mobile == mobile,
            Asset.created_at >= dedupe_window
        ).first()
        
        if existing_lead:
            days_ago = (datetime.utcnow() - existing_lead.created_at).days
            reason = f"Duplicate submission. Last submitted {days_ago} days ago."
            return True, reason
        
        return False, None
    
    @staticmethod
    def create_lead(
        db: Session,
        mobile: str,
        name: Optional[str],
        email: Optional[str],
        landing_id: uuid.UUID,
        campaign_id: uuid.UUID,
        ip: str,
        user_agent: str,
        referrer: Optional[str],
        geo: Optional[dict],
        utm: Optional[dict]
    ) -> Asset:
        """
        Create a new lead
        
        Args:
            db: Database session
            mobile: Normalized mobile number
            name: Lead name
            email: Lead email
            landing_id: Landing page UUID
            campaign_id: Campaign UUID
            ip: Client IP address
            user_agent: User agent string
            referrer: Referrer URL
            geo: Geo information dictionary
            utm: UTM parameters dictionary
        
        Returns:
            Created Asset object
        """
        lead = Asset(
            id=uuid.uuid4(),
            mobile=mobile,
            name=name,
            email=email,
            landing_id=landing_id,
            campaign_id=campaign_id,
            ip=ip,
            user_agent=user_agent,
            referrer=referrer,
            geo=geo,
            utm=utm,
            status="NEW"
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        return lead
