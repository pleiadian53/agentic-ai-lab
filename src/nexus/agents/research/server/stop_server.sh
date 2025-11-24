#!/bin/bash
# Stop the Research Agent FastAPI server

echo "Stopping Research Agent API..."

# Find the process running on port 8004
PID=$(lsof -ti:8004)

if [ -z "$PID" ]; then
    echo "No server found running on port 8004"
    exit 0
fi

# Kill the process
kill -TERM $PID 2>/dev/null

# Wait a moment and check if it's still running
sleep 1
if lsof -ti:8004 > /dev/null 2>&1; then
    echo "Server didn't stop gracefully, forcing shutdown..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Verify it's stopped
if lsof -ti:8004 > /dev/null 2>&1; then
    echo "❌ Failed to stop server on port 8004"
    exit 1
else
    echo "✓ Research Agent API stopped successfully"
    exit 0
fi
