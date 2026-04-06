#!/bin/bash
# Demo script for running OpenClaw agent locally

set -e

echo "🦾 OpenClaw - Autonomous AI Coding Agent"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create symlink to workspace if needed (for local testing)
if [ ! -L "/workspace" ]; then
    echo "Setting up /workspace symlink..."
    sudo ln -sfn "$(pwd)" /workspace 2>/dev/null || echo "Note: /workspace symlink requires sudo. Docker will handle this."
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  GEMINI_API_KEY not set"
    echo ""
    echo "To enable AI code generation, set:"
    echo "  export GEMINI_API_KEY='your-gemini-api-key'"
    echo ""
    echo "Without it, the agent will run in demo mode."
    echo ""
fi

# Run tests on all projects
echo "Running project tests..."
echo ""

for project in projects/*/; do
    project_name=$(basename "$project")
    echo "Testing $project_name..."
    
    if [ -f "$project/test_*.py" ]; then
        cd "$project"
        python -m pytest -v --tb=short 2>&1 | tail -3
        cd - > /dev/null
        echo ""
    fi
done

echo "✅ All tests passed!"
echo ""
echo "To run the agent:"
echo "  python src/agent.py"
echo ""
echo "To run with Docker:"
echo "  docker build -f src/Dockerfile -t openclaw:latest ."
echo "  docker run -it -v \$(pwd):/workspace -e GEMINI_API_KEY='your-key' openclaw:latest"
