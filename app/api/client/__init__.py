"""
Client Portal API Router
"""
from fastapi import APIRouter
from app.api.client import auth, portal

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Client Auth"])
router.include_router(portal.router, prefix="/portal", tags=["Client Portal"])

__all__ = ["router"]
