#!/usr/bin/env python3
"""
Simple dashboard to monitor the OpenClaw Agentic System
Shows real-time stats and recent activity
"""

import os
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = os.getcwd()

def get_commits_by_day(days=7):
    """Get commit count by day for last N days."""
    commits_by_day = defaultdict(int)
    
    for day_offset in range(days):
        date = datetime.now() - timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        
        result = subprocess.run(
            ['git', 'log', '--since', f"{date_str} 00:00", '--until', f"{date_str} 23:59", '--oneline'],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            commits_by_day[date_str] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    
    return commits_by_day

def get_recent_commits(n=10):
    """Get last N commits."""
    result = subprocess.run(
        ['git', 'log', '-n', str(n), '--pretty=format:%h|%ad|%s', '--date=format:%H:%M'],
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )
    
    if result.returncode == 0:
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                hash, time, msg = line.split('|', 2)
                commits.append((hash, time, msg))
        return commits
    return []

def get_agent_status():
    """Check if agents are running."""
    openclaw_running = False
    supervisor_running = False
    
    openclaw_pid_file = os.path.join(WORKSPACE, '.openclaw.pid')
    supervisor_pid_file = os.path.join(WORKSPACE, '.supervisor.pid')
    
    if os.path.exists(openclaw_pid_file):
        try:
            with open(openclaw_pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            openclaw_running = True
        except (OSError, ValueError):
            pass
    
    if os.path.exists(supervisor_pid_file):
        try:
            with open(supervisor_pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            supervisor_running = True
        except (OSError, ValueError):
            pass
    
    return openclaw_running, supervisor_running

def print_bar_chart(value, max_value, width=20):
    """Print a simple bar chart."""
    filled = int((value / max(max_value, 1)) * width)
    bar = '█' * filled + '░' * (width - filled)
    return bar

def main():
    print("\n" + "="*70)
    print("  🤖 OpenClaw Agentic System Dashboard")
    print("="*70)
    
    # Agent Status
    openclaw, supervisor = get_agent_status()
    print("\n📊 Agent Status:")
    print(f"  OpenClaw:   {'🟢 Running' if openclaw else '🔴 Stopped'}")
    print(f"  Supervisor: {'🟢 Running' if supervisor else '🔴 Stopped'}")
    
    # Commits by Day
    print("\n📅 Commits per Day (Last 7 Days):")
    commits_by_day = get_commits_by_day(7)
    max_commits = max(commits_by_day.values()) if commits_by_day else 10
    
    for date_str in sorted(commits_by_day.keys(), reverse=True):
        count = commits_by_day[date_str]
        bar = print_bar_chart(count, max_commits, 30)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%a")
        print(f"  {date_str} ({day_name}): {bar} {count} commits")
    
    # Today's Stats
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_commits = commits_by_day.get(today_str, 0)
    
    print(f"\n📈 Today's Progress:")
    print(f"  Commits so far: {today_commits}")
    print(f"  Target range:   4-10 commits/day")
    
    if today_commits < 4:
        print(f"  Status:         🟡 Below target")
    elif today_commits <= 10:
        print(f"  Status:         🟢 On track")
    else:
        print(f"  Status:         🔵 Above target")
    
    # Recent Commits
    print("\n📝 Recent Commits:")
    recent = get_recent_commits(10)
    
    for hash, time, msg in recent:
        # Highlight if message looks good
        if any(word in msg.lower() for word in ['add', 'fix', 'improve', 'update', 'refactor']):
            indicator = "✓"
        else:
            indicator = "·"
        
        # Truncate long messages
        if len(msg) > 50:
            msg = msg[:47] + "..."
        
        print(f"  {indicator} {hash} ({time}) {msg}")
    
    # Summary
    print("\n" + "="*70)
    total_week = sum(commits_by_day.values())
    avg_per_day = total_week / 7
    print(f"  Weekly Total: {total_week} commits | Daily Average: {avg_per_day:.1f}")
    print("="*70)
    
    print("\nCommands:")
    print("  ./agentic_system.sh status  - Check detailed status")
    print("  ./agentic_system.sh logs    - View logs")
    print("  git log --oneline -20       - See commit history")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDashboard closed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you're in the automation directory.")
