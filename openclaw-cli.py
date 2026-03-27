#!/usr/bin/env python3
"""
OpenClaw CLI - Command-line interface to control the OpenClaw agent
Access your autonomous AI coding agent from the terminal
"""

import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin
from datetime import datetime

class OpenClawCLI:
    def __init__(self, host: str = "http://localhost", port: int = 18789):
        self.base_url = f"{host}:{port}"
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, raw: bool = False) -> Any:
        """Make HTTP request to API"""
        try:
            url = urljoin(self.base_url, endpoint)
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, json=data)
            else:
                return {"error": f"Unknown method: {method}"}
            
            if resp.status_code >= 400:
                return {"error": f"HTTP {resp.status_code}: {resp.text}"}
            
            if raw:
                return resp.text
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def health(self) -> Dict:
        """Check API health"""
        return self._request("GET", "/api/health")
    
    def info(self) -> Dict:
        """Get service info"""
        return self._request("GET", "/api/info")
    
    def list_projects(self) -> Dict:
        """List all projects"""
        return self._request("GET", "/api/projects")
    
    def project_details(self, project: str) -> Dict:
        """Get details about a project"""
        return self._request("GET", f"/api/query/project-details/{project}")
    
    def get_file(self, project: str, filename: str) -> Dict:
        """Get file content"""
        return self._request("GET", f"/api/query/file-content/{project}/{filename}")
    
    def get_logs(self, limit: int = 20) -> Dict:
        """Get recent logs"""
        return self._request("GET", f"/api/logs?limit={limit}")
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return self._request("GET", "/api/stats")
    
    def build_queue(self) -> Dict:
        """Check build queue"""
        return self._request("GET", "/api/query/build-queue")
    
    # CONTROL COMMANDS
    
    def assign_task(self, project: str, task: str, priority: str = "medium") -> Dict:
        """Assign a task to a project"""
        data = {"project": project, "task": task, "priority": priority}
        return self._request("POST", "/api/control/assign-task", data)
    
    def force_build(self, project: str, priority: str = "high") -> Dict:
        """Force agent to build a project"""
        data = {"project": project, "priority": priority}
        return self._request("POST", "/api/control/force-build", data)
    
    def generate_feature(self, project: str, feature: str, description: str = "") -> Dict:
        """Request feature generation"""
        data = {"project": project, "feature": feature, "description": description}
        return self._request("POST", "/api/control/generate-feature", data)
    
    def set_api_key(self, api_key: str) -> Dict:
        """Set Gemini API key"""
        data = {"api_key": api_key}
        return self._request("POST", "/api/control/set-api-key", data)
    
    def restart_agent(self) -> Dict:
        """Restart the agent"""
        return self._request("POST", "/api/control/restart-agent", {})
    
    def clear_cache(self) -> Dict:
        """Clear improvement files"""
        return self._request("POST", "/api/control/clear-cache", {})

def format_output(data: Any, indent: int = 2) -> str:
    """Format output nicely"""
    if isinstance(data, dict):
        if "error" in data:
            return f"❌ Error: {data['error']}"
        return json.dumps(data, indent=indent)
    return str(data)

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw CLI - Control your autonomous AI coding agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  openclaw-cli.py status                                    # Check agent status
  openclaw-cli.py projects                                  # List projects
  openclaw-cli.py project todo_app                          # Project details
  openclaw-cli.py build todo_app                            # Force build
  openclaw-cli.py feature todo_app "Add notifications"      # Request feature
  openclaw-cli.py task todo_app "Add API endpoint"          # Assign task
  openclaw-cli.py logs --limit 30                           # View logs
  openclaw-cli.py stats                                     # Show statistics
  openclaw-cli.py queue                                     # Check build queue
  openclaw-cli.py set-key YOUR_GEMINI_KEY                   # Configure API key
        """
    )
    
    parser.add_argument("--host", default="http://localhost", help="API host (default: localhost)")
    parser.add_argument("--port", type=int, default=18789, help="API port (default: 18789)")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Info commands
    subparsers.add_parser("health", help="Check API health")
    subparsers.add_parser("info", help="Get service info")
    subparsers.add_parser("status", help="Check agent status (alias for health)")
    subparsers.add_parser("projects", help="List all projects")
    subparsers.add_parser("stats", help="Get statistics")
    subparsers.add_parser("queue", help="Check build queue")
    
    # Query commands
    project_parser = subparsers.add_parser("project", help="Get project details")
    project_parser.add_argument("project_name")
    
    file_parser = subparsers.add_parser("file", help="Get file content")
    file_parser.add_argument("project_name")
    file_parser.add_argument("filename")
    
    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument("--limit", type=int, default=20, help="Number of lines")
    
    # Control commands
    build_parser = subparsers.add_parser("build", help="Force build a project")
    build_parser.add_argument("project_name")
    build_parser.add_argument("--priority", default="high", choices=["low", "medium", "high"])
    
    feature_parser = subparsers.add_parser("feature", help="Request feature generation")
    feature_parser.add_argument("project_name")
    feature_parser.add_argument("feature_name")
    feature_parser.add_argument("--description", default="")
    
    task_parser = subparsers.add_parser("task", help="Assign task to project")
    task_parser.add_argument("project_name")
    task_parser.add_argument("task_description")
    task_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high"])
    
    key_parser = subparsers.add_parser("set-key", help="Set Gemini API key")
    key_parser.add_argument("api_key")
    
    subparsers.add_parser("restart", help="Restart agent")
    subparsers.add_parser("clear-cache", help="Clear improvement files")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = OpenClawCLI(args.host, args.port)
    result = None
    
    try:
        if args.command == "health" or args.command == "status":
            result = cli.health()
        elif args.command == "info":
            result = cli.info()
        elif args.command == "projects":
            result = cli.list_projects()
        elif args.command == "project":
            result = cli.project_details(args.project_name)
        elif args.command == "file":
            result = cli.get_file(args.project_name, args.filename)
        elif args.command == "logs":
            result = cli.get_logs(args.limit)
        elif args.command == "stats":
            result = cli.get_stats()
        elif args.command == "queue":
            result = cli.build_queue()
        elif args.command == "build":
            result = cli.force_build(args.project_name, args.priority)
            print(f"✅ Build queued for {args.project_name}")
        elif args.command == "feature":
            result = cli.generate_feature(args.project_name, args.feature_name, args.description)
            print(f"✅ Feature '{args.feature_name}' queued for {args.project_name}")
        elif args.command == "task":
            result = cli.assign_task(args.project_name, args.task_description, args.priority)
            print(f"✅ Task assigned to {args.project_name}")
        elif args.command == "set-key":
            result = cli.set_api_key(args.api_key)
            print(f"✅ API key configured")
        elif args.command == "restart":
            result = cli.restart_agent()
            print(f"✅ Agent restart requested")
        elif args.command == "clear-cache":
            result = cli.clear_cache()
            print(f"✅ Cache cleared")
        
        if result and args.command not in ["build", "feature", "task", "set-key", "restart", "clear-cache"]:
            print(format_output(result))
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
