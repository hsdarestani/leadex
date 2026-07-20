"""
Client Portal API
Endpoints for clients to view their leads and statistics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import io
from app.core.database import get_db
from app.models import Client, Asset, Delivery
from app.api.client.dependencies import get_current_client
from app.utils.time import to_tehran_iso
router = APIRouter()


class ClientStats(BaseModel):
    """Client statistics"""
    total_leads: int
    today_leads: int
    week_leads: int
    month_leads: int
    successful_deliveries: int
    failed_deliveries: int
    delivery_success_rate: float
    credits_balance: float
    credits_used: float


class LeadResponse(BaseModel):
    """Lead response for client"""
    id: str
    mobile: str
    name: Optional[str]
    email: Optional[str]
    status: str
    created_at: datetime
    created_at_tehran: Optional[str] = None
    updated_at_tehran: Optional[str] = None
    delivered_at: Optional[datetime]
    delivery_status: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/stats", response_model=ClientStats)
def get_client_stats(
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get client statistics
    
    Returns statistics about the client's leads and deliveries
    """
    # Total leads assigned to this client
    total_leads = db.query(func.count(Delivery.id)).filter(
        Delivery.client_id == client.id
    ).scalar() or 0
    
    # Today's leads
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_leads = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.client_id == client.id,
            Delivery.timestamp >= today_start
        )
    ).scalar() or 0

    # Week's leads
    week_start = datetime.utcnow() - timedelta(days=7)
    week_leads = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.client_id == client.id,
            Delivery.timestamp >= week_start
        )
    ).scalar() or 0

    # Month's leads
    month_start = datetime.utcnow() - timedelta(days=30)
    month_leads = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.client_id == client.id,
            Delivery.timestamp >= month_start
        )
    ).scalar() or 0
    
    # Successful deliveries
    successful_deliveries = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.client_id == client.id,
            Delivery.success == True
        )
    ).scalar() or 0
    
    # Failed deliveries
    failed_deliveries = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.client_id == client.id,
            Delivery.success == False
        )
    ).scalar() or 0
    
    # Delivery success rate
    delivery_success_rate = (successful_deliveries / total_leads * 100) if total_leads > 0 else 0
    
    # Credits used (total deliveries * credit cost per lead)
    credits_used = total_leads * client.credit_cost_per_lead
    
    return ClientStats(
        total_leads=total_leads,
        today_leads=today_leads,
        week_leads=week_leads,
        month_leads=month_leads,
        successful_deliveries=successful_deliveries,
        failed_deliveries=failed_deliveries,
        delivery_success_rate=round(delivery_success_rate, 2),
        credits_balance=client.credits_balance,
        credits_used=credits_used
    )


@router.get("/leads", response_model=List[LeadResponse])
def get_client_leads(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Get client's leads
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status_filter**: Filter by delivery status (success, failed)
    
    Returns list of leads assigned to this client
    """
    # Query deliveries for this client
    query = db.query(Delivery, Asset).join(
        Asset, Delivery.asset_id == Asset.id
    ).filter(
        Delivery.client_id == client.id
    )
    
    # Apply status filter
    if status_filter:
        if status_filter.lower() == "success":
            query = query.filter(Delivery.success == True)
        elif status_filter.lower() == "failed":
            query = query.filter(Delivery.success == False)
    
    # Order by timestamp descending
    query = query.order_by(Delivery.timestamp.desc())

    # Pagination
    deliveries = query.offset(skip).limit(limit).all()

    # Build response
    leads = []
    for delivery, asset in deliveries:
        leads.append(LeadResponse(
            id=str(asset.id),
            mobile=asset.mobile,
            name=asset.name,
            email=asset.email,
            status=asset.status,
            created_at=asset.created_at,
            created_at_tehran=to_tehran_iso(lead.created_at),
            updated_at_tehran=to_tehran_iso(lead.updated_at),
            delivered_at=delivery.timestamp,
            delivery_status="success" if delivery.success else "failed"
        ))
    
    return leads


@router.get("/leads/export")
def export_client_leads(
    status_filter: Optional[str] = None,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Export client's leads to CSV

    - **status_filter**: Filter by delivery status (success, failed)

    Returns CSV file with all leads assigned to this client
    """
    # Query deliveries for this client
    query = db.query(Delivery, Asset).join(
        Asset, Delivery.asset_id == Asset.id
    ).filter(
        Delivery.client_id == client.id
    )

    # Apply status filter
    if status_filter:
        if status_filter.lower() == "success":
            query = query.filter(Delivery.success == True)
        elif status_filter.lower() == "failed":
            query = query.filter(Delivery.success == False)

    # Order by timestamp descending
    query = query.order_by(Delivery.timestamp.desc())

    # Get all deliveries
    deliveries = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Lead ID',
        'Mobile',
        'Name',
        'Email',
        'Status',
        'Created At',
        'Delivered At',
        'Delivery Status',
        'Delivery Method',
        'IP Address',
        'Referrer'
    ])

    # Write data
    for delivery, asset in deliveries:
        writer.writerow([
            str(asset.id),
            asset.mobile,
            asset.name or '',
            asset.email or '',
            asset.status,
            asset.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            delivery.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Success' if delivery.success else 'Failed',
            delivery.delivery_method,
            asset.ip or '',
            asset.referrer or ''
        ])

    # Get CSV content
    csv_content = output.getvalue()
    output.close()

    # Return CSV file
    filename = f"leads_{client.name.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

