import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Validate that the loaded data is a list to prevent TypeErrors in subsequent operations.
                if not isinstance(data, list):
                    logging.warning(f"Tasks file '{TASKS_FILE}' contains non-list data. Initializing with an empty list.")
                    return []
                return data
            except json.JSONDecodeError:
                # Handle cases where the file is empty or contains malformed JSON.
                logging.warning(f"Tasks file '{TASKS_FILE}' is empty or malformed JSON. Initializing with an empty list.")
                return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(load_tasks())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    
    # Validate title first as it's mandatory and must be a string
    if not data or not data.get('title') or not isinstance(data.get('title'), str) or not data.get('title').strip():
        return jsonify({'error': 'Title is required and must be a non-empty string'}), 400

    # Validate description type. If present and not a string, return error.
    description_val = data.get('description')
    if description_val is not None and not isinstance(description_val, str):
        return jsonify({'error': 'Description must be a string'}), 400
    # Use the description, strip it if it's a string, otherwise default to empty.
    description_to_use = description_val.strip() if isinstance(description_val, str) else ''

    # Validate priority type. If present and not a string, return error.
    priority_val = data.get('priority')
    if priority_val is not None and not isinstance(priority_val, str):
        return jsonify({'error': 'Priority must be a string'}), 400
    
    # Determine priority to use, lowercasing if it's a string, otherwise defaulting to 'medium'.
    priority_to_use = (priority_val.lower() if isinstance(priority_val, str) else 'medium')

    tasks = load_tasks()
    
    # More robust ID generation: filter for valid integer IDs before finding the maximum.
    # This prevents potential TypeErrors if the tasks.json file contains entries with
    # missing or non-integer 'id' fields due to external modification or corruption.
    current_ids = [t['id'] for t in tasks if isinstance(t.get('id'), int)]
    new_id = max(current_ids, default=0) + 1

    new_task = {
        'id': new_id,
        'title': data.get('title').strip(),
        'description': description_to_use,
        'priority': priority_to_use,
        'status': 'todo',
        'created_at': datetime.now().isoformat()
    }

    # Basic validation for priority against valid options. If invalid, default to 'medium'.
    # This maintains the original behavior of defaulting for invalid string values.
    valid_priorities = ['low', 'medium', 'high']
    if new_task['priority'] not in valid_priorities:
        new_task['priority'] = 'medium'

    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    task_found = False
    updated_task = None

    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            update_data = request.json
            if not update_data:
                return jsonify({'error': 'No update data provided'}), 400

            # Update title if present and valid
            if 'title' in update_data:
                title_val = update_data['title']
                if not isinstance(title_val, str) or not title_val.strip():
                    return jsonify({'error': 'Title cannot be empty and must be a string'}), 400
                task['title'] = title_val.strip()

            # Update description if present and valid
            if 'description' in update_data:
                description_val = update_data['description']
                if not isinstance(description_val, str):
                    return jsonify({'error': 'Description must be a string'}), 400
                task['description'] = description_val.strip()

            # Update priority if present and valid
            if 'priority' in update_data:
                priority_val_raw = update_data['priority']
                if not isinstance(priority_val_raw, str):
                    return jsonify({'error': 'Priority must be a string'}), 400
                
                priority_val = priority_val_raw.lower()
                valid_priorities = ['low', 'medium', 'high']
                if priority_val in valid_priorities:
                    task['priority'] = priority_val
                else:
                    return jsonify({'error': f'Invalid priority. Must be one of {valid_priorities}'}), 400

            # Update status if present and valid
            if 'status' in update_data:
                status_val_raw = update_data['status']
                if not isinstance(status_val_raw, str):
                    return jsonify({'error': 'Status must be a string'}), 400
                
                status_val = status_val_raw.lower()
                valid_statuses = ['todo', 'in-progress', 'done']
                if status_val in valid_statuses:
                    task['status'] = status_val
                else:
                    return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400

            tasks[i] = task
            save_tasks(tasks)
            updated_task = task
            task_found = True
            break

    if task_found:
        return jsonify(updated_task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    initial_task_count = len(load_tasks())
    tasks = [t for t in load_tasks() if t['id'] != task_id]
    if len(tasks) == initial_task_count:
        return jsonify({'error': 'Task not found'}), 404
    save_tasks(tasks)
    return jsonify({'message': 'Task deleted successfully'}), 200

if __name__ == '__main__':
    # Ensure tasks.json exists if running for the first time
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
    app.run(debug=True, port=5000)
