#!/usr/bin/env bash
#
# AgentShell Project Bootstrap Script
#
# Usage:
#   ~/.context/scripts/start-agentshell.sh <project-name> [project-type]
#
# Examples:
#   start-agentshell.sh my-django-app python
#   start-agentshell.sh my-api laravel
#   start-agentshell.sh my-frontend react
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTEXT_DIR="$HOME/.context"
REPO_BASE="$HOME/Repository"

# Functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Validate input
if [ -z "$1" ]; then
    print_error "Project name is required"
    echo ""
    echo "Usage: $(basename $0) <project-name> [project-type]"
    echo ""
    echo "Examples:"
    echo "  $(basename $0) my-django-app python"
    echo "  $(basename $0) my-api laravel"
    echo "  $(basename $0) my-frontend react"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_TYPE="${2:-general}"
PROJECT_PATH="$REPO_BASE/$PROJECT_NAME"

# Check if project already exists
if [ -d "$PROJECT_PATH" ]; then
    print_error "Project directory already exists: $PROJECT_PATH"
    exit 1
fi

# Start bootstrap process
print_header "AgentShell Project Bootstrap"

echo "Project: $PROJECT_NAME"
echo "Type: $PROJECT_TYPE"
echo "Path: $PROJECT_PATH"
echo ""

# Create project directory
print_info "Creating project directory..."
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"
print_success "Created $PROJECT_PATH"

# Initialize git
print_info "Initializing git repository..."
git init -q
print_success "Git repository initialized"

# Create AgentShell directory structure
print_info "Creating AgentShell structure..."

# .state/ - Ephemeral execution state (NOT git-tracked)
mkdir -p .state/{queue,graph,cache,sessions}

cat > .state/README.md << 'EOF'
# .state/

**Execution state for this project (NOT git-tracked)**

This folder contains ephemeral, machine-local execution state.

---

## What is This?

Redux-like state store for AgentShell execution tracking.

**NOT committed to git** - Rebuilt from `docs/` if needed.

---

## Structure

```
.state/
├── current.json        # Current execution state
├── queue/              # Pending tasks
│   └── pending.json
├── graph/              # Task dependencies
│   └── tasks.json
├── cache/              # Temporary data
└── sessions/           # Session snapshots
```

---

## Philosophy

- Machines are ephemeral containers
- Git is source of truth
- .state/ rebuilds from docs/ on new machines
- Zero attachment to local state
EOF

# Create current.json
cat > .state/current.json << EOF
{
  "version": "1.0.0",
  "updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "repository": "$PROJECT_NAME",
  "remote": null,
  "branch": "main",
  "current_task": null,
  "last_completed": null,
  "next_number": 1,
  "agentshell_version": "1.0.0"
}
EOF

# Create empty queue
echo '{"pending": []}' > .state/queue/pending.json

# Create empty graph
echo '{"tasks": {}, "dependencies": {}}' > .state/graph/tasks.json

# Create cache placeholder
touch .state/cache/.gitkeep

print_success "Created .state/ structure"

# docs/ - Repository knowledge (git-tracked)
print_info "Creating docs/ structure..."
mkdir -p docs/{agents,context,tasks,progress,sessions}

# Copy agent templates from .context
if [ -f "$CONTEXT_DIR/agents/AANG.md" ]; then
    cp "$CONTEXT_DIR/agents/AANG.md" docs/agents/

    # Customize with project name
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed syntax
        sed -i '' "s/Cast Club/$PROJECT_NAME/g" docs/agents/AANG.md
    else
        # Linux sed syntax
        sed -i "s/Cast Club/$PROJECT_NAME/g" docs/agents/AANG.md
    fi

    print_success "Created docs/agents/AANG.md"
fi

if [ -f "$CONTEXT_DIR/agents/MO.md" ]; then
    cp "$CONTEXT_DIR/agents/MO.md" docs/agents/

    # Customize with project name
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/Cast Club/$PROJECT_NAME/g" docs/agents/MO.md
    else
        sed -i "s/Cast Club/$PROJECT_NAME/g" docs/agents/MO.md
    fi

    print_success "Created docs/agents/MO.md"
fi

# Copy patterns template
if [ -f "$CONTEXT_DIR/bilal/PATTERNS.md" ]; then
    cp "$CONTEXT_DIR/bilal/PATTERNS.md" docs/context/
    print_success "Created docs/context/PATTERNS.md"
fi

# Create project README
cat > docs/README.md << EOF
# $PROJECT_NAME Documentation

AgentShell-powered development for $PROJECT_NAME.

---

## Structure

