"""
Admin Statistics Endpoints
System statistics and analytics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import Asset, Client, Delivery, StoredLead, BatchQueue, AdminUser
from app.api.dependencies import get_current_admin
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get dashboard statistics
    
    Args:
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        Dashboard statistics
    """
    # Total leads by status
    total_leads = db.query(func.count(Asset.id)).scalar()
    leads_by_status = db.query(
        Asset.status,
        func.count(Asset.id)
    ).group_by(Asset.status).all()
    
    status_counts = {status: count for status, count in leads_by_status}
    
    # Total clients
    total_clients = db.query(func.count(Client.id)).scalar()
    active_clients = db.query(func.count(Client.id)).filter(Client.status == "active").scalar()
    
    # Total deliveries
    total_deliveries = db.query(func.count(Delivery.id)).scalar()
    successful_deliveries = db.query(func.count(Delivery.id)).filter(Delivery.success == True).scalar()
    
    # Stored leads
    stored_leads_count = db.query(func.count(StoredLead.id)).scalar()

    # Pending batches (all batches are pending by nature)
    pending_batches = db.query(func.count(BatchQueue.id)).scalar()
    
    # Today's leads
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_leads = db.query(func.count(Asset.id)).filter(
        Asset.created_at >= today_start
    ).scalar()
    
    # This week's leads
    week_start = datetime.utcnow() - timedelta(days=7)
    week_leads = db.query(func.count(Asset.id)).filter(
        Asset.created_at >= week_start
    ).scalar()
    
    # Client statistics
    clients = db.query(Client).all()
    client_stats = []
    
    for client in clients:
        assigned_leads = db.query(func.count(Delivery.id)).filter(
            Delivery.client_id == client.id
        ).scalar()
        
        successful_deliveries_count = db.query(func.count(Delivery.id)).filter(
            Delivery.client_id == client.id,
            Delivery.success == True
        ).scalar()
        
        client_stats.append({
            "id": str(client.id),
            "name": client.name,
            "percentage": client.percentage,
            "credits_balance": client.credits_balance,
            "status": client.status,
            "assigned_leads": assigned_leads,
            "successful_deliveries": successful_deliveries_count,
            "delivery_rate": (successful_deliveries_count / assigned_leads * 100) if assigned_leads > 0 else 0
        })
    
    return {
        "overview": {
            "total_leads": total_leads,
            "today_leads": today_leads,
            "week_leads": week_leads,
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "delivery_success_rate": (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
            "stored_leads": stored_leads_count,
            "pending_batches": pending_batches
        },
        "leads_by_status": status_counts,
        "clients": client_stats
    }


@router.get("/delivery-methods")
def get_delivery_method_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get statistics by delivery method
    
    Args:
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        Delivery method statistics
    """
    # Deliveries by method
    deliveries_by_method = db.query(
        Delivery.delivery_method,
        func.count(Delivery.id).label("total"),
        func.sum(func.cast(Delivery.success, func.Integer)).label("successful")
    ).group_by(Delivery.delivery_method).all()
    
    method_stats = []
    for method, total, successful in deliveries_by_method:
        successful = successful or 0
        method_stats.append({
            "method": method,
            "total_attempts": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0
        })
    
    return {
        "delivery_methods": method_stats
    }

