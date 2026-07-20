"""
Credit Management Service
Handles credit checking, deduction, and balance tracking
"""
from sqlalchemy.orm import Session
from app.models import Client, Delivery
from app.core.config import settings
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class CreditService:
    """Service for credit management operations"""
    
    @staticmethod
    def check_balance(client: Client) -> float:
        """
        Check client's current credit balance
        
        Args:
            client: Client object
            
        Returns:
            Current credit balance
        """
        return client.credits_balance
    
    @staticmethod
    def has_sufficient_credits(client: Client, num_leads: int = 1) -> bool:
        """
        Check if client has enough credits for specified number of leads
        
        Args:
            client: Client object
            num_leads: Number of leads to check for (default: 1)
            
        Returns:
            True if client has enough credits, False otherwise
        """
        required_credits = num_leads * client.credit_cost_per_lead
        return client.credits_balance >= required_credits
    
    @staticmethod
    def reserve_credits(client: Client, num_leads: int, db: Session) -> bool:
        """
        Reserve credits for lead assignment (deduct from balance)
        NOTE: Credits are reserved when leads are assigned, not when delivered
        This prevents double-spending
        
        Args:
            client: Client object
            num_leads: Number of leads to reserve credits for
            db: Database session
            
        Returns:
            True if credits were reserved successfully, False otherwise
        """
        required_credits = num_leads * client.credit_cost_per_lead
        
        if client.credits_balance < required_credits:
            logger.warning(f"Client {client.name} has insufficient credits: {client.credits_balance} < {required_credits}")
            return False
        
        # Deduct credits
        client.credits_balance -= required_credits
        client.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Reserved {required_credits} credits for client {client.name}. New balance: {client.credits_balance}")
        return True
    
    @staticmethod
    def refund_credits(client: Client, num_leads: int, db: Session) -> None:
        """
        Refund credits to client (e.g., when delivery fails after max retries)
        
        Args:
            client: Client object
            num_leads: Number of leads to refund credits for
            db: Database session
        """
        refund_amount = num_leads * client.credit_cost_per_lead
        
        client.credits_balance += refund_amount
        client.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Refunded {refund_amount} credits to client {client.name}. New balance: {client.credits_balance}")
    
    @staticmethod
    def add_credits(client: Client, amount: float, db: Session) -> None:
        """
        Add credits to client's balance (e.g., when admin tops up)
        
        Args:
            client: Client object
            amount: Amount of credits to add
            db: Database session
        """
        client.credits_balance += amount
        client.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Added {amount} credits to client {client.name}. New balance: {client.credits_balance}")
    
    @staticmethod
    def deduct_credits(client: Client, amount: float, db: Session) -> bool:
        """
        Deduct credits from client's balance
        
        Args:
            client: Client object
            amount: Amount of credits to deduct
            db: Database session
            
        Returns:
            True if credits were deducted successfully, False if insufficient balance
        """
        if client.credits_balance < amount:
            logger.warning(f"Client {client.name} has insufficient credits: {client.credits_balance} < {amount}")
            return False
        
        client.credits_balance -= amount
        client.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Deducted {amount} credits from client {client.name}. New balance: {client.credits_balance}")
        return True
    
    @staticmethod
    def get_credit_usage_stats(client: Client, db: Session) -> dict:
        """
        Get credit usage statistics for a client
        
        Args:
            client: Client object
            db: Database session
            
        Returns:
            Dictionary with credit usage stats
        """
        # Count successful deliveries
        successful_deliveries = db.query(Delivery).filter(
            Delivery.client_id == client.id,
            Delivery.success == True
        ).count()
        
        # Count failed deliveries
        failed_deliveries = db.query(Delivery).filter(
            Delivery.client_id == client.id,
            Delivery.success == False
        ).count()
        
        # Count pending deliveries
        pending_deliveries = db.query(Delivery).filter(
            Delivery.client_id == client.id,
            Delivery.success == False
        ).count()
        
        # Calculate total credits spent (successful deliveries only)
        credits_spent = successful_deliveries * client.credit_cost_per_lead
        
        # Calculate reserved credits (pending deliveries)
        credits_reserved = pending_deliveries * client.credit_cost_per_lead
        
        return {
            "current_balance": client.credits_balance,
            "credits_spent": credits_spent,
            "credits_reserved": credits_reserved,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "pending_deliveries": pending_deliveries,
            "credit_cost_per_lead": client.credit_cost_per_lead
        }
    
    @staticmethod
    def process_delivery_result(delivery: Delivery, success: bool, db: Session) -> None:
        """
        Process delivery result and handle credit logic
        
        NOTE: In our system, credits are deducted when leads are ASSIGNED, not when delivered.
        This function is for tracking purposes only.
        
        Args:
            delivery: Delivery object
            success: Whether delivery was successful
            db: Database session
        """
        if success:
            # Delivery successful - credits already deducted during assignment
            delivery.success = True
            logger.info(f"Delivery {delivery.id} successful. Credits already deducted during assignment.")
        else:
            # Delivery failed
            if delivery.attempt_number >= settings.RETRY_ATTEMPTS:
                # Max retries reached - refund credits
                client = db.query(Client).filter(Client.id == delivery.client_id).first()
                if client:
                    CreditService.refund_credits(client, 1, db)
                    logger.info(f"Delivery {delivery.id} failed after max retries. Credits refunded.")
                
                delivery.success = False
            else:
                # Will retry - keep credits reserved
                delivery.success = False
                logger.info(f"Delivery {delivery.id} failed. Will retry. Credits remain reserved.")
        
        delivery.updated_at = datetime.utcnow()
        db.commit()
