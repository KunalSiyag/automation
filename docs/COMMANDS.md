# 🦾 OpenClaw CLI - Command Reference

Complete guide to commanding your autonomous AI coding agent via REST API.

---

## 🚀 Quick Start

### Python CLI

```bash
# Make executable
chmod +x openclaw-cli.py

# Check agent status
./openclaw-cli.py status

# List projects
./openclaw-cli.py projects

# Force build a project
./openclaw-cli.py build todo_app

# Request a feature
./openclaw-cli.py feature todo_app "Add notifications" --description "Send email alerts"

# Assign a task
./openclaw-cli.py task todo_app "Add API endpoint" --priority high

# Set Gemini API key
./openclaw-cli.py set-key YOUR_GEMINI_API_KEY_HERE
```

### Direct HTTP (cURL)

```bash
# Health check
curl http://localhost:18789/api/health

# List projects
curl http://localhost:18789/api/projects

# Force build
curl -X POST http://localhost:18789/api/control/force-build \
  -H "Content-Type: application/json" \
  -d '{"project":"todo_app","priority":"high"}'

# Request feature
curl -X POST http://localhost:18789/api/control/generate-feature \
  -H "Content-Type: application/json" \
  -d '{"project":"todo_app","feature":"Add notifications","description":"Send alerts"}'

# Set API key
curl -X POST http://localhost:18789/api/control/set-api-key \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_KEY_HERE"}'
```

---

## 📊 Info & Monitoring Commands

### Check Status

```bash
./openclaw-cli.py status
```

Returns:
```json
{
  "service": "OpenClaw Agent API",
  "status": "ok",
  "timestamp": "2026-03-27T18:21:18.301765"
}
```

### List Projects

```bash
./openclaw-cli.py projects
```

Returns:
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

### Get Project Details

```bash
./openclaw-cli.py project todo_app
```

Returns:
```json
{
  "project": "todo_app",
  "path": "/workspace/projects/todo_app",
  "file_count": 3,
  "files": [
    {"name": "models.py", "lines": 42, "type": "code", "improvement": false},
    {"name": "test_models.py", "lines": 98, "type": "test", "improvement": false}
  ]
}
```

### View File Content

```bash
./openclaw-cli.py file todo_app models.py
```

Returns file content and metadata.

### Get Statistics

```bash
./openclaw-cli.py stats
```

Returns:
```json
{
  "total_lines_logged": 2543,
  "projects": 4,
  "has_gemini_key": false
}
```

### View Logs

```bash
# Last 20 lines (default)
./openclaw-cli.py logs

# Last 50 lines
./openclaw-cli.py logs --limit 50
```

### Check Build Queue

```bash
./openclaw-cli.py queue
```

Returns pending build requests and feature requests.

---

## 🎯 Control & Command Endpoints

### Force Build a Project

```bash
./openclaw-cli.py build todo_app --priority high
```

This queues an immediate build. The agent will pick up the signal and prioritize this project.

### Request Feature Generation

```bash
./openclaw-cli.py feature todo_app "Add notifications" \
  --description "Send email alerts to users"
```

Requests the agent to generate a specific feature for a project.

### Assign Task

```bash
./openclaw-cli.py task todo_app "Add database persistence" --priority high
```

Assign a task that will appear in TASKS.md for the agent to work on.

### Configure Gemini API Key

**This is required for real code generation!**

```bash
./openclaw-cli.py set-key sk-xxxxxxxxxxxxxxxxxxxxx
```

After setting the key:
1. Restart the container: `docker restart openclaw-agent`
2. The agent will now use real Gemini AI for code generation

### Clear Cache

```bash
./openclaw-cli.py clear-cache
```

Removes all `improvement_NNN.py` files, resetting the agent's work history.

### Restart Agent

```bash
./openclaw-cli.py restart
```

Requests agent restart (manual container restart recommended).

---

## 🔌 HTTP API Endpoints

### Base URL
```
http://localhost:18789
```

### Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/info` | Service information |
| GET | `/api/projects` | List all projects |
| GET | `/api/stats` | Statistics |
| GET | `/api/logs?limit=20` | Recent logs |
| GET | `/api/docs` | Documentation |

### Query Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/query/project-details/<project>` | Project details and files |
| GET | `/api/query/file-content/<project>/<filename>` | Get file content |
| GET | `/api/query/build-queue` | Pending build requests |

### Control Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/control/force-build` | Queue project build |
| POST | `/api/control/generate-feature` | Request feature |
| POST | `/api/control/assign-task` | Assign task |
| POST | `/api/control/set-api-key` | Configure API key |
| POST | `/api/control/restart-agent` | Restart agent |
| POST | `/api/control/clear-cache` | Clear improvements |

---

## 📝 HTTP Request Examples

### Force Build

```bash
curl -X POST http://localhost:18789/api/control/force-build \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "priority": "high"
  }'
```

Response:
```json
{
  "status": "build_queued",
  "project": "todo_app",
  "message": "Build signal queued for todo_app",
  "timestamp": "2026-03-27T18:22:10.123456"
}
```

