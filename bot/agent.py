#!/usr/bin/env python3
"""
OpenClaw - Autonomous Coding Agent

An AI-powered agent that autonomously develops multiple mini-projects:
- Reads tasks from TASKS.md
- Processes queued build/feature/task commands from API signals
- Generates improvements using Google Gemini API
- Runs tests before committing
- Makes local git commits with backdated timestamps
- Logs all activities to bot_log.md
"""

import glob
import json
import os
import random
import re
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from git import Repo
import google.generativeai as genai

# --- CONFIG ---
WORKSPACE = os.getenv("WORKSPACE", "/workspace")
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")
TASKS_FILE = os.path.join(WORKSPACE, "TASKS.md")
LOG_FILE = os.path.join(WORKSPACE, "bot_log.md")

MIN_SLEEP = int(os.getenv("OPENCLAW_MIN_SLEEP", "20"))
MAX_SLEEP = int(os.getenv("OPENCLAW_MAX_SLEEP", "60"))

# Initialize Gemini
model = None
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("⚠️  GEMINI_API_KEY not set. Running in fallback generation mode.")
else:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
    except Exception as exc:
        print(f"⚠️  Gemini init error: {exc}. Falling back to deterministic code.")
        model = None


# --- LOGGING ---
def log_action(action: str, details: str = ""):
    """Log actions to bot_log.md."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {action}"
    if details:
        log_entry += f" - {details}"
    log_entry += "\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(log_entry)
    except Exception as exc:
        print(f"Failed to write log: {exc}")

    print(log_entry.strip())


# --- BACKDATE GENERATOR ---
START_DATE = datetime.now() - timedelta(days=730)  # ~2 years ago
commit_counter = 0


def generate_backdate(offset: int = 0) -> str:
    """Generate a backdated timestamp spread naturally over time."""
    global commit_counter
    days = min(commit_counter + offset, 720)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    dt = START_DATE + timedelta(days=days, hours=hours, minutes=minutes)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def initialize_commit_counter() -> None:
    """Start commit counter near current git history size for natural progression."""
    global commit_counter
    try:
        repo = Repo(WORKSPACE)
        commit_counter = sum(1 for _ in repo.iter_commits())
    except Exception:
        commit_counter = 0


# --- SAFETY CHECKS ---
def is_path_safe(path: str) -> bool:
    """Ensure path is within /workspace."""
    try:
        real_path = os.path.realpath(path)
        workspace_real = os.path.realpath(WORKSPACE)
        return real_path.startswith(workspace_real)
    except Exception:
        return False


def initialize_agent() -> None:
    """Initialize agent on startup."""
    initialize_commit_counter()
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", WORKSPACE],
            capture_output=True,
            timeout=5,
            check=False,
        )
        log_action("INIT", "Git safe.directory configured")
    except Exception as exc:
        log_action("WARN", f"Git config failed: {exc}")


# --- TASK PARSING ---
def read_tasks() -> Dict[str, str]:
    """Parse TASKS.md and return project->status mapping."""
    tasks: Dict[str, str] = {}
    current_project: Optional[str] = None

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if line.startswith("## "):
                    current_project = line[3:].strip()
                    tasks[current_project] = "PLANNED"
                    continue

                if not current_project:
                    continue

                if line.startswith("**Status:**"):
                    tasks[current_project] = line.replace("**Status:**", "", 1).strip()
                elif line.startswith("Status:"):
                    tasks[current_project] = line.replace("Status:", "", 1).strip()
    except Exception as exc:
        log_action("ERROR", f"Failed to read TASKS.md: {exc}")

    return tasks


# --- PROJECT SELECTION ---
def get_valid_projects() -> List[str]:
    """Get list of valid project directories."""
    if not os.path.exists(PROJECTS_DIR):
        return []

    projects: List[str] = []
    for item in os.listdir(PROJECTS_DIR):
        path = os.path.join(PROJECTS_DIR, item)
        if os.path.isdir(path) and is_path_safe(path):
            projects.append(item)

    return sorted(projects)


def select_project(tasks: Dict[str, str], preferred_project: Optional[str] = None) -> Optional[str]:
    """Select a project to work on."""
    projects = get_valid_projects()
    if not projects:
        log_action("WARN", "No valid projects found")
        return None

    if preferred_project and preferred_project in projects:
        return preferred_project

    in_progress = [p for p in projects if tasks.get(p, "").upper() == "IN_PROGRESS"]
    if in_progress:
        return random.choice(in_progress)

    return random.choice(projects)


# --- COMMAND HANDLING ---
def check_for_commands() -> List[Dict[str, Any]]:
    """Collect queued command files from API in chronological order."""
    command_files: List[str] = []
    for pattern in (".build_*", ".feature_*", ".task_*"):
        command_files.extend(glob.glob(os.path.join(WORKSPACE, pattern)))

    if not command_files:
        return []

    command_files.sort(key=lambda path: os.path.getmtime(path))

    commands: List[Dict[str, Any]] = []
    for signal_file in command_files:
        basename = os.path.basename(signal_file)
        command_type = "unknown"
        if basename.startswith(".build_"):
            command_type = "build"
        elif basename.startswith(".feature_"):
            command_type = "feature"
        elif basename.startswith(".task_"):
            command_type = "task"

        try:
            with open(signal_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)

            command_id = payload.get("id") or basename
            payload["id"] = command_id
            payload["type"] = command_type
            payload["signal_file"] = signal_file
            commands.append(payload)
            log_action("COMMAND", f"Dequeued {command_type} ({command_id})")
        except Exception as exc:
            log_action("ERROR", f"Failed reading command file {basename}: {exc}")
        finally:
            try:
                os.remove(signal_file)
            except Exception as exc:
                log_action("DEBUG", f"Failed deleting signal file {basename}: {exc}")

    return commands


# --- PROMPTING + GENERATION ---
def _project_context(project_path: str) -> str:
    """Build compact context describing project files."""
    lines: List[str] = []
    count = 0
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".pytest_cache"}]
        rel_root = os.path.relpath(root, project_path)
        rel_root = "." if rel_root == "." else rel_root

        for filename in sorted(files):
            if filename.startswith("."):
                continue
            count += 1
            if count > 40:
                break
            rel_file = filename if rel_root == "." else f"{rel_root}/{filename}"
            lines.append(f"- {rel_file}")
        if count > 40:
            break

    return "\n".join(lines)


def _directive_text(command: Optional[Dict[str, Any]]) -> str:
    if not command:
        return (
            "Pick one safe, incremental improvement that strengthens reliability or usability "
            "without breaking existing behavior."
        )

    command_type = command.get("type")
    if command_type == "build":
        return (
            "Improve build/test reliability for this project. "
            "Focus on error handling, validation, or small refactors."
        )

    if command_type == "feature":
        feature = command.get("feature", "Requested feature")
        description = command.get("description", "")
        details = f"Feature request: {feature}."
        if description:
            details += f" Description: {description}."
        return details

    if command_type == "task":
        task = command.get("task", "Requested task")
        priority = command.get("priority", "medium")
        return f"Task request ({priority} priority): {task}."

    return "Apply one small safe improvement."


def generate_improvement(
    project_name: str,
    project_path: str,
    command: Optional[Dict[str, Any]],
) -> str:
    """Generate code improvement using Gemini or fallback."""
    if model is None:
        log_action("WARN", "Gemini unavailable, using fallback code")
        return get_fallback_code(project_name, command)

    try:
        prompt = f"""You are OpenClaw, an autonomous Python coding agent.

