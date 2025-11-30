#!/bin/bash

# Clean up any stale Xvfb lock files
rm -f /tmp/.X99-lock

# Start Xvfb in the background
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &

# Export display environment variable
export DISPLAY=:99

# Wait a moment for Xvfb to be ready
sleep 1

# Execute the passed command
exec "$@"
