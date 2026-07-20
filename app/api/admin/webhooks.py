"""
Admin Webhooks API
Endpoints for webhook testing, logs, and management
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.models import AdminUser, Client, WebhookLog
from app.api.dependencies import get_current_admin
from app.services.webhook_service import WebhookService
import uuid

router = APIRouter()


class WebhookTestRequest(BaseModel):
    """Request to test a webhook"""
    client_id: str
    webhook_url: str
    test_payload: Optional[Dict[str, Any]] = None
    method: str = "POST"


class WebhookTestResponse(BaseModel):
    """Response from webhook test"""
    success: bool
    log_id: str
    status_code: Optional[int]
    response_time_ms: float
    response_body: Optional[str]
    error_message: Optional[str]


class WebhookLogResponse(BaseModel):
    """Webhook log response"""
    id: str
    client_id: str
    client_name: str
    webhook_url: str
    method: str
    request_payload: Optional[Dict[str, Any]]
    response_status_code: Optional[int]
    response_body: Optional[str]
    response_time_ms: Optional[float]
    success: bool
    error_message: Optional[str]
    attempt_number: int
    is_retry: bool
    is_test: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookStatsResponse(BaseModel):
    """Webhook statistics"""
    total_webhooks: int
    successful_webhooks: int
    failed_webhooks: int
    success_rate: float
    average_response_time_ms: float
    total_test_webhooks: int
    total_production_webhooks: int


@router.post("/test", response_model=WebhookTestResponse)
def test_webhook(
    request: WebhookTestRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Test a webhook endpoint
    
    Sends a test request to the specified webhook URL and logs the result
    """
    try:
        client_uuid = uuid.UUID(request.client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id format"
        )
    
    result = WebhookService.test_webhook(
        db=db,
        client_id=client_uuid,
        webhook_url=request.webhook_url,
        test_payload=request.test_payload,
        method=request.method
    )
    
    if not result.get("success") and result.get("error") == "Client not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return WebhookTestResponse(**result)


@router.get("/logs", response_model=List[WebhookLogResponse])
def get_webhook_logs(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    is_test: Optional[bool] = Query(None, description="Filter by test mode"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get webhook logs with filtering
    
    Returns a list of webhook logs with optional filters
    """
    client_uuid = None
    if client_id:
        try:
            client_uuid = uuid.UUID(client_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id format"
            )
    
    logs = WebhookService.get_webhook_logs(
        db=db,
        client_id=client_uuid,
        is_test=is_test,
        success=success,
        limit=limit,
        offset=offset
    )
    
    # Format response
    result = []
    for log in logs:
        result.append(WebhookLogResponse(
            id=str(log.id),
            client_id=str(log.client_id),
            client_name=log.client.name,
            webhook_url=log.webhook_url,
            method=log.method,
            request_payload=log.request_payload,
            response_status_code=log.response_status_code,
            response_body=log.response_body,
            response_time_ms=log.response_time_ms,
            success=log.success,
            error_message=log.error_message,
            attempt_number=log.attempt_number,
            is_retry=log.is_retry,
            is_test=log.is_test,
            created_at=log.created_at
        ))
    
    return result


@router.get("/logs/{log_id}", response_model=WebhookLogResponse)
def get_webhook_log(
    log_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific webhook log by ID
    
    Returns detailed information about a webhook log
    """
    try:
        log_uuid = uuid.UUID(log_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid log_id format"
        )
    
    log = db.query(WebhookLog).filter(WebhookLog.id == log_uuid).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook log not found"
        )
    
    return WebhookLogResponse(
        id=str(log.id),
        client_id=str(log.client_id),
        client_name=log.client.name,
        webhook_url=log.webhook_url,
        method=log.method,
        request_payload=log.request_payload,
        response_status_code=log.response_status_code,
        response_body=log.response_body,
        response_time_ms=log.response_time_ms,
        success=log.success,
        error_message=log.error_message,
        attempt_number=log.attempt_number,
        is_retry=log.is_retry,
        is_test=log.is_test,
        created_at=log.created_at
    )


@router.get("/stats", response_model=WebhookStatsResponse)
def get_webhook_stats(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get webhook statistics

    Returns aggregated statistics about webhook calls
    """
    from sqlalchemy import func

    query = db.query(WebhookLog)

    if client_id:
        try:
            client_uuid = uuid.UUID(client_id)
            query = query.filter(WebhookLog.client_id == client_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id format"
            )

    # Get counts
    total_webhooks = query.count()
    successful_webhooks = query.filter(WebhookLog.success == True).count()
    failed_webhooks = query.filter(WebhookLog.success == False).count()
    total_test_webhooks = query.filter(WebhookLog.is_test == True).count()
    total_production_webhooks = query.filter(WebhookLog.is_test == False).count()

    # Calculate success rate
    success_rate = (successful_webhooks / total_webhooks * 100) if total_webhooks > 0 else 0.0

    # Calculate average response time
    avg_response_time = db.query(func.avg(WebhookLog.response_time_ms)).filter(
        WebhookLog.response_time_ms.isnot(None)
    )

    if client_id:
        avg_response_time = avg_response_time.filter(WebhookLog.client_id == client_uuid)

    avg_response_time = avg_response_time.scalar() or 0.0

    return WebhookStatsResponse(
        total_webhooks=total_webhooks,
        successful_webhooks=successful_webhooks,
        failed_webhooks=failed_webhooks,
        success_rate=round(success_rate, 2),
        average_response_time_ms=round(avg_response_time, 2),
        total_test_webhooks=total_test_webhooks,
        total_production_webhooks=total_production_webhooks
    )

