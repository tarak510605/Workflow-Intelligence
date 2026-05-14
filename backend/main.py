"""
Workflow Intelligence Platform - FastAPI Backend

A production-grade AI-powered workflow intelligence platform providing:
- Workspace generation and management
- Analytics on employees, projects, and tasks
- AI-powered operational insights
- Risk analysis and bottleneck detection
- Data export capabilities

The platform analyzes organizational workflow data to provide actionable insights
for improving productivity, managing risks, and optimizing resource allocation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from backend.routes import router
from backend.models import HealthCheckResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Workflow Intelligence Platform",
    description="AI-powered operational analytics and insights platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Workflow Intelligence Platform",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "workspace": "/workspace/generate",
            "analytics": "/analytics/",
            "insights": "/ai/summary",
            "export": "/export/"
        }
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Info"])
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(router)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Workflow Intelligence Platform starting up...")
    logger.info("API documentation available at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Workflow Intelligence Platform shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
