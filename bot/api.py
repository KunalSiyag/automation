#!/usr/bin/env python3
"""
OpenClaw REST API Server

Provides endpoints to monitor and control the autonomous agent.
Runs on port 18789 and serves agent status, logs, and project information.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

WORKSPACE = os.getenv("WORKSPACE", "/workspace")
LOG_FILE = os.path.join(WORKSPACE, "bot_log.md")
TASKS_FILE = os.path.join(WORKSPACE, "TASKS.md")
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_log_file():
    """Read and parse the bot_log.md file."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                return f.read()
        return ""
    except Exception as e:
        return f"Error reading log: {e}"


def parse_logs():
    """Parse logs and extract activity data."""
    log_content = read_log_file()
    logs = []
    
    for line in log_content.split('\n'):
        if line.strip():
            logs.append(line)
    
    return logs


def get_git_history(limit=20):
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "-C", WORKSPACE, "log", "--oneline", f"-{limit}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        return []
    except Exception as e:
        return [f"Error: {e}"]


def get_git_status():
    """Get git status."""
    try:
        result = subprocess.run(
            ["git", "-C", WORKSPACE, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception:
        return ""


def read_tasks_file():
    """Read TASKS.md file."""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                return f.read()
        return ""
    except Exception as e:
        return f"Error reading TASKS.md: {e}"


def get_projects():
    """Get list of projects."""
    projects = []
    try:
        if os.path.exists(PROJECTS_DIR):
            for item in os.listdir(PROJECTS_DIR):
                path = os.path.join(PROJECTS_DIR, item)
                if os.path.isdir(path):
                    # Count test files
                    test_count = len([f for f in os.listdir(path) 
                                     if f.startswith('test_') and f.endswith('.py')])
                    projects.append({
                        "name": item,
                        "path": path,
                        "tests": test_count
                    })
    except Exception as e:
        pass
    
    return projects


def get_project_test_status(project_name):
    """Run tests for a project and get status."""
    try:
        project_path = os.path.join(PROJECTS_DIR, project_name)
        result = subprocess.run(
            ["python", "-m", "pytest", "-q", "--tb=no"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse pytest output
        output = result.stdout + result.stderr
        if "passed" in output:
            # Extract counts
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                return {
                    "status": "PASS",
                    "output": output.split('\n')[-2:],
                    "return_code": result.returncode
                }
        
        return {
            "status": "FAIL" if result.returncode != 0 else "UNKNOWN",
            "output": output.split('\n')[-5:],
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "output": ["Test timed out"]}
    except Exception as e:
        return {"status": "ERROR", "output": [str(e)]}


def get_agent_status():
    """Get agent process status."""
    try:
        # Try to find agent process
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        is_running = "agent.py" in result.stdout
        
        return {
            "running": is_running,
            "last_log": parse_logs()[-1] if parse_logs() else None
        }
    except Exception as e:
        return {"running": False, "error": str(e)}


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "OpenClaw Agent API"
    })


@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """Get agent status."""
    return jsonify(get_agent_status())


@app.route('/api/logs', methods=['GET'])
def logs():
    """Get activity logs."""
    limit = request.args.get('limit', 50, type=int)
    all_logs = parse_logs()
    recent_logs = all_logs[-limit:] if all_logs else []
    
    return jsonify({
        "total_lines": len(all_logs),
        "logs": recent_logs,
        "limit": limit
    })


@app.route('/api/logs/raw', methods=['GET'])
def logs_raw():
    """Get raw log file content."""
    return read_log_file(), 200, {'Content-Type': 'text/plain'}


@app.route('/api/projects', methods=['GET'])
def projects():
    """Get list of projects."""
    project_list = get_projects()
    
    return jsonify({
        "count": len(project_list),
        "projects": project_list
    })


@app.route('/api/projects/<project_name>/tests', methods=['GET'])
def project_tests(project_name):
    """Get test status for a project."""
    status = get_project_test_status(project_name)
    
    return jsonify({
        "project": project_name,
        "test_status": status
    })


@app.route('/api/tasks', methods=['GET'])
def tasks():
    """Get project tasks."""
    content = read_tasks_file()
    
    return jsonify({
        "content": content
    })


@app.route('/api/git/history', methods=['GET'])
def git_history():
    """Get git commit history."""
    limit = request.args.get('limit', 20, type=int)
    history = get_git_history(limit)
    
    return jsonify({
        "commits": history,
        "limit": limit
    })


@app.route('/api/git/status', methods=['GET'])
def git_status_endpoint():
    """Get git status."""
    status = get_git_status()
    
    return jsonify({
        "status": status
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get overall statistics."""
    logs = parse_logs()
    history = get_git_history(100)
    projects = get_projects()
    
    # Count activities
    starts = sum(1 for log in logs if "START" in log)
    selects = sum(1 for log in logs if "SELECT" in log)
    tests = sum(1 for log in logs if "TEST" in log)
    commits = sum(1 for log in logs if "COMMIT" in log)
    errors = sum(1 for log in logs if "ERROR" in log)
    
    return jsonify({
        "uptime_seconds": len(logs) * 5,  # Rough estimate
        "total_activities": len(logs),
        "activities": {
            "starts": starts,
            "projects_selected": selects,
            "tests_run": tests,
            "commits_made": commits,
            "errors": errors
        },
        "git_commits": len(history),
        "projects_count": len(projects),
        "agent_status": get_agent_status()["running"]
    })


@app.route('/api/info', methods=['GET'])
def info():
    """Get OpenClaw system information."""
    return jsonify({
        "name": "OpenClaw",
        "version": "0.1.0",
        "description": "Autonomous AI Coding Agent",
        "workspace": WORKSPACE,
        "api_version": "1.0",
        "endpoints": {
            "health": "/api/health",
            "agent_status": "/api/agent/status",
            "logs": "/api/logs",
            "logs_raw": "/api/logs/raw",
            "projects": "/api/projects",
            "project_tests": "/api/projects/<name>/tests",
            "tasks": "/api/tasks",
            "git_history": "/api/git/history",
            "git_status": "/api/git/status",
            "stats": "/api/stats",
            "info": "/api/info",
            "docs": "/api/docs"
        }
    })


@app.route('/api/docs', methods=['GET'])
def docs():
    """API documentation."""
    return jsonify({
        "title": "OpenClaw REST API",
        "version": "1.0.0",
        "description": "Monitor and manage the autonomous coding agent",
        "base_url": "http://localhost:18789",
        "endpoints": [
            {
                "path": "/api/health",
                "method": "GET",
                "description": "Health check"
            },
            {
                "path": "/api/agent/status",
                "method": "GET",
                "description": "Get agent process status"
            },
            {
                "path": "/api/logs",
                "method": "GET",
                "description": "Get recent activity logs",
                "params": {"limit": "Number of logs (default: 50)"}
            },
            {
                "path": "/api/logs/raw",
                "method": "GET",
                "description": "Get raw log file"
            },
            {
                "path": "/api/projects",
                "method": "GET",
                "description": "List all projects"
            },
            {
                "path": "/api/projects/<name>/tests",
                "method": "GET",
                "description": "Run tests for a project"
            },
            {
                "path": "/api/tasks",
                "method": "GET",
                "description": "Get project tasks"
            },
            {
                "path": "/api/git/history",
                "method": "GET",
                "description": "Get git commit history",
                "params": {"limit": "Number of commits (default: 20)"}
            },
            {
                "path": "/api/git/status",
                "method": "GET",
                "description": "Get git status"
            },
            {
                "path": "/api/stats",
                "method": "GET",
                "description": "Get system statistics"
            },
            {
                "path": "/api/info",
                "method": "GET",
                "description": "Get API information"
            }
        ]
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info."""
    return jsonify({
        "message": "OpenClaw Agent API",
        "version": "0.1.0",
        "status": "running",
        "api_docs": "Visit /api/docs for documentation",
        "agent_status": get_agent_status()
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "docs": "Visit /api/docs for documentation"
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=18789,
        debug=False,
        threaded=True
    )
