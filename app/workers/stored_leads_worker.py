"""
Stored Leads Worker
Redistributes stored leads every 1 minute in batches of 10
"""
import time
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import StoredLead, Asset
from app.services.distribution_service import DistributionService
from app.core.config import settings
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StoredLeadsWorker:
    """Worker for redistributing stored leads"""
    
    def __init__(self):
        self.interval_seconds = settings.STORED_LEADS_INTERVAL_MINUTES * 60
        self.batch_size = settings.BATCH_SIZE
        self.running = False
    
    def get_stored_leads_batch(self, db: Session) -> list:
        """
        Get a batch of stored leads to redistribute
        
        Args:
            db: Database session
            
        Returns:
            List of lead IDs to redistribute
        """
        # Get oldest stored leads (FIFO)
        stored_leads = db.query(StoredLead).order_by(
            StoredLead.created_at.asc()
        ).limit(self.batch_size).all()
        
        if not stored_leads:
            return []
        
        lead_ids = [stored_lead.asset_id for stored_lead in stored_leads]
        
        logger.info(f"Retrieved {len(lead_ids)} stored leads for redistribution")
        return lead_ids, stored_leads
    
    def process_batch(self, db: Session) -> dict:
        """
        Process a batch of stored leads
        
        Args:
            db: Database session
            
        Returns:
            Distribution results
        """
        # Get batch of stored leads
        result = self.get_stored_leads_batch(db)
        
        if not result:
            logger.debug("No stored leads to redistribute")
            return {"processed": 0}
        
        lead_ids, stored_lead_records = result
        
        logger.info(f"Processing batch of {len(lead_ids)} stored leads")
        
        # Attempt redistribution
        distribution_results = DistributionService.distribute_batch(lead_ids, db)
        
        # Remove successfully assigned leads from stored_leads table
        if distribution_results.get("assigned", 0) > 0:
            assigned_lead_ids = []
            for assignment in distribution_results.get("assignments", {}).values():
                assigned_lead_ids.extend([uuid.UUID(lid) for lid in assignment.get("lead_ids", [])])
            
            if assigned_lead_ids:
                # Delete stored lead records for assigned leads
                db.query(StoredLead).filter(
                    StoredLead.asset_id.in_(assigned_lead_ids)
                ).delete(synchronize_session=False)
                
                db.commit()
                
                logger.info(f"Removed {len(assigned_lead_ids)} stored leads that were successfully assigned")
        
        # Update retry count for leads that remain stored
        if distribution_results.get("stored", 0) > 0:
            stored_lead_ids = [uuid.UUID(lid) for lid in distribution_results.get("stored_lead_ids", [])]
            
            for stored_lead in stored_lead_records:
                if stored_lead.asset_id in stored_lead_ids:
                    stored_lead.retry_count += 1
            
            db.commit()
            
            logger.info(f"{len(stored_lead_ids)} leads remain stored (no credits available)")
        
        return {
            "processed": len(lead_ids),
            "assigned": distribution_results.get("assigned", 0),
            "still_stored": distribution_results.get("stored", 0)
        }
    
    def run(self):
        """
        Main worker loop - runs continuously
        """
        self.running = True
        logger.info(f"Stored Leads Worker started (interval: {self.interval_seconds}s, batch size: {self.batch_size})")
        
        while self.running:
            try:
                db = SessionLocal()
                
                try:
                    results = self.process_batch(db)
                    
                    if results.get("processed", 0) > 0:
                        logger.info(f"Batch processed: {results}")
                    
                finally:
                    db.close()
                
                # Sleep for interval
                time.sleep(self.interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in stored leads worker: {e}", exc_info=True)
                time.sleep(self.interval_seconds)
        
        logger.info("Stored Leads Worker stopped")
    
    def stop(self):
        """Stop the worker"""
        self.running = False


if __name__ == "__main__":
    worker = StoredLeadsWorker()
    worker.run()

