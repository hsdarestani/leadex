from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class LandingPage(Base):
    __tablename__ = "landing_pages"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Landing Page Information
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    
    # Captcha Configuration
    captcha_type = Column(String(50), default="reCAPTCHA_v3")  # reCAPTCHA_v3, hCaptcha
    
    # Foreign Key
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="landing_pages")
    assets = relationship("Asset", back_populates="landing_page")
    
    def __repr__(self):
        return f"<LandingPage {self.slug}>"
