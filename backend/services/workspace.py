"""Workspace service for data generation and management."""

import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any
import uuid
import random
from faker import Faker

fake = Faker()


class WorkspaceService:
    """Service for generating and managing workflow data."""
    
    def __init__(self, db_path: str = "output/workflow_data.sqlite"):
        """Initialize workspace service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_database_path(self) -> str:
        """Get database path."""
        return self.db_path
    
    def generate_workspace(
        self,
        num_employees: int = 50,
        num_projects: int = 20,
        num_teams: int = 5,
        tasks_per_project: int = 15,
        workload_intensity: float = 0.7,
        completion_rate: float = 0.7,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a complete workspace with seed data.
        
        Args:
            num_employees: Number of employees to generate
            num_projects: Number of projects to generate
            num_teams: Number of teams to generate
            tasks_per_project: Average tasks per project
            workload_intensity: Workload intensity (0.1-1.0)
            completion_rate: Task completion rate (0.0-1.0)
        
        Returns:
            Tuple of (workspace_id, statistics)
        """
        # Remove old database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        workspace_id = str(uuid.uuid4())
        
        # Create connection and initialize schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        self._initialize_schema(cursor)
        
        # Generate data
        stats = {}
        
        # 1. Organizations
        org_ids = self._generate_organizations(cursor)
        stats["organizations"] = len(org_ids)
        
        # 2. Teams
        team_ids = self._generate_teams(cursor, org_ids, num_teams)
        stats["teams"] = len(team_ids)
        
        # 3. Employees/Users
        user_ids = self._generate_users(cursor, org_ids, team_ids, num_employees)
        stats["employees"] = len(user_ids)
        
        # 4. Projects
        project_ids = self._generate_projects(cursor, team_ids, num_projects)
        stats["projects"] = len(project_ids)
        
        # 5. Tasks with realistic distribution
        task_ids = self._generate_tasks(
            cursor, project_ids, user_ids,
            tasks_per_project, workload_intensity, completion_rate
        )
        stats["tasks"] = len(task_ids)
        
        # 6. Subtasks
        subtask_count = self._generate_subtasks(cursor, task_ids)
        stats["subtasks"] = subtask_count
        
        # 7. Comments
        comment_count = self._generate_comments(cursor, task_ids)
        stats["comments"] = comment_count
        
        # 8. Tags
        tag_count = self._generate_tags(cursor, task_ids)
        stats["tags"] = tag_count
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return workspace_id, stats
    
    def _initialize_schema(self, cursor):
        """Initialize database schema."""
        schema = """
        -- Organizations
        CREATE TABLE organizations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Teams
        CREATE TABLE teams (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        );
        
        -- Users/Employees
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            team_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );
        
        -- Projects
        CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );
        
        -- Tasks
        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            assignee_id TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'open',
            due_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assignee_id) REFERENCES users(id)
        );
        
        -- Subtasks
        CREATE TABLE subtasks (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
        
        -- Comments
        CREATE TABLE comments (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Tags
        CREATE TABLE tags (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Task-Tag associations
        CREATE TABLE task_tags (
            task_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            PRIMARY KEY (task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );
        """
        
        for statement in schema.split(';'):
            if statement.strip():
                cursor.execute(statement)
    
    def _generate_organizations(self, cursor) -> list:
        """Generate organizations."""
        org_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO organizations (id, name)
            VALUES (?, ?)
        """, (org_id, "Acme Corp"))
        return [org_id]
    
    def _generate_teams(self, cursor, org_ids: list, num_teams: int) -> list:
        """Generate teams."""
        teams = [
            "Engineering",
            "Product",
            "Design",
            "Marketing",
            "Operations",
            "Sales",
            "HR",
            "Finance"
        ]
        
        team_ids = []
        for i in range(min(num_teams, len(teams))):
            team_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO teams (id, organization_id, name)
                VALUES (?, ?, ?)
            """, (team_id, org_ids[0], teams[i]))
            team_ids.append(team_id)
        
        return team_ids
    
    def _generate_users(self, cursor, org_ids: list, team_ids: list, num_employees: int) -> list:
        """Generate users/employees."""
        user_ids = []
        
        for i in range(num_employees):
            user_id = str(uuid.uuid4())
            name = fake.name()
            email = f"{name.lower().replace(' ', '.')}@acmecorp.com"
            team_id = random.choice(team_ids)
            
            cursor.execute("""
                INSERT INTO users (id, organization_id, name, email, team_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, org_ids[0], name, email, team_id))
            
            user_ids.append(user_id)
        
        return user_ids
    
    def _generate_projects(self, cursor, team_ids: list, num_projects: int) -> list:
        """Generate projects."""
        project_ids = []
        
        for i in range(num_projects):
            project_id = str(uuid.uuid4())
            team_id = random.choice(team_ids)
            name = f"{fake.catch_phrase().title()}"
            
            cursor.execute("""
                INSERT INTO projects (id, team_id, name, description)
                VALUES (?, ?, ?, ?)
            """, (project_id, team_id, name, f"Project for {name}"))
            
            project_ids.append(project_id)
        
        return project_ids
    
    def _generate_tasks(
        self,
        cursor,
        project_ids: list,
        user_ids: list,
        tasks_per_project: int,
        workload_intensity: float,
        completion_rate: float
    ) -> list:
        """Generate tasks with realistic distribution."""
        task_ids = []
        priorities = ["low", "medium", "high"]
        statuses = ["open", "in_progress", "completed"]
        
        for project_id in project_ids:
            num_tasks = int(tasks_per_project * (0.5 + workload_intensity))
            
            for i in range(num_tasks):
                task_id = str(uuid.uuid4())
                priority = random.choice(priorities)
                
                # Assign tasks
                if random.random() > 0.15:
                    assignee_id = random.choice(user_ids)
                else:
                    assignee_id = None
                
                # Determine status
                if random.random() < completion_rate:
                    status = "completed"
                else:
                    status = random.choice(["open", "in_progress"])
                
                # Due dates
                if random.random() > 0.3:
                    days_ahead = random.randint(-10, 30)
                    due_date = datetime.utcnow() + timedelta(days=days_ahead)
                else:
                    due_date = None
                
                created_days_ago = random.randint(1, 60)
                created_at = datetime.utcnow() - timedelta(days=created_days_ago)
                
                completed_at = None
                if status == "completed":
                    completed_at = created_at + timedelta(days=random.randint(1, 20))
                
                cursor.execute("""
                    INSERT INTO tasks
                    (id, project_id, title, assignee_id, priority, status, due_date, created_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, project_id,
                    f"Task: {fake.sentence()}",
                    assignee_id, priority, status, due_date,
                    created_at, completed_at
                ))
                
                task_ids.append(task_id)
        
        return task_ids
    
    def _generate_subtasks(self, cursor, task_ids: list) -> int:
        """Generate subtasks for tasks."""
        count = 0
        
        for task_id in random.sample(task_ids, int(len(task_ids) * 0.3)):
            num_subtasks = random.randint(1, 3)
            
            for i in range(num_subtasks):
                subtask_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO subtasks (id, task_id, title, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    subtask_id, task_id,
                    f"Subtask: {fake.sentence()}",
                    random.choice(["open", "completed"])
                ))
                count += 1
        
        return count
    
    def _generate_comments(self, cursor, task_ids: list) -> int:
        """Generate comments on tasks."""
        count = 0
        user_ids = self._get_user_ids(cursor)
        
        for task_id in random.sample(task_ids, int(len(task_ids) * 0.4)):
            num_comments = random.randint(1, 4)
            
            for i in range(num_comments):
                comment_id = str(uuid.uuid4())
                user_id = random.choice(user_ids)
                
                cursor.execute("""
                    INSERT INTO comments (id, task_id, user_id, content)
                    VALUES (?, ?, ?, ?)
                """, (
                    comment_id, task_id, user_id,
                    fake.paragraph()
                ))
                count += 1
        
        return count
    
    def _generate_tags(self, cursor, task_ids: list) -> int:
        """Generate tags and tag associations."""
        tag_names = ["urgent", "bug", "feature", "documentation", "refactor", "research"]
        tag_ids = []
        
        for tag_name in tag_names:
            tag_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO tags (id, name) VALUES (?, ?)
            """, (tag_id, tag_name))
            tag_ids.append(tag_id)
        
        count = 0
        for task_id in random.sample(task_ids, int(len(task_ids) * 0.5)):
            num_tags = random.randint(1, 2)
            
            for tag_id in random.sample(tag_ids, num_tags):
                try:
                    cursor.execute("""
                        INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)
                    """, (task_id, tag_id))
                    count += 1
                except:
                    pass
        
        return count + len(tag_ids)
    
    def _get_user_ids(self, cursor) -> list:
        """Get all user IDs from database."""
        cursor.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current database statistics."""
        if not os.path.exists(self.db_path):
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        tables = ["organizations", "teams", "users", "projects", "tasks", "subtasks", "comments", "tags"]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        conn.close()
        
        return stats
