#!/bin/bash
echo "====================================================="
echo " DermaScan AI (V5) - Startup Sequence"
echo "====================================================="

# 1. Initialize Conda for the script context
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dermascan

# Kill any existing processes on the required ports
echo "Cleaning up hanging ports..."
fuser -k 8000/tcp 2>/dev/null
fuser -k 3000/tcp 2>/dev/null

# 2. Start the FastAPI Backend (Background Process)
echo "Booting FastAPI Backend (Port 8000)..."
cd v5/api
uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

# 3. Start the Next.js Frontend (Foreground Process)
echo "Booting Next.js Frontend (Port 3000)..."
echo "Waiting 5 seconds for backend to initialize models..."
sleep 5

cd v5/ui
npm run dev &
FRONTEND_PID=$!

echo "====================================================="
echo " 🚀 DermaScan AI is LIVE!"
echo " 🌐 Web Interface: http://localhost:3000"
echo " 🔌 API Endpoint:  http://127.0.0.1:8000"
echo " Press Ctrl+C to shut down."
echo "====================================================="

# Trap Ctrl+C to kill both background processes
trap "echo 'Shutting down DermaScan...'; kill $BACKEND_PID; kill $FRONTEND_PID; exit" INT

# Wait for foreground process
wait $FRONTEND_PID
