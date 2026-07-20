"""Admin lead-management endpoints."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.core.database import get_db
from app.models import AdminUser, Asset, Client, Delivery
from app.utils.time import to_tehran_iso

router = APIRouter()


# Historical rows may contain NULL or the old value "NEW". The admin frontend
# works with the canonical lower-case statuses below.
def normalize_lead_status(value: Optional[str]) -> str:
    normalized = (value or "pending").strip().lower()
    return "pending" if normalized in {"", "new"} else normalized


def apply_status_filter(query, status_filter: Optional[str]):
    if not status_filter:
        return query

    normalized = normalize_lead_status(status_filter)
    if normalized == "pending":
        return query.filter(
            or_(
                Asset.status.is_(None),
                func.trim(Asset.status) == "",
                func.lower(Asset.status).in_(["new", "pending"]),
            )
        )

    return query.filter(func.lower(Asset.status) == normalized)


def serialize_client(client: Optional[Client]):
    if not client:
        return None
    return {"id": str(client.id), "name": client.name}


def serialize_lead(lead: Asset, assigned_client=None, delivery_count: int = 0):
    return {
        "id": str(lead.id),
        "mobile": lead.mobile,
        "name": lead.name,
        "email": lead.email,
        "status": normalize_lead_status(lead.status),
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        "created_at_tehran": to_tehran_iso(lead.created_at) if lead.created_at else None,
        "updated_at_tehran": to_tehran_iso(lead.updated_at) if lead.updated_at else None,
        "client": assigned_client,
        "delivery_count": delivery_count,
        "ip": lead.ip,
        "user_agent": lead.user_agent,
        "referrer": lead.referrer,
        "geo": lead.geo,
        "utm": lead.utm,
    }


@router.get("/")
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100000),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """List leads with pagination, canonical statuses and delivery details."""
    query = apply_status_filter(db.query(Asset), status_filter)
    leads = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for lead in leads:
        deliveries = (
            db.query(Delivery)
            .filter(Delivery.asset_id == lead.id)
            .order_by(Delivery.timestamp.desc())
            .all()
        )

        assigned_client = None
        if deliveries:
            client = db.query(Client).filter(Client.id == deliveries[0].client_id).first()
            assigned_client = serialize_client(client)

        if client_id and (
            not assigned_client or assigned_client["id"] != str(client_id)
        ):
            continue

        result.append(
            serialize_lead(
                lead,
                assigned_client=assigned_client,
                delivery_count=len(deliveries),
            )
        )

    return {"leads": result, "total": len(result)}


@router.get("/stats/summary")
def get_lead_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Return statistics using the same canonical statuses as the list API."""
    total_leads = db.query(Asset).count()
    raw_counts = (
        db.query(Asset.status, func.count(Asset.id).label("count"))
        .group_by(Asset.status)
        .all()
    )

    status_breakdown = {
        "pending": 0,
        "assigned": 0,
        "delivered": 0,
        "failed": 0,
    }
    for raw_status, count in raw_counts:
        canonical_status = normalize_lead_status(raw_status)
        status_breakdown[canonical_status] = (
            status_breakdown.get(canonical_status, 0) + count
        )

    return {
        "total_leads": total_leads,
        "status_breakdown": status_breakdown,
    }


