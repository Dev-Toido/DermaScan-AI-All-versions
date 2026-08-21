#!/bin/bash
# Script to launch DermaScan AI V3 with a single click

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Activate the virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment 'venv' not found in $DIR"
    sleep 5
    exit 1
fi

# Run the Streamlit application
echo "Starting DermaScan AI V3..."
cd v3 && python -m streamlit run app_v3.py && cd ..

# Keep terminal open if it fails
if [ $? -ne 0 ]; then
    echo "Application exited with an error."
    read -p "Press enter to continue..."
fi
