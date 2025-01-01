import os
import time
import random
from datetime import datetime, timedelta
from git import Repo
import google.generativeai as genai

# --- CONFIG ---
WORKSPACE = "/workspace"
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

repo = Repo(WORKSPACE)

# --- BACKDATE GENERATOR ---
START_DATE = datetime.now() - timedelta(days=730)  # ~2 years ago

def generate_backdate(iteration):
    # spread commits over time naturally
    dt = START_DATE + timedelta(days=iteration, hours=random.randint(0, 6))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# --- PROJECT SELECTION ---
def select_project():
    projects = os.listdir(PROJECTS_DIR)
    return random.choice(projects) if projects else None

# --- GEMINI CODE GEN ---
def generate_code(project_path):
    prompt = f"""
You are an autonomous coding agent.

Improve the project in: {project_path}

Rules:
- Make small safe improvements
- Do NOT break code
- Return ONLY valid Python code
"""

    response = model.generate_content(prompt)
    return response.text

# --- APPLY CHANGE ---
def make_change(project_path):
    code = generate_code(project_path)

    file_path = os.path.join(project_path, "auto_update.py")

    with open(file_path, "w") as f:
        f.write(code)

# --- TEST ---
def run_tests(project_path):
    return os.system(f"cd {project_path} && pytest") == 0

# --- COMMIT WITH BACKDATE ---
def commit_changes(iteration):
    repo.git.add(A=True)

    if repo.is_dirty():
        commit_date = generate_backdate(iteration)

        os.environ["GIT_AUTHOR_DATE"] = commit_date
        os.environ["GIT_COMMITTER_DATE"] = commit_date

        repo.index.commit(f"bot: update ({commit_date})")

        print(f"✅ Commit at {commit_date}")

# --- LOOP ---
def loop():
    iteration = 0

    while True:
        project = select_project()

        if not project:
            print("No projects found")
            time.sleep(10)
            continue

        project_path = os.path.join(PROJECTS_DIR, project)

        make_change(project_path)

        if run_tests(project_path):
            commit_changes(iteration)
            iteration += 1
        else:
            print("❌ Tests failed")

        time.sleep(random.randint(30, 90))


if __name__ == "__main__":
    loop()
