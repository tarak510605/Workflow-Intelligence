"""AI Insights routes."""

from fastapi import APIRouter, HTTPException
from backend.models import InsightGenerationRequest, InsightResponse
from backend.analytics import AnalyticsService, InsightService
from backend.services import WorkspaceService

router = APIRouter()

workspace_service = WorkspaceService()


def get_insight_service():
    """Get insight service instance."""
    db_path = workspace_service.get_database_path()
    analytics = AnalyticsService(db_path)
    return InsightService(analytics)


@router.post("/summary", response_model=InsightResponse)
async def generate_operational_summary(request: InsightGenerationRequest):
    """Generate AI-powered operational insights and recommendations.
    
    This endpoint analyzes workflow data and generates business-friendly
    insights including risk assessments and actionable recommendations.
    
    Args:
        request: InsightGenerationRequest with analysis parameters
            - focus_area: 'overall', 'employees', 'projects', 'risks', 'productivity'
            - include_recommendations: Include actionable recommendations
            - depth_level: 'quick', 'standard', or 'detailed'
    
    Returns:
        InsightResponse with insights, recommendations, and risk scores
    """
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area=request.focus_area,
            include_recommendations=request.include_recommendations,
            depth_level=request.depth_level
        )
        
        return InsightResponse(**insights)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/insights/overall")
async def get_overall_insights(depth: str = "standard"):
    """Get overall operational health insights."""
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area="overall",
            include_recommendations=True,
            depth_level=depth
        )
        return InsightResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/insights/employees")
async def get_employee_insights(depth: str = "standard"):
    """Get employee-focused insights."""
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area="employees",
            include_recommendations=True,
            depth_level=depth
        )
        return InsightResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/insights/projects")
async def get_project_insights(depth: str = "standard"):
    """Get project-focused insights."""
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area="projects",
            include_recommendations=True,
            depth_level=depth
        )
        return InsightResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/insights/risks")
async def get_risk_insights(depth: str = "standard"):
    """Get risk-focused insights."""
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area="risks",
            include_recommendations=True,
            depth_level=depth
        )
        return InsightResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/insights/productivity")
async def get_productivity_insights(depth: str = "standard"):
    """Get productivity-focused insights."""
    try:
        insight_service = get_insight_service()
        insights = insight_service.generate_insights(
            focus_area="productivity",
            include_recommendations=True,
            depth_level=depth
        )
        return InsightResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")
