"""Insight generation service for AI-powered recommendations."""

import random
from datetime import datetime
from typing import Dict, List, Any
import uuid


class InsightService:
    """Service for generating AI-powered insights and recommendations."""
    
    def __init__(self, analytics_service):
        """Initialize insight service.
        
        Args:
            analytics_service: AnalyticsService instance for data access
        """
        self.analytics = analytics_service
    
    def generate_insights(
        self,
        focus_area: str = "overall",
        include_recommendations: bool = True,
        depth_level: str = "standard"
    ) -> Dict[str, Any]:
        """Generate insights based on workflow data.
        
        Args:
            focus_area: 'overall', 'employees', 'projects', 'risks', 'productivity'
            include_recommendations: Include actionable recommendations
            depth_level: 'quick', 'standard', or 'detailed'
        
        Returns:
            Dictionary containing insights and recommendations
        """
        
        if focus_area == "overall":
            return self._generate_overall_insights(include_recommendations, depth_level)
        elif focus_area == "employees":
            return self._generate_employee_insights(include_recommendations, depth_level)
        elif focus_area == "projects":
            return self._generate_project_insights(include_recommendations, depth_level)
        elif focus_area == "risks":
            return self._generate_risk_insights(include_recommendations, depth_level)
        elif focus_area == "productivity":
            return self._generate_productivity_insights(include_recommendations, depth_level)
        else:
            return self._generate_overall_insights(include_recommendations, depth_level)
    
    def _generate_overall_insights(
        self,
        include_recommendations: bool,
        depth_level: str
    ) -> Dict[str, Any]:
        """Generate overall operational insights."""
        
        emp_data = self.analytics.get_employee_workload()
        proj_data = self.analytics.get_project_health()
        risk_data = self.analytics.get_risk_analysis()
        task_data = self.analytics.get_task_distribution()
        
        insights = []
        recommendations = []
        
        # Workload insights
        avg_workload = emp_data["summary"]["average_workload"]
        insights.append(
            f"Team average workload: {avg_workload:.0f} tasks per employee."
        )
        
        if avg_workload > 35:
            insights.append(
                f"Current workload is {((avg_workload / 35) - 1) * 100:.0f}% above recommended capacity."
            )
            if include_recommendations:
                recommendations.append(
                    "Consider redistributing tasks or extending deadlines to balance workload."
                )
        
        # Project health insights
        healthy = proj_data["summary"]["healthy_projects"]
        at_risk = proj_data["summary"]["at_risk_projects"]
        
        if at_risk > 0:
            insights.append(
                f"{at_risk} project(s) showing signs of risk due to overdue or unassigned tasks."
            )
            if include_recommendations:
                recommendations.append(
                    "Review at-risk projects for resource constraints or dependency issues."
                )
        
        # Task completion insight
        completion_rate = task_data["summary"]["completion_rate"]
        insights.append(
            f"Task completion rate: {completion_rate * 100:.1f}% across all projects."
        )
        
        # Risk level
        risk_level = risk_data["risk_level"]
        insights.append(
            f"Overall operational risk level: {risk_level.upper()}."
        )
        
        if risk_data["risk_score"] > 0.5 and include_recommendations:
            recommendations.append(
                "Conduct a risk mitigation review with team leads."
            )
        
        risk_score = risk_data["risk_score"]
        
        return {
            "insight_id": str(uuid.uuid4()),
            "title": "Operational Health Summary",
            "focus_area": "overall",
            "insights": insights[:5 if depth_level == "quick" else 10],
            "recommendations": recommendations,
            "risk_score": risk_score,
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "depth_level": depth_level,
                "employee_count": emp_data["summary"]["total_employees"],
                "project_count": proj_data["summary"]["total_projects"],
                "total_tasks": task_data["summary"]["total_tasks"]
            }
        }
    
    def _generate_employee_insights(
        self,
        include_recommendations: bool,
        depth_level: str
    ) -> Dict[str, Any]:
        """Generate employee-focused insights."""
        
        emp_prod = self.analytics.get_employee_productivity()
        emp_workload = self.analytics.get_employee_workload()
        
        insights = []
        recommendations = []
        
        # High performers
        high_performers = emp_prod["summary"]["high_performers"]
        at_risk = emp_prod["summary"]["at_risk"]
        
        insights.append(
            f"Identified {high_performers} high-performing employees maintaining strong completion rates."
        )
        
        if at_risk > 0:
            insights.append(
                f"{at_risk} employee(s) showing performance concerns and may need support."
            )
            if include_recommendations:
                recommendations.append(
                    "Schedule 1:1s with at-risk employees to understand blockers and provide support."
                )
        
        # Workload distribution
        avg_workload = emp_workload["summary"]["average_workload"]
        max_workload = max((e["total_tasks"] for e in emp_workload["employees"]), default=0)
        min_workload = min((e["total_tasks"] for e in emp_workload["employees"]), default=0)
        
        if max_workload > 0 and min_workload > 0:
            imbalance = max_workload - min_workload
            insights.append(
                f"Workload imbalance detected: {imbalance} task difference between most and least loaded employees."
            )
            if include_recommendations:
                recommendations.append(
                    "Rebalance workload distribution to improve team efficiency."
                )
        
        return {
            "insight_id": str(uuid.uuid4()),
            "title": "Employee Performance & Productivity Analysis",
            "focus_area": "employees",
            "insights": insights,
            "recommendations": recommendations,
            "risk_score": at_risk / max(emp_prod["summary"]["high_performers"] + at_risk + emp_prod["summary"]["on_track"], 1),
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "high_performers": high_performers,
                "at_risk_employees": at_risk,
                "average_productivity": emp_prod["summary"]["average_productivity"]
            }
        }
    
    def _generate_project_insights(
        self,
        include_recommendations: bool,
        depth_level: str
    ) -> Dict[str, Any]:
        """Generate project-focused insights."""
        
        proj_data = self.analytics.get_project_health()
        
        insights = []
        recommendations = []
        
        at_risk = proj_data["summary"]["at_risk_projects"]
        healthy = proj_data["summary"]["healthy_projects"]
        total = proj_data["summary"]["total_projects"]
        
        insights.append(
            f"Project Portfolio: {healthy} healthy, {at_risk} at-risk out of {total} total projects."
        )
        
        if at_risk > 0:
            # Get specific at-risk projects
            at_risk_projs = [p for p in proj_data["projects"] if p["status"] == "at_risk"]
            for proj in at_risk_projs[:3]:
                insights.append(
                    f"'{proj['name']}' has {proj['overdue_tasks']} overdue tasks. "
                    f"Current completion: {proj['completion_rate']*100:.0f}%"
                )
            
            if include_recommendations:
                recommendations.append(
                    "Prioritize sprint planning on at-risk projects to get back on track."
                )
        
        avg_health = proj_data["summary"]["average_health"]
        insights.append(
            f"Average project health score: {avg_health*100:.0f}%."
        )
        
        return {
            "insight_id": str(uuid.uuid4()),
            "title": "Project Health & Timeline Analysis",
            "focus_area": "projects",
            "insights": insights[:5 if depth_level == "quick" else 10],
            "recommendations": recommendations,
            "risk_score": at_risk / total if total > 0 else 0,
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "healthy_projects": healthy,
                "at_risk_projects": at_risk,
                "average_health_score": avg_health
            }
        }
    
    def _generate_risk_insights(
        self,
        include_recommendations: bool,
        depth_level: str
    ) -> Dict[str, Any]:
        """Generate risk-focused insights."""
        
        risk_data = self.analytics.get_risk_analysis()
        
        insights = []
        recommendations = []
        
        insights.append(
            f"Risk Assessment: {risk_data['risk_level'].upper()} risk level detected."
        )
        
        if risk_data["overloaded_employees"]:
            insights.append(
                f"Found {len(risk_data['overloaded_employees'])} overloaded employee(s) "
                f"with excessive pending task counts."
            )
            if include_recommendations:
                recommendations.append(
                    "Redistribute tasks from overloaded employees to prevent burnout and maintain quality."
                )
        
        if risk_data["projects_with_deadline_risk"]:
            insights.append(
                f"{len(risk_data['projects_with_deadline_risk'])} project(s) have deadline risk "
                f"with overdue or near-deadline tasks."
            )
            if include_recommendations:
                recommendations.append(
                    "Conduct risk mitigation reviews for deadline-at-risk projects."
                )
        
        if risk_data["stalled_tasks"]:
            insights.append(
                f"Identified {len(risk_data['stalled_tasks'])} stalled task(s) with no recent updates."
            )
            if include_recommendations:
                recommendations.append(
                    "Investigate and unblock stalled tasks to prevent project delays."
                )
        
        return {
            "insight_id": str(uuid.uuid4()),
            "title": "Risk & Bottleneck Analysis",
            "focus_area": "risks",
            "insights": insights,
            "recommendations": recommendations,
            "risk_score": risk_data["risk_score"],
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "overloaded_employees": len(risk_data["overloaded_employees"]),
                "deadline_risk_projects": len(risk_data["projects_with_deadline_risk"]),
                "stalled_tasks": len(risk_data["stalled_tasks"]),
                "total_risks": risk_data["summary"]["total_risks_identified"]
            }
        }
    
    def _generate_productivity_insights(
        self,
        include_recommendations: bool,
        depth_level: str
    ) -> Dict[str, Any]:
        """Generate productivity-focused insights."""
        
        prod_data = self.analytics.get_employee_productivity()
        task_data = self.analytics.get_task_distribution()
        
        insights = []
        recommendations = []
        
        avg_prod = prod_data["summary"]["average_productivity"]
        insights.append(
            f"Average team productivity score: {avg_prod*100:.0f}% of optimal capacity."
        )
        
        completion_rate = task_data["summary"]["completion_rate"]
        insights.append(
            f"Task completion rate: {completion_rate*100:.1f}%. "
            f"{task_data['summary']['total_tasks'] - sum(v for k, v in task_data['status_distribution'].items() if k != 'completed')} tasks remaining."
        )
        
        if task_data["overdue_tasks"] > 0:
            insights.append(
                f"⚠️ {task_data['overdue_tasks']} overdue task(s) requiring immediate attention."
            )
            if include_recommendations:
                recommendations.append(
                    "Prioritize and resolve overdue tasks immediately to restore schedule."
                )
        
        if task_data["unassigned_tasks"] > 0:
            insights.append(
                f"{task_data['unassigned_tasks']} unassigned task(s) may be blocking progress."
            )
            if include_recommendations:
                recommendations.append(
                    "Assign pending tasks to available team members to increase throughput."
                )
        
        avg_age = task_data["average_task_age_days"]
        insights.append(
            f"Average open task age: {avg_age:.0f} days (should be < 30)."
        )
        
        return {
            "insight_id": str(uuid.uuid4()),
            "title": "Productivity & Throughput Analysis",
            "focus_area": "productivity",
            "insights": insights[:5 if depth_level == "quick" else 10],
            "recommendations": recommendations,
            "risk_score": 1.0 - avg_prod,
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "average_productivity": avg_prod,
                "completion_rate": completion_rate,
                "overdue_tasks": task_data["overdue_tasks"],
                "unassigned_tasks": task_data["unassigned_tasks"]
            }
        }
