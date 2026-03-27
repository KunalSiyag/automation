# 🎮 OpenClaw Control Demo - Interactive Guide

This guide walks you through commanding your OpenClaw agent step-by-step.

---

## Prerequisites

✅ Docker container running: `openclaw-agent`  
✅ API responding on port 18789  
✅ Python 3 installed on your machine

---

## 🎬 Demo Session

### Step 1: Verify Agent is Running

```bash
python3 openclaw-cli.py status
```

Expected output:
```json
{
  "service": "OpenClaw Agent API",
  "status": "ok",
  "timestamp": "2026-03-27T18:23:44.655181"
}
```

---

### Step 2: List Available Projects

```bash
python3 openclaw-cli.py projects
```

Output shows your 4 projects:
- `code_explainer` - Python code analysis tool
- `data_analyzer` - Data processing library
- `todo_app` - Task management application
- `web_scraper` - Web scraping utilities

---

### Step 3: Inspect a Project

Get details about the `todo_app` project:

```bash
python3 openclaw-cli.py project todo_app
```

Output shows:
- All files in the project
- Whether files are tests or code
- Whether improvements have been generated
- Line counts for each file

---

### Step 4: View a File

See the main code file:

```bash
python3 openclaw-cli.py file todo_app models.py
```

Or check the test file:

```bash
python3 openclaw-cli.py file todo_app test_models.py
```

---

### Step 5: Configure API Key (CRITICAL!)

To enable real AI-powered code generation:

```bash
# Get your free Gemini API key from:
# https://makersuite.google.com

python3 openclaw-cli.py set-key YOUR_GEMINI_API_KEY_HERE
```

---

### Step 6: Restart Agent to Apply API Key

```bash
docker restart openclaw-agent
```

Wait 10 seconds for container to restart.

---

### Step 7: Verify API Key is Set

```bash
python3 openclaw-cli.py stats
```

Look for `"has_gemini_key": true` in the output.

---

### Step 8: Queue a Build

Tell the agent to develop the `todo_app` project:

```bash
python3 openclaw-cli.py build todo_app --priority high
```

Response:
```
✅ Build queued for todo_app
```

---

### Step 9: Check Build Queue

See what commands are queued:

```bash
python3 openclaw-cli.py queue
```

Output shows your pending build request:
```json
{
  "pending": 1,
  "queue": [
    {
      "request": ".build_todo_app",
      "data": {
        "project": "todo_app",
        "priority": "high",
        "requested_at": "2026-03-27T18:23:44.655181"
      }
    }
  ]
}
```

---

### Step 10: Monitor Agent Progress

Watch what the agent is doing:

```bash
python3 openclaw-cli.py logs --limit 20
```

You'll see entries like:
```
[COMMAND] Received build signal
[SELECT] Working on project: todo_app
[EXEC] Processing build command for todo_app
```

---

### Step 11: Request a Specific Feature

Ask the agent to add a feature:

```bash
python3 openclaw-cli.py feature data_analyzer "Add CSV export support" \
  --description "Export analysis results to CSV files"
```

Response:
```
✅ Feature 'Add CSV export support' queued for data_analyzer
```

---

### Step 12: Check Queue Again

```bash
python3 openclaw-cli.py queue
```

Now shows both the build and feature requests pending.

---

### Step 13: Assign a Task

Request that a task be worked on:

```bash
python3 openclaw-cli.py task web_scraper "Add proxy support" --priority high
```

---

### Step 14: View Agent Statistics

```bash
python3 openclaw-cli.py stats
```

Shows:
- Total lines logged
- Number of projects
- Whether Gemini API is configured

---

### Step 15: Check Project Results

After the agent processes commands, check what was generated:

```bash
python3 openclaw-cli.py project todo_app
```

Look for `improvement_NNN.py` files - these are the generated improvements!

---

### Step 16: View Generated Code

See what the agent generated:

```bash
python3 openclaw-cli.py file todo_app improvement_000.py
```

This shows the AI-generated code for the improvement.

---

### Step 17: Monitor Continuously

