"""
Client Authentication API
Password-protected link token authentication for clients
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from app.core.database import get_db
from app.models import Client
from app.utils.auth import verify_password, create_access_token
from app.core.config import settings

router = APIRouter()


class ClientLogin(BaseModel):
    """Client login request"""
    token: str
    password: str = None  # Optional password if client has set one


class ClientLoginResponse(BaseModel):
    """Client login response"""
    access_token: str
    token_type: str
    client_id: str
    client_name: str
    credits_balance: float


@router.post("/login", response_model=ClientLoginResponse)
def client_login(credentials: ClientLogin, db: Session = Depends(get_db)):
    """
    Client login using password-protected link token
    
    - **token**: Password-protected link token (required)
    - **password**: Client password (optional, if client has set one)
    
    Returns JWT access token for client portal access
    """
    # Find client by token
    client = db.query(Client).filter(
        Client.password_protected_link_token == credentials.token
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Check if client is active
    if client.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is inactive"
        )
    
    # If client has a password, verify it
    if client.client_password:
        if not credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password required"
            )

        # Compare plain text passwords (passwords are stored as plain text for now)
        if credentials.password != client.client_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(client.id), "type": "client", "token": credentials.token},
        expires_delta=access_token_expires
    )
    
    return ClientLoginResponse(
        access_token=access_token,
        token_type="bearer",
        client_id=str(client.id),
        client_name=client.name,
        credits_balance=client.credits_balance
    )


@router.post("/logout")
def client_logout():
    """
    Client logout
    
    Note: Since we're using JWT tokens, logout is handled client-side
    by removing the token from storage
    """
    return {"message": "Logged out successfully"}

