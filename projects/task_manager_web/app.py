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
    if not data or not data.get('title') or not isinstance(data.get('title'), str) or not data.get('title').strip():
        return jsonify({'error': 'Title is required and must be a non-empty string'}), 400

    tasks = load_tasks()
    new_task = {
        'id': max([t['id'] for t in tasks], default=0) + 1,
        'title': data.get('title').strip(),
        'description': data.get('description', '').strip(),
        'priority': data.get('priority', 'medium').lower(),
        'status': 'todo',
        'created_at': datetime.now().isoformat()
    }

    # Basic validation for priority
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

            # Update fields if present
            if 'title' in update_data and (not isinstance(update_data['title'], str) or not update_data['title'].strip()):
                return jsonify({'error': 'Title cannot be empty'}), 400
            if 'title' in update_data: task['title'] = update_data['title'].strip()

            if 'description' in update_data: task['description'] = update_data['description'].strip()

            if 'priority' in update_data:
                valid_priorities = ['low', 'medium', 'high']
                priority_val = update_data['priority'].lower()
                if priority_val in valid_priorities:
                    task['priority'] = priority_val
                else:
                    return jsonify({'error': f'Invalid priority. Must be one of {valid_priorities}'}), 400

            if 'status' in update_data:
                valid_statuses = ['todo', 'in-progress', 'done']
                status_val = update_data['status'].lower()
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
