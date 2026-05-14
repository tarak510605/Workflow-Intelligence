"""Response models for Workflow Intelligence Platform API."""

from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str
    timestamp: datetime
    version: str


class WorkspaceGenerationResponse(BaseModel):
    """Response model for workspace generation."""
    
    success: bool
    message: str
    workspace_id: str
    statistics: Dict[str, Any]
    generated_at: datetime


class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoints."""
    
    metric_name: str
    data: Dict[str, Any]
    summary: str
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "metric_name": "employee_workload",
                "data": {
                    "employees": ["Alice", "Bob"],
                    "workload": [42, 38],
                    "capacity": 40
                },
                "summary": "Average workload across team is 40 tasks per employee",
                "timestamp": "2024-05-14T10:00:00Z"
            }
        }


class InsightResponse(BaseModel):
    """Response model for AI insights."""
    
    insight_id: str
    title: str
    insights: List[str]
    recommendations: List[str]
    risk_score: float
    generated_at: datetime
    focus_area: str
    
    class Config:
        schema_extra = {
            "example": {
                "insight_id": "insight_001",
                "title": "Operational Health Summary",
                "insights": [
                    "Backend Team workload increased 18% this sprint.",
                    "Project Alpha has elevated deadline risk due to task dependency delays."
                ],
                "recommendations": [
                    "Consider redistributing tasks from Backend Team.",
                    "Expedite critical path tasks on Project Alpha."
                ],
                "risk_score": 0.65,
                "generated_at": "2024-05-14T10:00:00Z",
                "focus_area": "overall"
            }
        }
