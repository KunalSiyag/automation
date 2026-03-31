"""
Task Manager Web Application
A full-featured task management web app with Flask backend
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
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
    tasks = load_tasks()
    new_task = {
        'id': max([t['id'] for t in tasks], default=0) + 1,
        'title': data.get('title'),
        'description': data.get('description', ''),
        'priority': data.get('priority', 'medium'),
        'status': 'todo',
        'created_at': datetime.now().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task.update(request.json)
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = [t for t in load_tasks() if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify({'message': 'Deleted'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
