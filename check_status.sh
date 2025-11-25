#!/bin/bash
# Check the status of the monitoring system

cd "$(dirname "$0")"

echo "=================================="
echo "ASU Auto-Enrollment System Status"
echo "=================================="
echo ""

# Check checker status
echo "📊 Class Checker:"
echo "----------------"
if [ -f checker.pid ]; then
    PID=$(cat checker.pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "✓ RUNNING (PID: $PID)"
        echo ""
        ps -p $PID -o pid,etime,rss,command | tail -n +2
    else
        echo "✗ NOT RUNNING (stale PID file)"
    fi
else
    CHECKER_PIDS=$(ps aux | grep "[c]lass_checker.py" | awk '{print $2}')
    
    if [ -z "$CHECKER_PIDS" ]; then
        echo "✗ NOT RUNNING"
    else
        echo "✓ RUNNING (PID: $CHECKER_PIDS)"
        echo "⚠ Warning: No PID file found"
        ps aux | grep "[c]lass_checker.py"
    fi
fi

echo ""
echo "📝 Enroller:"
echo "------------"
ENROLLER_PIDS=$(ps aux | grep "[a]uto_enroller.py" | awk '{print $2}')

if [ -z "$ENROLLER_PIDS" ]; then
    echo "✗ NOT RUNNING"
else
    echo "✓ RUNNING (PID: $ENROLLER_PIDS)"
    ps aux | grep "[a]uto_enroller.py"
fi

echo ""
echo "📋 Recent Checker Logs:"
echo "-----------------------"
if [ -f checker.log ]; then
    tail -n 15 checker.log
else
    echo "(No log file found)"
fi

echo ""
echo "📋 Recent Enroller Logs:"
echo "------------------------"
if [ -f enroller.log ]; then
    tail -n 10 enroller.log
else
    echo "(No log file found)"
fi

echo ""
echo "=================================="
