#!/bin/bash

# start_monitoring.sh
# Usage: ./start_monitoring.sh <CLASS_NUMBER> <TERM_CODE> <ENROLLMENT_TERM>
# Example: ./start_monitoring.sh 12345 2241 "2024 Spring"

# Check if all arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <CLASS_NUMBER> <TERM_CODE> <ENROLLMENT_TERM>"
    echo "Example: $0 75255 2261 \"2026 Spring\""
    exit 1
fi

CLASS_NUMBER=$1
TERM_CODE=$2
ENROLLMENT_TERM=$3

echo "Starting Class Auto-Enroller Monitoring..."
echo "Class Number: $CLASS_NUMBER"
echo "Term Code: $TERM_CODE"
echo "Enrollment Term: $ENROLLMENT_TERM"

# Export variables for docker-compose
export CLASS_NUMBER
export TERM_CODE
export ENROLLMENT_TERM

# Run docker compose in detached mode
# We use --build to ensure any changes are picked up
# Note: Using 'docker compose' (v2) provided by Docker Desktop
docker compose up -d --build

echo "Monitoring started in background."
echo "View logs with: docker compose logs -f"
