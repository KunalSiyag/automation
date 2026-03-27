"""
Task models for todo application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


@dataclass
class Task:
    """Task model."""
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: int = 1  # 1=low, 2=medium, 3=high
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    task_id: Optional[int] = None
    
    def mark_done(self):
        """Mark task as completed."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
    
    def update(self, title: str = None, description: str = None, priority: int = None):
        """Update task properties."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority


class TaskManager:
    """Manages a collection of tasks."""
    
    def __init__(self):
        """Initialize task manager."""
        self.tasks: List[Task] = []
        self.next_id = 1
    
    def add_task(self, title: str, description: str = "", priority: int = 1) -> Task:
        """Add a new task."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            task_id=self.next_id
        )
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return self.tasks
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks filtered by status."""
        return [t for t in self.tasks if t.status == status]
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID."""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                del self.tasks[i]
                return True
        return False
    
    def get_incomplete_tasks(self) -> List[Task]:
        """Get all incomplete tasks."""
        return [t for t in self.tasks if t.status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS)]
    
    def get_task_count(self) -> dict:
        """Get count of tasks by status."""
        counts = {
            "total": len(self.tasks),
            "todo": len([t for t in self.tasks if t.status == TaskStatus.TODO]),
            "in_progress": len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS]),
            "done": len([t for t in self.tasks if t.status == TaskStatus.DONE]),
        }
        return counts
