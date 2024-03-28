# 🎮 OpenClaw Control Guide - Full Command System

**Now you can fully command your autonomous AI coding agent!**

---

## What Changed

Previously, OpenClaw was running but you couldn't command it. Now:

✅ **Command API (api_v2.py)** - Send commands to control what the agent builds  
✅ **CLI Tool (openclaw-cli.py)** - Command-line interface for easy access  
✅ **Control Signals** - Agent watches for `.build_*` and `.feature_*` files  
✅ **Queue System** - Track what commands are pending  

---

## 🚀 Getting Started

### 1. Check Agent Status

```bash
python3 openclaw-cli.py status
```

Output:
```json
{
  "service": "OpenClaw Agent API",
  "status": "ok",
  "timestamp": "2026-03-27T18:21:18.301765"
}
```

### 2. List Available Projects

```bash
python3 openclaw-cli.py projects
```

Output:
```json
{
  "count": 4,
  "projects": [
    {"name": "code_explainer", "tests": 9},
    {"name": "data_analyzer", "tests": 10},
    {"name": "todo_app", "tests": 10},
    {"name": "web_scraper", "tests": 9}
  ]
}
```

### 3. **IMPORTANT: Set Gemini API Key for Real Code Generation**

```bash
python3 openclaw-cli.py set-key YOUR_GEMINI_API_KEY_HERE
```

Then restart the container:
```bash
docker restart openclaw-agent
```

**Without this, the agent runs in demo mode (fallback code only).**

### 4. Command the Agent to Build

```bash
python3 openclaw-cli.py build todo_app --priority high
```

Response:
```
✅ Build queued for todo_app
```

### 5. Request Specific Features

```bash
python3 openclaw-cli.py feature todo_app "Add email notifications" \
  --description "Send email alerts when tasks are due"
```

Response:
```
✅ Feature 'Add email notifications' queued for todo_app
```

### 6. Check Build Queue

```bash
python3 openclaw-cli.py queue
```

This shows all pending commands the agent will process.

### 7. View Agent Logs

```bash
python3 openclaw-cli.py logs --limit 30
```

Watch what the agent is doing in real-time.

---

## 🎯 Complete Command Reference

### Monitoring Commands

```bash
# Check API health
python3 openclaw-cli.py status

# Get service info
python3 openclaw-cli.py info

# List all projects
python3 openclaw-cli.py projects

# Get project details
python3 openclaw-cli.py project todo_app

# Get file content
python3 openclaw-cli.py file todo_app models.py

# View statistics
python3 openclaw-cli.py stats

# View logs (last 20 lines)
python3 openclaw-cli.py logs

# View more logs
python3 openclaw-cli.py logs --limit 50

# Check build queue
python3 openclaw-cli.py queue
```

### Control Commands

```bash
# Force build a project
python3 openclaw-cli.py build todo_app
python3 openclaw-cli.py build todo_app --priority high

# Request feature generation
python3 openclaw-cli.py feature todo_app "Add authentication"
python3 openclaw-cli.py feature todo_app "Add API endpoint" \
  --description "REST endpoint for task creation"

# Assign a task
python3 openclaw-cli.py task todo_app "Add database persistence"
python3 openclaw-cli.py task todo_app "Optimize queries" --priority high

# Configure Gemini API key
python3 openclaw-cli.py set-key YOUR_API_KEY_HERE

# Clear improvement files
python3 openclaw-cli.py clear-cache

# Restart agent
python3 openclaw-cli.py restart
```

---

## 💻 Direct HTTP Requests (cURL)

If you prefer curl over the CLI:

### Force Build

```bash
curl -X POST http://localhost:18789/api/control/force-build \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "priority": "high"
  }'
```

### Request Feature

```bash
curl -X POST http://localhost:18789/api/control/generate-feature \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "feature": "Add notifications",
    "description": "Email and SMS alerts"
  }'
```

### Assign Task

```bash
curl -X POST http://localhost:18789/api/control/assign-task \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "task": "Add database persistence",
    "priority": "medium"
  }'
```

### Set API Key

```bash
curl -X POST http://localhost:18789/api/control/set-api-key \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_GEMINI_API_KEY_HERE"
  }'
```

### Get Project Details

```bash
curl http://localhost:18789/api/query/project-details/todo_app
```

### Get File Content

```bash
curl http://localhost:18789/api/query/file-content/todo_app/models.py
```

---

## 🔄 How It Works

