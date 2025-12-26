#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AgentShell v2.0 Setup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════╝${NC}"
echo ""

REPOSITORY_NAME=$(basename "$(pwd)")
echo -e "${BLUE}→${NC} Repository: ${GREEN}$REPOSITORY_NAME${NC}"
echo ""

# ============================================================================
# MIGRATION DETECTION
# ============================================================================

MIGRATION_TYPE="none"

# Check for Kernel
if [ -f ".kernel/config.yaml" ]; then
    MIGRATION_TYPE="kernel"
    echo -e "${YELLOW}⚠ Kernel v2.3 detected${NC}"
    echo "This will migrate from Kernel to AgentShell v2.0"
    echo ""
    echo "Changes:"
    echo "  • .kernel/ → .kernel-archive/ (preserved)"
    echo "  • .channel/ → .channel-archive/ (preserved)"
    echo "  • .docs/tasks/ → .docs/tasks/ (no change)"
    echo "  • Creates: .agentshell.config.json"
    echo ""
    read -p "Proceed with migration? (y/n): " proceed

    if [ "$proceed" != "y" ]; then
        echo "Cancelled. No changes made."
        exit 0
    fi
fi

# Check for AgentShell v1.0
if [ -d "docs/agents" ] && [ -f "docs/agents/AANG.md" ] && [ ! -f ".agentshell.config.json" ]; then
    MIGRATION_TYPE="agentshell_v1"
    echo -e "${YELLOW}⚠ AgentShell v1.0 detected${NC}"
    echo "This will upgrade to AgentShell v2.0"
    echo ""
    echo "Preservation:"
    echo "  • docs/agents/ → PRESERVED (documentation)"
    echo "  • docs/tasks/ → PRESERVED"
    echo "  • docs/sessions/ → PRESERVED"
    echo ""
    echo "New additions:"
    echo "  • .agentshell.config.json (git-excluded)"
    echo "  • .state/ directory"
    echo ""
    read -p "Proceed with upgrade? (y/n): " proceed

    if [ "$proceed" != "y" ]; then
        echo "Cancelled. No changes made."
        exit 0
    fi
fi

# ============================================================================
# MIGRATION: KERNEL → AGENTSHELL
# ============================================================================

