import os
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='../templates', static_folder='../static')
WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())

def get_recent_commits(n=10):
    result = subprocess.run(
        ['git', 'log', '-n', str(n), '--pretty=format:%h|%ad|%s', '--date=format:%H:%M'],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    commits = []
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                h, t, m = line.split('|', 2)
                commits.append({'hash': h, 'time': t, 'msg': m})
    return commits

def get_commits_today():
    date_str = datetime.now().strftime("%Y-%m-%d")
    result = subprocess.run(
        ['git', 'log', '--since', f"{date_str} 00:00", '--until', f"{date_str} 23:59", '--oneline'],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    if result.returncode == 0 and result.stdout.strip():
        return len(result.stdout.strip().split('\n'))
    return 0

def get_docker_status(container_name):
    """Check if a docker container is running."""
    try:
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
            capture_output=True, text=True
        )
        return result.stdout.strip() == 'true'
    except Exception:
        return False

def get_agent_status():
    openclaw_running = get_docker_status('openclaw-agent')
    supervisor_running = get_docker_status('openclaw-supervisor')

    return openclaw_running, supervisor_running

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    commits = get_recent_commits(5)
    today = get_commits_today()
    openclaw, supervisor = get_agent_status()

    return jsonify({
        'commits': commits,
        'commits_today': today,
        'openclaw': openclaw,
        'supervisor': supervisor
    })

def read_log_file(filename, num_lines=10):
    filepath = os.path.join(WORKSPACE, filename)
    if not os.path.exists(filepath):
        return []

    try:
        # Get the last N lines using tail
        result = subprocess.run(
            ['tail', '-n', str(num_lines), filepath],
            capture_output=True, text=True
        )
        return [line for line in result.stdout.strip().split('\n') if line.strip()]
    except Exception:
        return []

@app.route('/api/logs')
def logs():
    # Read actual logs from bot_log.md and supervisor_log.md
    bot_logs = read_log_file('bot_log.md', 8)
    supervisor_logs = read_log_file('docs/supervisor_log.md', 5)
    if not supervisor_logs:
        supervisor_logs = read_log_file('supervisor_log.md', 5)

    recent_commits = get_recent_commits(2)

    all_logs = []

    # Add supervisor logs
    for log in supervisor_logs:
        all_logs.append(f"[SUPERVISOR] {log}")

    # Add bot logs
    for log in bot_logs:
        if log.startswith("## ") or log.startswith("### "):
            all_logs.append(f"[OpenClaw] {log}")
        else:
            # truncate long bot log lines
            log_str = log[:100] + "..." if len(log) > 100 else log
            all_logs.append(f"[OpenClaw] {log_str}")

    # Add recent commits
    for c in recent_commits:
        all_logs.append(f"[{c['time']}] Git commit: {c['hash']} - '{c['msg']}'")

    if not all_logs:
        all_logs = ["_ awaiting command..."]

    return jsonify({
        'logs': all_logs[-15:]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)