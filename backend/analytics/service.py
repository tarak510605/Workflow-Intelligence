"""Analytics service for computing workflow metrics and insights."""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import json


class AnalyticsService:
    """Service for computing analytics on workflow data."""
    
    def __init__(self, db_path: str):
        """Initialize analytics service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ============================================================================
    # EMPLOYEE ANALYTICS
    # ============================================================================
    
    def get_employee_workload(self) -> Dict[str, Any]:
        """Get employee workload distribution and metrics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            u.id,
            u.name,
            COUNT(t.id) as total_tasks,
            SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN t.due_date < datetime('now') AND t.status != 'completed' THEN 1 ELSE 0 END) as overdue_tasks
        FROM users u
        LEFT JOIN tasks t ON u.id = t.assignee_id
        GROUP BY u.id
        ORDER BY total_tasks DESC
        LIMIT 100
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        employees = []
        total_tasks = 0
        completed_tasks = 0
        overdue_tasks = 0
        
        for row in rows:
            emp = {
                "id": row[0],
                "name": row[1],
                "total_tasks": row[2] or 0,
                "completed_tasks": row[3] or 0,
                "overdue_tasks": row[4] or 0,
                "completion_rate": (row[3] or 0) / (row[2] or 1)
            }
            employees.append(emp)
            total_tasks += emp["total_tasks"]
            completed_tasks += emp["completed_tasks"]
            overdue_tasks += emp["overdue_tasks"]
        
        return {
            "employees": employees,
            "summary": {
                "total_employees": len(employees),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "average_workload": total_tasks / len(employees) if employees else 0,
                "average_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            }
        }
    
    def get_employee_productivity(self) -> Dict[str, Any]:
        """Get productivity metrics by employee."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Calculate task completion rates
        query = """
        SELECT 
            u.id,
            u.name,
            COUNT(t.id) as assigned_tasks,
            SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
            SUM(CASE WHEN t.priority = 'high' THEN 1 ELSE 0 END) as high_priority_tasks,
            SUM(CASE WHEN t.priority = 'high' AND t.status = 'completed' THEN 1 ELSE 0 END) as high_priority_completed,
            CAST(julianday('now') - MAX(julianday(t.completed_at)) AS INTEGER) as days_since_last_completion
        FROM users u
        LEFT JOIN tasks t ON u.id = t.assignee_id
        GROUP BY u.id
        ORDER BY completed_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            completed = row[3] or 0
            assigned = row[2] or 1
            completion_rate = completed / assigned
            
            productivity_score = min(1.0, (
                completion_rate * 0.5 +
                (row[5] or 0) / max((row[4] or 1), 1) * 0.3 +
                (1.0 if (row[6] or 999) < 30 else 0.5) * 0.2
            ))
            
            metrics.append({
                "employee_id": row[0],
                "name": row[1],
                "assigned_tasks": assigned,
                "completed_tasks": completed,
                "completion_rate": completion_rate,
                "high_priority_tasks": row[4] or 0,
                "high_priority_completed": row[5] or 0,
                "productivity_score": productivity_score,
                "status": "high_performer" if productivity_score > 0.8 else (
                    "at_risk" if productivity_score < 0.4 else "on_track"
                )
            })
        
        return {
            "metrics": metrics,
            "summary": {
                "high_performers": len([m for m in metrics if m["status"] == "high_performer"]),
                "at_risk": len([m for m in metrics if m["status"] == "at_risk"]),
                "on_track": len([m for m in metrics if m["status"] == "on_track"]),
                "average_productivity": sum(m["productivity_score"] for m in metrics) / len(metrics) if metrics else 0
            }
        }
    
    # ============================================================================
    # PROJECT ANALYTICS
    # ============================================================================
    
    def get_project_health(self) -> Dict[str, Any]:
        """Get project health scores and status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            p.id,
            p.name,
            COUNT(t.id) as total_tasks,
            SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN t.due_date < datetime('now') AND t.status != 'completed' THEN 1 ELSE 0 END) as overdue_tasks,
            SUM(CASE WHEN t.assignee_id IS NULL THEN 1 ELSE 0 END) as unassigned_tasks,
            p.created_at
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.id
        ORDER BY p.name
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        projects = []
        for row in rows:
            total = row[2] or 1
            completed = row[3] or 0
            overdue = row[4] or 0
            unassigned = row[5] or 0
            
            completion_rate = completed / total
            at_risk_rate = overdue / total if total > 0 else 0
            
            # Health score calculation
            health_score = (
                completion_rate * 0.4 +
                (1.0 - at_risk_rate) * 0.4 +
                (1.0 - (unassigned / total)) * 0.2
            )
            
            status = "healthy" if health_score > 0.75 else (
                "at_risk" if health_score < 0.5 else "caution"
            )
            
            projects.append({
                "project_id": row[0],
                "name": row[1],
                "total_tasks": total,
                "completed_tasks": completed,
                "completion_rate": completion_rate,
                "overdue_tasks": overdue,
                "unassigned_tasks": unassigned,
                "health_score": health_score,
                "status": status,
                "created_at": row[6]
            })
        
        return {
            "projects": projects,
            "summary": {
                "total_projects": len(projects),
                "healthy_projects": len([p for p in projects if p["status"] == "healthy"]),
                "at_risk_projects": len([p for p in projects if p["status"] == "at_risk"]),
                "average_health": sum(p["health_score"] for p in projects) / len(projects) if projects else 0
            }
        }
    
    # ============================================================================
    # TASK ANALYTICS
    # ============================================================================
    
    def get_task_distribution(self) -> Dict[str, Any]:
        """Get task distribution across statuses and priorities."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Status distribution
        status_query = """
        SELECT status, COUNT(*) as count
        FROM tasks
        GROUP BY status
        """
        
        # Priority distribution
        priority_query = """
        SELECT priority, COUNT(*) as count
        FROM tasks
        GROUP BY priority
        """
        
        cursor.execute(status_query)
        status_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute(priority_query)
        priority_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Overdue tasks
        overdue_query = """
        SELECT COUNT(*) FROM tasks
        WHERE due_date < datetime('now') AND status != 'completed'
        """
        cursor.execute(overdue_query)
        overdue_count = cursor.fetchone()[0]
        
        # Unassigned tasks
        unassigned_query = """
        SELECT COUNT(*) FROM tasks WHERE assignee_id IS NULL
        """
        cursor.execute(unassigned_query)
        unassigned_count = cursor.fetchone()[0]
        
        # Average aging
        aging_query = """
        SELECT AVG(CAST(julianday('now') - julianday(created_at) AS INTEGER))
        FROM tasks WHERE status != 'completed'
        """
        cursor.execute(aging_query)
        avg_aging = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "status_distribution": status_dist,
            "priority_distribution": priority_dist,
            "overdue_tasks": overdue_count,
            "unassigned_tasks": unassigned_count,
            "average_task_age_days": round(avg_aging, 1),
            "summary": {
                "total_tasks": sum(status_dist.values()),
                "open_tasks": status_dist.get("open", 0) + status_dist.get("in_progress", 0),
                "completion_rate": status_dist.get("completed", 0) / sum(status_dist.values()) if status_dist else 0
            }
        }
    
    # ============================================================================
    # RISK ANALYTICS
    # ============================================================================
    
    def get_risk_analysis(self) -> Dict[str, Any]:
        """Analyze operational risks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Overloaded employees
        overload_query = """
        SELECT 
            u.id, u.name, COUNT(t.id) as task_count
        FROM users u
        LEFT JOIN tasks t ON u.id = t.assignee_id AND t.status != 'completed'
        GROUP BY u.id
        HAVING COUNT(t.id) > 20
        ORDER BY task_count DESC
        """
        cursor.execute(overload_query)
        overloaded = [{"employee": row[1], "pending_tasks": row[2]} for row in cursor.fetchall()]
        
        # Projects with high deadline risk
        deadline_risk_query = """
        SELECT 
            p.id, p.name,
            COUNT(CASE WHEN t.due_date < datetime('now') AND t.status != 'completed' THEN 1 END) as overdue_count,
            COUNT(CASE WHEN t.due_date BETWEEN datetime('now') AND datetime('now', '+7 days') AND t.status != 'completed' THEN 1 END) as at_risk_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.id
        HAVING (overdue_count + at_risk_count) > 0
        ORDER BY (overdue_count + at_risk_count) DESC
        """
        cursor.execute(deadline_risk_query)
        risky_projects = [
            {"project": row[1], "overdue_tasks": row[2], "at_risk_tasks": row[3]}
            for row in cursor.fetchall()
        ]
        
        # Stalled tasks (no updates)
        stalled_query = """
        SELECT 
            t.id, t.title, 
            CAST(julianday('now') - julianday(t.updated_at) AS INTEGER) as days_stalled
        FROM tasks t
        WHERE t.status != 'completed' AND t.updated_at < datetime('now', '-7 days')
        ORDER BY days_stalled DESC
        LIMIT 20
        """
        cursor.execute(stalled_query)
        stalled_tasks = [
            {"task": row[1], "days_stalled": row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Overall risk score
        risk_score = min(1.0, (
            len(overloaded) * 0.1 +
            len(risky_projects) * 0.15 +
            len(stalled_tasks) * 0.05
        ))
        
        return {
            "risk_score": risk_score,
            "risk_level": "critical" if risk_score > 0.7 else (
                "high" if risk_score > 0.5 else (
                    "medium" if risk_score > 0.3 else "low"
                )
            ),
            "overloaded_employees": overloaded,
            "projects_with_deadline_risk": risky_projects,
            "stalled_tasks": stalled_tasks,
            "summary": {
                "total_risks_identified": len(overloaded) + len(risky_projects) + len(stalled_tasks),
                "immediate_attention_required": len(overloaded) + len(risky_projects)
            }
        }
    
    # ============================================================================
    # DATABASE STATISTICS
    # ============================================================================
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        tables = [
            "users", "projects", "tasks", "teams", "organizations",
            "subtasks", "comments", "tags"
        ]
        
        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0
        
        conn.close()
        
        return {
            "entity_counts": stats,
            "total_entities": sum(stats.values()),
            "generated_at": datetime.utcnow().isoformat()
        }
