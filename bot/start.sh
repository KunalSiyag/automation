#!/usr/bin/env bash
set -euo pipefail

cd /app

if [[ -f /workspace/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source /workspace/.env
  set +a
fi

python -u agent.py &
AGENT_PID=$!

python -u api_v2.py &
API_PID=$!

shutdown() {
  kill "$AGENT_PID" "$API_PID" 2>/dev/null || true
  wait "$AGENT_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}

trap shutdown SIGTERM SIGINT

wait -n "$AGENT_PID" "$API_PID"
EXIT_CODE=$?
shutdown
exit "$EXIT_CODE"
