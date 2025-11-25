#!/bin/bash
# Start the class availability monitor
# This script runs the checker in the background which will
# automatically trigger the enroller when seats become available

cd "$(dirname "$0")"

echo "=================================="
echo "ASU Class Auto-Enrollment System"
echo "=================================="
echo ""

# Check if already running
if [ -f checker.pid ]; then
    PID=$(cat checker.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠ Checker is already running (PID: $PID)"
        echo ""
        echo "To stop it: ./stop_monitoring.sh"
        echo "To check status: ./check_status.sh"
        exit 1
    else
        echo "Removing stale PID file..."
        rm checker.pid
    fi
fi

# Start the checker in background
echo "Starting class availability checker..."
nohup python3 class_checker.py > checker.log 2>&1 &
PID=$!

# Save PID
echo $PID > checker.pid

echo "✓ Checker started successfully!"
echo ""
echo "Process ID: $PID"
echo "Log file: checker.log"
echo ""
echo "The checker is now monitoring class availability."
echo "When seats become available, it will automatically"
echo "launch the enrollment script with a visible browser."
echo ""
echo "Useful commands:"
echo "  - View logs: tail -f checker.log"
echo "  - Check status: ./check_status.sh"
echo "  - Stop monitoring: ./stop_monitoring.sh"
echo ""

