from fastapi import APIRouter
from app.api.admin import auth, clients, leads, stats, analytics, webhooks, imports, notifications, advanced, performance, reports

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Admin Auth"])
router.include_router(clients.router, prefix="/clients", tags=["Admin Clients"])
router.include_router(leads.router, prefix="/leads", tags=["Admin Leads"])
router.include_router(stats.router, prefix="/stats", tags=["Admin Stats"])
router.include_router(analytics.router, prefix="/analytics", tags=["Admin Analytics"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Admin Webhooks"])
router.include_router(imports.router, prefix="/imports", tags=["Admin Imports"])
router.include_router(notifications.router, prefix="/notifications", tags=["Admin Notifications"])
router.include_router(advanced.router, prefix="/advanced", tags=["Admin Advanced Features"])
router.include_router(performance.router, prefix="/performance", tags=["Performance & Monitoring"])
router.include_router(reports.router, prefix="/reports", tags=["Reports & Export"])

__all__ = ["router"]
