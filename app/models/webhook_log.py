"""
Webhook Log Model
Tracks all webhook requests and responses for debugging and monitoring
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=True, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True, index=True)
    
    # Webhook Information
    webhook_url = Column(Text, nullable=False)
    method = Column(String(10), default="POST")  # POST, GET, PUT, etc.
    
    # Request Information
    request_headers = Column(JSON, nullable=True)  # Request headers sent
    request_payload = Column(JSON, nullable=True)  # Request body sent
    
    # Response Information
    response_status_code = Column(Integer, nullable=True)  # HTTP status code
    response_headers = Column(JSON, nullable=True)  # Response headers received
    response_body = Column(Text, nullable=True)  # Response body received
    response_time_ms = Column(Float, nullable=True)  # Response time in milliseconds
    
    # Status
    success = Column(Boolean, default=False, index=True)  # Whether the webhook call succeeded
    error_message = Column(Text, nullable=True)  # Error message if failed
    
    # Retry Information
    attempt_number = Column(Integer, default=1)  # 1, 2, 3
    is_retry = Column(Boolean, default=False)  # Whether this is a retry attempt
    
    # Test Mode
    is_test = Column(Boolean, default=False, index=True)  # Whether this is a test webhook
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    client = relationship("Client", backref="webhook_logs")
    delivery = relationship("Delivery", backref="webhook_logs")
    asset = relationship("Asset", backref="webhook_logs")
    
    def __repr__(self):
        return f"<WebhookLog {self.id} - {self.webhook_url} - {self.response_status_code}>"

