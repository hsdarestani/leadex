from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Delivery Methods Configuration
    webhook_url = Column(Text, nullable=True)
    google_sheet_id = Column(String(255), nullable=True)
    accept_sms = Column(Boolean, default=False)
    accept_email = Column(Boolean, default=False)
    accept_webhook = Column(Boolean, default=False)
    accept_sheets = Column(Boolean, default=False)
    # WhatsApp details (rich text) - appended to WhatsApp message when lead.has_whatsapp == True
    whatsapp_details_richtext = Column(Text, nullable=True)    
    # Distribution Configuration
    percentage = Column(Float, default=0.0)  # 0-100
    priority_order = Column(Integer, default=0)
    weight = Column(Integer, default=1)
    
    # Time Windows (JSON: [{"day": "monday", "start": "09:00", "end": "17:00"}])
    time_windows = Column(JSON, nullable=True)
    
    # Regions (JSON: ["AE", "SA", "US"])
    regions = Column(JSON, nullable=True)
    
    # Credits
    credits_balance = Column(Float, default=0.0)
    credit_cost_per_lead = Column(Float, default=1.0)
    
    # Status
    status = Column(String(20), default="active")  # active, inactive
    
    # Client Dashboard Access
    password_protected_link_token = Column(String(255), unique=True, nullable=False)
    client_password = Column(String(255), nullable=True)  # Hashed password
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    deliveries = relationship("Delivery", back_populates="client", cascade="all, delete-orphan")
    # Note: crm_integrations and webhook_subscriptions are Phase 14 features
    # Commented out until those tables are created
    # crm_integrations = relationship("CRMIntegration", back_populates="client", cascade="all, delete-orphan")
    # webhook_subscriptions = relationship("WebhookSubscription", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.name} ({self.percentage}%)>"
