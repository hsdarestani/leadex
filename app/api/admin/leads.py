"""
Admin Lead Management Endpoints
View and manage leads
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Asset, Client, Delivery, AdminUser
from app.api.dependencies import get_current_admin
from datetime import datetime
import uuid
from app.utils.time import to_tehran_iso
router = APIRouter()


@router.get("/")
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100000),  # Increased for CSV exports
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    List all leads with pagination and filters
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Optional status filter
        client_id: Optional client ID filter
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        List of leads with delivery information
    """
    query = db.query(Asset)
    
    if status_filter:
        query = query.filter(Asset.status == status_filter)
    
    leads = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for lead in leads:
        # Get delivery information
        deliveries = db.query(Delivery).filter(Delivery.asset_id == lead.id).all()
        
        # Get assigned client if any
        assigned_client = None
        if deliveries:
            latest_delivery = deliveries[0]
            client = db.query(Client).filter(Client.id == latest_delivery.client_id).first()
            if client:
                assigned_client = {
                    "id": str(client.id),
                    "name": client.name
                }
        
        # Filter by client_id if provided
        if client_id and (not assigned_client or assigned_client["id"] != str(client_id)):
            continue
        
        result.append({
            "id": str(lead.id),
            "mobile": lead.mobile,
            "name": lead.name,
            "email": lead.email,
            "status": lead.status,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            "created_at_tehran": to_tehran_iso(lead.created_at) if lead.created_at else None,
            "updated_at_tehran": to_tehran_iso(lead.updated_at) if lead.updated_at else None,
            "client": assigned_client,
            "delivery_count": len(deliveries),
            "ip": lead.ip,
            "user_agent": lead.user_agent,
            "referrer": lead.referrer,
            "geo": lead.geo,
            "utm": lead.utm
        })

    return {"leads": result, "total": len(result)}


@router.get("/{lead_id}")
def get_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get detailed information about a specific lead
    
    Args:
        lead_id: Lead UUID
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        Lead details with delivery history
        
    Raises:
        HTTPException: If lead not found
    """
    lead = db.query(Asset).filter(Asset.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Get delivery history
    deliveries = db.query(Delivery).filter(Delivery.asset_id == lead.id).all()
    
    delivery_history = []
    for delivery in deliveries:
        client = db.query(Client).filter(Client.id == delivery.client_id).first()
        delivery_history.append({
            "id": str(delivery.id),
            "client": {
                "id": str(client.id),
                "name": client.name
            } if client else None,
            "delivery_method": delivery.delivery_method,
            "success": delivery.success,
            "attempt_number": delivery.attempt_number,
            "response_status": delivery.response_status,
            "created_at_tehran": to_tehran_iso(delivery.timestamp) if delivery.timestamp else None,
            "created_at": delivery.timestamp.isoformat() if delivery.timestamp else None
        })
    
    return {
        "id": str(lead.id),
        "mobile": lead.mobile,
        "name": lead.name,
        "email": lead.email,
        "status": lead.status,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        "created_at_tehran": to_tehran_iso(lead.created_at) if lead.created_at else None,
        "updated_at_tehran": to_tehran_iso(lead.updated_at) if lead.updated_at else None,
        "ip": lead.ip,
        "user_agent": lead.user_agent,
        "referrer": lead.referrer,
        "geo": lead.geo,
        "utm": lead.utm,
        "delivery_history": delivery_history
    }


from pydantic import BaseModel

class BulkDeleteRequest(BaseModel):
    lead_ids: List[str]

class BulkResendRequest(BaseModel):
    lead_ids: List[str]
    client_id: Optional[str] = None

class BulkAssignRequest(BaseModel):
    lead_ids: List[str]
    client_id: str


@router.post("/bulk/delete")
def bulk_delete_leads(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Bulk delete leads
    """
    deleted_count = 0
    errors = []
    
    for lead_id_str in request.lead_ids:
        try:
            lead_id = uuid.UUID(lead_id_str)
            lead = db.query(Asset).filter(Asset.id == lead_id).first()
            if lead:
                db.delete(lead)
                deleted_count += 1
            else:
                errors.append(f"Lead {lead_id_str} not found")
        except Exception as e:
            errors.append(f"Error deleting {lead_id_str}: {str(e)}")
    
    db.commit()
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "errors": errors
    }


