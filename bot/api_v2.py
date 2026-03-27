"""
OpenClaw Control API v2
Provides command endpoints to control agent behavior
"""
import os
import json
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)

WORKSPACE = os.getenv('WORKSPACE', '/workspace')
BOT_DIR = os.path.join(WORKSPACE, 'bot')
PROJECTS_DIR = os.path.join(WORKSPACE, 'projects')

# ============================================================================
# CONTROL ENDPOINTS - Command the agent
# ============================================================================

@app.route('/api/control/assign-task', methods=['POST'])
def assign_task():
    """Assign a task to a specific project"""
    try:
        data = request.get_json()
        project = data.get('project')
        task = data.get('task')
        priority = data.get('priority', 'medium')
        
        if not project or not task:
            return {'error': 'project and task required'}, 400
        
        # Read current TASKS.md
        tasks_file = os.path.join(WORKSPACE, 'TASKS.md')
        with open(tasks_file, 'r') as f:
            content = f.read()
        
        # Append new task
        if project not in content:
            content += f"\n## {project}\nStatus: ASSIGNED\nPriority: {priority}\nTasks:\n"
        
        # Write back
        with open(tasks_file, 'w') as f:
            f.write(content)
        
        return {
            'status': 'assigned',
            'project': project,
            'task': task,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/control/force-build', methods=['POST'])
def force_build():
    """Force agent to build/improve a specific project"""
    try:
        data = request.get_json()
        project = data.get('project')
        
        if not project:
            return {'error': 'project required'}, 400
        
        project_path = os.path.join(PROJECTS_DIR, project)
        if not os.path.exists(project_path):
            return {'error': f'Project {project} not found'}, 404
        
        # Create a signal file for the agent to pick up
        signal_file = os.path.join(WORKSPACE, f'.build_{project}')
        with open(signal_file, 'w') as f:
            f.write(json.dumps({
                'project': project,
                'requested_at': datetime.now().isoformat(),
                'priority': data.get('priority', 'high')
            }))
        
        return {
            'status': 'build_queued',
            'project': project,
            'message': f'Build signal queued for {project}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/control/generate-feature', methods=['POST'])
def generate_feature():
    """Tell agent to generate a specific feature for a project"""
    try:
        data = request.get_json()
        project = data.get('project')
        feature = data.get('feature')
        description = data.get('description', '')
        
        if not project or not feature:
            return {'error': 'project and feature required'}, 400
        
        # Create feature request file
        request_file = os.path.join(WORKSPACE, f'.feature_{project}_{int(datetime.now().timestamp())}')
        with open(request_file, 'w') as f:
            f.write(json.dumps({
                'project': project,
                'feature': feature,
                'description': description,
                'requested_at': datetime.now().isoformat()
            }))
        
        return {
            'status': 'feature_queued',
            'project': project,
            'feature': feature,
            'message': f'Feature request queued: {feature}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/control/set-api-key', methods=['POST'])
def set_api_key():
    """Set Gemini API key for real code generation"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return {'error': 'api_key required'}, 400
        
        # Write to .env file
        env_file = os.path.join(WORKSPACE, '.env')
        with open(env_file, 'w') as f:
            f.write(f'GEMINI_API_KEY={api_key}\n')
        
        # Also set in current environment
        os.environ['GEMINI_API_KEY'] = api_key
        
        return {
            'status': 'api_key_set',
            'message': 'Gemini API key configured. Restart agent to apply.',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/control/restart-agent', methods=['POST'])
def restart_agent():
    """Restart the agent process"""
    try:
        # This would need PID tracking - return status
        return {
            'status': 'restart_requested',
            'message': 'Agent restart requested. Manual restart needed: docker restart openclaw-agent',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/control/clear-cache', methods=['POST'])
def clear_cache():
    """Clear improvement files (reset agent state)"""
    try:
        # Remove all improvement_NNN.py files
        count = 0
        for project in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, project)
            if os.path.isdir(project_path):
                for file in os.listdir(project_path):
                    if file.startswith('improvement_') and file.endswith('.py'):
                        os.remove(os.path.join(project_path, file))
                        count += 1
        
        return {
            'status': 'cache_cleared',
            'files_removed': count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

# ============================================================================
# QUERY ENDPOINTS - Get detailed info
# ============================================================================

@app.route('/api/query/project-details/<project>')
def project_details(project):
    """Get detailed info about a project"""
    try:
        project_path = os.path.join(PROJECTS_DIR, project)
        if not os.path.exists(project_path):
            return {'error': f'Project {project} not found'}, 404
        
        files = []
        for file in os.listdir(project_path):
            if file.endswith('.py'):
                file_path = os.path.join(project_path, file)
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                files.append({
                    'name': file,
                    'lines': lines,
                    'type': 'test' if file.startswith('test_') else 'code',
                    'improvement': file.startswith('improvement_')
                })
        
        return {
            'project': project,
            'path': project_path,
            'files': sorted(files, key=lambda x: x['name']),
            'file_count': len(files),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/query/file-content/<project>/<filename>')
def file_content(project, filename):
    """Get content of a specific file"""
    try:
        # Security: prevent directory traversal
        if '..' in filename or '/' in filename:
            return {'error': 'Invalid filename'}, 400
        
        file_path = os.path.join(PROJECTS_DIR, project, filename)
        if not os.path.exists(file_path):
            return {'error': f'File not found'}, 404
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        return {
            'project': project,
            'filename': filename,
            'lines': len(content.split('\n')),
            'size': len(content),
            'content': content
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/query/build-queue')
def build_queue():
    """Check pending build requests"""
    try:
        queue = []
        for file in os.listdir(WORKSPACE):
            if file.startswith('.build_') or file.startswith('.feature_'):
                file_path = os.path.join(WORKSPACE, file)
                with open(file_path, 'r') as f:
                    queue.append({
                        'request': file,
                        'data': json.load(f)
                    })
        
        return {
            'pending': len(queue),
            'queue': queue
        }
    except Exception as e:
        return {'error': str(e)}, 500

# ============================================================================
# ORIGINAL READ-ONLY ENDPOINTS (preserved from api.py)
# ============================================================================

@app.route('/api/health')
def health():
    return {
        'service': 'OpenClaw Agent API',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/info')
def info():
    return {
        'name': 'OpenClaw',
        'version': '2.0',
        'features': ['autonomous-agent', 'rest-api', 'git-integration', 'command-control'],
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/projects')
def projects():
    try:
        if not os.path.exists(PROJECTS_DIR):
            return {'count': 0, 'projects': []}
        
        projects_list = []
        for name in os.listdir(PROJECTS_DIR):
            path = os.path.join(PROJECTS_DIR, name)
            if os.path.isdir(path):
                test_files = [f for f in os.listdir(path) if f.startswith('test_')]
                projects_list.append({
                    'name': name,
                    'tests': len(test_files)
                })
        
        return {'count': len(projects_list), 'projects': sorted(projects_list, key=lambda x: x['name'])}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/logs')
def logs():
    try:
        limit = request.args.get('limit', 50, type=int)
        log_file = os.path.join(WORKSPACE, 'bot_log.md')
        
        if not os.path.exists(log_file):
            return {'logs': [], 'total': 0}
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        recent = lines[-limit:] if limit > 0 else lines
        return {'logs': recent, 'total': len(lines), 'limit': limit}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/stats')
def stats():
    try:
        log_file = os.path.join(WORKSPACE, 'bot_log.md')
        
        stats = {
            'total_lines_logged': 0,
            'projects': 0,
            'has_gemini_key': 'GEMINI_API_KEY' in os.environ
        }
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                stats['total_lines_logged'] = len(f.readlines())
        
        if os.path.exists(PROJECTS_DIR):
            stats['projects'] = len([d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))])
        
        return stats
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/docs')
def docs():
    return {
        'endpoints': {
            'control': [
                {'POST /api/control/assign-task': 'Assign task to project'},
                {'POST /api/control/force-build': 'Force build a project'},
                {'POST /api/control/generate-feature': 'Request feature generation'},
                {'POST /api/control/set-api-key': 'Set Gemini API key'},
                {'POST /api/control/restart-agent': 'Restart agent'},
                {'POST /api/control/clear-cache': 'Clear improvement files'}
            ],
            'query': [
                {'GET /api/query/project-details/<project>': 'Get project details'},
                {'GET /api/query/file-content/<project>/<filename>': 'Get file content'},
                {'GET /api/query/build-queue': 'Check pending requests'}
            ],
            'monitor': [
                {'GET /api/health': 'Health check'},
                {'GET /api/info': 'Service info'},
                {'GET /api/projects': 'List projects'},
                {'GET /api/logs': 'Get recent logs'},
                {'GET /api/stats': 'Statistics'},
                {'GET /api/docs': 'This endpoint'}
            ]
        }
    }

@app.errorhandler(404)
def not_found(e):
    return {'error': 'Endpoint not found. Try GET /api/docs'}, 404

@app.errorhandler(500)
def server_error(e):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18789, debug=False)
