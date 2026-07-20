from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.monitoring import performance_middleware
from app.core.rate_limiter import rate_limit_middleware
from app.api.landing import router as landing_router
from app.api.admin import router as admin_router
from app.api.public.submit import router as public_router

app = FastAPI(
    title="Leadex API",
    description="Lead Distribution System - Phase 12 Performance Optimized",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
app.middleware("http")(performance_middleware)

# Rate limit middleware
app.middleware("http")(rate_limit_middleware)

# Include routers FIRST (before static files)
app.include_router(landing_router, prefix="/api/landing")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(public_router, prefix="/api/public", tags=["public"])

# Import and include client router
from app.api.client import router as client_router
app.include_router(client_router, prefix="/api/client")

@app.get("/")
async def root():
    return {
        "message": "Leadex API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Serve static HTML files (must be after all API routes to avoid conflicts)
import os
from fastapi.responses import FileResponse

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static HTML files from public folder (fallback after all API routes)"""
    if not file_path or file_path == "":
        file_path = "index.html"

    full_path = os.path.join(static_dir, file_path)

    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)

    # Return 404 if file not found
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
