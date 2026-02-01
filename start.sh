#!/bin/bash
# Photo Booth Startup Script (Linux/Mac)
# This script sets up and runs the photo booth application

set -e  # Exit on error

# Load configuration
if [ -f "config.env" ]; then
    source config.env
else
    echo "Warning: config.env not found. Using defaults."
    PYTHON_VERSION="3.13.9"
    VENV_DIR="venv"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Photo Booth Application - Startup"
echo "=================================================="
echo ""

# Ask user which mode to run
echo "Select email sending mode:"
echo "1. Gmail API (100 emails/day unverified, requires OAuth setup)"
echo "2. SMTP (500 emails/day, simpler setup with app password)"
echo ""
read -p "Enter your choice (1 or 2): " mode_choice

case $mode_choice in
    1)
        SCRIPT_TO_RUN="photo_booth.py"
        MODE_NAME="Gmail API"
        ;;
    2)
        SCRIPT_TO_RUN="photo_booth_smtp.py"
        MODE_NAME="SMTP"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Starting in $MODE_NAME mode..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Get installed Python version
INSTALLED_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Installed Python version: $INSTALLED_VERSION"
echo "Configured Python version: $PYTHON_VERSION"

# Check if we need to use a specific Python version
PYTHON_CMD="python3"

# Try to find the specific version if configured
if command -v "python$PYTHON_VERSION" &> /dev/null; then
    PYTHON_CMD="python$PYTHON_VERSION"
    echo "Using: $PYTHON_CMD"
elif command -v "python${PYTHON_VERSION%.*}" &> /dev/null; then
    # Try major.minor version (e.g., python3.13)
    PYTHON_CMD="python${PYTHON_VERSION%.*}"
    echo "Using: $PYTHON_CMD"
else
    echo "Note: Exact version $PYTHON_VERSION not found, using default python3"
    echo "If you need a specific version, install it and update config.env"
fi

echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists."
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install/update requirements
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "=================================================="
echo "Starting Photo Booth Application ($MODE_NAME)..."
echo "=================================================="
echo ""

# Run the application
python "$SCRIPT_TO_RUN"

# Deactivate on exit
deactivate