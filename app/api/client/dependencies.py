"""
Client Portal Dependencies
Authentication and authorization dependencies for client portal
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Client
from app.utils.auth import decode_access_token

# HTTP Bearer token security
security = HTTPBearer()


def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Client:
    """
    Get the current authenticated client
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Client object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Check token type
    token_type = payload.get("type")
    if token_type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type"
        )
    
    # Get client ID from token
    client_id: str = payload.get("sub")
    if client_id is None:
        raise credentials_exception
    
    # Get client from database
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise credentials_exception
    
    # Check if client is active
    if client.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is inactive"
        )
    
    return client