Watch the agent work in real-time:

```bash
watch -n 5 "python3 openclaw-cli.py logs --limit 10"
```

Press Ctrl+C to stop watching.

---

### Step 18: Get All Statistics

```bash
python3 openclaw-cli.py stats
python3 openclaw-cli.py projects
python3 openclaw-cli.py info
```

---

## 🔄 Full Development Cycle

### Scenario: Develop Multiple Projects

```bash
# 1. Set API key (if not done already)
python3 openclaw-cli.py set-key YOUR_GEMINI_API_KEY

# 2. Queue builds on all projects
python3 openclaw-cli.py build code_explainer --priority high
python3 openclaw-cli.py build data_analyzer --priority high
python3 openclaw-cli.py build todo_app --priority high
python3 openclaw-cli.py build web_scraper --priority high

# 3. Request features for each
python3 openclaw-cli.py feature code_explainer "Add type hints"
python3 openclaw-cli.py feature data_analyzer "Add plotting"
python3 openclaw-cli.py feature todo_app "Add authentication"
python3 openclaw-cli.py feature web_scraper "Add error handling"

# 4. Monitor progress
python3 openclaw-cli.py logs --limit 30

# 5. Check queue status
python3 openclaw-cli.py queue

# 6. Wait and check results
python3 openclaw-cli.py stats
python3 openclaw-cli.py project todo_app

# 7. View generated code
python3 openclaw-cli.py file todo_app improvement_000.py
```

---

## 🐍 Python Integration Example

Use the CLI from Python scripts:

```python
from openclaw_cli import OpenClawCLI

# Initialize
cli = OpenClawCLI("http://localhost", 18789)

# Get projects
projects = cli.list_projects()
print(f"Found {projects['count']} projects")

# Queue builds
for project in projects['projects']:
    result = cli.force_build(project['name'])
    print(f"Queued: {project['name']}")

# Check results
for project in projects['projects']:
    details = cli.project_details(project['name'])
    print(f"{project['name']}: {details['file_count']} files")
```

---

## 🎯 Advanced: Remote Access

Access your agent from a different machine:

```bash
# On remote machine
python3 openclaw-cli.py --host http://your-server-ip --port 18789 status

# Or use SSH tunnel
ssh -L 18789:localhost:18789 user@your-server

# Then use local CLI
python3 openclaw-cli.py status
```

---

## 🛠️ Troubleshooting

### API not responding
```bash
# Check container status
docker ps | grep openclaw

# View container logs
docker logs openclaw-agent

# Restart
docker restart openclaw-agent
```

### Agent not processing commands
```bash
# Check build queue
python3 openclaw-cli.py queue

# View logs
python3 openclaw-cli.py logs --limit 50

# Verify API key is set
python3 openclaw-cli.py stats
```

### No improvements being generated
```bash
# Likely missing Gemini API key
# Check:
python3 openclaw-cli.py stats
# Look for "has_gemini_key": true

# If false, set it:
python3 openclaw-cli.py set-key YOUR_KEY
docker restart openclaw-agent
```

---

## 🚀 Next Steps

1. **Run the demo:**
   ```bash
   python3 openclaw-cli.py status
   python3 openclaw-cli.py projects
   ```

2. **Set API key:**
   ```bash
   python3 openclaw-cli.py set-key YOUR_GEMINI_API_KEY
   docker restart openclaw-agent
   ```

3. **Command the agent:**
   ```bash
   python3 openclaw-cli.py build todo_app --priority high
   python3 openclaw-cli.py feature data_analyzer "Add new feature"
   ```

4. **Monitor progress:**
   ```bash
   python3 openclaw-cli.py logs --limit 50
   python3 openclaw-cli.py queue
   ```

5. **Check results:**
   ```bash
   python3 openclaw-cli.py project todo_app
   python3 openclaw-cli.py file todo_app improvement_000.py
   ```

---

**🎉 You now have a fully controllable AI coding agent!**

For more details, see COMMANDS.md and CONTROL_GUIDE.md
