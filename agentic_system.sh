#!/bin/bash
# OpenClaw + Supervisor Management Script
# Manages the complete agentic system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WORKSPACE="$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# PID files
OPENCLAW_PID="$WORKSPACE/.openclaw.pid"
SUPERVISOR_PID="$WORKSPACE/.supervisor.pid"

function log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

function log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
}

function check_venv() {
    if [ ! -d "$WORKSPACE/venv" ]; then
        log_warn "Virtual environment not found, creating..."
        python3 -m venv "$WORKSPACE/venv"
        source "$WORKSPACE/venv/bin/activate"
        pip install -r "$WORKSPACE/bot/requirements.txt"
        log_success "Virtual environment created"
    fi
}

function activate_venv() {
    source "$WORKSPACE/venv/bin/activate"
}

function start_openclaw() {
    if [ -f "$OPENCLAW_PID" ] && kill -0 $(cat "$OPENCLAW_PID") 2>/dev/null; then
        log_warn "OpenClaw is already running (PID: $(cat $OPENCLAW_PID))"
        return 0
    fi
    
    log_info "Starting OpenClaw agent..."
    activate_venv
    
    nohup python3 "$WORKSPACE/bot/agent.py" > "$WORKSPACE/openclaw.out" 2>&1 &
    echo $! > "$OPENCLAW_PID"
    
    sleep 2
    if kill -0 $(cat "$OPENCLAW_PID") 2>/dev/null; then
        log_success "OpenClaw started (PID: $(cat $OPENCLAW_PID))"
    else
        log_error "OpenClaw failed to start"
        rm -f "$OPENCLAW_PID"
        return 1
    fi
}

function start_supervisor() {
    if [ -f "$SUPERVISOR_PID" ] && kill -0 $(cat "$SUPERVISOR_PID") 2>/dev/null; then
        log_warn "Supervisor is already running (PID: $(cat $SUPERVISOR_PID))"
        return 0
    fi
    
    log_info "Starting Supervisor agent..."
    activate_venv
    
    nohup python3 "$WORKSPACE/bot/supervisor.py" > "$WORKSPACE/supervisor.out" 2>&1 &
    echo $! > "$SUPERVISOR_PID"
    
    sleep 2
    if kill -0 $(cat "$SUPERVISOR_PID") 2>/dev/null; then
        log_success "Supervisor started (PID: $(cat $SUPERVISOR_PID))"
    else
        log_error "Supervisor failed to start"
        rm -f "$SUPERVISOR_PID"
        return 1
    fi
}

function stop_openclaw() {
    if [ ! -f "$OPENCLAW_PID" ]; then
        log_warn "OpenClaw PID file not found"
        return 0
    fi
    
    local pid=$(cat "$OPENCLAW_PID")
    if kill -0 $pid 2>/dev/null; then
        log_info "Stopping OpenClaw (PID: $pid)..."
        kill $pid
        sleep 2
        
        if kill -0 $pid 2>/dev/null; then
            log_warn "Forcefully killing OpenClaw..."
            kill -9 $pid 2>/dev/null || true
        fi
        
        log_success "OpenClaw stopped"
    else
        log_warn "OpenClaw process not running"
    fi
    
    rm -f "$OPENCLAW_PID"
}

function stop_supervisor() {
    if [ ! -f "$SUPERVISOR_PID" ]; then
        log_warn "Supervisor PID file not found"
        return 0
    fi
    
    local pid=$(cat "$SUPERVISOR_PID")
    if kill -0 $pid 2>/dev/null; then
        log_info "Stopping Supervisor (PID: $pid)..."
        kill $pid
        sleep 2
        
        if kill -0 $pid 2>/dev/null; then
            log_warn "Forcefully killing Supervisor..."
            kill -9 $pid 2>/dev/null || true
        fi
        
        log_success "Supervisor stopped"
    else
        log_warn "Supervisor process not running"
    fi
    
    rm -f "$SUPERVISOR_PID"
}

function status() {
    echo -e "\n${BLUE}=== OpenClaw Agentic System Status ===${NC}\n"
    
    # OpenClaw status
    if [ -f "$OPENCLAW_PID" ] && kill -0 $(cat "$OPENCLAW_PID") 2>/dev/null; then
        echo -e "OpenClaw:   ${GREEN}●${NC} Running (PID: $(cat $OPENCLAW_PID))"
    else
        echo -e "OpenClaw:   ${RED}●${NC} Stopped"
    fi
    
    # Supervisor status
    if [ -f "$SUPERVISOR_PID" ] && kill -0 $(cat "$SUPERVISOR_PID") 2>/dev/null; then
        echo -e "Supervisor: ${GREEN}●${NC} Running (PID: $(cat $SUPERVISOR_PID))"
    else
        echo -e "Supervisor: ${RED}●${NC} Stopped"
    fi
    
    echo ""
    
    # Recent commits today
    if command -v git &> /dev/null; then
        local today=$(date +%Y-%m-%d)
        local commits_today=$(git -C "$WORKSPACE" log --since="$today 00:00:00" --oneline 2>/dev/null | wc -l || echo "0")
        echo -e "Commits today: ${GREEN}$commits_today${NC}"
    fi
    
    echo ""
}

function logs() {
    local lines=${1:-50}
    
    echo -e "\n${BLUE}=== OpenClaw Logs (last $lines lines) ===${NC}"
    if [ -f "$WORKSPACE/bot_log.md" ]; then
        tail -n $lines "$WORKSPACE/bot_log.md"
    else
        log_warn "No OpenClaw logs found"
    fi
    
    echo -e "\n${BLUE}=== Supervisor Logs (last $lines lines) ===${NC}"
    if [ -f "$WORKSPACE/supervisor_log.md" ]; then
        tail -n $lines "$WORKSPACE/supervisor_log.md"
    else
        log_warn "No Supervisor logs found"
    fi
}

function start_all() {
    check_python
    check_venv
    
    log_info "Starting OpenClaw Agentic System..."
    start_openclaw
    sleep 3
    start_supervisor
    
    echo ""
    status
    
    log_success "System started successfully!"
    echo ""
    echo "Monitor with: $0 status"
    echo "View logs:    $0 logs"
    echo "Stop system:  $0 stop"
}

function stop_all() {
    log_info "Stopping OpenClaw Agentic System..."
    stop_supervisor
    stop_openclaw
    log_success "System stopped"
}

function restart_all() {
    log_info "Restarting OpenClaw Agentic System..."
    stop_all
    sleep 2
    start_all
}

function show_help() {
    cat << EOF
OpenClaw Agentic System Management Script

Usage: $0 [command]

Commands:
    start       Start OpenClaw and Supervisor
    stop        Stop OpenClaw and Supervisor
    restart     Restart the entire system
    status      Show status of all components
    logs [N]    Show last N lines of logs (default: 50)
    
    start-openclaw    Start only OpenClaw agent
    stop-openclaw     Stop only OpenClaw agent
    start-supervisor  Start only Supervisor agent
    stop-supervisor   Stop only Supervisor agent
    
    help        Show this help message

Examples:
    $0 start           # Start the system
    $0 status          # Check if running
    $0 logs 100        # View last 100 log lines
    $0 restart         # Restart everything

EOF
}

# Main command handler
case "${1:-}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status
        ;;
    logs)
        logs "${2:-50}"
        ;;
    start-openclaw)
        check_python
        check_venv
        start_openclaw
        ;;
    stop-openclaw)
        stop_openclaw
        ;;
    start-supervisor)
        check_python
        check_venv
        start_supervisor
        ;;
    stop-supervisor)
        stop_supervisor
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
