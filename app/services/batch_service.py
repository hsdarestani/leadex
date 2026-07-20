"""
Batch queue service for lead accumulation and distribution triggering
"""
from sqlalchemy.orm import Session
from app.models import BatchQueue, Asset
from app.core.config import settings
import uuid
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BatchService:
    """Service for batch queue operations"""
    
    @staticmethod
    def get_or_create_current_batch(db: Session) -> BatchQueue:
        """
        Get the current active batch or create a new one
        
        Args:
            db: Database session
        
        Returns:
            Current BatchQueue object
        """
        # Get the most recent batch that's not full
        current_batch = db.query(BatchQueue).filter(
            BatchQueue.lead_count < settings.BATCH_SIZE
        ).order_by(BatchQueue.created_at.desc()).first()
        
        if not current_batch:
            # Create new batch
            current_batch = BatchQueue(
                id=uuid.uuid4(),
                lead_count=0,
                asset_ids=[]
            )
            db.add(current_batch)
            db.commit()
            db.refresh(current_batch)
        
        return current_batch
    
    @staticmethod
    def add_lead_to_batch(db: Session, lead_id: uuid.UUID) -> Tuple[bool, Optional[list]]:
        """
        Add a lead to the current batch
        
        Args:
            db: Database session
            lead_id: Lead UUID to add
        
        Returns:
            Tuple of (batch_full: bool, lead_ids_to_distribute: Optional[list])
            If batch_full is True, lead_ids_to_distribute contains the batch to distribute
        """
        # Get or create current batch
        batch = BatchService.get_or_create_current_batch(db)
        
        # Add lead to batch
        asset_ids = batch.asset_ids or []
        asset_ids.append(str(lead_id))
        
        batch.asset_ids = asset_ids
        batch.lead_count = len(asset_ids)
        
        db.commit()
        db.refresh(batch)
        
        # Check if batch is full
        if batch.lead_count >= settings.BATCH_SIZE:
            # Batch is full, trigger distribution
            lead_ids_to_distribute = [uuid.UUID(id) for id in batch.asset_ids]
            
            # Update lead statuses to PENDING
            db.query(Asset).filter(
                Asset.id.in_(lead_ids_to_distribute)
            ).update({"status": "PENDING"}, synchronize_session=False)
            
            # Mark batch as distributed
            batch.status = "DISTRIBUTED"
            
            db.commit()
            
            return True, lead_ids_to_distribute
        
        return False, None
    
    @staticmethod
    def trigger_distribution(db: Session, lead_ids: list) -> dict:
        """
        Trigger distribution for a batch of leads
        
        Args:
            db: Database session
            lead_ids: List of lead UUIDs to distribute
            
        Returns:
            Distribution results dictionary
        """
        from app.services.distribution_service import DistributionService
        
        logger.info(f"🚀 Triggering distribution for batch of {len(lead_ids)} leads")
        
        # Call distribution service
        results = DistributionService.distribute_batch(lead_ids, db)
        
        logger.info(f"Distribution complete: {results}")
        return results
