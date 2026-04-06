# 🚀 Quick Start Guide - OpenClaw Agentic System

This guide will get you up and running with the new agentic system in 5 minutes.

## What Changed?

### The Problem
Your OpenClaw agent was making **useless commits** that looked AI-generated:
- ❌ Commits like: `[todo_app] auto: Fallback in-place update`
- ❌ Code changes: Adding dummy `openclaw_note_*()` functions
- ❌ No commit timing control
- ❌ All commits looked robotic

### The Solution
We built a **2-agent system** that creates **human-like commits**:
- ✅ Natural messages: `Add type hints to models`, `Fix validation bug`
- ✅ Real improvements: Type hints, docs, validation, error handling
- ✅ **4-10 commits per day** (configurable)
- ✅ Only commits during work hours (8 AM - 10 PM)
- ✅ Quality monitoring and auto-correction

## Architecture

```
Supervisor Agent                    OpenClaw Agent
       │                                   │
       │  1. Monitors commit quality       │
       │  2. Manages daily cadence         │
       │  3. Queues improvement tasks ────>│
       │                                   │
       │  4. Generates code changes        │
       │  5. Runs tests                    │
       │  6. Makes human-like commits      │
       │                                   │
       └────<─── Reports back ─────────────┘
```

## Installation

### 1. Check Requirements

```bash
# You need Python 3.8+
python3 --version

# And git
git --version
```

### 2. Install Dependencies

```bash
cd /home/kunalsiyag/Desktop/automation

# Activate virtual environment (or create if missing)
source venv/bin/activate

# Install requirements
pip install -r src/requirements.txt
```

### 3. Configure API Key

Make sure your `.env` file has the Gemini API key:

```bash
# Check it exists
grep GEMINI_API_KEY .env

# If not, add it
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

## Usage

### Start the System

```bash
./agentic_system.sh start
```

This starts **both** agents (OpenClaw + Supervisor).

Expected output:
```
[INFO] Starting OpenClaw Agentic System...
[SUCCESS] OpenClaw started (PID: 12345)
[SUCCESS] Supervisor started (PID: 12346)

=== OpenClaw Agentic System Status ===

OpenClaw:   ● Running (PID: 12345)
Supervisor: ● Running (PID: 12346)

Commits today: 0

[SUCCESS] System started successfully!
```

### Check Status

```bash
./agentic_system.sh status
```

Shows:
- Are agents running?
- How many commits today?

### View Logs

```bash
# Last 50 lines
./agentic_system.sh logs

# Last 100 lines
./agentic_system.sh logs 100

# Follow logs in real-time
tail -f bot_log.md
tail -f supervisor_log.md
```

### Stop the System

```bash
./agentic_system.sh stop
```

## What to Expect

### First Hour
The supervisor will:
1. Set a daily target (e.g., 7 commits)
2. Calculate timing to spread commits naturally
3. Queue improvement tasks for OpenClaw
4. Monitor quality of commits made

### Throughout the Day
You'll see commits like:
```bash
$ git log --oneline -10
a7f3b2e Add type hints to models
9c4e1a3 Improve documentation in analyzer  
5d2f8b1 Fix validation bug
2a9c7e4 Add logging to scraper
1e5d3c2 Refactor explainer for clarity
```

**NOT** like this anymore:
```bash
746f04a [code_explainer] auto: Fallback in-place update  ❌
15506ba [todo_app] auto: Fallback in-place update        ❌
```

### Commit Patterns
- **Timing**: Spread across 8 AM - 10 PM
- **Quantity**: 4-10 commits per day
- **Quality**: Real code improvements
- **Messages**: Human-like, varied, descriptive

## Configuration

### Change Daily Commit Range

Edit `src/supervisor.py`:

```python
MIN_COMMITS_PER_DAY = 4    # Change to your min
MAX_COMMITS_PER_DAY = 10   # Change to your max
```

### Change Work Hours

Edit `src/supervisor.py`:

```python
WORK_HOURS_START = 8    # Start hour (24h format)
WORK_HOURS_END = 22     # End hour (24h format)
```

### Change Sleep Intervals

Edit `.env`:

```bash
OPENCLAW_MIN_SLEEP=20   # Min seconds between iterations
OPENCLAW_MAX_SLEEP=60   # Max seconds between iterations
```

## Monitoring

### Check Recent Commits

```bash
# Last 20 commits
git log --oneline -20

