#!/usr/bin/env bash
#
# Session Distiller for AgentShell
#
# Wrapper script for the Python-based session distiller.
#
# Usage:
#   distill-session.sh [session-id]      # Distill specific session
#   distill-session.sh --latest           # Distill most recent session
#   distill-session.sh --list             # List recent sessions
#   distill-session.sh --help             # Show help
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/session-distiller/distill.py"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if distill.py exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: distill.py not found${NC}"
    echo "Expected at: $PYTHON_SCRIPT"
    exit 1
fi

# Check dependencies
check_dependencies() {
    python3 - <<'EOF'
import sys
missing = []

try:
    import jinja2
except ImportError:
    missing.append('jinja2')

try:
    import anthropic
except ImportError:
    missing.append('anthropic')

if missing:
    print(f"Missing Python packages: {', '.join(missing)}")
    print(f"\nInstall with:")
    print(f"  pip install {' '.join(missing)}")
    sys.exit(1)
EOF

    if [ $? -ne 0 ]; then
        exit 1
    fi
}

# Show help
show_help() {
    echo "Session Distiller for AgentShell"
    echo ""
    echo "Usage:"
    echo "  distill-session.sh [session-id]       Distill specific session"
    echo "  distill-session.sh --latest            Distill most recent session"
    echo "  distill-session.sh --list              List recent sessions"
    echo "  distill-session.sh --no-ai [session]   Skip AI summarization"
    echo "  distill-session.sh --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  distill-session.sh 359ddc91-b696-476e-8ad8-5c707647800a"
    echo "  distill-session.sh --latest"
    echo "  distill-session.sh --list"
    echo ""
    echo "Environment variables:"
    echo "  ANTHROPIC_API_KEY    Required for AI summarization"
    echo ""
    echo "Output:"
    echo "  Creates draft markdown in docs/sessions/*.draft.md"
    echo "  Review and edit before finalizing"
    echo ""
}

# Parse arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --list)
        check_dependencies
        python3 "$PYTHON_SCRIPT" --list
        exit 0
        ;;
    --latest)
        check_dependencies
        python3 "$PYTHON_SCRIPT" --latest "${@:2}"
        ;;
    --no-ai)
        check_dependencies
        python3 "$PYTHON_SCRIPT" --no-ai "${@:2}"
        ;;
    "")
        show_help
        exit 1
        ;;
    *)
        check_dependencies
        python3 "$PYTHON_SCRIPT" "$@"
        ;;
esac
