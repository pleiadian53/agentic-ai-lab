#!/bin/bash
# Stop the Nexus Research Agent Web Server
# This script gracefully stops the server running on port 8004

echo "============================================================"
echo "🛑 Stopping Nexus Research Agent Web Server"
echo "============================================================"
echo ""

# Find the process running on port 8004
PID=$(lsof -ti:8004)

if [ -z "$PID" ]; then
    echo "ℹ️  No server found running on port 8004"
    echo ""
    echo "The server is not currently running."
    exit 0
fi

echo "📍 Found server process: PID $PID"
echo ""

# Try graceful shutdown first (SIGTERM)
echo "⏳ Attempting graceful shutdown (SIGTERM)..."
kill -TERM $PID 2>/dev/null

# Wait a moment and check if it's still running
sleep 2

if lsof -ti:8004 > /dev/null 2>&1; then
    echo "⚠️  Server didn't stop gracefully, forcing shutdown (SIGKILL)..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Verify it's stopped
if lsof -ti:8004 > /dev/null 2>&1; then
    echo ""
    echo "❌ Failed to stop server on port 8004"
    echo ""
    echo "You may need to manually kill the process:"
    echo "  lsof -ti:8004 | xargs kill -9"
    exit 1
else
    echo ""
    echo "============================================================"
    echo "✅ Research Agent Web Server stopped successfully"
    echo "============================================================"
    exit 0
fi
