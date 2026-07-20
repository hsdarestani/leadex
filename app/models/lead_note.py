"""
Lead Note Model
Tracks notes and comments on leads
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class LeadNote(Base):
    __tablename__ = "lead_notes"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Keys
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=True, index=True)
    created_by_client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True)
    
    # Note Content
    note = Column(Text, nullable=False)
    
    # Metadata
    is_internal = Column(Boolean, default=False)  # Internal notes only visible to admins
    is_pinned = Column(Boolean, default=False, index=True)  # Pinned notes appear at top
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset = relationship("Asset", backref="notes")
    created_by_admin = relationship("AdminUser", backref="lead_notes")
    created_by_client = relationship("Client", backref="lead_notes")
    
    def __repr__(self):
        return f"<LeadNote {self.id} - Asset {self.asset_id}>"


class LeadTag(Base):
    __tablename__ = "lead_tags"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Tag Details
    name = Column(String(100), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True)  # Hex color code
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<LeadTag {self.name}>"


class AssetTag(Base):
    __tablename__ = "asset_tags"
    
    # Composite Primary Key
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), primary_key=True, index=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("lead_tags.id"), primary_key=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=True)
    
    # Relationships
    asset = relationship("Asset", backref="asset_tags")
    tag = relationship("LeadTag", backref="asset_tags")
    created_by_admin = relationship("AdminUser", backref="asset_tags")
    
    def __repr__(self):
        return f"<AssetTag Asset:{self.asset_id} Tag:{self.tag_id}>"

