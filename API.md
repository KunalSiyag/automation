# 🦾 OpenClaw REST API Documentation

Complete guide to using the OpenClaw REST API for monitoring and managing the autonomous agent.

## Overview

The OpenClaw REST API provides real-time monitoring and management of the autonomous coding agent. The API runs on **port 18789** and is accessible via HTTP.

**Base URL:** `http://localhost:18789`

## Quick Start

### Health Check
```bash
curl http://localhost:18789/api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-03-27T18:08:20.949617",
  "service": "OpenClaw Agent API"
}
```

### Get Agent Status
```bash
curl http://localhost:18789/api/agent/status
```

### View Recent Logs
```bash
curl http://localhost:18789/api/logs?limit=50
```

## API Endpoints

### Health & Information

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-27T18:08:20.949617",
  "service": "OpenClaw Agent API"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

#### `GET /api/info`
Get OpenClaw system information and available endpoints.

**Response:**
```json
{
  "name": "OpenClaw",
  "version": "0.1.0",
  "description": "Autonomous AI Coding Agent",
  "workspace": "/workspace",
  "api_version": "1.0",
  "endpoints": {
    "health": "/api/health",
    "agent_status": "/api/agent/status",
    "logs": "/api/logs",
    "projects": "/api/projects",
    ...
  }
}
```

---

#### `GET /api/docs`
Get comprehensive API documentation.

**Response:**
```json
{
  "title": "OpenClaw REST API",
  "version": "1.0.0",
  "description": "Monitor and manage the autonomous coding agent",
  "base_url": "http://localhost:18789",
  "endpoints": [...]
}
```

---

#### `GET /`
Root endpoint with basic API info.

**Response:**
```json
{
  "message": "OpenClaw Agent API",
  "version": "0.1.0",
  "status": "running",
  "api_docs": "Visit /api/docs for documentation",
  "agent_status": {...}
}
```

---

### Agent Management

#### `GET /api/agent/status`
Get the current status of the agent process.

**Response:**
```json
{
  "running": true,
  "last_log": "[2026-03-27T18:08:20] SLEEP - 45 seconds"
}
```

**Fields:**
- `running` (boolean) - Whether the agent is currently running
- `last_log` (string) - Most recent log entry

---

### Logs & Activity

#### `GET /api/logs`
Get recent activity logs from the agent.

**Query Parameters:**
- `limit` (integer, default: 50) - Number of logs to return

**Example:**
```bash
curl http://localhost:18789/api/logs?limit=20
```

**Response:**
```json
{
  "total_lines": 968,
  "logs": [
    "[2026-03-27T18:08:20] SELECT - Working on project: todo_app",
    "[2026-03-27T18:08:20] IMPROVEMENT - Applied to improvement_000.py",
    "[2026-03-27T18:08:21] TEST_FAIL - /workspace/projects/todo_app",
    ...
  ],
  "limit": 20
}
```

---

#### `GET /api/logs/raw`
Get the complete raw log file.

**Response:** Plain text log file content

**Example:**
```bash
curl http://localhost:18789/api/logs/raw > agent.log
```

---

### Projects Management

#### `GET /api/projects`
Get list of all projects.

**Response:**
```json
{
  "count": 4,
  "projects": [
    {
      "name": "todo_app",
      "path": "/workspace/projects/todo_app",
      "tests": 10
    },
    {
      "name": "data_analyzer",
      "path": "/workspace/projects/data_analyzer",
      "tests": 10
    },
    {
      "name": "web_scraper",
      "path": "/workspace/projects/web_scraper",
      "tests": 9
    },
    {
      "name": "code_explainer",
      "path": "/workspace/projects/code_explainer",
      "tests": 9
    }
  ]
}
```

---

#### `GET /api/projects/<name>/tests`
Run tests for a specific project and get results.

**Parameters:**
- `name` (string) - Project name (e.g., `todo_app`)

**Example:**
```bash
curl http://localhost:18789/api/projects/todo_app/tests
```

