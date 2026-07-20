"""
Custom Field Model
Allows dynamic custom fields for leads
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class FieldType(str, enum.Enum):
    """Custom field type enum"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"


class CustomField(Base):
    __tablename__ = "custom_fields"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Field Details
    name = Column(String(255), nullable=False, unique=True, index=True)
    label = Column(String(255), nullable=False)
    field_type = Column(SQLEnum(FieldType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Field Configuration
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    default_value = Column(Text, nullable=True)
    
    # For SELECT and MULTISELECT types
    options = Column(JSON, nullable=True)  # Array of options
    
    # Validation
    validation_rules = Column(JSON, nullable=True)  # Custom validation rules
    
    # Display
    display_order = Column(Integer, default=0)
    show_in_list = Column(Boolean, default=False)  # Show in lead list view
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CustomField {self.name} - {self.field_type}>"


class CustomFieldValue(Base):
    __tablename__ = "custom_field_values"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    custom_field_id = Column(UUID(as_uuid=True), ForeignKey("custom_fields.id"), nullable=False, index=True)
    
    # Value (stored as text, parsed based on field_type)
    value = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", backref="custom_field_values")
    custom_field = relationship("CustomField", backref="values")
    
    def __repr__(self):
        return f"<CustomFieldValue Asset:{self.asset_id} Field:{self.custom_field_id}>"


class LeadScore(Base):
    __tablename__ = "lead_scores"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Key
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, unique=True, index=True)
    
    # Score Details
    score = Column(Integer, default=0, nullable=False, index=True)
    grade = Column(String(10), nullable=True, index=True)  # A, B, C, D, F
    
    # Score Components (for transparency)
    score_breakdown = Column(JSON, nullable=True)  # Details of how score was calculated
    
    # Metadata
    last_calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculation_version = Column(String(50), nullable=True)  # Track scoring algorithm version
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", backref="lead_score", uselist=False)
    
    def __repr__(self):
        return f"<LeadScore Asset:{self.asset_id} Score:{self.score} Grade:{self.grade}>"

