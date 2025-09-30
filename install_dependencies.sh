#!/bin/bash

echo "Installing Document Scanner Dependencies..."

# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3-pip python3-venv tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx libglib2.0-0

# Create virtual environment (optional but recommended)
python3 -m venv scanner-env
source scanner-env/bin/activate

# Install Python packages
pip3 install -r requirements.txt

echo "Installation complete!"
echo "To start the scanner:"
echo "source scanner-env/bin/activate  # If using virtual environment"
echo "python3 app.py"
echo ""
echo "Then open http://localhost:5000 in your browser"