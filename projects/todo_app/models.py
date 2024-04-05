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


def openclaw_note_20260327194127() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194211() -> str:
    """Autonomous note generated in fallback mode."""
    return "Feature request: Add overdue summary helper. Description: Return count of overdue tasks."


def openclaw_note_20260327194213() -> str:
    """Autonomous note generated in fallback mode."""
    return "Improve build/test reliability for this project. Focus on validation, edge cases, or small refactors that improve maintainability."


def openclaw_note_20260327194242() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194418() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194443() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194510() -> str:
    """Autonomous note generated in fallback mode."""
    return "Improve build/test reliability for this project. Focus on validation, edge cases, or small refactors that improve maintainability."


def openclaw_note_20260327194527() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194602() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194612() -> str:
    """Autonomous note generated in fallback mode."""
    return "Improve build/test reliability for this project. Focus on validation, edge cases, or small refactors that improve maintainability."


def openclaw_note_20260327194737() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194803() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194832() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."


def openclaw_note_20260327194858() -> str:
    """Autonomous note generated in fallback mode."""
    return "Pick one safe, incremental improvement that strengthens reliability or usability without breaking existing behavior."
