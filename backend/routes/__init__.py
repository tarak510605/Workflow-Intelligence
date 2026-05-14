"""Route initialization and configuration."""

from fastapi import APIRouter
from .workspace import router as workspace_router
from .analytics import router as analytics_router
from .insights import router as insights_router
from .export import router as export_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(workspace_router, prefix="/workspace", tags=["Workspace"])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
router.include_router(insights_router, prefix="/ai", tags=["AI Insights"])
router.include_router(export_router, prefix="/export", tags=["Data Export"])

__all__ = ["router"]
