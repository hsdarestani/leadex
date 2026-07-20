"""
Integration models for CRM and external systems
"""
import uuid
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CRMIntegration(Base):
    """CRM integration configuration"""
    __tablename__ = "crm_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)

    # CRM type: salesforce, hubspot, zoho
    crm_type = Column(String(50), nullable=False, index=True)

    # Credentials (encrypted in production)
    api_key = Column(String(500))
    api_secret = Column(String(500))
    access_token = Column(Text)
    refresh_token = Column(Text)
    instance_url = Column(String(500))

    # Configuration
    config = Column(JSON, default={})  # Field mappings, sync settings

    # Sync settings
    sync_enabled = Column(Boolean, default=True, index=True)
    sync_direction = Column(String(20), default='bidirectional')  # outbound, inbound, bidirectional
    auto_sync = Column(Boolean, default=False)
    sync_frequency = Column(Integer, default=60)  # minutes

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_sync_at = Column(DateTime, nullable=True, index=True)
    last_sync_status = Column(String(20), nullable=True)  # success, failed, partial
    last_error = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    # Note: back_populates commented out until Client model is updated
    client = relationship("Client")  # back_populates="crm_integrations"
    sync_logs = relationship("CRMSyncLog", back_populates="integration", cascade="all, delete-orphan")


class CRMSyncLog(Base):
    """Log of CRM sync operations"""
    __tablename__ = "crm_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey('crm_integrations.id', ondelete='CASCADE'), nullable=False, index=True)

    # Sync details
    sync_type = Column(String(20), nullable=False)  # manual, auto, scheduled
    direction = Column(String(20), nullable=False)  # outbound, inbound

    # Results
    status = Column(String(20), nullable=False, index=True)  # success, failed, partial
    records_processed = Column(Integer, default=0)
    records_succeeded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    # Error details
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, default={})

    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Relationships
    integration = relationship("CRMIntegration", back_populates="sync_logs")


class WebhookSubscription(Base):
    """Webhook subscriptions for external systems"""
    __tablename__ = "webhook_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', ondelete='CASCADE'), nullable=True, index=True)

    # Subscription details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    endpoint_url = Column(String(1000), nullable=False)

    # Events to subscribe to
    events = Column(JSON, nullable=False, default=[])  # ['lead.created', 'lead.assigned', etc.]

    # Security
    secret_key = Column(String(500), nullable=False)  # For HMAC signature
    use_hmac = Column(Boolean, default=True)
    hmac_algorithm = Column(String(20), default='sha256')

    # Headers
    custom_headers = Column(JSON, default={})

    # Retry configuration
    retry_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)  # seconds
    retry_backoff = Column(String(20), default='exponential')  # linear, exponential

    # Filtering
    filters = Column(JSON, default={})  # Filter events based on conditions

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_triggered_at = Column(DateTime, nullable=True, index=True)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    # Note: back_populates commented out until Client model is updated
    client = relationship("Client")  # back_populates="webhook_subscriptions"
    deliveries = relationship("WebhookDeliveryLog", back_populates="subscription", cascade="all, delete-orphan")


class WebhookDeliveryLog(Base):
    """Log of webhook delivery attempts"""
    __tablename__ = "webhook_delivery_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('webhook_subscriptions.id', ondelete='CASCADE'), nullable=False, index=True)

    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)

    # Delivery details
    attempt_number = Column(Integer, default=1)
    status = Column(String(20), nullable=False, index=True)  # pending, delivered, failed

    # HTTP details
    http_status_code = Column(Integer, nullable=True)
    request_headers = Column(JSON, default={})
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    response_headers = Column(JSON, default={})

    # Timing
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    responded_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Error details
    error_message = Column(Text, nullable=True)
    will_retry = Column(Boolean, default=False)
    next_retry_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    subscription = relationship("WebhookSubscription", back_populates="deliveries")


# Add relationships to Client model
def add_integration_relationships():
    """Add integration relationships to Client model"""
    from app.models.client import Client

    if not hasattr(Client, 'crm_integrations'):
        Client.crm_integrations = relationship("CRMIntegration", back_populates="client", cascade="all, delete-orphan")

    if not hasattr(Client, 'webhook_subscriptions'):
        Client.webhook_subscriptions = relationship("WebhookSubscription", back_populates="client", cascade="all, delete-orphan")