\`\`\`
docs/
├── agents/           # Agent configurations
│   ├── AANG.md      # Planning agent
│   └── MO.md        # Execution agent
├── context/         # Project patterns & conventions
│   └── PATTERNS.md
├── tasks/           # Task specifications
├── progress/        # Session logs
└── sessions/        # Notable AI sessions
\`\`\`

---

## Quick Start

1. **Start Planning Session** (Aang - Opus)
   \`\`\`bash
   claude-code --model opus
   # Load docs/agents/AANG.md context
   # Bilal describes requirements in prose
   # Aang creates task files in docs/tasks/
   \`\`\`

2. **Execute Tasks** (M-O - Sonnet)
   \`\`\`bash
   claude-code --model sonnet
   # Load docs/agents/MO.md context
   # M-O executes from task files
   # Updates .state/current.json
   \`\`\`

---

## Philosophy

- **Docs as State**: Documentation drives execution
- **Prose → Task → Code**: Clear chain from idea to implementation
- **Scope is Sacred**: Only modify what task specifies
- **Git First**: Machines are ephemeral, git is truth

---

Project Type: $PROJECT_TYPE
AgentShell Version: 1.0.0
EOF

print_success "Created docs/ structure"

# Create .gitignore
print_info "Creating .gitignore..."
cat > .gitignore << 'EOF'
# AgentShell execution state (ephemeral, machine-local)
.state/

# Dependencies (varies by project type)
node_modules/
vendor/
venv/
__pycache__/
*.pyc

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db
EOF

print_success "Created .gitignore"

# Create project README
print_info "Creating project README..."
cat > README.md << EOF
# $PROJECT_NAME

[Brief description of your project]

---

## Tech Stack

- Type: $PROJECT_TYPE
- AgentShell: v1.0.0

---

## Getting Started

[Installation and setup instructions]

---

## Development

This project uses **AgentShell** for AI-augmented development.

### Planning (Aang - Opus)
\`\`\`bash
claude-code --model opus
\`\`\`

### Execution (M-O - Sonnet)
\`\`\`bash
claude-code --model sonnet
\`\`\`

See [docs/README.md](docs/README.md) for full AgentShell workflow.

---

## License

[Your license]
EOF

print_success "Created README.md"

# Initial git commit
print_info "Creating initial commit..."
git add .
git commit -q -m "init: Bootstrap AgentShell structure

🤖 Generated with [AgentShell](https://github.com/BilalMahmud12/.context)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
print_success "Initial commit created"

# Update ~/.context/repository.json
print_info "Registering project in .context/repository.json..."

# Check if repository.json exists
if [ ! -f "$CONTEXT_DIR/repository.json" ]; then
    print_error "repository.json not found at $CONTEXT_DIR/repository.json"
    echo ""
    echo "Please manually add this project to repository.json:"
    echo ""
    echo "  \"$PROJECT_NAME\": {"
    echo "    \"name\": \"$PROJECT_NAME\","
    echo "    \"remote\": null,"
    echo "    \"local_path\": \"$PROJECT_PATH\","
    echo "    \"type\": \"$PROJECT_TYPE\","
    echo "    \"status\": \"active\","
    echo "    \"agentshell_version\": \"1.0.0\""
    echo "  }"
else
    # Use Python to update JSON (more reliable than sed/jq)
    python3 << PYTHON_SCRIPT
import json
import os

repo_file = "$CONTEXT_DIR/repository.json"

with open(repo_file, 'r') as f:
    data = json.load(f)

# Add new repository
data['repositories']['$PROJECT_NAME'] = {
    'name': '$PROJECT_NAME',
    'remote': None,
    'local_path': '$PROJECT_PATH',
    'type': '$PROJECT_TYPE',
    'status': 'active',
    'agents': {
        'aang': True,
        'mo': True,
        'zuko': False
    },
    'current_branch': 'main',
    'agentshell_version': '1.0.0'
}

# Update timestamp
from datetime import datetime
data['updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open(repo_file, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')

print('✓ Updated repository.json')
PYTHON_SCRIPT

    print_success "Registered in repository.json"
fi

# Summary
print_header "Bootstrap Complete"

echo "Project: $PROJECT_NAME"
echo "Path: $PROJECT_PATH"
echo ""
echo "Next steps:"
echo ""
echo "  1. cd $PROJECT_PATH"
echo "  2. Create GitHub repo (if needed):"
echo "     gh repo create $PROJECT_NAME --private --source=."
echo "  3. Push initial commit:"
echo "     git remote add origin git@github.com:YOUR_USERNAME/$PROJECT_NAME.git"
echo "     git push -u origin main"
echo "  4. Start planning with Aang (Opus):"
echo "     claude-code --model opus"
echo ""

print_success "Ready for AgentShell development!"
