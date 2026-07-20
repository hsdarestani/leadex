"""
Report models for saved reports and templates
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Report(Base):
    """Saved custom reports"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Report configuration
    report_type = Column(String(50), nullable=False)  # leads, clients, analytics, custom
    fields = Column(JSON, nullable=False)  # Selected fields to include
    filters = Column(JSON)  # Filter conditions
    grouping = Column(JSON)  # Grouping configuration
    aggregations = Column(JSON)  # Aggregation functions
    sorting = Column(JSON)  # Sort order

    # Template or custom
    is_template = Column(Boolean, default=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey('reports.id'), nullable=True)

    # Owner
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey('admin_users.id'))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    created_by = relationship("AdminUser", foreign_keys=[created_by_admin_id])
    schedules = relationship("ReportSchedule", back_populates="report", cascade="all, delete-orphan")
    exports = relationship("ReportExport", back_populates="report", cascade="all, delete-orphan")


class ReportSchedule(Base):
    """Scheduled report generation and delivery"""
    __tablename__ = "report_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('reports.id'), nullable=False)

    # Schedule configuration
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, custom
    cron_expression = Column(String(100))  # For custom schedules
    day_of_week = Column(Integer)  # For weekly (0=Monday, 6=Sunday)
    day_of_month = Column(Integer)  # For monthly (1-31)
    time_of_day = Column(String(5))  # HH:MM format

    # Delivery configuration
    delivery_method = Column(String(20), default='email')  # email, webhook
    recipients = Column(JSON, nullable=False)  # List of email addresses or webhook URLs
    export_format = Column(String(10), default='pdf')  # pdf, excel, csv

    # Status
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="schedules")


class ReportExport(Base):
    """Report export history"""
    __tablename__ = "report_exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('reports.id'), nullable=False)

    # Export details
    export_format = Column(String(10), nullable=False)  # pdf, excel, csv
    file_path = Column(String(500))  # Path to generated file
    file_size = Column(Integer)  # Size in bytes

    # Generation details
    generated_by_admin_id = Column(UUID(as_uuid=True), ForeignKey('admin_users.id'))
    generated_at = Column(DateTime, default=datetime.utcnow)
    record_count = Column(Integer)  # Number of records in export

    # Status
    status = Column(String(20), default='pending')  # pending, completed, failed
    error_message = Column(Text)

    # Relationships
    report = relationship("Report", back_populates="exports")
    generated_by = relationship("AdminUser")
