"""
Admin Notification API
Endpoints for managing notifications and preferences
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.models import (
    AdminUser,
    Notification,
    NotificationPreference,
    EmailTemplate,
    NotificationType,
    NotificationChannel,
    NotificationStatus
)
from app.services.notification_service import NotificationService


router = APIRouter()


# Pydantic Models
class NotificationResponse(BaseModel):
    id: str
    type: str
    channel: str
    status: str
    recipient_email: Optional[str]
    subject: Optional[str]
    message: str
    sent_at: Optional[datetime]
    failed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    total_notifications: int
    sent: int
    failed: int
    pending: int
    success_rate: float


class SendTestEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str


class NotificationPreferenceResponse(BaseModel):
    id: str
    notification_type: str
    email_enabled: bool
    sms_enabled: bool
    webhook_enabled: bool
    in_app_enabled: bool
    email_address: Optional[str]
    phone_number: Optional[str]
    webhook_url: Optional[str]
    threshold_value: Optional[int]
    
    class Config:
        from_attributes = True


class UpdatePreferenceRequest(BaseModel):
    notification_type: str
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    webhook_url: Optional[str] = None
    threshold_value: Optional[int] = None


@router.get("/history", response_model=List[NotificationResponse])
def get_notification_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    type_filter: Optional[str] = Query(None),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification history"""
    query = db.query(Notification)
    
    # Apply filters
    if status_filter:
        query = query.filter(Notification.status == status_filter)
    
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    
    # Get notifications
    notifications = query.order_by(desc(Notification.created_at)).limit(limit).offset(offset).all()
    
    return [
        NotificationResponse(
            id=str(n.id),
            type=n.type.value,
            channel=n.channel.value,
            status=n.status.value,
            recipient_email=n.recipient_email,
            subject=n.subject,
            message=n.message,
            sent_at=n.sent_at,
            failed_at=n.failed_at,
            error_message=n.error_message,
            retry_count=n.retry_count,
            created_at=n.created_at
        )
        for n in notifications
    ]


@router.get("/stats", response_model=NotificationStatsResponse)
def get_notification_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    total = db.query(Notification).count()
    sent = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
    failed = db.query(Notification).filter(Notification.status == NotificationStatus.FAILED).count()
    pending = db.query(Notification).filter(Notification.status == NotificationStatus.PENDING).count()
    
    success_rate = (sent / total * 100) if total > 0 else 0.0
    
    return NotificationStatsResponse(
        total_notifications=total,
        sent=sent,
        failed=failed,
        pending=pending,
        success_rate=success_rate
    )


@router.post("/test-email")
def send_test_email(
    request: SendTestEmailRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send a test email"""
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Test Email</h2>
        <p>{request.message}</p>
        <br>
        <p>This is a test email from Leadex.</p>
    </body>
    </html>
    """
    
    success, error = NotificationService.send_email(
        to_email=request.to_email,
        subject=request.subject,
        html_content=html_content,
        text_content=request.message
    )
    
    if success:
        return {"message": "Test email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {error}")


@router.post("/retry/{notification_id}")
def retry_notification(
    notification_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retry a failed notification"""
    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID")

    notification = db.query(Notification).filter(Notification.id == notif_uuid).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.status != NotificationStatus.FAILED:
        raise HTTPException(status_code=400, detail="Only failed notifications can be retried")

    if notification.retry_count >= notification.max_retries:
        raise HTTPException(status_code=400, detail="Maximum retry attempts reached")

    # Reset status to pending
    notification.status = NotificationStatus.PENDING
    notification.error_message = None
    db.commit()

    # Try to send
    success = NotificationService.send_notification(db, notif_uuid)

    if success:
        return {"message": "Notification sent successfully"}
    else:
        return {"message": "Notification retry failed", "error": notification.error_message}


@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
def get_notification_preferences(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification preferences for admin user"""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.admin_user_id == admin.id
    ).all()

    return [
        NotificationPreferenceResponse(
            id=str(p.id),
            notification_type=p.notification_type.value,
            email_enabled=p.email_enabled,
            sms_enabled=p.sms_enabled,
            webhook_enabled=p.webhook_enabled,
            in_app_enabled=p.in_app_enabled,
            email_address=p.email_address,
            phone_number=p.phone_number,
            webhook_url=p.webhook_url,
            threshold_value=p.threshold_value
        )
        for p in preferences
    ]


@router.post("/preferences")
def update_notification_preference(
    request: UpdatePreferenceRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update notification preference"""
    # Validate notification type
    try:
        notif_type = NotificationType(request.notification_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification type")

    # Find or create preference
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.admin_user_id == admin.id,
        NotificationPreference.notification_type == notif_type
    ).first()

    if not preference:
        preference = NotificationPreference(
            id=uuid.uuid4(),
            admin_user_id=admin.id,
            notification_type=notif_type
        )
        db.add(preference)

    # Update fields
    if request.email_enabled is not None:
        preference.email_enabled = request.email_enabled
    if request.sms_enabled is not None:
        preference.sms_enabled = request.sms_enabled
    if request.webhook_enabled is not None:
        preference.webhook_enabled = request.webhook_enabled
    if request.in_app_enabled is not None:
        preference.in_app_enabled = request.in_app_enabled
    if request.email_address is not None:
        preference.email_address = request.email_address
    if request.phone_number is not None:
        preference.phone_number = request.phone_number
    if request.webhook_url is not None:
        preference.webhook_url = request.webhook_url
    if request.threshold_value is not None:
        preference.threshold_value = request.threshold_value

    preference.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(preference)

    return {
        "message": "Preference updated successfully",
        "preference": NotificationPreferenceResponse(
            id=str(preference.id),
            notification_type=preference.notification_type.value,
            email_enabled=preference.email_enabled,
            sms_enabled=preference.sms_enabled,
            webhook_enabled=preference.webhook_enabled,
            in_app_enabled=preference.in_app_enabled,
            email_address=preference.email_address,
            phone_number=preference.phone_number,
            webhook_url=preference.webhook_url,
            threshold_value=preference.threshold_value
        )
    }

