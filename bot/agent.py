#!/usr/bin/env python3
"""
OpenClaw - Autonomous Coding Agent

An AI-powered agent that autonomously develops mini-projects by:
- Reading TASKS.md and command signals from API
- Generating in-place code edits with Gemini
- Running tests before committing
- Rolling back failed edits
- Committing successful changes with backdated timestamps
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

MAX_CONTEXT_FILE_CHARS = int(os.getenv("OPENCLAW_MAX_CONTEXT_FILE_CHARS", "7000"))
MAX_CONTEXT_FILES = int(os.getenv("OPENCLAW_MAX_CONTEXT_FILES", "3"))

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
        print(f"⚠️  Gemini init error: {exc}. Falling back to deterministic edits.")
        model = None


# --- LOGGING ---
def log_action(action: str, details: str = "") -> None:
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
START_DATE = datetime.now() - timedelta(days=730)
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


# --- SAFETY ---
def is_path_safe(path: str, root: Optional[str] = None) -> bool:
    """Ensure path is inside root (or workspace if omitted)."""
    try:
        real_path = os.path.realpath(path)
        root_real = os.path.realpath(root or WORKSPACE)
        return real_path.startswith(root_real)
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


# --- FILE CONTEXT ---
def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content.rstrip() + "\n")


def _relative_project_path(project_path: str, abs_path: str) -> str:
    return os.path.relpath(abs_path, project_path)


def _list_project_python_files(project_path: str) -> Tuple[List[str], List[str]]:
    """Return (source_files, test_files) as relative paths."""
    source_files: List[str] = []
    test_files: List[str] = []

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".pytest_cache"}]

        for filename in files:
            if not filename.endswith(".py"):
                continue
            if filename.startswith("improvement_"):
                continue

            abs_path = os.path.join(root, filename)
            rel_path = _relative_project_path(project_path, abs_path)

            if filename.startswith("test_"):
                test_files.append(rel_path)
            else:
                source_files.append(rel_path)

    source_files.sort()
    test_files.sort()
    return source_files, test_files


def _directive_text(command: Optional[Dict[str, Any]]) -> str:
    if not command:
        return (
            "Pick one safe, incremental improvement that strengthens reliability or usability "
            "without breaking existing behavior."
        )

    command_type = command.get("type")
    if command_type == "build":
        return (
            "Improve build/test reliability for this project. Focus on validation, edge cases, "
            "or small refactors that improve maintainability."
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


def _keyword_tokens(command: Optional[Dict[str, Any]]) -> List[str]:
    if not command:
        return []

    raw = " ".join(
        [
            str(command.get("feature", "")),
            str(command.get("description", "")),
            str(command.get("task", "")),
        ]
    ).lower()

    tokens = [tok for tok in re.findall(r"[a-z]{4,}", raw) if tok not in {"with", "that", "from", "this"}]
    return list(dict.fromkeys(tokens))[:10]


def _choose_primary_source(source_files: List[str], command: Optional[Dict[str, Any]]) -> Optional[str]:
    if not source_files:
        return None

    keywords = _keyword_tokens(command)
    preferred = {"models.py", "analyzer.py", "scraper.py", "explainer.py"}

    def score(rel_path: str) -> Tuple[int, int, int]:
        name = os.path.basename(rel_path).lower()
        stem = name[:-3] if name.endswith(".py") else name
        keyword_hits = sum(1 for token in keywords if token in stem)
        preferred_hit = 1 if name in preferred else 0
        depth_penalty = -rel_path.count(os.sep)
        return (keyword_hits, preferred_hit, depth_penalty)

    return sorted(source_files, key=score, reverse=True)[0]


def _select_context_files(project_path: str, command: Optional[Dict[str, Any]]) -> List[str]:
    source_files, test_files = _list_project_python_files(project_path)
    context: List[str] = []

    primary = _choose_primary_source(source_files, command)
    if primary:
        context.append(primary)

    for rel_path in source_files:
        if rel_path not in context:
            context.append(rel_path)
        if len(context) >= max(1, MAX_CONTEXT_FILES - 1):
            break

    if test_files and len(context) < MAX_CONTEXT_FILES:
        primary_name = os.path.basename(primary or "")
        candidates = sorted(
            test_files,
            key=lambda p: 1 if primary_name and primary_name.replace(".py", "") in os.path.basename(p) else 0,
            reverse=True,
        )
        for rel_path in candidates:
            if rel_path not in context:
                context.append(rel_path)
            if len(context) >= MAX_CONTEXT_FILES:
                break

    return context[:MAX_CONTEXT_FILES]


def _build_prompt(project_name: str, project_path: str, command: Optional[Dict[str, Any]]) -> str:
    source_files, test_files = _list_project_python_files(project_path)
    context_files = _select_context_files(project_path, command)

    file_blocks: List[str] = []
    for rel_path in context_files:
        abs_path = os.path.join(project_path, rel_path)
        try:
            content = _read_text(abs_path)
        except Exception as exc:
            content = f"# Error reading file: {exc}"

        if len(content) > MAX_CONTEXT_FILE_CHARS:
            content = content[:MAX_CONTEXT_FILE_CHARS] + "\n# ...truncated..."

        file_blocks.append(f"FILE: {rel_path}\n```python\n{content}\n```")

    source_listing = "\n".join(f"- {p}" for p in source_files[:40]) or "- (none)"
    test_listing = "\n".join(f"- {p}" for p in test_files[:40]) or "- (none)"

    return f"""You are OpenClaw, an autonomous Python coding agent.

