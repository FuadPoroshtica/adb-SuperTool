#!/bin/bash
# Android SuperTool Launcher (Linux/Mac)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
    python supertool.py "$@"
else
    # Check if dependencies are installed globally
    if python3 -c "import rich" 2>/dev/null; then
        python3 supertool.py "$@"
    else
        echo "Virtual environment not found. Running setup..."
        python3 setup.py
        echo ""
        echo "Setup complete. Run this script again to start the tool."
    fi
fi