1. **You send command** → CLI or HTTP request
2. **API creates signal file** → `.build_*` or `.feature_*` in /workspace
3. **Agent detects signal** → Checks for commands every iteration
4. **Agent processes command** → Generates code for requested project/feature
5. **Tests validate changes** → Runs pytest
6. **Successful changes committed** → Git commit with backdated timestamp
7. **Logs updated** → All actions logged to bot_log.md

---

## 🎯 Workflow Example

### Setup (One-Time)

```bash
# 1. Get Gemini API key from https://makersuite.google.com
# 2. Set it in OpenClaw
python3 openclaw-cli.py set-key YOUR_API_KEY

# 3. Restart agent to enable real code generation
docker restart openclaw-agent

# 4. Verify
python3 openclaw-cli.py stats
# Should show "has_gemini_key": true
```

### Development Workflow

```bash
# 1. Queue builds on all projects
python3 openclaw-cli.py build code_explainer --priority high
python3 openclaw-cli.py build data_analyzer --priority high
python3 openclaw-cli.py build todo_app --priority high
python3 openclaw-cli.py build web_scraper --priority high

# 2. Request specific features
python3 openclaw-cli.py feature data_analyzer "Add visualization support"
python3 openclaw-cli.py feature todo_app "Add recurring tasks"
python3 openclaw-cli.py feature web_scraper "Add rate limiting"

# 3. Monitor progress
python3 openclaw-cli.py logs --limit 20

# 4. Check statistics
python3 openclaw-cli.py stats

# 5. View project details
python3 openclaw-cli.py project data_analyzer
```

---

## 📊 Understanding Agent Behavior

### Demo Mode (No API Key)
- Agent uses fallback code templates
- Tests fail (by design - fallback code is minimal)
- No commits are made
- Good for testing the system

### Production Mode (With API Key)
- Agent uses Google Gemini to generate real code
- Generated code is tested with pytest
- If tests pass → code is committed with backdated timestamp
- If tests fail → code is rejected, agent tries next project
- All activity logged to bot_log.md

### Command Processing
- Agent checks for commands at the start of each iteration
- Commands are processed and removed
- Commands trigger immediate project selection
- Agent prioritizes commanded projects over regular rotation

---

## 🔍 Monitoring Tips

### Watch Agent in Real-Time

```bash
# Continuously show latest logs
watch -n 5 "python3 openclaw-cli.py logs --limit 10"
```

### Monitor Project Development

```bash
# Check what's happening with todo_app
python3 openclaw-cli.py project todo_app

# View its test file
python3 openclaw-cli.py file todo_app test_models.py

# Inspect current source file
python3 openclaw-cli.py file todo_app models.py
```

### Track Statistics

```bash
# Show project count, API key status
python3 openclaw-cli.py stats

# Queue status
python3 openclaw-cli.py queue
```

---

## ⚠️ Important Notes

### Gemini API Key
- **Required for real development** - Without it, agent uses fallback templates
- Get one free at: https://makersuite.google.com
- Stored in /workspace/.env file
- Must restart container after setting

### Docker Container
```bash
# View logs
docker logs openclaw-agent

# Restart
docker restart openclaw-agent

# Stop
docker stop openclaw-agent

# Remove and restart
docker stop openclaw-agent
docker rm openclaw-agent
docker run -d -p 18789:18789 \
  -e GEMINI_API_KEY="your-key" \
  -v $(pwd):/workspace \
  openclaw:latest
```

### Port Forwarding
For external access:
```bash
# SSH tunnel
ssh -L 18789:localhost:18789 user@remote-server

# Then use CLI
python3 openclaw-cli.py --host http://localhost projects
```

---

## 🚀 Next Steps

1. **Enable Real Code Generation**
   ```bash
   python3 openclaw-cli.py set-key YOUR_GEMINI_API_KEY
   docker restart openclaw-agent
   ```

2. **Queue Builds**
   ```bash
   python3 openclaw-cli.py build todo_app --priority high
   ```

3. **Request Features**
   ```bash
   python3 openclaw-cli.py feature data_analyzer "Add CSV export"
   ```

4. **Monitor Progress**
   ```bash
   python3 openclaw-cli.py logs --limit 30
   ```

5. **Check Results**
   ```bash
   python3 openclaw-cli.py project todo_app
   python3 openclaw-cli.py stats
   ```

---

## ✨ Key Differences from Before

| Before | Now |
|--------|-----|
| Read-only monitoring | Full command control |
| Can't tell agent what to build | Queue builds and features |
| No way to set API key | CLI command to set API key |
| Can't see build queue | `queue` command shows pending |
| Limited project info | Full project details with files |

---

**🎉 You now have full control over your autonomous AI coding agent!**

Start commanding it: `python3 openclaw-cli.py --help`