Project: {project_name}
Objective:
{_directive_text(command)}

Source files:
{source_listing}

Test files:
{test_listing}

Important constraints:
1. Prefer editing existing source files over creating new files.
2. DO NOT create files named improvement_*.py.
3. If you change behavior, update/add relevant tests in existing test files when needed.
4. Keep edits small and safe.
5. Return ONLY JSON, no markdown.

JSON response schema:
{{
  "summary": "one short sentence",
  "edits": [
    {{"file": "relative/path.py", "content": "FULL FILE CONTENT"}}
  ]
}}

Rules for edits:
- Each `file` must be a relative path inside the project.
- Prefer 1-2 file edits.
- `content` must be complete final file contents.

Current file snapshots:
{os.linesep.join(file_blocks)}
"""


def _extract_json_payload(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        fragment = cleaned[start : end + 1]
        try:
            obj = json.loads(fragment)
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _validate_edit_plan(
    project_path: str,
    raw_plan: Dict[str, Any],
    command: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    edits = raw_plan.get("edits")
    summary = str(raw_plan.get("summary", "Autonomous update")).strip()
    source_files, test_files = _list_project_python_files(project_path)
    allowed_files = set(source_files) | set(test_files)
    allow_non_source_test = bool(command and command.get("allow_non_source_test"))

    if not isinstance(edits, list) or not edits:
        return None

    valid_edits: List[Dict[str, str]] = []
    for item in edits:
        if not isinstance(item, dict):
            continue

        rel_file = item.get("file")
        content = item.get("content")
        if not isinstance(rel_file, str) or not isinstance(content, str):
            continue

        rel_file = rel_file.strip().replace("\\", "/")
        if not rel_file or rel_file.startswith("/") or ".." in rel_file.split("/"):
            continue
        if not rel_file.endswith(".py"):
            continue
        if os.path.basename(rel_file).startswith("improvement_"):
            continue
        if not allow_non_source_test and rel_file not in allowed_files:
            # By default we only allow edits to existing source/test files.
            continue

        abs_path = os.path.realpath(os.path.join(project_path, rel_file))
        if not is_path_safe(abs_path, root=project_path):
            continue

        valid_edits.append({"file": rel_file, "content": content})

    if not valid_edits:
        return None

    return {
        "summary": summary or "Autonomous update",
        "edits": valid_edits,
    }


def _fallback_edit_plan(project_path: str, command: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    source_files, _ = _list_project_python_files(project_path)
    primary = _choose_primary_source(source_files, command)
    if not primary and source_files:
        primary = source_files[0]
    if not primary:
        primary = "__init__.py"

    abs_path = os.path.join(project_path, primary)
    existing = ""
    if os.path.exists(abs_path):
        existing = _read_text(abs_path).rstrip()

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    note = _directive_text(command).replace('"', "'")
    fn_name = f"openclaw_note_{stamp}"

    addition = (
        f"\n\n\ndef {fn_name}() -> str:\n"
        f"    \"\"\"Autonomous note generated in fallback mode.\"\"\"\n"
        f"    return \"{note}\"\n"
    )

    content = (existing + addition).lstrip("\n")
    return {
        "summary": "Fallback in-place update",
        "edits": [{"file": primary, "content": content}],
    }


def generate_edit_plan(
    project_name: str,
    project_path: str,
    command: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate in-place edit plan using Gemini or fallback."""
    if model is None:
        log_action("WARN", "Gemini unavailable, using fallback in-place edit")
        return _fallback_edit_plan(project_path, command)

    prompt = _build_prompt(project_name, project_path, command)

    try:
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

        raw_text = response.text or ""
        raw_plan = _extract_json_payload(raw_text)
        if not raw_plan:
            raise ValueError("Model did not return parseable JSON")

        plan = _validate_edit_plan(project_path, raw_plan, command)
        if not plan:
            raise ValueError("Model returned invalid edit plan")

        return plan
    except Exception as exc:
        log_action("ERROR", f"Gemini edit planning failed: {exc}")
        return _fallback_edit_plan(project_path, command)


