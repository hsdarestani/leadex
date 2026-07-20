"""
Delivery Worker
Background worker that processes delivery jobs with retry logic
"""
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.core.database import SessionLocal
from app.models import Asset, Client, Delivery
from app.services.delivery_orchestrator import DeliveryOrchestrator
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeliveryWorker:
    """Background worker for processing delivery jobs"""
    
    @staticmethod
    def process_pending_deliveries():
        """
        Process all pending deliveries with retry logic
        
        Finds leads that are ASSIGNED but not yet delivered,
        and attempts delivery with exponential backoff
        """
        db = SessionLocal()
        
        try:
            logger.info("=" * 70)
            logger.info("DELIVERY WORKER - Processing pending deliveries")
            logger.info("=" * 70)
            
            # Find leads that need delivery
            # Status = ASSIGNED means credits were deducted but delivery not yet attempted/completed
            pending_leads = db.query(Asset).filter(
                Asset.status == "ASSIGNED"
            ).all()
            
            if not pending_leads:
                logger.info("No pending deliveries found")
                return
            
            logger.info(f"Found {len(pending_leads)} leads pending delivery")
            
            for lead in pending_leads:
                try:
                    # Find the client this lead was assigned to
                    # Get the most recent delivery record for this lead
                    latest_delivery = db.query(Delivery).filter(
                        Delivery.asset_id == lead.id
                    ).order_by(Delivery.timestamp.desc()).first()
                    
                    if not latest_delivery:
                        logger.warning(f"No delivery record found for lead {lead.id}")
                        continue
                    
                    client = db.query(Client).filter(
                        Client.id == latest_delivery.client_id
                    ).first()
                    
                    if not client:
                        logger.warning(f"Client not found for lead {lead.id}")
                        continue
                    
                    # Determine attempt number
                    attempt_count = db.query(Delivery).filter(
                        and_(
                            Delivery.asset_id == lead.id,
                            Delivery.client_id == client.id
                        )
                    ).count()
                    
                    next_attempt = attempt_count + 1
                    
                    # Check if we've exceeded max retries
                    if next_attempt > settings.RETRY_ATTEMPTS:
                        logger.warning(f"Lead {lead.id} exceeded max retries ({settings.RETRY_ATTEMPTS})")
                        lead.status = "FAILED"
                        lead.updated_at = datetime.utcnow()
                        db.commit()
                        continue
                    
                    # Check if we should retry based on exponential backoff
                    if latest_delivery and not latest_delivery.success:
                        # Exponential backoff: 1 min, 5 min, 15 min
                        backoff_minutes = [1, 5, 15]
                        wait_minutes = backoff_minutes[min(attempt_count - 1, len(backoff_minutes) - 1)]
                        
                        next_retry_time = latest_delivery.timestamp + timedelta(minutes=wait_minutes)
                        
                        if datetime.utcnow() < next_retry_time:
                            logger.info(f"Lead {lead.id} waiting for retry (next attempt at {next_retry_time})")
                            continue
                    
                    # Attempt delivery
                    logger.info(f"Attempting delivery for lead {lead.id} (attempt {next_attempt}/{settings.RETRY_ATTEMPTS})")
                    
                    result = DeliveryOrchestrator.deliver_lead(
                        lead=lead,
                        client=client,
                        db=db,
                        attempt_number=next_attempt
                    )
                    
                    if result["overall_success"]:
                        logger.info(f"✅ Lead {lead.id} delivered successfully")
                    else:
                        logger.warning(f"❌ Lead {lead.id} delivery failed (attempt {next_attempt})")
                    
                    # Small delay between deliveries
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing lead {lead.id}: {str(e)}", exc_info=True)
                    db.rollback()
                    continue
            
            logger.info("Delivery worker completed")
            
        except Exception as e:
            logger.error(f"Delivery worker error: {str(e)}", exc_info=True)
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def run_forever(interval_seconds: int = 60):
        """
        Run the delivery worker in a loop
        
        Args:
            interval_seconds: Seconds to wait between runs (default: 60)
        """
        logger.info(f"Starting delivery worker (interval: {interval_seconds}s)")
        
        while True:
            try:
                DeliveryWorker.process_pending_deliveries()
            except Exception as e:
                logger.error(f"Delivery worker loop error: {str(e)}", exc_info=True)
            
            time.sleep(interval_seconds)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the worker
    DeliveryWorker.run_forever(interval_seconds=60)

