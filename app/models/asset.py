from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text
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
    mobile = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True)

    # Foreign Keys
    landing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("landing_pages.id"),
        nullable=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id"),
        nullable=True,
    )

    # Metadata
    ip = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    fingerprint = Column(String(255), nullable=True)

    # Geo Information
    geo = Column(JSON, nullable=True)

    # UTM Parameters
    utm = Column(JSON, nullable=True)

    # WhatsApp registry check
    has_whatsapp = Column(Boolean, nullable=True)
    has_whatsapp_checked_at = Column(DateTime, nullable=True)

    # Canonical statuses: pending, assigned, delivered, failed
    status = Column(
        String(20),
        default="pending",
        server_default="pending",
        nullable=False,
        index=True,
    )
    dedupe_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    landing_page = relationship("LandingPage", back_populates="assets")
    campaign = relationship("Campaign", back_populates="assets")
    deliveries = relationship(
        "Delivery",
        back_populates="asset",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Asset {self.mobile} - {self.status}>"
