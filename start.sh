#!/bin/bash

# Quick start script for Longevity Dashboard

echo "=========================================="
echo "LONGEVITY DASHBOARD"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please create a .env file with your Garmin credentials:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your GARMIN_EMAIL and GARMIN_PASSWORD"
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f longevity_dashboard.db ]; then
    echo "⚠️  Database not initialized!"
    echo ""
    echo "Please run initial setup first:"
    echo "  python3 backend/scripts/initial_setup.py"
    echo ""
    exit 1
fi

echo "Starting backend API server..."
python3 backend/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo ""
echo "Starting frontend dashboard..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ Dashboard starting!"
echo "=========================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
