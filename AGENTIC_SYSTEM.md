# 🤖 OpenClaw Agentic System

A sophisticated multi-agent system where a Supervisor agent monitors and orchestrates an OpenClaw coding agent to produce high-quality, human-like commits across multiple projects.

## 🎯 Overview

This system consists of two cooperating agents:

### 1. **OpenClaw Agent** (bot/agent.py)
- Autonomous coding agent that makes improvements to projects
- Generates meaningful code changes using Gemini AI
- Runs tests before committing
- Falls back to intelligent improvements if AI unavailable

### 2. **Supervisor Agent** (bot/supervisor.py)
- Monitors OpenClaw's performance and commit quality
- Manages daily commit cadence (4-10 commits/day)
- Distributes commits naturally across work hours (8 AM - 10 PM)
- Intervenes when quality drops or schedule falls behind
- Queues targeted improvement tasks for OpenClaw

## ✨ Key Features

### Human-Like Commits
- **Natural commit messages**: "Add type annotations to models", "Fix validation bug", etc.
- **No AI markers**: Removed patterns like "auto:", "[agent]", "Fallback update"
- **Variety**: Rotates through different commit styles and improvement types
- **Realistic timing**: Commits spread naturally throughout work hours

### Intelligent Fallback
When Gemini AI is unavailable, the system generates **real improvements**:
- Add type hints to functions
- Add/improve docstrings
- Add input validation
- Improve error handling
- Add logging statements

### Quality Control
- **Commit quality scoring**: Monitors each commit for human-like characteristics
- **Automatic intervention**: Triggers rebuilds when quality drops
- **Fallback streak detection**: Prevents too many fallback commits in a row
- **Test validation**: All commits must pass tests

### Natural Cadence Management
- **Daily targets**: 4-10 commits per day (randomized)
- **Work hours**: Only commits during 8 AM - 10 PM
- **Smart timing**: Distributes commits to meet daily target
- **Project rotation**: Naturally cycles through available projects

## 🚀 Quick Start

### 1. Start the System

```bash
./agentic_system.sh start
```

This starts both OpenClaw and the Supervisor.

### 2. Check Status

```bash
./agentic_system.sh status
```

Output shows:
- Whether agents are running
- Process IDs
- Commits made today

### 3. Monitor Logs

```bash
# View last 50 lines
./agentic_system.sh logs

# View last 100 lines
./agentic_system.sh logs 100
```

Two log files are maintained:
- `bot_log.md` - OpenClaw agent activity
- `supervisor_log.md` - Supervisor decisions and interventions

### 4. Stop the System

```bash
./agentic_system.sh stop
```

## 📋 Management Commands

```bash
./agentic_system.sh start            # Start both agents
./agentic_system.sh stop             # Stop both agents
./agentic_system.sh restart          # Restart the system
./agentic_system.sh status           # Check status
./agentic_system.sh logs [N]         # View logs

# Individual agent control
./agentic_system.sh start-openclaw   # Start only OpenClaw
./agentic_system.sh stop-openclaw    # Stop only OpenClaw
./agentic_system.sh start-supervisor # Start only Supervisor
./agentic_system.sh stop-supervisor  # Stop only Supervisor
```

## 🔧 Configuration

### Environment Variables

Set in `.env` file or environment:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
WORKSPACE=/workspace                    # Default: current directory
OPENCLAW_MIN_SLEEP=20                   # Min seconds between iterations
OPENCLAW_MAX_SLEEP=60                   # Max seconds between iterations
OPENCLAW_MAX_CONTEXT_FILE_CHARS=7000    # Max chars per context file
OPENCLAW_MAX_CONTEXT_FILES=3            # Max files in context
```

### Supervisor Settings

Edit `bot/supervisor.py`:

```python
MIN_COMMITS_PER_DAY = 4      # Minimum daily commits
MAX_COMMITS_PER_DAY = 10     # Maximum daily commits
WORK_HOURS_START = 8         # Start work hour (24h format)
WORK_HOURS_END = 22          # End work hour (24h format)
MIN_QUALITY_SCORE = 0.6      # Minimum acceptable commit quality
MAX_FALLBACK_STREAK = 2      # Max consecutive fallback commits
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│         Supervisor Agent                    │
│  - Monitors commit quality                  │
│  - Manages daily cadence (4-10/day)         │
│  - Queues commands for OpenClaw             │
│  - Intervenes on quality/schedule issues    │
└────────────┬────────────────────────────────┘
             │ Commands via .task_*.json files
             ↓
