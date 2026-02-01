#!/bin/bash
# Send Archived Photos Startup Script (Linux/Mac)

set -e  # Exit on error

# Load configuration
if [ -f "config.env" ]; then
    source config.env
else
    PYTHON_VERSION="3.13.9"
    VENV_DIR="venv"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Send Archived Photos - Startup"
echo "=================================================="
echo ""

# Ask user which mode to use
echo "Select email sending mode:"
echo "1. Gmail API"
echo "2. SMTP"
echo ""
read -p "Enter your choice (1 or 2): " mode_choice

case $mode_choice in
    1)
        SCRIPT_TO_RUN="send_archived_photos.py"
        MODE_NAME="Gmail API"
        ;;
    2)
        SCRIPT_TO_RUN="send_archived_photos_smtp.py"
        MODE_NAME="SMTP"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Using $MODE_NAME mode..."
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run start_photobooth.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo ""
echo "=================================================="
echo "Starting Archived Photos Sender ($MODE_NAME)..."
echo "=================================================="
echo ""

# Run the script
python "$SCRIPT_TO_RUN"

# Deactivate on exit
deactivate