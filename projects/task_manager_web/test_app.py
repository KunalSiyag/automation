import pytest
from app import app, load_tasks, save_tasks # Import necessary functions for setup/teardown
import os
import json
import tempfile

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Create a temporary file for testing to ensure tests are isolated
    db_fd, db_path = tempfile.mkstemp(suffix=".json")
    # Configure the app to use the temporary file for tasks
    app.config['TASKS_FILE'] = db_path

    # Use Flask's test client and ensure the temporary file is cleaned up
    with app.test_client() as client:
        # Initialize the temporary tasks file with an empty list for consistent test starts
        save_tasks([]) 
        yield client
    
    # Teardown: Close the file descriptor and delete the temporary file
    os.close(db_fd)
    os.unlink(db_path)

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_get_tasks_empty(client):
    # Assumes the fixture has cleared the tasks file, which it does
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert response.json == []

def test_create_task_success(client):
    task_data = {
        'title': 'New Task',
        'description': 'This is a test task.',
        'priority': 'high'
    }
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 201
    assert response.json['title'] == 'New Task'
    assert response.json['description'] == 'This is a test task.'
    assert response.json['priority'] == 'high'
    assert response.json['status'] == 'todo'
    assert 'id' in response.json
    assert 'created_at' in response.json

    # Verify task is actually saved by loading directly from the (temp) file
    tasks = load_tasks()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'New Task'

def test_create_task_missing_title(client):
    response = client.post('/api/tasks', json={'description': 'No title here'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Title is required' in response.json['error']

def test_create_task_empty_title(client):
    response = client.post('/api/tasks', json={'title': '', 'description': 'Empty title'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Title is required' in response.json['error']

def test_create_task_invalid_description_type(client):
    response = client.post('/api/tasks', json={'title': 'Valid Title', 'description': 123})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Description must be a string' in response.json['error']

def test_create_task_invalid_priority_type(client):
    response = client.post('/api/tasks', json={'title': 'Valid Title', 'priority': 123})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Priority must be a string' in response.json['error']

def test_create_task_invalid_priority_value_defaults_to_medium(client):
    response = client.post('/api/tasks', json={'title': 'Invalid Priority Task', 'priority': 'super-high'})
    assert response.status_code == 201
    assert response.json['priority'] == 'medium' # Should default to medium

def test_get_multiple_tasks(client):
    # Create a few tasks
    client.post('/api/tasks', json={'title': 'Task One'})
    client.post('/api/tasks', json={'title': 'Task Two'})
    client.post('/api/tasks', json={'title': 'Task Three'})

    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]['title'] == 'Task One'
    assert response.json[1]['title'] == 'Task Two'

def test_update_task_success(client):
    # Create a task first
    create_response = client.post(
        '/api/tasks', 
        json={'title': 'Original Task', 'description': 'Original desc', 'priority': 'low', 'status': 'todo'}
    )
    assert create_response.status_code == 201
    task_id = create_response.json['id']

    # Update the task
    update_data = {
        'title': 'Updated Task',
        'priority': 'high',
        'status': 'in-progress',
        'description': 'Updated description'
    }
    update_response = client.put(f'/api/tasks/{task_id}', json=update_data)
    assert update_response.status_code == 200
    assert update_response.json['id'] == task_id
    assert update_response.json['title'] == 'Updated Task'
    assert update_response.json['description'] == 'Updated description'
    assert update_response.json['priority'] == 'high'
    assert update_response.json['status'] == 'in-progress'
    assert 'updated_at' in update_response.json

    # Verify state in file
    tasks = load_tasks()
    assert len(tasks) == 1
    assert tasks[0]['id'] == task_id
    assert tasks[0]['title'] == 'Updated Task'
    assert tasks[0]['priority'] == 'high'
    assert tasks[0]['status'] == 'in-progress'
    assert tasks[0]['description'] == 'Updated description'

def test_update_task_not_found(client):
    response = client.put('/api/tasks/999', json={'title': 'Non-existent'})
    assert response.status_code == 404
    assert 'error' in response.json
    assert response.json['error'] == 'Task not found'

def test_update_task_no_data_provided(client):
    create_response = client.post('/api/tasks', json={'title': 'Test Task'})
    task_id = create_response.json['id']
    response = client.put(f'/api/tasks/{task_id}', json={})
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'] == 'No update data provided'

def test_update_task_invalid_title(client):
    create_response = client.post('/api/tasks', json={'title': 'Valid'}) 
    task_id = create_response.json['id']

    response = client.put(f'/api/tasks/{task_id}', json={'title': ''})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Title cannot be empty' in response.json['error']

    response = client.put(f'/api/tasks/{task_id}', json={'title': 123})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Title cannot be empty and must be a string' in response.json['error']

def test_update_task_invalid_priority(client):
    create_response = client.post('/api/tasks', json={'title': 'Valid'})
    task_id = create_response.json['id']

    response = client.put(f'/api/tasks/{task_id}', json={'priority': 'ultra-high'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid priority' in response.json['error']

    response = client.put(f'/api/tasks/{task_id}', json={'priority': 123})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Priority must be a string' in response.json['error']

def test_update_task_invalid_status(client):
    create_response = client.post('/api/tasks', json={'title': 'Valid'})
    task_id = create_response.json['id']

    response = client.put(f'/api/tasks/{task_id}', json={'status': 'completed'}) # 'completed' is an invalid status
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid status' in response.json['error']

    response = client.put(f'/api/tasks/{task_id}', json={'status': 123})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Status must be a string' in response.json['error']

def test_delete_task_success(client):
    create_response = client.post('/api/tasks', json={'title': 'Task to delete'})
    task_id = create_response.json['id']

    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Task deleted successfully'

    # Verify task is actually deleted
    tasks = load_tasks()
    assert len(tasks) == 0

def test_delete_task_not_found(client):
    response = client.delete('/api/tasks/999')
    assert response.status_code == 404
    assert 'error' in response.json
    assert response.json['error'] == 'Task not found'
