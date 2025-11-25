#!/bin/bash
# Start the Nexus Research Agent Web Server

echo "============================================================"
echo "🚀 Starting Nexus Research Agent Web Server"
echo "============================================================"
echo ""

# Check if port 8004 is already in use
if lsof -ti:8004 > /dev/null 2>&1; then
    echo "⚠️  Port 8004 is already in use!"
    echo "📍 Stopping existing server..."
    lsof -ti:8004 | xargs kill -9
    sleep 1
    echo "✅ Existing server stopped"
    echo ""
fi

# Change to project directory
cd "$(dirname "$0")/.." || exit 1

echo "📂 Project directory: $(pwd)"
echo ""

# Activate conda environment and start server
echo "🔧 Activating conda environment: agentic-ai"
echo "🌐 Starting server on http://localhost:8004"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

mamba run -n agentic-ai python -m nexus.agents.research.server.app
