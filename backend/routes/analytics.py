"""Analytics routes for workflow metrics."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.analytics import AnalyticsService
from backend.services import WorkspaceService

router = APIRouter()

workspace_service = WorkspaceService()


def get_analytics():
    """Get analytics service instance."""
    db_path = workspace_service.get_database_path()
    return AnalyticsService(db_path)


@router.get("/employees")
async def get_employee_analytics():
    """Get employee workload and assignment analytics.
    
    Returns:
        - Total employee count
        - Individual workload distribution
        - Completion rates
        - Overdue task counts
    """
    try:
        analytics = get_analytics()
        data = analytics.get_employee_workload()
        
        return {
            "metric_name": "employee_workload",
            "data": data,
            "summary": f"Total employees: {data['summary']['total_employees']}, "
                      f"Average workload: {data['summary']['average_workload']:.1f} tasks",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving employee analytics: {str(e)}")


@router.get("/projects")
async def get_project_analytics():
    """Get project health and status analytics.
    
    Returns:
        - Project health scores
        - Completion rates
        - Overdue task counts
        - Overall project status
    """
    try:
        analytics = get_analytics()
        data = analytics.get_project_health()
        
        return {
            "metric_name": "project_health",
            "data": data,
            "summary": f"Total projects: {data['summary']['total_projects']}, "
                      f"Healthy: {data['summary']['healthy_projects']}, "
                      f"At risk: {data['summary']['at_risk_projects']}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving project analytics: {str(e)}")


@router.get("/tasks")
async def get_task_analytics():
    """Get task distribution and status analytics.
    
    Returns:
        - Status distribution (open, in_progress, completed, blocked)
        - Priority distribution
        - Overdue and unassigned task counts
        - Average task age
    """
    try:
        analytics = get_analytics()
        data = analytics.get_task_distribution()
        
        return {
            "metric_name": "task_distribution",
            "data": data,
            "summary": f"Total tasks: {data['summary']['total_tasks']}, "
                      f"Completed: {data['summary']['completion_rate']*100:.1f}%, "
                      f"Overdue: {data['overdue_tasks']}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task analytics: {str(e)}")


@router.get("/productivity")
async def get_productivity_analytics():
    """Get employee productivity metrics.
    
    Returns:
        - Productivity scores per employee
        - High performers
        - At-risk employees
        - Performance trends
    """
    try:
        analytics = get_analytics()
        data = analytics.get_employee_productivity()
        
        return {
            "metric_name": "employee_productivity",
            "data": data,
            "summary": f"High performers: {data['summary']['high_performers']}, "
                      f"At risk: {data['summary']['at_risk']}, "
                      f"Average productivity: {data['summary']['average_productivity']*100:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving productivity analytics: {str(e)}")


@router.get("/risks")
async def get_risk_analytics():
    """Get operational risk analysis.
    
    Returns:
        - Overall risk score
        - Overloaded employees
        - Projects with deadline risk
        - Stalled tasks
        - Bottleneck detection
    """
    try:
        analytics = get_analytics()
        data = analytics.get_risk_analysis()
        
        return {
            "metric_name": "risk_analysis",
            "data": data,
            "summary": f"Risk level: {data['risk_level'].upper()}, "
                      f"Risk score: {data['risk_score']:.2f}, "
                      f"Risks identified: {data['summary']['total_risks_identified']}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving risk analytics: {str(e)}")


@router.get("/statistics")
async def get_database_statistics():
    """Get overall database statistics.
    
    Returns:
        - Entity counts (users, projects, tasks, etc.)
        - Database size information
        - Generated timestamp
    """
    try:
        analytics = get_analytics()
        data = analytics.get_database_statistics()
        
        return {
            "metric_name": "database_statistics",
            "data": data,
            "summary": f"Total entities: {data['total_entities']}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
