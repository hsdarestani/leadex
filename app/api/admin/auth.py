"""
Admin Authentication Endpoints
Login and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import AdminUser
from app.schemas.admin import AdminLogin, AdminLoginResponse
from app.utils.auth import verify_password, create_access_token
from app.api.dependencies import get_current_admin
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(
    credentials: AdminLogin,
    db: Session = Depends(get_db)
):
    """
    Admin login endpoint
    
    Authenticates admin user and returns JWT access token
    
    Args:
        credentials: Admin login credentials (email, password)
        db: Database session
        
    Returns:
        AdminLoginResponse with access token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find admin user by email
    admin = db.query(AdminUser).filter(AdminUser.email == credentials.email).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email, "role": admin.role},
        expires_delta=access_token_expires
    )
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        email=admin.email,
        role=admin.role
    )


@router.post("/logout")
def admin_logout():
    """
    Admin logout endpoint
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage
    
    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}


@router.get("/me")
def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get current admin user information

    Args:
        current_admin: Current authenticated admin user

    Returns:
        Admin user information
    """
    return {
        "id": str(current_admin.id),
        "email": current_admin.email,
        "role": current_admin.role,
        "created_at": current_admin.created_at.isoformat() if current_admin.created_at else None
    }