┌─────────────────────────────────────────────┐
│         OpenClaw Agent                      │
│  - Reads command queue                      │
│  - Generates code improvements              │
│  - Runs tests                               │
│  - Commits if tests pass                    │
└─────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│         Projects                            │
│  - todo_app/                                │
│  - data_analyzer/                           │
│  - web_scraper/                             │
│  - code_explainer/                          │
└─────────────────────────────────────────────┘
```

## 📊 How It Works

### OpenClaw Workflow

1. **Check for commands**: Reads `.task_*.json`, `.feature_*.json`, `.build_*.json` files
2. **Select project**: Chooses from TASKS.md or command queue
3. **Generate improvement**: 
   - Uses Gemini AI for intelligent edits
   - Falls back to deterministic improvements if AI unavailable
4. **Apply changes**: Edits project files directly
5. **Run tests**: Validates changes with pytest
6. **Commit**: If tests pass, commits with human-like message and backdated timestamp
7. **Sleep**: Random interval before next iteration

### Supervisor Workflow

1. **Monitor cadence**: Check if commit timing is appropriate
2. **Analyze quality**: Score recent commits for human-likeness
3. **Trigger commits**: Queue tasks when it's time for next commit
4. **Quality intervention**: Request rebuilds if quality drops
5. **Schedule intervention**: Queue additional tasks if behind target
6. **Sleep**: 3-7 minutes between supervision cycles

### Commit Message Generation

The system generates natural commit messages based on change type:

```python
Type hints → "Add type annotations to models"
Docstrings → "Update documentation for analyzer"
Validation → "Strengthen validation in scraper"
Error handling → "Better error handling in explainer"
Logging → "Add logging to models"
Features → "Implement task filtering"
Fixes → "Fix validation bug"
```

Occasionally adds casual touches:
- "- needs more testing"
- "- minor cleanup"
- "- quick fix"

## 🔍 Monitoring & Debugging

### Check Recent Commits

```bash
git log --oneline -20
```

Should show varied, descriptive messages without AI patterns.

### Check Commit Distribution

```bash
git log --since="1 week ago" --pretty=format:"%h %ad %s" --date=short
```

Should show 4-10 commits per day during work hours.

### View Supervisor Decisions

```bash
tail -f supervisor_log.md
```

Shows:
- When commits are triggered
- Quality scores
- Intervention decisions
- Project rotation

### View OpenClaw Activity

```bash
tail -f bot_log.md
```

Shows:
- Project selection
- Edit generation
- Test results
- Commit success/failure

## 🎯 Quality Metrics

The system tracks several quality indicators:

### Commit Quality Score (0-1)
- **1.0**: Perfect human-like commit
- **0.8-0.9**: Good quality
- **0.6-0.7**: Acceptable (threshold)
- **<0.6**: Poor quality (triggers intervention)

Factors:
- ✅ Specific, descriptive messages (+0.2)
- ✅ Multiple files changed (+0.1)
- ❌ Generic terms like "update", "change" (-0.1)
- ❌ AI patterns like "auto:", "generated" (-0.3)
- ❌ "Fallback" in message (-0.4)

### Intervention Triggers

**Quality Issues:**
- 2+ consecutive fallback commits
- Average quality < 0.6

**Schedule Issues:**
- Less than 70% of expected commits by current time

## 📝 Example Session

```bash
# Start system
$ ./agentic_system.sh start
[INFO] Starting OpenClaw Agentic System...
[SUCCESS] OpenClaw started (PID: 12345)
[SUCCESS] Supervisor started (PID: 12346)

=== OpenClaw Agentic System Status ===

OpenClaw:   ● Running (PID: 12345)
Supervisor: ● Running (PID: 12346)

Commits today: 3

[SUCCESS] System started successfully!

