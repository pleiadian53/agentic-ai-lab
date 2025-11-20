#!/bin/bash
# Stop the Chart Agent API service gracefully

echo "Stopping Chart Agent API..."

# Find the process running on port 8003
PID=$(lsof -ti:8003)

if [ -z "$PID" ]; then
    echo "No service running on port 8003"
    exit 0
fi

echo "Found process: $PID"

# Send SIGTERM for graceful shutdown
kill -TERM $PID

# Wait for process to stop (max 10 seconds)
for i in {1..10}; do
    if ! kill -0 $PID 2>/dev/null; then
        echo "✓ Service stopped gracefully"
        exit 0
    fi
    echo "Waiting for shutdown... ($i/10)"
    sleep 1
done

# Force kill if still running
if kill -0 $PID 2>/dev/null; then
    echo "⚠ Forcing shutdown..."
    kill -9 $PID
    echo "✓ Service stopped (forced)"
else
    echo "✓ Service stopped"
fi
