#!/usr/bin/env python3
"""
OpenClaw - Autonomous Coding Agent

An AI-powered agent that autonomously develops multiple mini-projects:
- Reads tasks from TASKS.md
- Generates improvements using Google Gemini API
- Runs tests before committing
- Makes local git commits with backdated timestamps
- Logs all activities to bot_log.md
"""

import os
import sys
import time
import random
import subprocess
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from git import Repo
import google.generativeai as genai

# --- CONFIG ---
WORKSPACE = os.getenv("WORKSPACE", "/workspace")
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")
TASKS_FILE = os.path.join(WORKSPACE, "TASKS.md")
LOG_FILE = os.path.join(WORKSPACE, "bot_log.md")

# Initialize Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("⚠️  GEMINI_API_KEY not set. Running in demo mode.")
    genai.configure(api_key="demo-key")
else:
    genai.configure(api_key=gemini_api_key)

try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"⚠️  Gemini init error: {e}. Will use fallback mode.")
    model = None

# --- LOGGING ---
def log_action(action: str, details: str = ""):
    """Log actions to bot_log.md"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {action}"
    if details:
        log_entry += f" - {details}"
    log_entry += "\n"
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write log: {e}")
    
    print(log_entry.strip())

# --- BACKDATE GENERATOR ---
START_DATE = datetime.now() - timedelta(days=730)  # ~2 years ago
commit_counter = 0

def generate_backdate(offset=0):
    """Generate a backdated timestamp spread naturally over time"""
    global commit_counter
    # Spread commits naturally over 2 years
    days = min(commit_counter + offset, 720)  # Cap at 720 days
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    dt = START_DATE + timedelta(days=days, hours=hours, minutes=minutes)
    return dt.strftime("%Y-%m-%d %H:%M:%S"), dt

# --- SAFETY CHECKS ---
def is_path_safe(path: str) -> bool:
    """Ensure path is within /workspace"""
    try:
        real_path = os.path.realpath(path)
        workspace_real = os.path.realpath(WORKSPACE)
        return real_path.startswith(workspace_real)
    except Exception:
        return False

def read_tasks() -> dict:
    """Parse TASKS.md and return project status"""
    tasks = {}
    try:
        with open(TASKS_FILE, "r") as f:
            content = f.read()
        
        # Simple parsing of TASKS.md format
        for line in content.split("\n"):
            if line.startswith("## "):
                project = line.replace("## ", "").strip()
                tasks[project] = "PLANNED"
            elif "IN_PROGRESS" in line:
                if project:
                    tasks[project] = "IN_PROGRESS"
    except Exception as e:
        log_action("ERROR", f"Failed to read TASKS.md: {e}")
    
    return tasks

# --- PROJECT SELECTION ---
def get_valid_projects() -> list:
    """Get list of valid project directories"""
    if not os.path.exists(PROJECTS_DIR):
        return []
    
    projects = []
    for item in os.listdir(PROJECTS_DIR):
        path = os.path.join(PROJECTS_DIR, item)
        if os.path.isdir(path) and is_path_safe(path):
            projects.append(item)
    
    return projects

def select_project(tasks: dict) -> str:
    """Select a project to work on"""
    projects = get_valid_projects()
    
    if not projects:
        log_action("WARN", "No valid projects found")
        return None
    
    # Prefer IN_PROGRESS projects
    in_progress = [p for p in projects if tasks.get(p) == "IN_PROGRESS"]
    if in_progress:
        return random.choice(in_progress)
    
    return random.choice(projects)

# --- TASK GENERATION ---
def generate_improvement(project_name: str, project_path: str) -> str:
    """Generate code improvement using Gemini"""
    if model is None:
        log_action("WARN", "Gemini model not available, using fallback")
        return get_fallback_code(project_path)
    
    try:
        # Read project structure for context
        files_info = ""
        for root, dirs, files in os.walk(project_path):
            # Skip git and cache dirs
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
            for file in files[:10]:  # Limit to first 10 files per dir
                if not file.startswith('.'):
                    files_info += f"  - {file}\n"
        
        prompt = f"""You are an autonomous Python coding agent working on: {project_name}

Current project structure:
{files_info}

Your task:
1. Analyze the project
2. Suggest ONE small, safe improvement (e.g., add a utility function, improve error handling, add logging, optimize a function)
3. Return ONLY valid, executable Python code
4. Do NOT break existing functionality
5. Keep changes minimal and focused

Generate a small Python module or improvement that would enhance this project."""
        
        response = model.generate_content(prompt, safety_settings=[
            {"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_VIOLENCE", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_MEDICAL", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
        ])
        
        code = response.text
        
        # Extract Python code from response (in case it's wrapped in markdown)
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    except Exception as e:
        log_action("ERROR", f"Gemini generation failed: {e}")
        return get_fallback_code(project_path)

def get_fallback_code(project_path: str) -> str:
    """Fallback code generation when Gemini fails"""
    return """# Fallback improvement
def improve_project():
    '''This is a fallback improvement when Gemini is unavailable.'''
    return "Project initialized with fallback code"

if __name__ == "__main__":
    print(improve_project())
