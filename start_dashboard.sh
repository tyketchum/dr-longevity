#!/bin/bash
# Longevity Dashboard Startup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏃 Starting Longevity Dashboard...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start backend
echo -e "${GREEN}Starting backend API...${NC}"
python3 backend/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Open browser
echo -e "${GREEN}Opening dashboard in browser...${NC}"
open http://localhost:3000

echo ""
echo -e "${BLUE}✅ Dashboard is running!${NC}"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop the dashboard, press Ctrl+C in this terminal"
echo ""

# Wait for user to press Ctrl+C
wait