### Generate Feature

```bash
curl -X POST http://localhost:18789/api/control/generate-feature \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "feature": "Add user authentication",
    "description": "JWT-based user login and registration"
  }'
```

Response:
```json
{
  "status": "feature_queued",
  "project": "todo_app",
  "feature": "Add user authentication",
  "message": "Feature request queued: Add user authentication",
  "timestamp": "2026-03-27T18:22:15.123456"
}
```

### Assign Task

```bash
curl -X POST http://localhost:18789/api/control/assign-task \
  -H "Content-Type: application/json" \
  -d '{
    "project": "todo_app",
    "task": "Add email notifications",
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

---

## 🐍 Python Integration

Use the CLI class from other Python scripts:

```python
from openclaw_cli import OpenClawCLI

cli = OpenClawCLI("http://localhost", 18789)

# Get projects
projects = cli.list_projects()
print(f"Found {projects['count']} projects")

# Force build
result = cli.force_build("todo_app", priority="high")
print(f"Build queued: {result['status']}")

# Set API key
cli.set_api_key("YOUR_API_KEY")

# Request feature
feature = cli.generate_feature(
    "todo_app",
    "Add notifications",
    "Email alerts for task updates"
)
print(f"Feature queued: {feature['message']}")
```

---

## 🔄 Complete Workflow Example

```bash
#!/bin/bash

# 1. Check current status
echo "=== Checking OpenClaw Status ==="
./openclaw-cli.py status

# 2. List projects
echo "=== Available Projects ==="
./openclaw-cli.py projects

# 3. Configure API key (required!)
echo "=== Setting Gemini API Key ==="
read -p "Enter your Gemini API key: " API_KEY
./openclaw-cli.py set-key "$API_KEY"

# 4. Request feature development
echo "=== Requesting Feature Development ==="
./openclaw-cli.py feature todo_app "Add recurring tasks" \
  --description "Support for repeating tasks daily/weekly/monthly"

# 5. Monitor progress
echo "=== Monitoring Agent ==="
for i in {1..5}; do
  echo "Check $i:"
  ./openclaw-cli.py logs --limit 10
  sleep 30
done

# 6. Check results
echo "=== Final Results ==="
./openclaw-cli.py stats
```

---

## ⚡ Usage Tips

### Remote Access

If running on a different machine:

```bash
./openclaw-cli.py --host http://your-server-ip --port 18789 projects
```

### Shell Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias oc="~/path/to/openclaw-cli.py"
alias oc-build="oc build"
alias oc-feature="oc feature"
alias oc-status="oc status"
alias oc-logs="oc logs --limit 30"
```

Then:
```bash
oc status
oc-build todo_app
oc-feature todo_app "New feature"
oc-logs
```

### Watch Agent Live

```bash
watch -n 5 "./openclaw-cli.py logs --limit 5"
```

---

## 🎯 Common Tasks

### Start Development on a New Project

```bash
# 1. Queue builds
./openclaw-cli.py build web_scraper --priority high
./openclaw-cli.py build data_analyzer --priority high

# 2. Request specific features
./openclaw-cli.py feature web_scraper "Add proxy support"
./openclaw-cli.py feature data_analyzer "Add CSV export"

# 3. Monitor progress
./openclaw-cli.py logs --limit 50
./openclaw-cli.py stats
```

### Enable Real Code Generation

```bash
# 1. Get Gemini API key from https://makersuite.google.com
# 2. Set it in OpenClaw
./openclaw-cli.py set-key YOUR_API_KEY

# 3. Restart container
docker restart openclaw-agent

# 4. Verify it's using the key
./openclaw-cli.py stats
# Should show "has_gemini_key": true
```

### Monitor Build Queue

```bash
# Check pending requests
./openclaw-cli.py queue

# Wait for completion
./openclaw-cli.py logs --limit 20
```

---

## 🚀 Production Deployment

For external server access:

```bash
# Start with port mapping
docker run -d -p 18789:18789 \
  -e GEMINI_API_KEY="your-key-here" \
  -v /your/workspace:/workspace \
  openclaw:latest

# Access from external terminal
./openclaw-cli.py --host http://your-server-ip projects
./openclaw-cli.py --host http://your-server-ip build todo_app
```

---

## 📖 Getting Help

```bash
./openclaw-cli.py --help
./openclaw-cli.py build --help
./openclaw-cli.py feature --help
```

---

## ✅ Next Steps

1. **Set Gemini API Key** (enable real code generation):
   ```bash
   ./openclaw-cli.py set-key YOUR_KEY
   docker restart openclaw-agent
   ```

2. **Queue a Build**:
   ```bash
   ./openclaw-cli.py build todo_app --priority high
   ```

3. **Request Features**:
   ```bash
   ./openclaw-cli.py feature data_analyzer "Add plotting support"
   ```

4. **Monitor Progress**:
   ```bash
   ./openclaw-cli.py logs --limit 30
   ```

---

**🎉 Your OpenClaw agent is now fully controllable from the command line!**