**Response:**
```json
{
  "project": "todo_app",
  "test_status": {
    "status": "PASS",
    "output": [
      "===== 10 passed in 0.01s =====",
      "All tests passed!"
    ],
    "return_code": 0
  }
}
```

**Possible Status Values:**
- `PASS` - All tests passed
- `FAIL` - Tests failed
- `TIMEOUT` - Test execution timed out
- `ERROR` - Error running tests
- `UNKNOWN` - Unknown test status

---

### Tasks & Configuration

#### `GET /api/tasks`
Get project tasks from TASKS.md.

**Response:**
```json
{
  "content": "# OpenClaw Tasks\n\n## todo_app\n**Status:** IN_PROGRESS\n\n..."
}
```

---

### Git Integration

#### `GET /api/git/history`
Get git commit history.

**Query Parameters:**
- `limit` (integer, default: 20) - Number of commits to return

**Example:**
```bash
curl http://localhost:18789/api/git/history?limit=10
```

**Response:**
```json
{
  "commits": [
    "12c3fda feat: Add REST API for agent monitoring",
    "7c63002 docs: Add complete index and navigation guide",
    "f556eeb docs: Add project delivery summary",
    ...
  ],
  "limit": 10
}
```

---

#### `GET /api/git/status`
Get git status (working directory changes).

**Response:**
```json
{
  "status": "M  bot/agent.py\n?? projects/new_file.py"
}
```

---

### Statistics & Analytics

#### `GET /api/stats`
Get overall statistics about the agent and projects.

**Response:**
```json
{
  "uptime_seconds": 4840,
  "total_activities": 968,
  "activities": {
    "starts": 2,
    "projects_selected": 23,
    "tests_run": 23,
    "commits_made": 0,
    "errors": 92
  },
  "git_commits": 6,
  "projects_count": 4,
  "agent_status": true
}
```

**Fields:**
- `uptime_seconds` - Approximate uptime in seconds
- `total_activities` - Total number of logged activities
- `activities` - Breakdown of activities:
  - `starts` - Number of agent starts
  - `projects_selected` - Number of projects selected
  - `tests_run` - Number of tests executed
  - `commits_made` - Number of commits made
  - `errors` - Number of errors encountered
- `git_commits` - Total number of git commits
- `projects_count` - Number of projects
- `agent_status` - Is agent currently running

---

## Error Handling

### Error Responses

#### 404 Not Found
```json
{
  "error": "Not found",
  "message": "The requested endpoint does not exist",
  "docs": "Visit /api/docs for documentation"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Description of the error"
}
```

---

## Usage Examples

### Monitor Agent in Real-Time

```bash
# Get fresh status every 5 seconds
watch -n 5 "curl -s http://localhost:18789/api/agent/status"
```

### Export Logs

```bash
# Save logs to file
curl -s http://localhost:18789/api/logs/raw > openclaw_logs.txt

# Get last 100 logs as JSON
curl -s http://localhost:18789/api/logs?limit=100 | python -m json.tool
```

### Check Project Tests

```bash
# Test all projects
for project in todo_app data_analyzer web_scraper code_explainer; do
  echo "Testing $project:"
  curl -s http://localhost:18789/api/projects/$project/tests | grep -o '"status":"[^"]*"'
done
```

### Monitor Statistics

```bash
# Get current statistics
curl -s http://localhost:18789/api/stats | python -m json.tool

# Get commit history
curl -s http://localhost:18789/api/git/history?limit=20 | python -m json.tool
```

### Create a Dashboard Script