# Check logs after a while
$ ./agentic_system.sh logs
[2026-03-31T18:30:00] SUPERVISOR: New daily target: 7 commits
[2026-03-31T18:33:15] SUPERVISOR: Triggering commit for todo_app
[2026-03-31T18:33:15] SUPERVISOR: Queued task command for todo_app
[2026-03-31T18:35:42] SELECT - Working on todo_app
[2026-03-31T18:35:45] EDIT - Updated models.py
[2026-03-31T18:35:47] TEST_PASS - /workspace/projects/todo_app
[2026-03-31T18:35:48] COMMIT - todo_app @ 2024-05-15 14:22:10
[2026-03-31T18:40:00] SUPERVISOR: Commit quality: 0.85 - 'Add type hints to models'
[2026-03-31T18:40:00] SUPERVISOR: Commit recorded: 4/7 today

# Check git history
$ git log --oneline -5
a7f3b2e Add type hints to models
9c4e1a3 Improve documentation in analyzer
5d2f8b1 Fix validation bug
2a9c7e4 Add logging to scraper
1e5d3c2 Refactor explainer for clarity
```

## 🛡️ Safety Features

- ✅ All file operations validated against workspace
- ✅ Never deletes entire project folders
- ✅ Tests must pass before committing
- ✅ Automatic rollback on test failure
- ✅ Respects timeout limits
- ✅ Comprehensive error handling and logging
- ✅ No remote pushes (local only)

## 🔧 Troubleshooting

### System Not Starting

```bash
# Check Python installation
python3 --version

# Check virtual environment
ls -la venv/

# Recreate venv if needed
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
```

### No Commits Being Made

1. Check Gemini API key: `grep GEMINI_API_KEY .env`
2. Check work hours: System only commits 8 AM - 10 PM
3. Check daily limit: May have reached max (10 commits/day)
4. Check supervisor logs: `tail -50 supervisor_log.md`

### Low Quality Commits

1. Check if Gemini is working: Look for "ERROR" in bot_log.md
2. Verify API key is valid
3. Check if in fallback mode too often
4. Supervisor should automatically intervene

### Tests Failing

1. Check test output in bot_log.md
2. Verify project test suites work: `cd projects/todo_app && pytest -v`
3. Check Python path configuration
4. Review recent edits that broke tests

## 📚 Files & Directories

```
automation/
├── bot/
│   ├── agent.py              # OpenClaw agent (enhanced)
│   ├── supervisor.py         # Supervisor agent (new)
│   ├── api.py                # API server (optional)
│   └── requirements.txt      # Python dependencies
├── projects/                 # Your projects
│   ├── todo_app/
│   ├── data_analyzer/
│   ├── web_scraper/
│   └── code_explainer/
├── agentic_system.sh        # Management script (new)
├── bot_log.md               # OpenClaw logs
├── supervisor_log.md        # Supervisor logs (new)
├── TASKS.md                 # Project tracking
├── .openclaw.pid            # OpenClaw process ID
├── .supervisor.pid          # Supervisor process ID
└── .env                     # Configuration
```

## 🎓 Key Improvements

### From Original System

**Before:**
- ❌ Fallback commits added useless `openclaw_note_*()` functions
- ❌ Generic messages: "auto: Fallback in-place update"
- ❌ No commit cadence management
- ❌ Ran continuously without schedule
- ❌ No quality monitoring

**After:**
- ✅ Fallback generates real improvements (type hints, docs, validation)
- ✅ Human-like messages: "Add type hints to models"
- ✅ 4-10 commits/day distributed naturally
- ✅ Only works during 8 AM - 10 PM
- ✅ Supervisor monitors and ensures quality

## 🤝 Usage Tips

1. **Let it run**: The system is designed for autonomous operation
2. **Check daily**: Use `./agentic_system.sh status` once per day
3. **Monitor quality**: Occasional `logs` check to see commit quality
4. **Git history**: Verify commits look human with `git log`
5. **Adjust targets**: Modify MIN/MAX_COMMITS_PER_DAY in supervisor.py
6. **Work hours**: Adjust WORK_HOURS_START/END to your preference

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

**OpenClaw Agentic System v2.0** - Autonomous, Human-Like Development at Scale