@router.get("/{lead_id}")
def get_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Get a lead with delivery history."""
    lead = db.query(Asset).filter(Asset.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    deliveries = (
        db.query(Delivery)
        .filter(Delivery.asset_id == lead.id)
        .order_by(Delivery.timestamp.desc())
        .all()
    )

    delivery_history = []
    for delivery in deliveries:
        client = db.query(Client).filter(Client.id == delivery.client_id).first()
        delivery_history.append(
            {
                "id": str(delivery.id),
                "client": serialize_client(client),
                "delivery_method": delivery.delivery_method,
                "success": delivery.success,
                "attempt_number": delivery.attempt_number,
                "response_status": delivery.response_status,
                "created_at_tehran": (
                    to_tehran_iso(delivery.timestamp)
                    if delivery.timestamp
                    else None
                ),
                "created_at": (
                    delivery.timestamp.isoformat()
                    if delivery.timestamp
                    else None
                ),
            }
        )

    result = serialize_lead(lead)
    result["delivery_history"] = delivery_history
    return result


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
    current_admin: AdminUser = Depends(get_current_admin),
):
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
        except Exception as exc:
            errors.append(f"Error deleting {lead_id_str}: {exc}")

    db.commit()
    return {
        "success": True,
        "deleted_count": deleted_count,
        "errors": errors,
    }


@router.post("/bulk/resend")
def bulk_resend_leads(
    request: BulkResendRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    resent_count = 0
    errors = []

    for lead_id_str in request.lead_ids:
        try:
            lead_id = uuid.UUID(lead_id_str)
            lead = db.query(Asset).filter(Asset.id == lead_id).first()
            if not lead:
                errors.append(f"Lead {lead_id_str} not found")
                continue

            if request.client_id:
                client_id = uuid.UUID(request.client_id)
            else:
                delivery = (
                    db.query(Delivery)
                    .filter(Delivery.asset_id == lead_id)
                    .order_by(Delivery.timestamp.desc())
                    .first()
                )
                if not delivery:
                    errors.append(f"Lead {lead_id_str} has no delivery history")
                    continue
                client_id = delivery.client_id

            client = db.query(Client).filter(Client.id == client_id).first()
            if not client:
                errors.append(f"Client {client_id} not found")
                continue

            result = DeliveryOrchestrator.deliver_lead(lead, client, db)
            if result.get("overall_success"):
                resent_count += 1
            else:
                details = [
                    item.get("error")
                    for item in result.get("deliveries", [])
                    if item.get("error")
                ]
                errors.append(
                    f"Failed to resend {lead_id_str}: "
                    + (", ".join(details) or "No delivery methods succeeded")
                )
        except Exception as exc:
            errors.append(f"Error resending {lead_id_str}: {exc}")

    return {
        "success": True,
        "resent_count": resent_count,
        "errors": errors,
    }


@router.post("/bulk/assign")
def bulk_assign_leads(
    request: BulkAssignRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    assigned_count = 0
    errors = []

    try:
        client_id = uuid.UUID(request.client_id)
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {
                "success": False,
                "error": f"Client {request.client_id} not found",
            }
    except Exception as exc:
        return {"success": False, "error": f"Invalid client ID: {exc}"}

    for lead_id_str in request.lead_ids:
        try:
            lead_id = uuid.UUID(lead_id_str)
            lead = db.query(Asset).filter(Asset.id == lead_id).first()
            if not lead:
                errors.append(f"Lead {lead_id_str} not found")
                continue

            result = DeliveryOrchestrator.deliver_lead(lead, client, db)
            if result.get("overall_success"):
                assigned_count += 1
            else:
                details = [
                    item.get("error")
                    for item in result.get("deliveries", [])
                    if item.get("error")
                ]
                errors.append(
                    f"Failed to assign {lead_id_str}: "
                    + (", ".join(details) or "No delivery methods succeeded")
                )
        except Exception as exc:
            errors.append(f"Error assigning {lead_id_str}: {exc}")

    return {
        "success": True,
        "assigned_count": assigned_count,
        "errors": errors,
    }


@router.post("/{lead_id}/resend")
def resend_single_lead(
    lead_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    from app.services.delivery_orchestrator import DeliveryOrchestrator

    lead = db.query(Asset).filter(Asset.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if client_id:
        target_client_id = client_id
    else:
        delivery = (
            db.query(Delivery)
            .filter(Delivery.asset_id == lead_id)
            .order_by(Delivery.timestamp.desc())
            .first()
        )
        if not delivery:
            raise HTTPException(
                status_code=400,
                detail="Lead has no delivery history and no client specified",
            )
        target_client_id = delivery.client_id

    client = db.query(Client).filter(Client.id == target_client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    result = DeliveryOrchestrator.deliver_lead(lead, client, db)
    if result.get("overall_success"):
        return {
            "success": True,
            "message": "Lead resent successfully",
            "result": result,
        }

    errors = [
        item.get("error")
        for item in result.get("deliveries", [])
        if item.get("error")
    ]
    error_message = ", ".join(errors) or "No delivery methods succeeded"
    raise HTTPException(
        status_code=500,
        detail=f"Failed to resend: {error_message}",
    )
