"""
Admin Client Management Endpoints
CRUD operations for clients
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Client, AdminUser
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.api.dependencies import get_current_admin
from datetime import datetime
import uuid
import secrets

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    List all clients with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Optional status filter
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        List of clients
    """
    query = db.query(Client)
    
    if status_filter:
        query = query.filter(Client.status == status_filter)
    
    clients = query.offset(skip).limit(limit).all()

    return [ClientResponse.from_client(client) for client in clients]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get a specific client by ID
    
    Args:
        client_id: Client UUID
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        Client details
        
    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse.from_client(client)


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Create a new client
    
    Args:
        client_data: Client creation data
        db: Database session
        current_admin: Current authenticated admin
        
    Returns:
        Created client
    """
    # Generate password-protected link token and password
    link_token = secrets.token_urlsafe(32)
    client_password = secrets.token_urlsafe(12)  # Generate random password

    # Create new client
    new_client = Client(
        name=client_data.name,
        email=client_data.email,
        phone_number=client_data.phone_number,
        percentage=client_data.percentage,
        credits_balance=client_data.credits_balance,
        credit_cost_per_lead=client_data.credit_cost_per_lead or 1.0,
        webhook_url=client_data.webhook_url,
        google_sheet_id=client_data.google_sheet_id,
        whatsapp_details_richtext=client_data.whatsapp_details_richtext,
        accept_webhook=client_data.accept_webhook,
        accept_email=client_data.accept_email,
        accept_sms=client_data.accept_sms,
        accept_sheets=client_data.accept_sheets,
        priority_order=client_data.priority_order or 0,
        status="active",
        password_protected_link_token=link_token,
        client_password=client_password  # Store plain text password for now
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return ClientResponse.from_client(new_client)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: uuid.UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Update an existing client

    Args:
        client_id: Client UUID
        client_data: Client update data
        db: Database session
        current_admin: Current authenticated admin

    Returns:
        Updated client

    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Update fields if provided
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)

    return ClientResponse.from_client(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Delete a client

    Args:
        client_id: Client UUID
        db: Database session
        current_admin: Current authenticated admin

    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    db.delete(client)
    db.commit()

    return None


@router.post("/{client_id}/credits", response_model=ClientResponse)
def add_credits(
    client_id: uuid.UUID,
    credits: float = Query(..., gt=0, description="Number of credits to add"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Add credits to a client

    Args:
        client_id: Client UUID
        credits: Number of credits to add
        db: Database session
        current_admin: Current authenticated admin

    Returns:
        Updated client

    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    client.credits_balance += credits
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)

    return ClientResponse.from_client(client)

