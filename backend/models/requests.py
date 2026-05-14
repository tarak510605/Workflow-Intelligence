"""Request models for Workflow Intelligence Platform API."""

from pydantic import BaseModel, Field
from typing import Optional


class WorkspaceGenerationRequest(BaseModel):
    """Request model for workspace generation."""
    
    num_employees: int = Field(
        default=50,
        ge=5,
        le=500,
        description="Number of employees to generate"
    )
    num_projects: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Number of projects to generate"
    )
    num_teams: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of teams to generate"
    )
    tasks_per_project: int = Field(
        default=15,
        ge=1,
        le=100,
        description="Average tasks per project"
    )
    workload_intensity: float = Field(
        default=0.7,
        ge=0.1,
        le=1.0,
        description="Workload intensity (0.1 = light, 1.0 = heavy)"
    )
    completion_rate: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Task completion rate"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "num_employees": 50,
                "num_projects": 20,
                "num_teams": 5,
                "tasks_per_project": 15,
                "workload_intensity": 0.7,
                "completion_rate": 0.7,
            }
        }


class InsightGenerationRequest(BaseModel):
    """Request model for AI insight generation."""
    
    focus_area: str = Field(
        default="overall",
        description="Focus area: overall, employees, projects, risks, productivity"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Include actionable recommendations"
    )
    depth_level: str = Field(
        default="standard",
        description="Insight depth: quick, standard, detailed"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "focus_area": "overall",
                "include_recommendations": True,
                "depth_level": "standard",
            }
        }
