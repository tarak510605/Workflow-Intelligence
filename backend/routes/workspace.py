"""Workspace generation routes."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.models import WorkspaceGenerationRequest, WorkspaceGenerationResponse
from backend.services import WorkspaceService
import os

router = APIRouter()

# Initialize workspace service
workspace_service = WorkspaceService()


@router.post("/generate", response_model=WorkspaceGenerationResponse)
async def generate_workspace(request: WorkspaceGenerationRequest):
    """Generate a new workspace with seed data.
    
    This endpoint generates a complete operational workflow dataset including:
    - Organizations and teams
    - Employees and user accounts
    - Projects and task structures
    - Tasks with assignments, priorities, and deadlines
    - Comments, subtasks, and dependencies
    
    Args:
        request: WorkspaceGenerationRequest with generation parameters
    
    Returns:
        WorkspaceGenerationResponse with generation status and statistics
    """
    try:
        workspace_id, stats = workspace_service.generate_workspace(
            num_employees=request.num_employees,
            num_projects=request.num_projects,
            num_teams=request.num_teams,
            tasks_per_project=request.tasks_per_project,
            workload_intensity=request.workload_intensity,
            completion_rate=request.completion_rate,
        )
        
        return WorkspaceGenerationResponse(
            success=True,
            message=f"Workspace generated successfully with ID: {workspace_id}",
            workspace_id=workspace_id,
            statistics=stats,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace generation failed: {str(e)}")


@router.get("/status")
async def get_workspace_status():
    """Get status of current workspace."""
    try:
        db_path = workspace_service.get_database_path()
        
        if not os.path.exists(db_path):
            return {
                "status": "no_workspace",
                "message": "No workspace has been generated yet",
                "db_path": db_path
            }
        
        stats = workspace_service.get_statistics()
        
        return {
            "status": "ready",
            "message": "Workspace is ready for analysis",
            "db_path": db_path,
            "statistics": stats,
            "last_generated": os.path.getmtime(db_path)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workspace status: {str(e)}")
