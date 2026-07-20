from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    # Delivery Information
    delivery_method = Column(String(50), nullable=False)  # webhook, whatsapp, email, google_sheet
    payload = Column(JSON, nullable=True)  # The data sent
    
    # Response Information
    response_status = Column(String(50), nullable=True)  # HTTP codes or provider codes
    response_body = Column(Text, nullable=True)
    
    # Attempt Information
    attempt_number = Column(Integer, default=1)  # 1, 2, 3
    success = Column(Boolean, default=False, index=True)
    
    # Credits
    credit_charged = Column(Float, default=0.0)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="deliveries")
    client = relationship("Client", back_populates="deliveries")
    
    def __repr__(self):
        return f"<Delivery {self.delivery_method} - {'Success' if self.success else 'Failed'}>"
