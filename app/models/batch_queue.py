from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base


class BatchQueue(Base):
    __tablename__ = "batch_queue"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Batch Information
    lead_count = Column(Integer, default=0)  # 0-9 (when it reaches 10, distribution starts)
    asset_ids = Column(JSON, default=list)  # List of asset UUIDs in this batch
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<BatchQueue {self.lead_count}/10>"