```bash
#!/bin/bash
# Simple dashboard showing agent status

while true; do
  clear
  echo "╔════════════════════════════════════════════╗"
  echo "║      OpenClaw Agent Dashboard             ║"
  echo "╚════════════════════════════════════════════╝"
  echo ""
  
  # Get stats
  STATS=$(curl -s http://localhost:18789/api/stats)
  echo "Agent Status: $(echo $STATS | grep -o '"agent_status":[^,]*')"
  echo "Total Activities: $(echo $STATS | grep -o '"total_activities":[^,]*')"
  echo "Commits Made: $(echo $STATS | grep -o '"commits_made":[^,]*')"
  echo "Errors: $(echo $STATS | grep -o '"errors":[^,]*')"
  echo ""
  
  # Get recent logs
  echo "Recent Activity:"
  curl -s http://localhost:18789/api/logs?limit=5 | grep -o '\[.*\]' | tail -3
  echo ""
  
  sleep 10
done
```

---

## Integration Examples

### Python

```python
import requests
import json

BASE_URL = "http://localhost:18789"

# Get agent status
response = requests.get(f"{BASE_URL}/api/agent/status")
status = response.json()
print(f"Agent running: {status['running']}")

# Get recent logs
response = requests.get(f"{BASE_URL}/api/logs?limit=50")
logs = response.json()
for log in logs['logs'][-5:]:
    print(log)

# Run tests for a project
response = requests.get(f"{BASE_URL}/api/projects/todo_app/tests")
result = response.json()
print(f"Test status: {result['test_status']['status']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:18789";

async function getAgentStatus() {
  const response = await fetch(`${BASE_URL}/api/agent/status`);
  const data = await response.json();
  console.log(`Agent running: ${data.running}`);
  return data;
}

async function getLogs(limit = 50) {
  const response = await fetch(`${BASE_URL}/api/logs?limit=${limit}`);
  const data = await response.json();
  return data.logs;
}

async function runProjectTests(projectName) {
  const response = await fetch(
    `${BASE_URL}/api/projects/${projectName}/tests`
  );
  const data = await response.json();
  console.log(`Test status: ${data.test_status.status}`);
  return data;
}

// Usage
getAgentStatus();
getLogs(20);
runProjectTests("todo_app");
```

### cURL Examples

```bash
# Health check with verbose output
curl -v http://localhost:18789/api/health

# Get logs and save to file with pretty printing
curl -s http://localhost:18789/api/logs | python -m json.tool > logs.json

# Get stats with custom formatting
curl -s http://localhost:18789/api/stats | python -c "
import sys, json
data = json.load(sys.stdin)
print(f'Commits: {data[\"activities\"][\"commits_made\"]}')
print(f'Errors: {data[\"activities\"][\"errors\"]}')
"

# Monitor logs in real-time
watch -n 2 "curl -s http://localhost:18789/api/logs?limit=10 | tail -5"
```

---

## Deployment

### Running Behind a Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name openclaw.example.com;

    location /api {
        proxy_pass http://localhost:18789/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose Setup

```yaml
version: '3'
services:
  openclaw:
    image: openclaw:latest
    ports:
      - "18789:18789"
    volumes:
      - ./automation:/workspace
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

### Enable HTTPS (Self-Signed Certificate)

```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use with reverse proxy or modify api.py to use ssl_context
```

---

## Rate Limiting & Performance

- **Request Timeout:** 30 seconds per request
- **Log File Size:** No limit (can grow large)
- **Concurrent Requests:** Unlimited (single-threaded default)
- **Response Format:** JSON (UTF-8)

---

## Troubleshooting

### API Not Responding

```bash
# Check if container is running
docker ps | grep openclaw

# View container logs
docker logs openclaw-agent

# Check port is exposed
netstat -tuln | grep 18789
```

### High Memory Usage

```bash
# Check container stats
docker stats openclaw-agent

# The agent accumulates logs - trim bot_log.md if needed
```

### Slow Test Execution

- Tests may take 30+ seconds
- Use `?limit=20` to reduce log data transfer

---

## Version

- API Version: 1.0.0
- OpenClaw Version: 0.1.0
- Python: 3.11+
- Flask: 3.0.0+

---

## Support

For issues or questions:
1. Check `/api/logs` for error messages
2. Review DEVELOPMENT.md in the project
3. Check Docker logs: `docker logs openclaw-agent`

---

**Last Updated:** 2026-03-27