@router.post("/bulk/resend")
def bulk_resend_leads(
    request: BulkResendRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Bulk resend leads to clients
    """
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    resent_count = 0
    errors = []

    for lead_id_str in request.lead_ids:
        try:
            lead_id = uuid.UUID(lead_id_str)
            lead = db.query(Asset).filter(Asset.id == lead_id).first()
            if lead:
                # Get client to resend to
                if request.client_id:
                    client_id = uuid.UUID(request.client_id)
                else:
                    # Get last client this was sent to
                    delivery = db.query(Delivery).filter(
                        Delivery.asset_id == lead_id
                    ).order_by(Delivery.timestamp.desc()).first()
                    if delivery:
                        client_id = delivery.client_id
                    else:
                        errors.append(f"Lead {lead_id_str} has no delivery history")
                        continue

                # Get client object
                client = db.query(Client).filter(Client.id == client_id).first()
                if not client:
                    errors.append(f"Client {client_id} not found")
                    continue

                # Resend
                result = DeliveryOrchestrator.deliver_lead(lead, client, db)
                if result.get('overall_success'):
                    resent_count += 1
                else:
                    error_details = [d.get('error') for d in result.get('deliveries', []) if 'error' in d]
                    error_msg = ', '.join(error_details) if error_details else 'No delivery methods succeeded'
                    errors.append(f"Failed to resend {lead_id_str}: {error_msg}")
            else:
                errors.append(f"Lead {lead_id_str} not found")
        except Exception as e:
            errors.append(f"Error resending {lead_id_str}: {str(e)}")

    return {
        "success": True,
        "resent_count": resent_count,
        "errors": errors
    }


@router.post("/bulk/assign")
def bulk_assign_leads(
    request: BulkAssignRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Bulk assign leads to a client
    """
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    assigned_count = 0
    errors = []

    # Verify client exists
    try:
        client_id = uuid.UUID(request.client_id)
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {
                "success": False,
                "error": f"Client {request.client_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Invalid client ID: {str(e)}"
        }

    for lead_id_str in request.lead_ids:
        try:
            lead_id = uuid.UUID(lead_id_str)
            lead = db.query(Asset).filter(Asset.id == lead_id).first()
            if lead:
                result = DeliveryOrchestrator.deliver_lead(lead, client, db)
                if result.get('overall_success'):
                    assigned_count += 1
                else:
                    error_details = [d.get('error') for d in result.get('deliveries', []) if 'error' in d]
                    error_msg = ', '.join(error_details) if error_details else 'No delivery methods succeeded'
                    errors.append(f"Failed to assign {lead_id_str}: {error_msg}")
            else:
                errors.append(f"Lead {lead_id_str} not found")
        except Exception as e:
            errors.append(f"Error assigning {lead_id_str}: {str(e)}")

    return {
        "success": True,
        "assigned_count": assigned_count,
        "errors": errors
    }


@router.post("/{lead_id}/resend")
def resend_single_lead(
    lead_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Resend a single lead
    """
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    lead = db.query(Asset).filter(Asset.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Determine client
    if client_id:
        target_client_id = client_id
    else:
        # Get last client
        delivery = db.query(Delivery).filter(
            Delivery.asset_id == lead_id
        ).order_by(Delivery.timestamp.desc()).first()
        if delivery:
            target_client_id = delivery.client_id
        else:
            raise HTTPException(status_code=400, detail="Lead has no delivery history and no client specified")

    # Get client object
    client = db.query(Client).filter(Client.id == target_client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Resend
    result = DeliveryOrchestrator.deliver_lead(lead, client, db)

    if result.get('overall_success'):
        return {
            "success": True,
            "message": "Lead resent successfully",
            "result": result
        }
    else:
        # Get error details from deliveries
        errors = [d.get('error') for d in result.get('deliveries', []) if 'error' in d]
        error_msg = ', '.join(errors) if errors else 'No delivery methods succeeded'
        raise HTTPException(status_code=500, detail=f"Failed to resend: {error_msg}")


@router.get("/stats/summary")
def get_lead_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get lead statistics summary
    """
    total_leads = db.query(Asset).count()
    
    # Count by status
    from sqlalchemy import func
    status_counts = db.query(
        Asset.status, func.count(Asset.id).label('count')
    ).group_by(Asset.status).all()
    
    status_breakdown = {status: count for status, count in status_counts}
    
    return {
        "total_leads": total_leads,
        "status_breakdown": status_breakdown
    }
