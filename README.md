# 🦾 OpenClaw - Autonomous AI Coding Agent

An intelligent autonomous agent that continuously develops and improves multiple mini-projects using Google Gemini AI. The agent runs inside a containerized environment with strict safety constraints, making local git commits with backdated timestamps.

## 🎯 Overview

OpenClaw is a proof-of-concept autonomous development system that:

- **Autonomous Development**: Continuously selects projects and generates improvements using AI
- **Sandboxed Execution**: Runs inside Docker with access only to `/workspace`
- **Test-Driven**: Validates all changes with pytest before committing
- **Version Controlled**: Makes local git commits with natural backdated timestamps
- **Safe & Constrained**: Respects strict boundaries and safety rules

For a Copilot-supervised workflow, see `COPILOT_SUPERVISION.md`.

## 📁 Project Structure

```
automation/
├── bot/
│   ├── agent.py          # Main autonomous agent
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Container configuration
├── projects/
│   ├── todo_app/         # Task management application
│   ├── data_analyzer/    # Data analysis utilities
│   ├── web_scraper/      # Web scraping tools
│   └── code_explainer/   # AI code explanation utility
├── TASKS.md              # Project tracking and status
├── bot_log.md            # Agent activity log
└── .gitignore
```

## 🏗️ Sample Projects

### 1. **todo_app** - Task Management System
A complete task manager with CRUD operations.

**Features:**
- Task creation with priority levels
- Status tracking (TODO, IN_PROGRESS, DONE)
- Task filtering and querying
- Complete test suite (10 tests)

**Files:**
- `models.py` - Task and TaskManager classes
- `test_models.py` - Comprehensive unit tests

### 2. **data_analyzer** - Data Analysis Tool
Load, analyze, and export data from CSV/JSON.

**Features:**
- JSON and CSV file loading
- Data filtering and column operations
- Statistical analysis (min, max, mean, median)
- Data export functionality
- Complete test suite (10 tests)

**Files:**
- `analyzer.py` - DataLoader and DataAnalyzer classes
- `test_analyzer.py` - File I/O and analysis tests

### 3. **web_scraper** - Web Scraping Utilities
Safe web scraping with rate limiting and validation.

**Features:**
- URL validation and normalization
- HTML parsing (links, headings, images, text)
- Rate limiting and visited tracking
- Safe extraction utilities
- Complete test suite (9 tests)

**Files:**
- `scraper.py` - URLValidator, HTMLParser, Scraper classes
- `test_scraper.py` - URL and HTML parsing tests

### 4. **code_explainer** - AI Code Analysis
Analyze and explain Python code structure.

**Features:**
- Code parsing with AST
- Extract functions, classes, imports
- Complexity metrics calculation
- Docstring extraction
- Markdown code formatting
- Complete test suite (9 tests)

**Files:**
- `explainer.py` - CodeParser, CodeFormatter, CodeSummary classes
- `test_explainer.py` - Code analysis tests

## 🚀 Quick Start

### Running Locally (without Docker)

1. **Clone and Setup:**
```bash
cd automation
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
```

2. **Configure Gemini API:**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

3. **Run the Agent:**
```bash
python bot/agent.py
```

### Running with Docker

1. **Build the Image:**
```bash
docker build -f bot/Dockerfile -t openclaw:latest .
```

2. **Run the Container:**
```bash
docker run -it \
  -v $(pwd):/workspace \
  -e GEMINI_API_KEY="your-gemini-api-key" \
  openclaw:latest
```

The agent will mount the current directory as `/workspace` and work only within `/workspace/projects`.

### Supervised Container Mode (Recommended)

Use this when Copilot (or another supervisor) is monitoring logs and issuing commands:

```bash
# Start everything
./manage_openclaw.sh up

# Watch logs continuously
./manage_openclaw.sh logs 200

# Queue commands for the agent
./manage_openclaw.sh build todo_app
./manage_openclaw.sh feature todo_app "Add due date reminders" "Send reminders for overdue tasks"
./manage_openclaw.sh task todo_app "Improve validation around task creation"

# Inspect pending queue
./manage_openclaw.sh queue
```

This uses `docker-compose.yml` to run API + agent in one container and keeps processing queued build/feature/task requests automatically.

## ⚙️ Agent Architecture

### Main Loop
```python
1. Read TASKS.md for project status
2. Select a project (prefer IN_PROGRESS)
3. Generate improvement code using Gemini API
4. Apply changes to project
5. Run pytest in project directory
6. If tests pass: commit with backdated timestamp
7. If tests fail: log failure and continue
8. Sleep for random interval (20-60s)
9. Repeat
```

### Key Components

**Gemini Integration:**
- Model: `gemini-1.5-flash-latest`
- Generates small, safe code improvements
- Context-aware prompts with project structure

**Backdated Commits:**
- Start date: ~2 years ago
- Incremental progression over 720 days
- Natural distribution across the timeline
- Uses `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE`

