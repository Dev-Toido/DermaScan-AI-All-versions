#!/bin/bash
echo "====================================================="
echo " DermaScan AI (V5) - Initial Setup"
echo "====================================================="

# 1. Initialize Conda for the script context
echo "[1/3] Setting up Conda Environment..."
source ~/miniconda3/etc/profile.d/conda.sh

# Check if environment already exists
if conda info --envs | grep -q "dermascan"; then
    echo "Environment 'dermascan' already exists. Updating..."
    conda env update -f environment.yml
else
    conda env create -f environment.yml
fi

conda activate dermascan

# 2. Install UI Dependencies
echo "[2/3] Installing Next.js Frontend Dependencies..."
cd v5/ui
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Node modules already installed."
fi
cd ../..

echo "[3/3] Setup Complete! 🎉"
echo "You can now run './start.sh' to boot up the AI application."
echo "====================================================="
