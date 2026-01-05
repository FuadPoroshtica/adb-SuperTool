#!/bin/bash
# ============================================================================
#  Android SuperTool - Linux Launcher
#  Run: ./Start_linux.sh
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         ANDROID SUPERTOOL - Mobile Shop Edition           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}[ERROR] Python 3 is not installed!${NC}"
    echo ""
    echo "Install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python found: $($PYTHON --version)"

# Check for python3-venv on Debian/Ubuntu
if [ ! -d "venv" ]; then
    $PYTHON -m venv --help &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[...]${NC} Installing python3-venv..."
        if command -v apt &> /dev/null; then
            sudo apt install -y python3-venv
        fi
    fi
fi

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[...]${NC} Creating virtual environment..."
    $PYTHON -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "Try: sudo apt install python3-venv"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created"

    # Install dependencies
    echo -e "${YELLOW}[...]${NC} Installing dependencies..."
    ./venv/bin/pip install -q -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install dependencies${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Dependencies installed"
fi

# Run the tool
echo ""
echo -e "${GREEN}Starting Android SuperTool...${NC}"
echo ""

./venv/bin/python supertool.py

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}Program exited with an error.${NC}"
    read -p "Press Enter to exit..."
fi