**Safety Features:**
- All file operations validated against `/workspace`
- Never executes dangerous shell commands
- Never deletes entire project folders
- Respects 30-second operation timeouts
- Comprehensive error handling and logging

**Testing:**
- All projects use pytest
- Tests run before each commit
- Failed tests prevent commits
- Full test output in logs

## 🔒 Safety Constraints

### What the Agent Does
✅ Generate and apply safe code improvements
✅ Run tests and validate changes
✅ Make local git commits only (never push)
✅ Work within `/workspace/projects/`
✅ Log all activities to `bot_log.md`
✅ Use backdated timestamps for commits

### What the Agent Never Does
❌ Access files outside `/workspace`
❌ Delete entire project folders
❌ Push changes to remote repositories
❌ Execute arbitrary shell commands
❌ Modify files without testing first
❌ Create infinite loops or hang

## 📝 TASKS.md Format

Track project status and tasks:

```markdown
## project_name
**Status:** IN_PROGRESS | PLANNED | COMPLETED

Description of the project.

### Tasks:
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
```

The agent reads this file to prioritize IN_PROGRESS projects.

## 📊 Activity Logging

All agent activities are logged to `bot_log.md`:

```
[2026-03-27T20:15:30.123456] START - OpenClaw agent starting
[2026-03-27T20:15:35.456789] SELECT - Working on project: todo_app
[2026-03-27T20:15:40.789012] IMPROVEMENT - Applied to improvement_000.py
[2026-03-27T20:15:42.345678] TEST_PASS - /workspace/projects/todo_app
[2026-03-27T20:15:43.678901] COMMIT - todo_app @ 2024-03-27 14:30:15
[2026-03-27T20:15:44.901234] SLEEP - 45 seconds
```

## 🧪 Testing Projects

Run tests for any project:

```bash
cd projects/todo_app
pytest -v

cd ../data_analyzer
pytest -v

cd ../web_scraper
pytest -v

cd ../code_explainer
pytest -v
```

All projects pass their test suites and are production-ready.

## 📋 Dependencies

**Python 3.11+**
- `google-generativeai` - Gemini API integration
- `GitPython` - Git operations
- `pytest` - Testing framework

**System**
- git
- Python 3.11 slim (Docker)

## 🔑 Environment Variables

```bash
GEMINI_API_KEY    # Required for AI code generation
WORKSPACE         # Default: /workspace (Docker)
```

## 📈 Performance

- **Commits**: ~1 commit per 50-90 seconds (random)
- **Test Suite**: All projects run in <100ms
- **Memory**: ~150-200MB per execution
- **Timeline**: Spreads commits naturally over 2 years

## 🛠️ Extending OpenClaw

### Add a New Project

1. Create project directory in `projects/`
2. Add `__init__.py`, core modules, and tests
3. Create `pytest.ini` for configuration
4. Update `TASKS.md` with project status
5. Agent will automatically discover and work on it

### Customize Agent Behavior

Edit `bot/agent.py`:
- `START_DATE` - Adjust timeline
- `generate_improvement()` - Modify prompt
- `run_tests()` - Change test command
- Sleep intervals - Adjust timing

## 📚 Example Output

```
[2026-03-27T20:20:15.123456] START - OpenClaw agent starting
[2026-03-27T20:20:20.234567] SELECT - Working on project: data_analyzer
[2026-03-27T20:20:25.345678] IMPROVEMENT - Applied to improvement_001.py
[2026-03-27T20:20:27.456789] TEST_PASS - /workspace/projects/data_analyzer
[2026-03-27T20:20:28.567890] COMMIT - data_analyzer @ 2024-08-15 09:22:45
[2026-03-27T20:20:29.678901] SLEEP - 35 seconds
[2026-03-27T20:21:04.789012] SELECT - Working on project: code_explainer
[2026-03-27T20:21:09.890123] IMPROVEMENT - Applied to improvement_002.py
[2026-03-27T20:21:11.901234] TEST_PASS - /workspace/projects/code_explainer
[2026-03-27T20:21:12.012345] COMMIT - code_explainer @ 2024-12-03 16:45:22
```

## 🎓 Educational Value

OpenClaw demonstrates:
- Autonomous AI agent design
- Safety-conscious constraints
- Git workflow automation
- Docker containerization
- Test-driven development
- Multi-project management
- Error handling and logging
- Responsible AI practices

## ⚠️ Important Notes

1. **API Costs**: Uses Gemini API - monitor for costs
2. **Local Only**: Never configures remote repositories
3. **Testing Required**: No commits without passing tests
4. **Logs**: Check `bot_log.md` for activity
5. **Sandbox**: Strictly limited to `/workspace`

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Improvements welcome! Consider:
- Additional safety constraints
- More sophisticated code generation
- Better logging and monitoring
- Performance optimizations
- Additional sample projects

## 📧 Support

For questions or issues:
1. Check `bot_log.md` for error messages
2. Review `TASKS.md` for project status
3. Examine individual project test output
4. Check Gemini API quota and limits

---

**OpenClaw v0.1.0** - Autonomous AI Development at Scale
