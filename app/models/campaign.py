from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Campaign Information
    name = Column(String(255), nullable=False)
    
    # Date Range
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Rules (JSON: distribution rules, filters, etc.)
    rules = Column(JSON, nullable=True)
    
    # Credits
    default_credit_cost = Column(Float, default=1.0)
    
    # Status
    active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assets = relationship("Asset", back_populates="campaign")
    landing_pages = relationship("LandingPage", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign {self.name}>"
