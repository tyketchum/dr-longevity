#!/bin/bash
# Stop Longevity Dashboard Servers

echo "Stopping Longevity Dashboard servers..."

# Kill backend (port 8000)
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Stopping backend server..."
    lsof -ti:8000 | xargs kill -9
    echo "✅ Backend stopped"
else
    echo "Backend was not running"
fi

# Kill frontend (port 3000)
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "Stopping frontend server..."
    lsof -ti:3000 | xargs kill -9
    echo "✅ Frontend stopped"
else
    echo "Frontend was not running"
fi

echo ""
echo "Dashboard stopped successfully!"
