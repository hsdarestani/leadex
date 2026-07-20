"""
Celery background tasks for async processing
"""
from datetime import datetime, timedelta
from typing import List
from celery import Task
from sqlalchemy.orm import Session
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.asset import Asset
from app.models.client import Client
from app.models.delivery import Delivery
from app.models.notification import Notification


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def send_email_task(self, to_email: str, subject: str, body: str, html_body: str = None):
    """
    Send email asynchronously

    Args:
        to_email: Recipient email
        subject: Email subject
        body: Plain text body
        html_body: HTML body (optional)
    """
    try:
        from app.services.email_service import send_email
        send_email(to_email, subject, body, html_body)
        return {'status': 'success', 'to': to_email}
    except Exception as e:
        # Retry up to 3 times with exponential backoff
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=DatabaseTask, bind=True)
def send_webhook_task(self, delivery_id: str):
    """
    Send webhook asynchronously

    Args:
        delivery_id: Delivery record ID
    """
    try:
        from app.services.delivery_service import retry_delivery

        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            return {'status': 'error', 'message': 'Delivery not found'}

        result = retry_delivery(self.db, delivery_id)
        return {'status': 'success', 'delivery_id': delivery_id, 'result': result}
    except Exception as e:
        # Retry up to 3 times
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=DatabaseTask, bind=True)
def distribute_leads_task(self, batch_size: int = 10):
    """
    Distribute leads to clients asynchronously

    Args:
        batch_size: Number of leads to distribute
    """
    try:
        from app.services.distribution_service import distribute_leads

        result = distribute_leads(self.db, batch_size)
        return {
            'status': 'success',
            'distributed': result.get('distributed_count', 0),
            'queued': result.get('queued_count', 0)
        }
    except Exception as e:
        self.retry(exc=e, countdown=60)


@celery_app.task(base=DatabaseTask, bind=True)
def process_stored_leads_task(self):
    """
    Process stored leads in queue (runs periodically)
    """
    try:
        from app.services.distribution_service import process_stored_leads

        result = process_stored_leads(self.db)
        return {
            'status': 'success',
            'processed': result.get('processed_count', 0)
        }
    except Exception as e:
        print(f"Error processing stored leads: {e}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def send_daily_summaries(self):
    """
    Send daily summary emails to all clients and admins
    """
    try:
        from app.services.notification_service import send_daily_summary

        # Get all active clients
        clients = self.db.query(Client).filter(Client.is_active == True).all()

        sent_count = 0
        for client in clients:
            try:
                send_daily_summary(self.db, client.id, 'client')
                sent_count += 1
            except Exception as e:
                print(f"Error sending daily summary to client {client.id}: {e}")

        return {
            'status': 'success',
            'sent_count': sent_count,
            'total_clients': len(clients)
        }
    except Exception as e:
        print(f"Error in daily summaries task: {e}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def send_weekly_summaries(self):
    """
    Send weekly summary emails to all clients and admins
    """
    try:
        from app.services.notification_service import send_weekly_summary

        # Get all active clients
        clients = self.db.query(Client).filter(Client.is_active == True).all()

        sent_count = 0
        for client in clients:
            try:
                send_weekly_summary(self.db, client.id, 'client')
                sent_count += 1
            except Exception as e:
                print(f"Error sending weekly summary to client {client.id}: {e}")

        return {
            'status': 'success',
            'sent_count': sent_count,
            'total_clients': len(clients)
        }
    except Exception as e:
        print(f"Error in weekly summaries task: {e}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def cleanup_old_data(self):
    """
    Cleanup old data (notifications, logs, etc.)
    Runs daily at 2 AM
    """
    try:
        # Delete notifications older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        deleted_notifications = self.db.query(Notification).filter(
            Notification.created_at < thirty_days_ago,
            Notification.is_read == True
        ).delete()

        self.db.commit()

        return {
            'status': 'success',
            'deleted_notifications': deleted_notifications
        }
    except Exception as e:
        self.db.rollback()
        print(f"Error in cleanup task: {e}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def calculate_lead_scores_batch(self, asset_ids: List[str]):
    """
    Calculate lead scores for multiple leads asynchronously

    Args:
        asset_ids: List of asset IDs to score
    """
    try:
        from app.services.advanced_service import calculate_lead_score

        scored_count = 0
        for asset_id in asset_ids:
            try:
                calculate_lead_score(self.db, asset_id)
                scored_count += 1
            except Exception as e:
                print(f"Error scoring lead {asset_id}: {e}")

        return {
            'status': 'success',
            'scored_count': scored_count,
            'total_leads': len(asset_ids)
        }
    except Exception as e:
        print(f"Error in batch scoring task: {e}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def retry_failed_deliveries(self):
    """
    Retry failed deliveries that haven't exceeded max retries
    """
    try:
        from app.services.delivery_service import retry_delivery

        # Get failed deliveries with retries remaining
        failed_deliveries = self.db.query(Delivery).filter(
            Delivery.status == 'FAILED',
            Delivery.retry_count < 3
        ).limit(100).all()

        retried_count = 0
        for delivery in failed_deliveries:
            try:
                retry_delivery(self.db, str(delivery.id))
                retried_count += 1
            except Exception as e:
                print(f"Error retrying delivery {delivery.id}: {e}")

        return {
            'status': 'success',
            'retried_count': retried_count,
            'total_failed': len(failed_deliveries)
        }
    except Exception as e:
        print(f"Error in retry failed deliveries task: {e}")
        return {'status': 'error', 'message': str(e)}