if [ "$MIGRATION_TYPE" = "kernel" ]; then
    echo ""
    echo -e "${BLUE}→${NC} Migrating from Kernel..."

    # Archive Kernel (never delete)
    if [ -d ".kernel" ]; then
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        mv .kernel ".kernel-archive-$TIMESTAMP"
        echo -e "${GREEN}✓${NC} Archived .kernel/ → .kernel-archive-$TIMESTAMP/"
    fi

    # Archive Channel
    if [ -d ".channel" ]; then
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        mv .channel ".channel-archive-$TIMESTAMP"
        echo -e "${GREEN}✓${NC} Archived .channel/ → .channel-archive-$TIMESTAMP/"
    fi

    # Preserve ALL .docs/ content
    if [ -d ".docs" ]; then
        total_files=$(find .docs -type f 2>/dev/null | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved .docs/ ($total_files files) - ALL content untouched"
    fi

    # Preserve ALL docs/ content
    if [ -d "docs" ]; then
        total_files=$(find docs -type f 2>/dev/null | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved docs/ ($total_files files) - ALL content untouched"
    fi

    # Preserve .docs/tasks/ (same location)
    if [ -d ".docs/tasks" ]; then
        task_count=$(find .docs/tasks -maxdepth 1 -type d | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved .docs/tasks/ ($task_count tasks)"
    fi

    # Auto-detect mode from archived config
    ARCHIVED_CONFIG=$(ls -t .kernel-archive-*/config.yaml 2>/dev/null | head -1)
    if [ -n "$ARCHIVED_CONFIG" ]; then
        JIRA_ENABLED=$(grep -A2 "jira:" "$ARCHIVED_CONFIG" | grep -q "enabled: true" && echo "true" || echo "false")

        if [ "$JIRA_ENABLED" = "true" ]; then
            MODE="jira"
            echo -e "${GREEN}✓${NC} Detected mode: Jira (from config)"
        else
            MODE="simple"
            echo -e "${GREEN}✓${NC} Detected mode: Simple (from config)"
        fi
    else
        MODE="jira"  # Default for Kernel projects
        echo -e "${YELLOW}⚠${NC} Defaulting to Jira mode"
    fi

    echo -e "${YELLOW}ℹ${NC}  All existing files in docs/ and .docs/ remain untouched"

    MIGRATION=true
fi

# ============================================================================
# MIGRATION: AGENTSHELL V1 → V2
# ============================================================================

if [ "$MIGRATION_TYPE" = "agentshell_v1" ]; then
    echo ""
    echo -e "${BLUE}→${NC} Upgrading from AgentShell v1.0..."

    # Preserve ALL docs/ content
    if [ -d "docs" ]; then
        total_files=$(find docs -type f | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved docs/ ($total_files files) - ALL content untouched"
    fi

    # Preserve docs/agents/ (becomes documentation)
    if [ -d "docs/agents" ]; then
        agent_count=$(find docs/agents -name "*.md" | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved docs/agents/ ($agent_count files) as documentation"
    fi

    # Preserve docs/tasks/
    if [ -d "docs/tasks" ]; then
        task_count=$(find docs/tasks -name "*.md" | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved docs/tasks/ ($task_count tasks)"

        # Extract next task number
        LAST_TASK=$(ls docs/tasks/*.md 2>/dev/null | grep -Eo '[0-9]{3}' | sort -n | tail -1)
        if [ -n "$LAST_TASK" ]; then
            NEXT_NUMBER=$((10#$LAST_TASK + 1))
            echo -e "${GREEN}✓${NC} Next task number: $NEXT_NUMBER"
        else
            NEXT_NUMBER=1
        fi
    fi

    # Preserve docs/sessions/
    if [ -d "docs/sessions" ]; then
        session_count=$(find docs/sessions -name "*.md" | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Preserved docs/sessions/ ($session_count sessions)"
    fi

    # Mode is always "simple" for v1.0 upgrades
    MODE="simple"
    echo -e "${GREEN}✓${NC} Mode: Simple (personal repositories)"
    echo -e "${YELLOW}ℹ${NC}  All existing files in docs/ remain untouched"

    MIGRATION=true
fi

# ============================================================================
# FRESH INSTALLATION
# ============================================================================

if [ "$MIGRATION_TYPE" = "none" ]; then
    echo "Select AgentShell mode:"
    echo ""
    echo "  1) Simple - Personal repositories, git-tracked tasks"
    echo "  2) Jira   - Enterprise repositories, Jira integration"
    echo ""
    read -p "Mode (1 or 2): " mode_choice

    if [ "$mode_choice" = "1" ]; then
        MODE="simple"
        NEXT_NUMBER=1
    elif [ "$mode_choice" = "2" ]; then
        MODE="jira"
    else
        echo "Invalid choice"
        exit 1
    fi

    MIGRATION=false
fi

echo -e "${GREEN}✓${NC} Mode: ${BLUE}$MODE${NC}"
echo ""

# ============================================================================
# REST OF SETUP
# ============================================================================

# Gather config
if [ "$MODE" = "jira" ]; then
    read -p "Jira URL: " jira_url
    read -p "Jira projects (comma-separated): " jira_projects
    read -p "Base branch (e.g., develop): " base_branch
else
    base_branch="main"
fi

read -p "Build command: " build_cmd
read -p "Test command: " test_cmd
read -p "Lint command: " lint_cmd

echo ""
echo -e "${BLUE}→${NC} Git user configuration (for commits in this repository)"
read -p "Git user name: " git_user_name
read -p "Git user email: " git_user_email

echo ""
echo -e "${BLUE}→${NC} Creating structure..."

# Create directories
mkdir -p .state/queue

if [ "$MODE" = "jira" ]; then
    mkdir -p .docs/tasks
    mkdir -p .docs/sessions
    TASK_LOCATION=".docs/tasks"
else
    mkdir -p docs/tasks
    mkdir -p docs/sessions
    TASK_LOCATION="docs/tasks"
fi

# Generate config
cat > .agentshell.config.json <<EOF
{
  "version": "2.0",
  "mode": "$MODE",
  "repository": {
    "name": "$REPOSITORY_NAME"
  },
  "agents": {
    "planning": "Aang",
    "execution": "M-O"
  },
  "stack": {
    "build": "$build_cmd",
    "test": "$test_cmd",
    "lint": "$lint_cmd"
  },
  "git": {
    "base_branch": "$base_branch",
    "claude_signature": false,
    "user": {
      "name": "$git_user_name",
      "email": "$git_user_email"
    }
  },
  "tasks": {
    "location": "$TASK_LOCATION",
    "next_number": ${NEXT_NUMBER:-1}
  }
}
EOF

echo -e "${GREEN}✓${NC} Created .agentshell.config.json"

# Create current.json
cat > .state/current.json <<EOF
{
  "version": "2.0",
  "updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "repository": "$REPOSITORY_NAME",
  "remote": null,
  "branch": "$base_branch",
  "current_task": null,
  "last_completed": null,
  "next_number": ${NEXT_NUMBER:-1},
  "agentshell_version": "2.0.0"
}
EOF

echo -e "${GREEN}✓${NC} Created .state/current.json"

# Create pending.json
cat > .state/queue/pending.json <<EOF
{
  "version": "2.0",
  "updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tasks": []
}
EOF

echo -e "${GREEN}✓${NC} Created .state/queue/pending.json"

# Create .git/info/exclude
mkdir -p .git/info
if [ "$MODE" = "jira" ]; then
    cat > .git/info/exclude <<EOF
# AgentShell v2.0 (Jira Mode)
# ONLY CODE in git - ZERO documentation
.agentshell.config.json
.docs/
.state/
EOF
else
    cat > .git/info/exclude <<EOF
# AgentShell v2.0 (Simple Mode)
.agentshell.config.json
.docs/
.state/
EOF
fi

echo -e "${GREEN}✓${NC} Updated .git/info/exclude"

echo ""
echo -e "${GREEN}╔════════════════════════════════╗${NC}"
echo -e "${GREEN}║   AgentShell v2.0 Ready!       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════╝${NC}"
echo ""
echo "Agents (4):"
echo "  /aang:plan     - Strategic planning (Opus)"
echo "  /aang:task     - Task writing (Sonnet)"
echo "  /mo:turbo      - Standard execution (Sonnet)"
echo "  /mo:eco        - Cost-efficient execution (Haiku)"
echo ""
echo "Commands (18):"
echo ""
echo "State & Queue:"
echo "  /task:close    - Close current task"
echo "  /task:queue    - Add task to queue"
echo "  /task:start    - Start specific task"
echo "  /task:list     - List pending tasks"
echo "  /task:remove   - Remove from queue"
echo ""
echo "Sessions:"
echo "  /distill       - Distill session"
echo "  /session:save  - Save snapshot"
echo "  /session:list  - List sessions"
echo ""
echo "Context:"
echo "  /context:task  - Load task context"
echo "  /history       - Show completed tasks"
echo ""
echo "Git:"
echo "  /branch:clean  - Clean merged branches"
echo "  /commit:amend  - Amend last commit"
echo ""
echo "Reports:"
echo "  /report:daily  - Daily summary"
echo "  /report:phase  - Phase progress"
echo ""
echo "Skills (2):"
echo "  /commit        - Smart commit workflow"
echo "  /pr            - Pull request creation"
echo ""

if [ "$MIGRATION" = "true" ]; then
    echo -e "${BLUE}Migration complete!${NC}"
    echo ""
    if [ "$MIGRATION_TYPE" = "kernel" ]; then
        echo "Rollback: Restore from .kernel-archive-*/ and .channel-archive-*/"
    elif [ "$MIGRATION_TYPE" = "agentshell_v1" ]; then
        echo "Your docs/agents/ files are preserved as documentation"
        echo "Executable agents are in ~/.claude/ (copied from ~/.context/)"
    fi
    echo ""
fi
