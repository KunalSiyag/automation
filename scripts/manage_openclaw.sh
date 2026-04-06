#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./manage_openclaw.sh <command> [args]

Commands:
  up             Build and start OpenClaw container in background
  down           Stop and remove OpenClaw container
  restart        Restart OpenClaw service
  logs [n]       Tail container logs (default: 120 lines)
  status         Show container and API status
  shell          Open shell in the running container
  queue          Show pending build/feature/task commands via CLI
  clean          Remove historical improvement_*.py files via API
  build <proj>   Queue a build for a project
  feature <proj> <feature> [description]
                 Queue a feature request
  task <proj> <task>
                 Queue a task request
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
shift || true

case "$cmd" in
  up)
    docker compose up -d --build openclaw
    ;;
  down)
    docker compose down
    ;;
  restart)
    docker compose restart openclaw
    ;;
  logs)
    lines="${1:-120}"
    docker compose logs -f --tail "$lines" openclaw
    ;;
  status)
    docker compose ps
    echo
    python3 openclaw-cli.py status || true
    ;;
  shell)
    docker compose exec openclaw bash
    ;;
  queue)
    python3 openclaw-cli.py queue
    ;;
  clean)
    python3 openclaw-cli.py clear-cache
    ;;
  build)
    project="${1:-}"
    if [[ -z "$project" ]]; then
      echo "Missing project name"
      exit 1
    fi
    python3 openclaw-cli.py build "$project"
    ;;
  feature)
    project="${1:-}"
    feature_name="${2:-}"
    description="${3:-}" 
    if [[ -z "$project" || -z "$feature_name" ]]; then
      echo "Usage: ./manage_openclaw.sh feature <project> <feature> [description]"
      exit 1
    fi
    if [[ -n "$description" ]]; then
      python3 openclaw-cli.py feature "$project" "$feature_name" --description "$description"
    else
      python3 openclaw-cli.py feature "$project" "$feature_name"
    fi
    ;;
  task)
    project="${1:-}"
    task_name="${2:-}"
    if [[ -z "$project" || -z "$task_name" ]]; then
      echo "Usage: ./manage_openclaw.sh task <project> <task>"
      exit 1
    fi
    python3 openclaw-cli.py task "$project" "$task_name"
    ;;
  *)
    usage
    exit 1
    ;;
esac
