"""
Notification Model
Tracks all system notifications and alerts
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enum"""
    LEAD_ASSIGNED = "lead_assigned"
    DELIVERY_SUCCESS = "delivery_success"
    DELIVERY_FAILED = "delivery_failed"
    CREDIT_LOW = "credit_low"
    CREDIT_DEPLETED = "credit_depleted"
    IMPORT_COMPLETED = "import_completed"
    IMPORT_FAILED = "import_failed"
    BATCH_READY = "batch_ready"
    WEBHOOK_FAILED = "webhook_failed"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"


class NotificationChannel(str, enum.Enum):
    """Notification channel enum"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    """Notification status enum"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Notification(Base):
    __tablename__ = "notifications"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=True, index=True)
    
    # Notification Details
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    channel = Column(SQLEnum(NotificationChannel), nullable=False, index=True)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False, index=True)
    
    # Recipients
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    recipient_webhook = Column(Text, nullable=True)
    
    # Content
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    
    # Metadata
    data = Column(JSON, nullable=True)  # Additional data for the notification
    
    # Delivery Information
    sent_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    client = relationship("Client", backref="notifications")
    admin_user = relationship("AdminUser", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.type} - {self.status}>"


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=True, index=True)
    
    # Preferences
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    webhook_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    
    # Custom Settings
    email_address = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    webhook_url = Column(Text, nullable=True)
    
    # Thresholds (for alerts like credit_low)
    threshold_value = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    client = relationship("Client", backref="notification_preferences")
    admin_user = relationship("AdminUser", backref="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreference {self.id} - {self.notification_type}>"


class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Template Details
    name = Column(String(255), nullable=False, unique=True, index=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    
    # Content
    subject = Column(String(500), nullable=False)
    html_template = Column(Text, nullable=False)
    text_template = Column(Text, nullable=True)
    
    # Variables (JSON array of variable names)
    variables = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<EmailTemplate {self.name} - {self.notification_type}>"

