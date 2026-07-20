from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Lead Information
    name = Column(String(255), nullable=True)
    mobile = Column(String(50), nullable=False, unique=True, index=True)  # Unique identifier
    email = Column(String(255), nullable=True)
    
    # Foreign Keys
    landing_id = Column(UUID(as_uuid=True), ForeignKey("landing_pages.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Metadata
    ip = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    fingerprint = Column(String(255), nullable=True)
    
    # Geo Information (JSON: {"country": "AE", "city": "Dubai", "lat": 25.2, "lon": 55.2})
    geo = Column(JSON, nullable=True)
    
    # UTM Parameters (JSON: {"utm_source": "google", "utm_medium": "cpc", ...})
    utm = Column(JSON, nullable=True)
    # WhatsApp registry check (optional)
    has_whatsapp = Column(Boolean, nullable=True)  # True/False/None(unknown)
    has_whatsapp_checked_at = Column(DateTime, nullable=True)
    # Status
    status = Column(String(20), default="NEW", index=True)  # NEW, PENDING, ASSIGNED, DELIVERED, FAILED
    dedupe_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    landing_page = relationship("LandingPage", back_populates="assets")
    campaign = relationship("Campaign", back_populates="assets")
    deliveries = relationship("Delivery", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset {self.mobile} - {self.status}>"
