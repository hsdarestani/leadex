"""
API Dependencies
Authentication and authorization dependencies for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import AdminUser
from app.utils.auth import decode_access_token

# HTTP Bearer token security
security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Get the current authenticated admin user
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        AdminUser object
        
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
    
    # Get user email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Get user from database
    admin = db.query(AdminUser).filter(AdminUser.email == email).first()
    if admin is None:
        raise credentials_exception
    
    return admin


def get_current_super_admin(
    current_admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """
    Get the current authenticated super admin user
    
    Args:
        current_admin: Current admin user
        
    Returns:
        AdminUser object
        
    Raises:
        HTTPException: If user is not a super admin
    """
    if current_admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_admin


def get_optional_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[AdminUser]:
    """
    Get the current admin user if authenticated, None otherwise
    
    Args:
        credentials: HTTP Bearer credentials (optional)
        db: Database session
        
    Returns:
        AdminUser object or None
    """
    if credentials is None:
        return None
    
    try:
        return get_current_admin(credentials, db)
    except HTTPException:
        return None