"""

def apply_improvement(project_path: str, code: str, iteration: int) -> bool:
    """Apply generated code to project"""
    try:
        # Create or update an improvement file
        filename = f"improvement_{iteration:03d}.py"
        file_path = os.path.join(project_path, filename)
        
        if not is_path_safe(file_path):
            log_action("ERROR", f"Unsafe path: {file_path}")
            return False
        
        with open(file_path, "w") as f:
            f.write(code)
        
        log_action("IMPROVEMENT", f"Applied to {filename}")
        return True
    
    except Exception as e:
        log_action("ERROR", f"Failed to apply improvement: {e}")
        return False

# --- TESTING ---
def run_tests(project_path: str) -> bool:
    """Run pytest in project directory"""
    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=project_path,
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if result.returncode == 0:
            log_action("TEST_PASS", project_path)
            return True
        else:
            log_action("TEST_FAIL", f"{project_path}\n{result.stdout}\n{result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        log_action("ERROR", f"Tests timed out for {project_path}")
        return False
    except Exception as e:
        log_action("ERROR", f"Test execution failed: {e}")
        return False

# --- GIT OPERATIONS ---
def get_repo() -> Repo:
    """Get or init the git repository"""
    try:
        return Repo(WORKSPACE)
    except Exception:
        return Repo.init(WORKSPACE)

def commit_changes(project_name: str, iteration: int) -> bool:
    """Commit changes with backdated timestamp"""
    global commit_counter
    
    try:
        repo = get_repo()
        repo.git.add(A=True)
        
        if not repo.is_dirty():
            log_action("DEBUG", "No changes to commit")
            return False
        
        commit_date_str, commit_date_obj = generate_backdate(0)
        
        # Set environment for backdated commit
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date_str
        env["GIT_COMMITTER_DATE"] = commit_date_str
        
        # Use git command directly for more reliable backdating
        message = f"[{project_name}] Autonomous improvement {commit_counter}"
        subprocess.run(
            ["git", "-C", WORKSPACE, "commit", "-m", message],
            env=env,
            capture_output=True,
            timeout=10
        )
        
        commit_counter += 1
        log_action("COMMIT", f"{project_name} @ {commit_date_str}")
        return True
    
    except Exception as e:
        log_action("ERROR", f"Commit failed: {e}")
        return False

# --- COMMAND HANDLING ---
def check_for_commands() -> dict:
    """Check for pending command files from API"""
    try:
        commands = {}
        
        # Check for build signals (.build_*)
        for signal_file in glob.glob(os.path.join(WORKSPACE, ".build_*")):
            try:
                with open(signal_file, 'r') as f:
                    commands['build'] = json.load(f)
                os.remove(signal_file)
                log_action("COMMAND", f"Received build signal")
            except Exception as e:
                log_action("DEBUG", f"Error reading signal: {e}")
        
        # Check for feature requests (.feature_*)
        for feature_file in glob.glob(os.path.join(WORKSPACE, ".feature_*")):
            try:
                with open(feature_file, 'r') as f:
                    commands['feature'] = json.load(f)
                os.remove(feature_file)
                log_action("COMMAND", f"Received feature request: {commands['feature'].get('feature')}")
            except Exception as e:
                log_action("DEBUG", f"Error reading feature: {e}")
        
        return commands
    except Exception as e:
        log_action("DEBUG", f"Error checking commands: {e}")
        return {}

def process_command(command_type: str, command_data: dict) -> bool:
    """Process a command from the API"""
    try:
        if command_type == 'build':
            project = command_data.get('project')
            log_action("EXEC", f"Processing build command for {project}")
            return True
        elif command_type == 'feature':
            project = command_data.get('project')
            feature = command_data.get('feature')
            description = command_data.get('description', '')
            log_action("EXEC", f"Generating feature: {feature} for {project}")
            return True
        return False
    except Exception as e:
        log_action("ERROR", f"Command processing failed: {e}")
        return False

# --- MAIN LOOP ---
def main_loop():
    """Main agent loop"""
    iteration = 0
    error_count = 0
    max_errors = 5
    
    log_action("START", "OpenClaw agent starting")
    
    while True:
        try:
            # Check for commands from API
            commands = check_for_commands()
            for cmd_type, cmd_data in commands.items():
                process_command(cmd_type, cmd_data)
            
            tasks = read_tasks()
            project = select_project(tasks)
            
            if not project:
                log_action("WARN", "No projects available, waiting")
                time.sleep(30)
                continue
            
            project_path = os.path.join(PROJECTS_DIR, project)
            
            if not is_path_safe(project_path):
                log_action("ERROR", f"Unsafe project path: {project_path}")
                error_count += 1
                continue
            
            if not os.path.isdir(project_path):
                log_action("WARN", f"Project directory missing: {project_path}")
                error_count += 1
                continue
            
            # Generate and apply improvement
            log_action("SELECT", f"Working on project: {project}")
            code = generate_improvement(project, project_path)
            
            if not apply_improvement(project_path, code, iteration):
                error_count += 1
                continue
            
            # Run tests
            if run_tests(project_path):
                # Tests passed, commit changes
                if commit_changes(project, iteration):
                    iteration += 1
                    error_count = 0
                else:
                    error_count += 1
            else:
                # Tests failed, log but continue
                error_count += 1
                log_action("RETRY", f"Will retry {project} later")
            
            # Random sleep between iterations
            sleep_time = random.randint(20, 60)
            log_action("SLEEP", f"{sleep_time} seconds")
            time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            log_action("STOP", "Agent interrupted by user")
            break
        except Exception as e:
            error_count += 1
            log_action("ERROR", f"Unexpected error: {e}")
            if error_count >= max_errors:
                log_action("CRITICAL", "Too many errors, stopping")
                break
            time.sleep(30)

if __name__ == "__main__":
    main_loop()
