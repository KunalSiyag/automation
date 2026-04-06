# 📖 OpenClaw Development Guide

Complete guide for understanding, running, and extending OpenClaw.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Running the Agent](#running-the-agent)
3. [Understanding the Projects](#understanding-the-projects)
4. [Agent Behavior](#agent-behavior)
5. [Safety Mechanisms](#safety-mechanisms)
6. [Extending the System](#extending-the-system)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Components

```
┌─────────────────────────────────────┐
│      OpenClaw Agent (agent.py)       │
├─────────────────────────────────────┤
│ • Project Selector                  │
│ • Gemini Code Generator             │
│ • Test Runner (pytest)              │
│ • Git Commit Manager                │
│ • Activity Logger                   │
└─────────────────────────────────────┘
         │
         ├──── Projects/ ────┬──── todo_app/
         │                   ├──── data_analyzer/
         │                   ├──── web_scraper/
         │                   └──── code_explainer/
         │
         ├──── TASKS.md (Project tracking)
         ├──── bot_log.md (Activity log)
         └──── .git/ (Version control)
```

### Data Flow

```
1. Read TASKS.md
   ↓
2. Select Project (prefer IN_PROGRESS)
   ↓
3. Analyze Project Structure
   ↓
4. Generate Code via Gemini API
   ↓
5. Apply Changes to Files
   ↓
6. Run pytest
   ↓
7. If PASS: Commit with Backdate → Repeat
   If FAIL: Log & Continue
```

## Running the Agent

### Prerequisites

- Python 3.11+
- git
- Optional: Docker
- Optional: Google Gemini API key

### Local Development Setup

```bash
# Clone and navigate
cd automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
export GEMINI_API_KEY="your-key-here"

# Run the agent
python src/agent.py
```

### Docker Setup

```bash
# Build image
docker build -f src/Dockerfile -t openclaw:latest .

# Run container with volume mount
docker run -it \
  --name openclaw-agent \
  -v $(pwd):/workspace \
  -e GEMINI_API_KEY="your-key-here" \
  openclaw:latest

# Run in background
docker run -d \
  --name openclaw-agent \
  -v $(pwd):/workspace \
  -e GEMINI_API_KEY="your-key-here" \
  openclaw:latest

# View logs
docker logs -f openclaw-agent

# Stop container
docker stop openclaw-agent
```

### Testing Projects

Run tests for individual projects:

```bash
cd projects/todo_app
python -m pytest -v

cd ../data_analyzer
python -m pytest -v

cd ../web_scraper
python -m pytest -v

cd ../code_explainer
python -m pytest -v
```

Run all tests:

```bash
# From automation root
for dir in projects/*/; do
  echo "Testing $(basename $dir)..."
  cd "$dir"
  python -m pytest -q
  cd - > /dev/null
done
```

## Understanding the Projects

### 1. todo_app - Task Management

**Purpose**: Demonstrate CRUD operations and state management

**Core Classes**:
- `TaskStatus` - Enum for task states
- `Task` - Individual task with title, description, status
- `TaskManager` - Collection management and querying

**Key Methods**:
```python
manager = TaskManager()
task = manager.add_task("Buy groceries", priority=2)
task.mark_done()
incomplete = manager.get_incomplete_tasks()
stats = manager.get_task_count()
```

**Test Coverage**: 10 unit tests
- Task creation and properties
- Status transitions
- Manager CRUD operations
- Filtering by status
- Statistics calculation

**Possible Improvements**:
- [ ] JSON persistence to file
- [ ] Task descriptions with markdown
- [ ] Due dates and reminders
- [ ] Priority-based sorting
- [ ] Archive completed tasks

### 2. data_analyzer - Data Processing

**Purpose**: Load, analyze, and export data

**Core Classes**:
- `DataLoader` - Load CSV/JSON and manipulate data
- `DataAnalyzer` - Statistical analysis

**Key Methods**:
```python
loader = DataLoader()
loader.load_csv("data.csv")
data = loader.get_data()
filtered = loader.filter_data("age", 30)
stats = DataAnalyzer.get_summary_stats([1,2,3,4,5])
```

**Test Coverage**: 10 unit tests
- JSON/CSV loading
- Data filtering
- Column operations
- Statistics (min, max, mean, median)
- Data export

**Possible Improvements**:
- [ ] Pandas integration for large files
- [ ] SQL database backend
- [ ] Data visualization helpers
- [ ] Groupby and aggregation
- [ ] Missing value handling

### 3. web_scraper - Web Utilities

**Purpose**: Safe web scraping tools with validation

**Core Classes**:
- `URLValidator` - URL validation and normalization
- `RateLimiter` - Prevent rate limiting
- `HTMLParser` - Extract data from HTML
- `Scraper` - Coordinate scraping operations

**Key Methods**:
```python
if URLValidator.is_valid_url(url):
    scraper = Scraper(rate_limit=1.0)
    links = HTMLParser.extract_links(html)
    text = HTMLParser.extract_text(html)
    headings = HTMLParser.extract_headings(html)
```

**Test Coverage**: 9 unit tests
- URL validation
- HTML parsing (links, text, headings, images)
- Visited tracking
- Data extraction

**Possible Improvements**:
- [ ] requests library integration
- [ ] CSS selector support
- [ ] JavaScript rendering
- [ ] robots.txt compliance
- [ ] Proxy rotation

### 4. code_explainer - Code Analysis

**Purpose**: Analyze and explain Python code structure

**Core Classes**:
- `CodeParser` - Parse Python and extract AST info
- `CodeFormatter` - Format code with annotations
- `CodeSummary` - Generate comprehensive summaries

**Key Methods**:
```python
parser = CodeParser(code)
if parser.parse():
    functions = parser.get_functions()
    classes = parser.get_classes()
    imports = parser.get_imports()
    metrics = parser.get_complexity_metrics()
```

**Test Coverage**: 9 unit tests
- Code parsing and error handling
- Function/class extraction
- Import tracking
- Complexity metrics
- Markdown formatting

**Possible Improvements**:
- [ ] Gemini AI explanations
- [ ] Type hint analysis
- [ ] Cyclomatic complexity calculation
- [ ] Security vulnerability detection
- [ ] Dead code detection

## Agent Behavior

### Main Loop Cycle

```python
while True:
    # 1. Read tasks
    tasks = read_tasks()
    
    # 2. Select project
    project = select_project(tasks)
    
    # 3. Generate code
    code = generate_improvement(project, path)
    
    # 4. Apply changes
    apply_improvement(project_path, code, iteration)
    
    # 5. Test
    if run_tests(project_path):
        # 6. Commit
        commit_changes(project, iteration)
        iteration += 1
    
    # 7. Sleep
    time.sleep(random.randint(20, 60))
```

### Project Selection Logic

```python
def select_project(tasks):
    projects = get_valid_projects()
    
    # Prefer IN_PROGRESS projects
    in_progress = [p for p in projects 
                   if tasks.get(p) == "IN_PROGRESS"]
    
    if in_progress:
        return random.choice(in_progress)
    
    return random.choice(projects)
```

### Backdated Commit Timeline

```
START: 2 years ago (Jan 2024)
↓
Iterate with natural spread
↓
Commit Date: START + (iteration_number * days) + random_hours
↓
Environment Variables:
  GIT_AUTHOR_DATE="2024-03-15 14:30:22"
  GIT_COMMITTER_DATE="2024-03-15 14:30:22"
↓
git commit ...
```

### Gemini Integration

```python
prompt = f"""
You are an autonomous Python coding agent.

Project: {project_name}
Structure:
{files_info}

Generate ONE small, safe improvement.
Return ONLY valid Python code.
"""

response = model.generate_content(prompt)
code = extract_python_from_response(response)
```

## Safety Mechanisms

### Path Validation

```python
def is_path_safe(path: str) -> bool:
    real_path = os.path.realpath(path)
    workspace = os.path.realpath(WORKSPACE)
    return real_path.startswith(workspace)
```

**Rules**:
- All file operations must be within `/workspace`
- Symbolic link attacks prevented by realpath()
- Parent directory traversal blocked

### Operation Constraints

```
✅ Allowed:
  • Read/write files in /workspace/projects/
  • Run pytest in project directories
  • Create improvement_*.py files
  • Make local git commits
  • Log to bot_log.md

❌ Prohibited:
  • Access files outside /workspace
  • Delete entire project folders
  • Push to remote repositories
  • Execute arbitrary shell commands
  • Network calls (except Gemini API)
  • Infinite loops without breaks
```

### Error Handling

```python
# Timeouts
result = subprocess.run(cmd, timeout=30)

# Safe file operations
if is_path_safe(path):
    with open(path, 'w') as f:
        f.write(content)

# API failures
if model is None:
    code = get_fallback_code(project_path)

# Commit failures
try:
    commit_changes(project, iteration)
except Exception as e:
    log_action("ERROR", f"Commit failed: {e}")
```

## Extending the System

### Adding a New Project

1. **Create directory structure**:
```bash
mkdir -p projects/my_project
touch projects/my_project/__init__.py
touch projects/my_project/main.py
touch projects/my_project/test_main.py
touch projects/my_project/pytest.ini
```

2. **Create main module** (`main.py`):
```python
"""
My Project - Description
"""

class MyClass:
    """Main class."""
    
    def do_something(self):
        """Do something useful."""
        return "result"

def my_function(x):
    """Useful function."""
    return x * 2
```

3. **Create tests** (`test_main.py`):
```python
import pytest
from main import MyClass, my_function

def test_function():
    assert my_function(5) == 10

def test_class():
    obj = MyClass()
    assert obj.do_something() is not None
```

4. **Create pytest config** (`pytest.ini`):
```ini
[pytest]
testpaths = .
python_files = test_*.py
addopts = -v --tb=short
```

5. **Update TASKS.md**:
```markdown
## my_project
**Status:** PLANNED

Description of the project.

### Tasks:
- [ ] Initial setup
- [ ] Core functionality
- [ ] Testing
```

6. **Commit**:
```bash
git add projects/my_project/
git commit -m "feat: Add my_project"
```

### Customizing Agent Behavior

Edit `src/agent.py`:

**Change API model**:
```python
model = genai.GenerativeModel("gemini-1.5-pro")  # or other model
```

**Modify code generation prompt**:
```python
prompt = f"""
Custom instructions for your specific use case.
Project: {project_name}
...
"""
```

**Adjust timing**:
```python
SLEEP_MIN = 10  # Minimum sleep seconds
SLEEP_MAX = 30  # Maximum sleep seconds
time.sleep(random.randint(SLEEP_MIN, SLEEP_MAX))
```

**Change backdate timeline**:
```python
START_DATE = datetime.now() - timedelta(days=365)  # 1 year instead of 2
```

**Add new safety checks**:
```python
def additional_validation(path: str) -> bool:
    # Custom validation logic
    return True
```

## Troubleshooting

### Agent Won't Start

**Problem**: ModuleNotFoundError for dependencies

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
python src/agent.py
```

### No Projects Found

**Problem**: Agent says "No projects available"

**Check**:
```bash
ls -la projects/
# Ensure directories exist and are readable

# Check TASKS.md exists
cat TASKS.md
```

### Tests Failing

**Problem**: "TEST_FAIL - /workspace/projects/..."

**Debug**:
```bash
cd projects/project_name
python -m pytest -v  # See actual error
```

**Common issues**:
- Missing imports: Add to `__init__.py`
- Wrong working directory: Check pytest.ini
- Relative paths: Use absolute paths

### Git Commits Not Appearing

**Problem**: Commits not showing in git log

**Check**:
```bash
git log --oneline --all
git log --oneline --decorate
git show <commit_sha>
```

**Verify config**:
```bash
git config user.email
git config user.name
git config core.excludesfile
```

### Gemini API Errors

**Problem**: "Gemini generation failed"

**Solutions**:
1. Check API key: `echo $GEMINI_API_KEY`
2. Check quota: Visit Google Cloud Console
3. Check rate limits: Wait and retry
4. Fallback code will generate anyway

### Docker Container Issues

**Problem**: Container exits immediately

**Debug**:
```bash
docker logs openclaw-agent
docker run -it --name test openclaw:latest /bin/bash
```

**Check mounts**:
```bash
docker run -it -v $(pwd):/workspace openclaw:latest ls /workspace
```

## Performance Tips

1. **Reduce sleep time**: Faster iteration (but uses more API quota)
2. **Batch improvements**: Modify agent to make multiple changes per commit
3. **Parallel projects**: Run multiple agents with different projects
4. **Cache Gemini responses**: Reuse similar prompts

## Monitoring

Check agent activity:

```bash
# Real-time logs
tail -f bot_log.md

# Git history
git log --oneline --graph

# Project status
cat TASKS.md

# Test health
for d in projects/*/; do
  cd "$d"
  python -m pytest -q
  cd - > /dev/null
done
```

## Next Steps

1. ✅ Set up development environment
2. ✅ Run tests on all projects
3. ✅ Read TASKS.md for current status
4. ✅ Start agent: `python src/agent.py`
5. ✅ Monitor: `tail -f bot_log.md`
6. ✅ Extend: Add new projects as needed

---

**Questions?** Check the README.md for overview or examine agent.py for implementation details.