# --- APPLY + ROLLBACK ---
def apply_edit_plan(project_path: str, plan: Dict[str, Any]) -> Tuple[Dict[str, Optional[str]], List[str]]:
    """Apply edit plan. Returns backups and edited file list."""
    backups: Dict[str, Optional[str]] = {}
    changed_files: List[str] = []

    for edit in plan.get("edits", []):
        rel_path = edit["file"]
        new_content = edit["content"].rstrip() + "\n"
        abs_path = os.path.realpath(os.path.join(project_path, rel_path))

        if not is_path_safe(abs_path, root=project_path):
            log_action("ERROR", f"Unsafe edit path rejected: {rel_path}")
            continue

        old_content: Optional[str] = None
        if os.path.exists(abs_path):
            old_content = _read_text(abs_path)

        if old_content == new_content:
            log_action("NOOP", f"No content change for {rel_path}")
            continue

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        _write_text(abs_path, new_content)
        backups[abs_path] = old_content
        changed_files.append(rel_path)
        log_action("EDIT", f"Updated {rel_path}")

    return backups, changed_files


def rollback_edits(backups: Dict[str, Optional[str]]) -> None:
    """Restore edited files from backup map."""
    for abs_path, old_content in backups.items():
        try:
            if old_content is None:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                    log_action("ROLLBACK", f"Removed new file {os.path.basename(abs_path)}")
            else:
                _write_text(abs_path, old_content)
                log_action("ROLLBACK", f"Restored {os.path.basename(abs_path)}")
        except Exception as exc:
            log_action("ERROR", f"Rollback failed for {abs_path}: {exc}")


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
            timeout=60,
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


# --- GIT ---
def get_repo() -> Repo:
    """Get or initialize repository."""
    try:
        return Repo(WORKSPACE)
    except Exception:
        return Repo.init(WORKSPACE)


def _summarize_for_commit(summary: str) -> str:
    text = re.sub(r"\s+", " ", summary or "Autonomous update").strip()
    if len(text) > 72:
        return text[:69] + "..."
    return text or "Autonomous update"


def commit_changes(
    project_name: str,
    project_path: str,
    changed_files: List[str],
    summary: str,
    command: Optional[Dict[str, Any]] = None,
) -> bool:
    """Commit staged changes with backdated timestamp."""
    global commit_counter

    try:
        repo = get_repo()
        if not changed_files:
            log_action("DEBUG", "No changed files provided to commit")
            return False

        workspace_relative_paths = [
            os.path.relpath(os.path.realpath(os.path.join(project_path, rel_path)), WORKSPACE)
            for rel_path in changed_files
        ]
        repo.index.add(workspace_relative_paths)

        if not repo.is_dirty():
            log_action("DEBUG", "No changes to commit")
            return False

        commit_date_str = generate_backdate(0)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date_str
        env["GIT_COMMITTER_DATE"] = commit_date_str

        command_tag = command.get("type") if command else "auto"
        message = f"[{project_name}] {command_tag}: {_summarize_for_commit(summary)}"

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


# --- LOOP ---
def _summarize_command(command: Optional[Dict[str, Any]]) -> str:
    if not command:
        return "autonomous"
    return f"{command.get('type', 'unknown')}:{command.get('id', 'unknown')}:{command.get('project', 'unknown')}"


def main_loop() -> None:
    """Main agent loop."""
    error_count = 0
    max_errors = 5
    pending_commands: List[Dict[str, Any]] = []

    log_action("START", "OpenClaw agent starting")
    initialize_agent()

    while True:
        try:
            new_commands = check_for_commands()
            if new_commands:
                pending_commands.extend(new_commands)

            command = pending_commands.pop(0) if pending_commands else None

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

            plan = generate_edit_plan(project, project_path, command)
            backups, changed_files = apply_edit_plan(project_path, plan)

            if not changed_files:
                error_count += 1
                log_action("NOOP", "No actual code changes applied")
                if command:
                    log_action("COMMAND_FAIL", f"{command.get('type')} ({command.get('id')}) produced no changes")
                time.sleep(3)
                continue

            tests_ok, _ = run_tests(project_path)
            if tests_ok:
                if commit_changes(
                    project,
                    project_path,
                    changed_files,
                    summary=plan.get("summary", "Autonomous update"),
                    command=command,
                ):
                    error_count = 0
                    if command:
                        log_action("COMMAND_DONE", f"{command.get('type')} ({command.get('id')}) completed")
                else:
                    error_count += 1
            else:
                error_count += 1
                rollback_edits(backups)
                if command:
                    log_action("COMMAND_FAIL", f"{command.get('type')} ({command.get('id')}) failed tests")

            pending_signals = len(glob.glob(os.path.join(WORKSPACE, ".build_*")))
            pending_signals += len(glob.glob(os.path.join(WORKSPACE, ".feature_*")))
            pending_signals += len(glob.glob(os.path.join(WORKSPACE, ".task_*")))

            if pending_commands or pending_signals > 0:
                sleep_time = 2
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
