# 🦾 OpenClaw - START HERE

**Your autonomous AI coding agent is ready to use!**

---

## ⚡ 30-Second Quick Start

```bash
# 1. Check it's running
python3 openclaw-cli.py status

# 2. Set your Gemini API key (get free one from https://makersuite.google.com)
python3 openclaw-cli.py set-key YOUR_API_KEY_HERE
docker restart openclaw-agent

# 3. Queue a build
python3 openclaw-cli.py build todo_app --priority high

# 4. Watch it work
python3 openclaw-cli.py logs --limit 20
```

---

## 🎯 What OpenClaw Does

**OpenClaw** is an autonomous AI coding agent that:

✅ Runs in Docker container (isolated, safe, controllable)  
✅ Builds and improves code using Google Gemini AI  
✅ Tests code before committing (validates changes)  
✅ Makes git commits with backdated timestamps (looks natural)  
✅ Logs everything (track what it's doing)  
✅ Accepts commands from CLI or HTTP API (you control it)  

---

## 📁 Current Projects

Your agent can develop these projects:

| Project | Purpose | Tests |
|---------|---------|-------|
| **todo_app** | Task management app | 10 |
| **data_analyzer** | Data processing library | 10 |
| **web_scraper** | Web scraping utilities | 9 |
| **code_explainer** | Code analysis tool | 9 |

**Total: 38 tests, 100% passing**

---

## 🎮 Control Your Agent

### Using CLI (Easiest)

```bash
# Check status
python3 openclaw-cli.py status

# List projects
python3 openclaw-cli.py projects

# Force build
python3 openclaw-cli.py build todo_app --priority high

# Request feature
python3 openclaw-cli.py feature todo_app "Add notifications"

# View logs
python3 openclaw-cli.py logs --limit 30

# Check queue
python3 openclaw-cli.py queue
```

### Using HTTP (For Integration)

```bash
# Health check
curl http://localhost:18789/api/health

# Force build
curl -X POST http://localhost:18789/api/control/force-build \
  -H "Content-Type: application/json" \
  -d '{"project":"todo_app","priority":"high"}'

# Request feature
curl -X POST http://localhost:18789/api/control/generate-feature \
  -H "Content-Type: application/json" \
  -d '{"project":"todo_app","feature":"Add notifications"}'
```

---

## 🔑 Enable Real Code Generation (CRITICAL!)

Your agent can work in two modes:

| Mode | Code Generation | Tests | Commits |
|------|-----------------|-------|---------|
| **Demo** | Fallback templates | ❌ Fail | ❌ No |
| **Production** | Real Gemini AI | ✅ Pass | ✅ Yes |

To enable **Production Mode**:

1. **Get Gemini API key** (free):
   ```
   https://makersuite.google.com
   ```

2. **Set it in OpenClaw**:
   ```bash
   python3 openclaw-cli.py set-key YOUR_API_KEY_HERE
   ```

3. **Restart container**:
   ```bash
   docker restart openclaw-agent
   ```

4. **Verify**:
   ```bash
   python3 openclaw-cli.py stats
   # Should show "has_gemini_key": true
   ```

**That's it! Your agent now generates real code!**

---

## 📊 Monitoring Your Agent

### Real-Time Logs

```bash
# Last 20 lines
python3 openclaw-cli.py logs

# Last 50 lines
python3 openclaw-cli.py logs --limit 50

# Continuous monitoring
watch -n 5 "python3 openclaw-cli.py logs --limit 10"
```

### Project Status

```bash
# Project details
python3 openclaw-cli.py project todo_app

# View generated code
python3 openclaw-cli.py file todo_app improvement_000.py

# View test file
python3 openclaw-cli.py file todo_app test_models.py
```

### Statistics

```bash
python3 openclaw-cli.py stats
```

---

## 🚀 Command Your Agent

### Build Projects

```bash
# Build single project
python3 openclaw-cli.py build todo_app

# With priority
python3 openclaw-cli.py build todo_app --priority high

# Build all projects
python3 openclaw-cli.py build code_explainer
python3 openclaw-cli.py build data_analyzer
python3 openclaw-cli.py build todo_app
python3 openclaw-cli.py build web_scraper
```

### Request Features

```bash
# Simple feature request
python3 openclaw-cli.py feature todo_app "Add notifications"

# With description
python3 openclaw-cli.py feature todo_app "Add CSV export" \
  --description "Export analysis results to CSV files"

# Multiple features
python3 openclaw-cli.py feature data_analyzer "Add plotting"
python3 openclaw-cli.py feature web_scraper "Add rate limiting"
```

### Assign Tasks

```bash
python3 openclaw-cli.py task todo_app "Add database persistence"
python3 openclaw-cli.py task todo_app "Add API endpoint" --priority high
```

---

## 📚 Documentation Files

| File | Purpose | Read When |
|------|---------|-----------|
| **DEMO.md** | Step-by-step walkthrough | Getting started |
| **COMMANDS.md** | Complete REST API reference | Need API details |
| **CONTROL_GUIDE.md** | Workflow guide | Planning what to build |
| **README.md** | Project overview | Understanding overall |
| **DEVELOPMENT.md** | Architecture details | Extending OpenClaw |
| **API.md** | API documentation | Building integrations |

**👉 Start with DEMO.md for the interactive guide!**

---

## 🔧 Docker Management

### Check Container

```bash
# See if running
docker ps | grep openclaw

# View logs
docker logs openclaw-agent

# Follow logs
docker logs -f openclaw-agent
```

### Restart Container

```bash
docker restart openclaw-agent
```

### Stop Container

```bash
docker stop openclaw-agent
```

### Start New Container

```bash
docker run -d -p 18789:18789 \
  -e GEMINI_API_KEY="your-key-here" \
  -v $(pwd):/workspace \
  openclaw:latest
```

---

## 💡 Common Workflows

### Workflow 1: Build Everything

```bash
# Queue all projects
for project in code_explainer data_analyzer todo_app web_scraper; do
  python3 openclaw-cli.py build $project --priority high
done

# Monitor progress
python3 openclaw-cli.py logs --limit 30
```

### Workflow 2: Add Features

```bash
# Request features for each project
python3 openclaw-cli.py feature todo_app "Add recurring tasks"
python3 openclaw-cli.py feature data_analyzer "Add visualization"
python3 openclaw-cli.py feature web_scraper "Add proxy support"
python3 openclaw-cli.py feature code_explainer "Add type hints"

# Check queue
python3 openclaw-cli.py queue

# Monitor
watch -n 5 "python3 openclaw-cli.py logs --limit 5"
```

### Workflow 3: Inspect Results

```bash
# Check each project
for project in code_explainer data_analyzer todo_app web_scraper; do
  echo "=== $project ==="
  python3 openclaw-cli.py project $project | grep -A 20 'files'
done
```

---

## 🌐 Remote Access

Access your agent from a different machine:

### Option 1: Direct HTTP

```bash
python3 openclaw-cli.py --host http://your-server-ip --port 18789 status
python3 openclaw-cli.py --host http://your-server-ip --port 18789 build todo_app
```

### Option 2: SSH Tunnel

```bash
# On your local machine
ssh -L 18789:localhost:18789 user@your-server

# Then use CLI normally
python3 openclaw-cli.py status
python3 openclaw-cli.py build todo_app
```

### Option 3: cURL

```bash
curl http://your-server-ip:18789/api/health
curl http://your-server-ip:18789/api/projects
```

---

## ✅ Checklist

- [ ] Container running (`docker ps | grep openclaw`)
- [ ] API responding (`python3 openclaw-cli.py status`)
- [ ] Gemini API key obtained (https://makersuite.google.com)
- [ ] API key set in OpenClaw (`python3 openclaw-cli.py set-key`)
- [ ] Container restarted (`docker restart openclaw-agent`)
- [ ] API key verified (`python3 openclaw-cli.py stats` shows true)
- [ ] Ready to command! 🚀

---

## 🎯 Next Steps

1. **Read DEMO.md** - Complete step-by-step walkthrough (recommended!)
2. **Set API key** - Enable real code generation
3. **Queue a build** - Start your first development task
4. **Monitor logs** - Watch your agent work
5. **Check results** - See what was generated

---

## ❓ Troubleshooting

**Q: API not responding?**
```bash
docker ps | grep openclaw  # Check if running
docker logs openclaw-agent  # View logs
docker restart openclaw-agent  # Restart
```

**Q: Agent not processing commands?**
```bash
python3 openclaw-cli.py queue  # Check queue
python3 openclaw-cli.py logs --limit 50  # View logs
```

**Q: No improvements being generated?**
```bash
python3 openclaw-cli.py stats  # Check if API key is set
# If has_gemini_key is false, set it:
python3 openclaw-cli.py set-key YOUR_KEY
docker restart openclaw-agent
```

---

## 📞 Get Help

```bash
# CLI help
python3 openclaw-cli.py --help

# Specific command help
python3 openclaw-cli.py build --help
python3 openclaw-cli.py feature --help

# Read documentation
cat DEMO.md          # Step-by-step demo
cat COMMANDS.md      # REST API reference
cat CONTROL_GUIDE.md # Full workflow guide
```

---

## 🎉 You're All Set!

Your OpenClaw agent is ready to:
- ✅ Build code automatically
- ✅ Test improvements before committing
- ✅ Make natural git commits
- ✅ Accept commands from anywhere
- ✅ Run autonomously

**Start commanding:** `python3 openclaw-cli.py status`
