# Copilot Supervision Loop for OpenClaw

This repository now supports a supervised automation loop:

- OpenClaw runs inside Docker and continuously improves projects.
- Copilot (supervisor) reads logs and issues build/feature/task commands.
- OpenClaw executes inside the container, runs tests, and commits successful changes.

## 1. Start OpenClaw

```bash
./manage_openclaw.sh up
./manage_openclaw.sh status
```

## 2. Watch Logs

```bash
./manage_openclaw.sh logs 200
```

Watch for these key events:

- `COMMAND` / `COMMAND_DONE`: queued command processed successfully.
- `TEST_FAIL`: generated change failed tests.
- `ROLLBACK`: failed change was removed automatically.
- `COMMIT`: successful improvement committed.

## 3. Instruct OpenClaw

```bash
./manage_openclaw.sh build todo_app
./manage_openclaw.sh feature todo_app "Add recurring tasks" "Allow daily/weekly recurrence metadata"
./manage_openclaw.sh task todo_app "Improve edge-case validation"
```

## 4. Verify Queue

```bash
./manage_openclaw.sh queue
```

Queue entries now include stable IDs and timestamps to make supervision easier.

## 5. Common Recovery Actions

```bash
# Restart service
./manage_openclaw.sh restart

# Clear generated improvement files
python3 openclaw-cli.py clear-cache
```

## Notes

- OpenClaw prioritizes queued commands over autonomous random work.
- If tests fail, OpenClaw removes the just-created improvement file to keep projects stable.
- For real LLM output, set `GEMINI_API_KEY` in `.env` and restart the service.
