# OpenClaw Autonomous Development Tasks

## Project Status Tracking

This file lists all mini-projects and their current development status.

---

## todo_app
**Status:** IN_PROGRESS

A simple task management application with persistence and testing.

### Tasks:
- [x] Setup project structure
- [x] Create core task model
- [x] Add basic CRUD operations
- [ ] Add persistence to JSON
- [ ] Implement task filtering
- [ ] Add priority levels
- [ ] Write comprehensive tests
- [ ] Add task descriptions

### Notes:
- Using JSON for storage initially
- Basic pytest test suite
- Can be extended with CLI interface

---

## web_scraper
**Status:** PLANNED

A web scraping utility for learning projects and data collection.

### Tasks:
- [ ] Setup project structure
- [ ] Implement basic HTTP fetcher
- [ ] Add HTML parser with BeautifulSoup
- [ ] Create data extraction utilities
- [ ] Add error handling
- [ ] Write parser tests
- [ ] Add rate limiting
- [ ] Create example scrapers

### Notes:
- Respects robots.txt
- Includes retry logic
- Safe error handling

---

## data_analyzer
**Status:** IN_PROGRESS

A data analysis tool for CSV and JSON files.

### Tasks:
- [x] Setup project structure
- [x] Create basic data loader
- [ ] Add statistical functions
- [ ] Implement CSV processing
- [ ] Add JSON processing
- [ ] Create visualization helpers
- [ ] Write analysis tests
- [ ] Add documentation

### Notes:
- Uses pandas for analysis
- Can export results to multiple formats
- Educational project for data science

---

## api_client
**Status:** PLANNED

A reusable HTTP client library for API interactions.

### Tasks:
- [ ] Setup project structure
- [ ] Implement base client
- [ ] Add request/response handling
- [ ] Create authentication support
- [ ] Add retry logic
- [ ] Implement rate limiting
- [ ] Write integration tests
- [ ] Add documentation

### Notes:
- OAuth and API key support
- Comprehensive error handling
- Based on requests library

---

## code_explainer
**Status:** IN_PROGRESS

A utility to explain Python code using AI (educational tool).

### Tasks:
- [x] Setup project structure
- [ ] Implement code parser
- [ ] Add AI explanation integration
- [ ] Create CLI interface
- [ ] Add markdown formatting
- [ ] Write generation tests
- [ ] Add caching for explanations
- [ ] Support multiple languages

### Notes:
- Uses AST for code analysis
- Formats explanations in markdown
- Great for learning and documentation

---

## ml_classifier
**Status:** PLANNED

A simple machine learning text classifier.

### Tasks:
- [ ] Setup project structure
- [ ] Implement data loader
- [ ] Create feature extraction
- [ ] Train basic classifier
- [ ] Add prediction interface
- [ ] Write evaluation tests
- [ ] Create training pipeline
- [ ] Add model persistence

### Notes:
- Uses scikit-learn
- Educational ML project
- Text classification focused

---

## fix_pytest_imports
**Status:** URGENT

Fix pytest ModuleNotFoundError issues by configuring PYTHONPATH in all projects.

### Problem:
- Tests fail with: `ModuleNotFoundError: No module named 'analyzer'` etc
- Reason: pytest can't find modules in the same directory

### Solution:
Update each project's `conftest.py` or `pytest.ini` to include project root in Python path:

1. Create/update conftest.py in each project directory with:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

2. Or update pytest.ini with:
```ini
[pytest]
pythonpath = .
```

### Tasks:
- [ ] Fix data_analyzer imports
- [ ] Fix todo_app imports
- [ ] Fix web_scraper imports
- [ ] Fix code_explainer imports
- [ ] Verify all tests pass

### Projects to Fix:
- /workspace/projects/data_analyzer/
- /workspace/projects/todo_app/
- /workspace/projects/web_scraper/
- /workspace/projects/code_explainer/

---

## Config Status

**Agent Configuration:**
- API: Google Gemini (gemini-1.5-flash-latest)
- Testing: pytest
- Version Control: git with backdated commits
- Log File: bot_log.md
- Workspace: /workspace
- Projects Dir: /workspace/projects

**Safety Rules:**
- Only modify files within /workspace
- Never delete entire project folders
- Always run tests before committing
- No external API calls (except Gemini)
- All commits are local only