# Commits today
git log --since="today" --oneline

# Commits this week
git log --since="1 week ago" --pretty=format:"%h %ad %s" --date=short
```

### Check Supervisor Decisions

```bash
tail -f supervisor_log.md
```

Look for:
- `Triggering commit for <project>` - When it queues work
- `Commit quality: 0.85` - Quality scores
- `Intervention needed: quality` - When it corrects issues
- `New daily target: 7 commits` - Daily goals

### Check OpenClaw Activity

```bash
tail -f bot_log.md
```

Look for:
- `SELECT - Working on <project>` - Project selection
- `EDIT - Updated <file>` - File changes
- `TEST_PASS` - Tests succeeded
- `COMMIT` - Successful commit
- `TEST_FAIL` - Tests failed (automatic rollback)

## Troubleshooting

### "No commits are being made"

**Check 1**: Is it work hours?
```bash
date +%H
# Should be between 8-22
```

**Check 2**: Already hit daily max?
```bash
./agentic_system.sh status
# Shows "Commits today: X"
```

**Check 3**: Are agents running?
```bash
./agentic_system.sh status
# Both should show green ●
```

### "Quality is poor"

The supervisor automatically intervenes! Check logs:
```bash
tail -50 supervisor_log.md | grep -i intervention
```

If needed, restart for fresh start:
```bash
./agentic_system.sh restart
```

### "Agent not starting"

**Check Python**:
```bash
python3 --version
# Need 3.8+
```

**Check dependencies**:
```bash
source venv/bin/activate
pip install -r src/requirements.txt
```

**Check for errors**:
```bash
cat openclaw.out
cat supervisor.out
```

### "Tests keep failing"

**Validate projects**:
```bash
cd projects/todo_app
pytest -v
```

If tests fail, the agent auto-rolls back changes. This is normal!

## Advanced Usage

### Manual Control

Start/stop agents independently:

```bash
# Start only OpenClaw
./agentic_system.sh start-openclaw

# Start only Supervisor  
./agentic_system.sh start-supervisor

# Stop specific agent
./agentic_system.sh stop-openclaw
./agentic_system.sh stop-supervisor
```

### Force Commits

Queue a specific task via the CLI (if API is running):

```bash
python3 openclaw-cli.py task todo_app "Add better validation"
```

### Adjust Quality Threshold

Edit `src/supervisor.py`:

```python
MIN_QUALITY_SCORE = 0.6      # Lower = more lenient
MAX_FALLBACK_STREAK = 2      # Max consecutive fallbacks
```

## Files Overview

```
automation/
├── agentic_system.sh        ← Main control script (NEW)
├── src/
│   ├── agent.py             ← OpenClaw (enhanced with human-like commits)
│   ├── supervisor.py        ← Supervisor agent (NEW)
│   └── requirements.txt
├── bot_log.md               ← OpenClaw activity log
├── supervisor_log.md        ← Supervisor decisions (NEW)
├── AGENTIC_SYSTEM.md        ← Full documentation (NEW)
└── QUICKSTART.md            ← This file (NEW)
```

## Next Steps

1. **Start the system**: `./agentic_system.sh start`
2. **Let it run for an hour**: Go grab coffee ☕
3. **Check commits**: `git log --oneline -10`
4. **Monitor quality**: `./agentic_system.sh logs`
5. **Adjust settings**: Edit `src/supervisor.py` if needed

## Summary

### Before
- Useless fallback commits
- AI-looking messages
- No timing control
- No quality management

### After  
- Real code improvements
- Human-like commit messages
- 4-10 commits/day during work hours
- Automatic quality monitoring
- Supervisor ensures standards

## Help

For detailed documentation, see:
- **AGENTIC_SYSTEM.md** - Full system documentation
- **README.md** - Original OpenClaw docs
- **COPILOT_SUPERVISION.md** - Manual supervision guide

---

**Questions?** Check the logs:
```bash
./agentic_system.sh logs 100
```

**Problems?** Restart:
```bash
./agentic_system.sh restart
```

**Success!** Check your commits:
```bash
git log --oneline -20
```

🎉 **Enjoy your human-like autonomous development system!**