Project: {project_name}
Project files (partial):
{_project_context(project_path)}

Objective:
{_directive_text(command)}

Strict output rules:
1. Return ONLY valid Python code (no markdown fences).
2. Keep it small and safe.
3. Must not import unavailable third-party packages.
4. Prefer helper functions/classes that can live in one module.
5. Do not include shell commands.
"""

        response = model.generate_content(
            prompt,
            safety_settings=[
                {"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_VIOLENCE", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_MEDICAL", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            ],
        )

        code = response.text or ""
        if "```python" in code:
            code = code.split("```python", 1)[1].split("```", 1)[0].strip()
        elif "```" in code:
            code = code.split("```", 1)[1].split("```", 1)[0].strip()

        if not code.strip():
            raise ValueError("Model returned empty code")

        return code
    except Exception as exc:
        log_action("ERROR", f"Gemini generation failed: {exc}")
        return get_fallback_code(project_name, command)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:40] or "improvement"


def _next_iteration(project_path: str) -> int:
    max_num = -1
    for file_path in Path(project_path).glob("improvement_*.py"):
        match = re.match(r"improvement_(\d+)\.py", file_path.name)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def get_fallback_code(project_name: str, command: Optional[Dict[str, Any]]) -> str:
    """Fallback code generation when Gemini fails."""
    directive = _directive_text(command)
    return f'''"""Fallback improvement module for {project_name}."""


def describe_improvement() -> str:
    """Return a deterministic description for fallback mode."""
    return "{directive}"
'''


def apply_improvement(project_path: str, code: str, command: Optional[Dict[str, Any]]) -> Optional[str]:
    """Apply generated code to project. Returns written file path on success."""
    try:
        iteration = _next_iteration(project_path)
        suffix = ""
        if command and command.get("type") in {"feature", "task"}:
            seed = command.get("feature") or command.get("task") or "request"
            suffix = f"_{_slugify(seed)}"

        filename = f"improvement_{iteration:03d}{suffix}.py"
        file_path = os.path.join(project_path, filename)

        if not is_path_safe(file_path):
            log_action("ERROR", f"Unsafe path: {file_path}")
            return None

        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write(code.rstrip() + "\n")

        log_action("IMPROVEMENT", f"Applied to {filename}")
        return file_path
    except Exception as exc:
        log_action("ERROR", f"Failed to apply improvement: {exc}")
        return None


# --- TESTING ---
def run_tests(project_path: str) -> Tuple[bool, str]:
    """Run pytest in project directory."""
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = project_path

        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=project_path,
            capture_output=True,
            timeout=45,
            text=True,
            env=env,
            check=False,
        )

        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            log_action("TEST_PASS", project_path)
            return True, output

        log_action("TEST_FAIL", f"{project_path}\n{output}")
        return False, output
    except subprocess.TimeoutExpired:
        message = f"Tests timed out for {project_path}"
        log_action("ERROR", message)
        return False, message
    except Exception as exc:
        message = f"Test execution failed: {exc}"
        log_action("ERROR", message)
        return False, message


# --- GIT OPERATIONS ---
def get_repo() -> Repo:
    """Get or init the git repository."""
    try:
        return Repo(WORKSPACE)
    except Exception:
        return Repo.init(WORKSPACE)


def commit_changes(project_name: str, command: Optional[Dict[str, Any]] = None) -> bool:
    """Commit changes with backdated timestamp."""
    global commit_counter

    try:
        repo = get_repo()
        repo.git.add(A=True)

        if not repo.is_dirty():
            log_action("DEBUG", "No changes to commit")
            return False

        commit_date_str = generate_backdate(0)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date_str
        env["GIT_COMMITTER_DATE"] = commit_date_str

        command_tag = command.get("type") if command else "auto"
        message = f"[{project_name}] {command_tag} improvement {commit_counter}"

        result = subprocess.run(
            ["git", "-C", WORKSPACE, "commit", "-m", message],
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

        if result.returncode != 0:
            log_action("ERROR", f"Commit failed: {result.stderr.strip()}")
            return False

        commit_counter += 1
        log_action("COMMIT", f"{project_name} @ {commit_date_str}")
        return True
    except Exception as exc:
        log_action("ERROR", f"Commit failed: {exc}")
        return False


def rollback_improvement(file_path: Optional[str]) -> None:
    """Remove the generated file when tests fail to keep workspace stable."""
    if not file_path:
        return

    try:
        if os.path.exists(file_path) and is_path_safe(file_path):
            os.remove(file_path)
            log_action("ROLLBACK", f"Removed failed improvement {os.path.basename(file_path)}")
    except Exception as exc:
        log_action("ERROR", f"Rollback failed for {file_path}: {exc}")


# --- MAIN LOOP ---
def _summarize_command(command: Optional[Dict[str, Any]]) -> str:
    if not command:
        return "autonomous"
    command_type = command.get("type", "unknown")
    command_id = command.get("id", "unknown")
    project = command.get("project", "unknown")
    return f"{command_type}:{command_id}:{project}"


def main_loop() -> None:
    """Main agent loop."""
    error_count = 0
    max_errors = 5

    log_action("START", "OpenClaw agent starting")
    initialize_agent()

    while True:
        try:
            commands = check_for_commands()
            command = commands[0] if commands else None

            tasks = read_tasks()
            forced_project = command.get("project") if command else None
            project = select_project(tasks, preferred_project=forced_project)

            if not project:
                log_action("WARN", "No projects available, waiting")
                time.sleep(30)
                continue

            project_path = os.path.join(PROJECTS_DIR, project)
            if not is_path_safe(project_path) or not os.path.isdir(project_path):
                error_count += 1
                log_action("ERROR", f"Invalid project path: {project_path}")
                time.sleep(10)
                continue

            log_action("SELECT", f"Working on {project} ({_summarize_command(command)})")

            code = generate_improvement(project, project_path, command)
            improvement_file = apply_improvement(project_path, code, command)
            if not improvement_file:
                error_count += 1
                continue

            tests_ok, _ = run_tests(project_path)
            if tests_ok:
                if commit_changes(project, command=command):
                    error_count = 0
                    if command:
                        log_action("COMMAND_DONE", f"{command.get('type')} ({command.get('id')}) completed")
                else:
                    error_count += 1
            else:
                error_count += 1
                rollback_improvement(improvement_file)
                if command:
                    log_action("COMMAND_FAIL", f"{command.get('type')} ({command.get('id')}) failed tests")

            pending_signals = len(glob.glob(os.path.join(WORKSPACE, ".build_*")))
            pending_signals += len(glob.glob(os.path.join(WORKSPACE, ".feature_*")))
            pending_signals += len(glob.glob(os.path.join(WORKSPACE, ".task_*")))

            if pending_signals > 0:
                sleep_time = 5
            else:
                sleep_time = random.randint(MIN_SLEEP, MAX_SLEEP)

            log_action("SLEEP", f"{sleep_time} seconds")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            log_action("STOP", "Agent interrupted by user")
            break
        except Exception as exc:
            error_count += 1
            log_action("ERROR", f"Unexpected error: {exc}")
            if error_count >= max_errors:
                log_action("CRITICAL", "Too many errors, stopping")
                break
            time.sleep(10)


if __name__ == "__main__":
    main_loop()
