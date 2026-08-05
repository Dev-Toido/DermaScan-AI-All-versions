#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# DermaScan AI V4 — Launch Script
# ═══════════════════════════════════════════════════════════════════════
# Starts both the FastAPI backend (port 8000) and Next.js frontend (port 3000)
#
# Usage:
#   chmod +x run_v4.sh
#   ./run_v4.sh
#
# To stop: press Ctrl+C (kills both processes)
# ═══════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       DermaScan AI V4 — Launch Sequence${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check Python & activate venv if available
if [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}Activating Python virtual environment...${NC}"
    source venv/bin/activate
fi

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found!${NC}"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)

# Load Node.js from our manual install if available
export PATH="$SCRIPT_DIR/node-v20.12.2-linux-x64/bin:$PATH"

# Load nvm if available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not found! Install it from https://nodejs.org/${NC}"
    exit 1
fi

# Check if model exists
if [ ! -f "v4/backend/dermascan_v3_best.keras" ] && [ ! -f "dermascan_v3_best.keras" ]; then
    echo -e "${YELLOW}Warning: Model file 'dermascan_v3_best.keras' not found!${NC}"
    echo -e "${YELLOW}The backend will start but predictions will fail.${NC}"
fi

# Install frontend deps if needed
if [ ! -d "v4/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd v4/frontend && npm install && cd ../..
    echo -e "${GREEN}✅ Frontend dependencies installed.${NC}"
fi

echo ""
echo -e "${GREEN}Starting FastAPI backend on http://localhost:8000 ...${NC}"
export PYTHONPATH="$SCRIPT_DIR/v3:$SCRIPT_DIR"
if [ -f "v4/backend/api.py" ]; then
    (cd v4/backend && $PYTHON api.py) &
    BACKEND_PID=$!
else
    $PYTHON api_v4.py &
    BACKEND_PID=$!
fi

echo -e "${GREEN}Starting Next.js frontend on http://localhost:3000 ...${NC}"
(cd v4/frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ DermaScan AI V4 is starting up!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Frontend:  ${CYAN}http://localhost:3000${NC}"
echo -e "  Backend:   ${CYAN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop both servers.${NC}"
echo ""

# Trap Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down DermaScan AI V4...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All processes stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait -n $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
cleanup
