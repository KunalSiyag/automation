#!/bin/bash
# Safe Git Reset - No sudo required
# This script reinitializes git repository without needing sudo

cd "$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Safe Git Reset (No Sudo Required)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -f "agentic_system.sh" ]; then
    echo "❌ Error: Must run from automation directory"
    exit 1
fi

echo "📦 Step 1: Backing up current git history..."
if [ -d ".git" ]; then
    cp -r .git .git_backup_$(date +%Y%m%d_%H%M%S)
    echo "   ✓ Backup created"
else
    echo "   ⚠ No .git directory found"
fi

echo ""
echo "🔧 Step 2: Removing problematic .git directory..."
rm -rf .git
echo "   ✓ Removed"

echo ""
echo "🎬 Step 3: Reinitializing git repository..."
git init
git config user.name "$(git config --global user.name || echo 'Kunal Siyag')"
git config user.email "$(git config --global user.email || echo 'kunalsiyag1@outlook.com')"
echo "   ✓ Git reinitialized"

echo ""
echo "📝 Step 4: Creating initial commit..."
git add .
git commit -m "Reinitialize repository with agentic system" -q
echo "   ✓ Initial commit created"

echo ""
echo "✅ Done! Git is now ready."
echo ""
echo "Next steps:"
echo "  1. Check status: ./agentic_system.sh status"
echo "  2. Wait 1-2 minutes for commits to start"
echo "  3. Verify: git log --oneline -5"
echo ""
