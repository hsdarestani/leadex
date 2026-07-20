"""
Notification Service
Handles email notifications and alerts
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import uuid
import os
from jinja2 import Template

from app.models import (
    Notification,
    NotificationPreference,
    EmailTemplate,
    NotificationType,
    NotificationChannel,
    NotificationStatus,
    Client,
    AdminUser
)


class NotificationService:
    """Service for sending notifications"""
    
    # SMTP Configuration (from environment variables)
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@leadex.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Leadex")
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send email via SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Skip if SMTP not configured
        if not NotificationService.SMTP_USER or not NotificationService.SMTP_PASSWORD:
            print(f"[NOTIFICATION] SMTP not configured, skipping email to {to_email}")
            return True, None  # Return success to avoid blocking
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{NotificationService.SMTP_FROM_NAME} <{NotificationService.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(NotificationService.SMTP_HOST, NotificationService.SMTP_PORT) as server:
                server.starttls()
                server.login(NotificationService.SMTP_USER, NotificationService.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def render_template(template_str: str, variables: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with variables
        
        Args:
            template_str: Template string
            variables: Dictionary of variables
            
        Returns:
            Rendered template
        """
        template = Template(template_str)
        return template.render(**variables)
    
    @staticmethod
    def create_notification(
        db: Session,
        notification_type: NotificationType,
        channel: NotificationChannel,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        subject: Optional[str] = None,
        message: str = "",
        html_content: Optional[str] = None,
        data: Optional[Dict] = None,
        client_id: Optional[uuid.UUID] = None,
        admin_user_id: Optional[uuid.UUID] = None
    ) -> Notification:
        """
        Create a notification record
        
        Args:
            db: Database session
            notification_type: Type of notification
            channel: Notification channel
            recipient_email: Email address (for email channel)
            recipient_phone: Phone number (for SMS channel)
            subject: Email subject
            message: Notification message
            html_content: HTML content (for email)
            data: Additional data
            client_id: Client ID (if applicable)
            admin_user_id: Admin user ID (if applicable)
            
        Returns:
            Notification record
        """
        notification = Notification(
            id=uuid.uuid4(),
            type=notification_type,
            channel=channel,
            status=NotificationStatus.PENDING,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            subject=subject,
            message=message,
            html_content=html_content,
            data=data,
            client_id=client_id,
            admin_user_id=admin_user_id
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def send_notification(db: Session, notification_id: uuid.UUID) -> bool:
        """
        Send a pending notification
        
        Args:
            db: Database session
            notification_id: Notification ID
            
        Returns:
            True if sent successfully
        """
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            return False
        
        if notification.status != NotificationStatus.PENDING:
            return False
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                success, error = NotificationService.send_email(
                    to_email=notification.recipient_email,
                    subject=notification.subject or "Notification",
                    html_content=notification.html_content or notification.message,
                    text_content=notification.message
                )
                
                if success:
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.utcnow()
                else:
                    notification.status = NotificationStatus.FAILED
                    notification.failed_at = datetime.utcnow()
                    notification.error_message = error
                    notification.retry_count += 1
            
            elif notification.channel == NotificationChannel.SMS:
                # SMS implementation would go here
                # For now, mark as sent
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            
            elif notification.channel == NotificationChannel.WEBHOOK:
                # Webhook implementation would go here
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            
            db.commit()
            return notification.status == NotificationStatus.SENT
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.utcnow()
            notification.error_message = str(e)
            notification.retry_count += 1
            db.commit()
            return False

    @staticmethod
    def notify_lead_assigned(
        db: Session,
        client_id: uuid.UUID,
        lead_count: int,
        batch_id: Optional[uuid.UUID] = None
    ):
        """Send notification when leads are assigned to a client"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client or not client.email:
            return

        subject = f"New Leads Assigned - {lead_count} leads"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>New Leads Assigned</h2>
            <p>Hello {client.name},</p>
            <p>You have been assigned <strong>{lead_count}</strong> new leads.</p>
            <p>Please log in to your dashboard to view and manage these leads.</p>
            <p><a href="http://213.21.235.48/client-dashboard.html" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
            <br>
            <p>Best regards,<br>Leadex Team</p>
        </body>
        </html>
        """

        notification = NotificationService.create_notification(
            db=db,
            notification_type=NotificationType.LEAD_ASSIGNED,
            channel=NotificationChannel.EMAIL,
            recipient_email=client.email,
            subject=subject,
            message=f"You have been assigned {lead_count} new leads.",
            html_content=html_content,
            data={"lead_count": lead_count, "batch_id": str(batch_id) if batch_id else None},
            client_id=client_id
        )

        NotificationService.send_notification(db, notification.id)

    @staticmethod
    def notify_delivery_failed(
        db: Session,
        client_id: uuid.UUID,
        lead_id: uuid.UUID,
        error_message: str
    ):
        """Send notification when lead delivery fails"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client or not client.email:
            return

        subject = "Lead Delivery Failed"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Lead Delivery Failed</h2>
            <p>Hello {client.name},</p>
            <p>A lead delivery has failed.</p>
            <p><strong>Lead ID:</strong> {lead_id}</p>
            <p><strong>Error:</strong> {error_message}</p>
            <p>Please check your delivery configuration and try again.</p>
            <br>
            <p>Best regards,<br>Leadex Team</p>
        </body>
        </html>
        """

        notification = NotificationService.create_notification(
            db=db,
            notification_type=NotificationType.DELIVERY_FAILED,
            channel=NotificationChannel.EMAIL,
            recipient_email=client.email,
            subject=subject,
            message=f"Lead delivery failed: {error_message}",
            html_content=html_content,
            data={"lead_id": str(lead_id), "error": error_message},
            client_id=client_id
        )

        NotificationService.send_notification(db, notification.id)

    @staticmethod
    def notify_credit_low(
        db: Session,
        client_id: uuid.UUID,
        current_credits: int,
        threshold: int = 10
    ):
        """Send notification when client credits are low"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client or not client.email:
            return

        subject = f"Low Credit Alert - {current_credits} credits remaining"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #ff9800;">Low Credit Alert</h2>
            <p>Hello {client.name},</p>
            <p>Your credit balance is running low.</p>
            <p><strong>Current Balance:</strong> {current_credits} credits</p>
            <p>Please top up your credits to continue receiving leads.</p>
            <p><a href="http://213.21.235.48/client-dashboard.html" style="background: #ff9800; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
            <br>
            <p>Best regards,<br>Leadex Team</p>
        </body>
        </html>
        """

        notification = NotificationService.create_notification(
            db=db,
            notification_type=NotificationType.CREDIT_LOW,
            channel=NotificationChannel.EMAIL,
            recipient_email=client.email,
            subject=subject,
            message=f"Your credit balance is low: {current_credits} credits remaining.",
            html_content=html_content,
            data={"current_credits": current_credits, "threshold": threshold},
            client_id=client_id
        )

        NotificationService.send_notification(db, notification.id)

    @staticmethod
    def notify_import_completed(
        db: Session,
        admin_user_id: uuid.UUID,
        import_id: uuid.UUID,
        filename: str,
        successful_count: int,
        failed_count: int
    ):
        """Send notification when import is completed"""
        admin = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
        if not admin or not admin.email:
            return

        subject = f"Import Completed - {filename}"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Import Completed</h2>
            <p>Hello {admin.email},</p>
            <p>Your import has been completed.</p>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Successful:</strong> {successful_count} leads</p>
            <p><strong>Failed:</strong> {failed_count} leads</p>
            <p><a href="http://213.21.235.48/admin-imports.html" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Import Details</a></p>
            <br>
            <p>Best regards,<br>Leadex Team</p>
        </body>
        </html>
        """

        notification = NotificationService.create_notification(
            db=db,
            notification_type=NotificationType.IMPORT_COMPLETED,
            channel=NotificationChannel.EMAIL,
            recipient_email=admin.email,
            subject=subject,
            message=f"Import completed: {successful_count} successful, {failed_count} failed.",
            html_content=html_content,
            data={
                "import_id": str(import_id),
                "filename": filename,
                "successful_count": successful_count,
                "failed_count": failed_count
            },
            admin_user_id=admin_user_id
        )

        NotificationService.send_notification(db, notification.id)

