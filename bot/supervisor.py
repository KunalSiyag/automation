#!/usr/bin/env python3
"""
OpenClaw Supervisor Agent

Monitors OpenClaw agent, manages commit quality and cadence.
Ensures 4-10 commits per day with natural distribution and human-like behavior.
"""

import os
import random
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import subprocess

# --- CONFIG ---
WORKSPACE = os.getenv("WORKSPACE", "/workspace")
LOG_FILE = os.path.join(WORKSPACE, "bot_log.md")
SUPERVISOR_LOG = os.path.join(WORKSPACE, "supervisor_log.md")
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")

# Commit cadence configuration
MIN_COMMITS_PER_DAY = 4
MAX_COMMITS_PER_DAY = 20
WORK_HOURS_START = 8  # 8 AM
WORK_HOURS_END = 22   # 10 PM

# Quality thresholds
MIN_QUALITY_SCORE = 0.6
MAX_FALLBACK_STREAK = 2


class CommitTracker:
    """Track commits and manage daily cadence."""
    
    def __init__(self):
        self.commits_today = 0
        self.current_date = datetime.now().date()
        self.last_commit_time = None
        self.daily_target = random.randint(MIN_COMMITS_PER_DAY, MAX_COMMITS_PER_DAY)
        self.project_rotation = []
        
    def update_date_if_needed(self):
        """Reset counter if new day."""
        now = datetime.now().date()
        if now != self.current_date:
            self.supervisor_log(f"New day - previous commits: {self.commits_today}, target was: {self.daily_target}")
            self.commits_today = 0
            self.current_date = now
            self.daily_target = random.randint(MIN_COMMITS_PER_DAY, MAX_COMMITS_PER_DAY)
            self.supervisor_log(f"New daily target: {self.daily_target} commits")
    
    def should_commit_now(self) -> bool:
        """Determine if we should trigger a commit based on cadence."""
        self.update_date_if_needed()
        
        # Don't exceed daily max
        if self.commits_today >= MAX_COMMITS_PER_DAY:
            return False
        
        # Check if we're in work hours
        current_hour = datetime.now().hour
        if current_hour < WORK_HOURS_START or current_hour >= WORK_HOURS_END:
            return False
        
        # If below daily target, be more aggressive
        if self.commits_today < self.daily_target:
            # Calculate time remaining in work day
            now = datetime.now()
            work_end = now.replace(hour=WORK_HOURS_END, minute=0, second=0)
            hours_remaining = (work_end - now).total_seconds() / 3600
            
            if hours_remaining > 0:
                commits_needed = self.daily_target - self.commits_today
                avg_time_between = hours_remaining / max(commits_needed, 1)
                
                # Add randomness - human behavior isn't perfectly timed
                if self.last_commit_time:
                    time_since_last = (now - self.last_commit_time).total_seconds() / 3600
                    if time_since_last >= avg_time_between * random.uniform(0.7, 1.3):
                        return True
                else:
                    return True
        
        return False
    
    def record_commit(self):
        """Record that a commit was made."""
        self.commits_today += 1
        self.last_commit_time = datetime.now()
        self.supervisor_log(f"Commit recorded: {self.commits_today}/{self.daily_target} today")
    
    def get_next_project(self, available_projects: List[str]) -> str:
        """Select next project with natural rotation."""
        if not available_projects:
            return None
        
        # Refresh rotation if empty or projects changed
        if not self.project_rotation or set(self.project_rotation) != set(available_projects):
            self.project_rotation = available_projects.copy()
            random.shuffle(self.project_rotation)
        
        # Pop from rotation
        project = self.project_rotation.pop(0)
        
        # Re-add to end for next rotation
        self.project_rotation.append(project)
        
        return project
    
    def supervisor_log(self, message: str):
        """Log supervisor actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] SUPERVISOR: {message}\n"
        try:
            with open(SUPERVISOR_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass
        print(log_entry.strip())


class QualityMonitor:
    """Monitor commit quality and detect issues."""
    
    def __init__(self):
        self.fallback_streak = 0
        self.recent_commits = []
        self.max_recent = 20
    
    def analyze_commit(self, commit_msg: str, files_changed: List[str]) -> float:
        """Analyze commit quality. Returns score 0-1."""
        score = 1.0
        
        # Penalize fallback commits
        if 'fallback' in commit_msg.lower():
            score -= 0.4
            self.fallback_streak += 1
        else:
            self.fallback_streak = 0
        
        # Penalize generic messages
        generic_terms = ['update', 'improvement', 'change', 'modify']
        if any(term in commit_msg.lower() for term in generic_terms):
            score -= 0.1
        
        # Penalize AI-looking patterns
        ai_patterns = ['auto:', 'autonomous', 'openclaw', 'generated']
        if any(pattern in commit_msg.lower() for pattern in ai_patterns):
            score -= 0.3
        
        # Reward specific, descriptive messages
        if len(commit_msg.split()) >= 4:
            score += 0.2
        
        # Check file changes are meaningful
        if not files_changed:
            score -= 0.5
        
        self.recent_commits.append({
            'message': commit_msg,
            'score': score,
            'time': datetime.now()
        })
        
        # Keep only recent commits
        if len(self.recent_commits) > self.max_recent:
            self.recent_commits.pop(0)
        
        return max(0, min(1, score))
    
    def get_average_quality(self) -> float:
        """Get average quality of recent commits."""
        if not self.recent_commits:
            return 1.0
        return sum(c['score'] for c in self.recent_commits) / len(self.recent_commits)
    
    def is_quality_concerning(self) -> bool:
        """Check if quality is below threshold."""
        if self.fallback_streak >= MAX_FALLBACK_STREAK:
            return True
        if self.get_average_quality() < MIN_QUALITY_SCORE:
            return True
        return False


class SupervisorAgent:
    """Main supervisor that orchestrates OpenClaw."""
    
    def __init__(self):
        self.tracker = CommitTracker()
        self.quality = QualityMonitor()
        self.openclaw_running = False
    
    def log(self, message: str):
        """Shortcut for logging."""
        self.tracker.supervisor_log(message)
    
    def get_available_projects(self) -> List[str]:
        """Get list of project directories."""
        if not os.path.exists(PROJECTS_DIR):
            return []
        
        projects = []
        for item in os.listdir(PROJECTS_DIR):
            path = os.path.join(PROJECTS_DIR, item)
            if os.path.isdir(path) and not item.startswith('.'):
                projects.append(item)
        return projects
    
    def queue_command(self, command_type: str, project: str, **kwargs):
        """Queue a command for OpenClaw to process."""
        command_id = f"{command_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payload = {
            'id': command_id,
            'type': command_type,
            'project': project,
            **kwargs
        }
        
        # Write command signal file
        signal_file = os.path.join(WORKSPACE, f".{command_type}_{command_id}.json")
        try:
            with open(signal_file, 'w') as f:
                json.dump(payload, f)
            self.log(f"Queued {command_type} command for {project}")
            return True
        except Exception as e:
            self.log(f"Failed to queue command: {e}")
            return False
    
    def read_recent_log_entries(self, lines: int = 50) -> List[str]:
        """Read recent OpenClaw log entries."""
        if not os.path.exists(LOG_FILE):
            return []
        
        try:
            with open(LOG_FILE, 'r') as f:
                return f.readlines()[-lines:]
        except Exception:
            return []
    
    def detect_last_commit_quality(self) -> Optional[float]:
        """Analyze quality of last commit from logs."""
        entries = self.read_recent_log_entries(30)
        
        # Find last COMMIT entry
        for entry in reversed(entries):
            if 'COMMIT' in entry:
                # Try to extract commit message from git
                try:
                    result = subprocess.run(
                        ['git', '-C', WORKSPACE, 'log', '-1', '--pretty=%s'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        commit_msg = result.stdout.strip()
                        # Get files changed
                        files_result = subprocess.run(
                            ['git', '-C', WORKSPACE, 'show', '--name-only', '--pretty=', 'HEAD'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        files = files_result.stdout.strip().split('\n') if files_result.returncode == 0 else []
                        
                        score = self.quality.analyze_commit(commit_msg, files)
                        self.log(f"Commit quality: {score:.2f} - '{commit_msg}'")
                        return score
                except Exception as e:
                    self.log(f"Error analyzing commit: {e}")
        
        return None
    
    def should_intervene(self) -> Tuple[bool, str]:
        """Check if supervisor should intervene."""
        # Check quality issues
        if self.quality.is_quality_concerning():
            return True, "quality"
        
        # Check if we're behind schedule
        self.tracker.update_date_if_needed()
        now = datetime.now()
        current_hour = now.hour
        
        if WORK_HOURS_START <= current_hour < WORK_HOURS_END:
            # Calculate expected commits by now
            hours_into_workday = current_hour - WORK_HOURS_START
            work_hours_total = WORK_HOURS_END - WORK_HOURS_START
            expected_commits = (hours_into_workday / work_hours_total) * self.tracker.daily_target
            
            if self.tracker.commits_today < expected_commits * 0.7:  # 30% tolerance
                return True, "behind_schedule"
        
        return False, ""
    
    def supervise_cycle(self):
        """One supervision cycle."""
        self.log("=== Supervision Cycle ===")
        
        # Check if it's time to commit based on cadence
        if self.tracker.should_commit_now():
            projects = self.get_available_projects()
            if projects:
                project = self.tracker.get_next_project(projects)
                self.log(f"Triggering commit for {project}")
                
                # Queue a task command
                improvement_types = [
                    "Add comprehensive docstrings",
                    "Improve type hints coverage",
                    "Strengthen input validation",
                    "Enhance error handling",
                    "Add logging for debugging",
                    "Refactor for better readability",
                    "Optimize performance",
                ]
                
                task = random.choice(improvement_types)
                self.queue_command('task', project, task=task, priority='medium')
            else:
                self.log("No projects available")
        
        # Monitor last commit quality
        quality_score = self.detect_last_commit_quality()
        if quality_score is not None and quality_score >= MIN_QUALITY_SCORE:
            self.tracker.record_commit()
        
        # Check if intervention needed
        should_intervene, reason = self.should_intervene()
        if should_intervene:
            self.log(f"Intervention needed: {reason}")
            self.handle_intervention(reason)
    
    def handle_intervention(self, reason: str):
        """Handle quality or schedule issues."""
        if reason == "quality":
            self.log("Quality issues detected - requesting rebuild")
            projects = self.get_available_projects()
            if projects:
                project = random.choice(projects)
                self.queue_command('build', project, priority='high')
        
        elif reason == "behind_schedule":
            commits_needed = self.tracker.daily_target - self.tracker.commits_today
            self.log(f"Behind schedule - need {commits_needed} more commits today")
            # Queue multiple tasks
            projects = self.get_available_projects()
            if projects:
                for _ in range(min(2, commits_needed)):
                    project = self.tracker.get_next_project(projects)
                    self.queue_command('task', project, task="Quick improvement", priority='high')
    
    def run(self):
        """Main supervisor loop."""
        self.log("OpenClaw Supervisor starting")
        self.log(f"Daily commit target: {self.tracker.daily_target}")
        
        while True:
            try:
                self.supervise_cycle()
                
                # Sleep with some randomness (human-like checking)
                sleep_time = random.randint(180, 420)  # 3-7 minutes
                self.log(f"Sleeping for {sleep_time}s")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.log("Supervisor stopped by user")
                break
            except Exception as e:
                self.log(f"Error in supervision cycle: {e}")
                time.sleep(60)


if __name__ == "__main__":
    supervisor = SupervisorAgent()
    supervisor.run()
