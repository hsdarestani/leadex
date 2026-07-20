from fastapi import APIRouter
from app.api.landing import submit

router = APIRouter()
router.include_router(submit.router, tags=["Landing Page"])

__all__ = ["router"]
