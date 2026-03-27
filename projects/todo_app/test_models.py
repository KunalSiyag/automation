"""
Tests for todo application models.
"""

import pytest
from models import Task, TaskStatus, TaskManager


def test_task_creation():
    """Test task creation."""
    task = Task(title="Test Task", description="A test task")
    assert task.title == "Test Task"
    assert task.description == "A test task"
    assert task.status == TaskStatus.TODO
    assert task.priority == 1


def test_task_mark_done():
    """Test marking task as done."""
    task = Task(title="Test Task")
    task.mark_done()
    assert task.status == TaskStatus.DONE
    assert task.completed_at is not None


def test_task_mark_in_progress():
    """Test marking task as in progress."""
    task = Task(title="Test Task")
    task.mark_in_progress()
    assert task.status == TaskStatus.IN_PROGRESS


def test_task_update():
    """Test updating task properties."""
    task = Task(title="Original", priority=1)
    task.update(title="Updated", priority=3)
    assert task.title == "Updated"
    assert task.priority == 3


def test_task_manager_add_task():
    """Test adding tasks to manager."""
    manager = TaskManager()
    task = manager.add_task("Test Task")
    assert task.task_id == 1
    assert len(manager.get_all_tasks()) == 1


def test_task_manager_get_task():
    """Test retrieving task from manager."""
    manager = TaskManager()
    task = manager.add_task("Test Task")
    retrieved = manager.get_task(task.task_id)
    assert retrieved is not None
    assert retrieved.title == "Test Task"


def test_task_manager_delete_task():
    """Test deleting task from manager."""
    manager = TaskManager()
    task = manager.add_task("Test Task")
    assert manager.delete_task(task.task_id)
    assert manager.get_task(task.task_id) is None


def test_task_manager_get_by_status():
    """Test filtering tasks by status."""
    manager = TaskManager()
    t1 = manager.add_task("Task 1")
    t2 = manager.add_task("Task 2")
    t2.mark_done()
    
    todo_tasks = manager.get_tasks_by_status(TaskStatus.TODO)
    assert len(todo_tasks) == 1
    assert todo_tasks[0].title == "Task 1"


def test_task_manager_incomplete_tasks():
    """Test getting incomplete tasks."""
    manager = TaskManager()
    t1 = manager.add_task("Task 1")
    t2 = manager.add_task("Task 2")
    t3 = manager.add_task("Task 3")
    
    t3.mark_done()
    incomplete = manager.get_incomplete_tasks()
    assert len(incomplete) == 2


def test_task_manager_count():
    """Test task count functionality."""
    manager = TaskManager()
    t1 = manager.add_task("Task 1")
    t2 = manager.add_task("Task 2")
    t3 = manager.add_task("Task 3")
    
    t2.mark_done()
    t3.mark_in_progress()
    
    counts = manager.get_task_count()
    assert counts["total"] == 3
    assert counts["todo"] == 1
    assert counts["in_progress"] == 1
    assert counts["done"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
