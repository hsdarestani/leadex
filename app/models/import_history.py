"""
Import History Model
Tracks all lead import operations
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class ImportStatus(str, enum.Enum):
    """Import status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some leads imported, some failed


class ImportHistory(Base):
    __tablename__ = "import_history"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True, index=True)
    landing_page_id = Column(UUID(as_uuid=True), ForeignKey("landing_pages.id"), nullable=True, index=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_type = Column(String(50), nullable=True)  # csv, xlsx, etc.
    
    # Import Configuration
    source = Column(String(100), nullable=True)  # Source identifier
    mapping = Column(JSON, nullable=True)  # Column mapping configuration
    
    # Import Status
    status = Column(SQLEnum(ImportStatus), default=ImportStatus.PENDING, nullable=False, index=True)
    
    # Import Statistics
    total_rows = Column(Integer, default=0)  # Total rows in file
    processed_rows = Column(Integer, default=0)  # Rows processed
    successful_imports = Column(Integer, default=0)  # Successfully imported leads
    failed_imports = Column(Integer, default=0)  # Failed imports
    duplicate_skipped = Column(Integer, default=0)  # Duplicates skipped
    
    # Error Information
    error_message = Column(Text, nullable=True)  # Overall error message
    error_details = Column(JSON, nullable=True)  # Detailed error log (row-by-row)
    
    # Processing Information
    started_at = Column(DateTime, nullable=True)  # When processing started
    completed_at = Column(DateTime, nullable=True)  # When processing completed
    processing_time_seconds = Column(Integer, nullable=True)  # Total processing time
    
    # Rollback Information
    can_rollback = Column(Boolean, default=True)  # Whether import can be rolled back
    rolled_back = Column(Boolean, default=False, index=True)  # Whether import was rolled back
    rolled_back_at = Column(DateTime, nullable=True)  # When rollback occurred
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    admin_user = relationship("AdminUser", backref="import_history")
    campaign = relationship("Campaign", backref="import_history")
    landing_page = relationship("LandingPage", backref="import_history")
    
    def __repr__(self):
        return f"<ImportHistory {self.id} - {self.filename} - {self.status}>"
    
    @property
    def success_rate(self):
        """Calculate success rate"""
        if self.total_rows == 0:
            return 0.0
        return (self.successful_imports / self.total_rows) * 100
    
    @property
    def is_complete(self):
        """Check if import is complete"""
        return self.status in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.PARTIAL]

