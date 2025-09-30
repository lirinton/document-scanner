#!/bin/bash

echo "Starting Document Scanner..."

# Activate virtual environment if it exists
if [ -d "scanner-env" ]; then
    source scanner-env/bin/activate
fi

# Check if requirements are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Required packages not found. Please run: bash install_dependencies.sh"
    exit 1
fi

# Check if camera is accessible
if python3 -c "import scanner; print('Camera available:', scanner.check_camera_available())"; then
    echo "Starting web server..."
    python3 app.py
else
    echo "Warning: Camera may not be accessible"
    echo "Starting web server anyway..."
    python3 app.py
fi