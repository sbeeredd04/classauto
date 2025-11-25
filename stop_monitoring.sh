#!/bin/bash
# Stop the class availability monitor

cd "$(dirname "$0")"

echo "Stopping class availability checker..."
echo ""

stopped=false

# Stop checker if PID file exists
if [ -f checker.pid ]; then
    PID=$(cat checker.pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping checker (PID: $PID)..."
        kill $PID 2>/dev/null
        sleep 1
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Force stopping..."
            kill -9 $PID 2>/dev/null
        fi
        
        echo "✓ Checker stopped"
        stopped=true
    else
        echo "Process $PID is not running"
    fi
    
    rm checker.pid
fi

# Stop any enroller processes
ENROLLER_PIDS=$(ps aux | grep "[a]uto_enroller.py" | awk '{print $2}')
if [ ! -z "$ENROLLER_PIDS" ]; then
    echo ""
    echo "Found running enroller process(es): $ENROLLER_PIDS"
    read -p "Stop enroller too? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $ENROLLER_PIDS 2>/dev/null
        echo "✓ Enroller stopped"
        stopped=true
    fi
fi

# Check for any remaining processes
CHECKER_PIDS=$(ps aux | grep "[c]lass_checker.py" | awk '{print $2}')
if [ ! -z "$CHECKER_PIDS" ]; then
    echo ""
    echo "Found other checker processes: $CHECKER_PIDS"
    kill $CHECKER_PIDS 2>/dev/null
    echo "✓ Additional processes stopped"
    stopped=true
fi

if [ "$stopped" = false ]; then
    echo "No running processes found"
fi

echo ""
echo "Done."

