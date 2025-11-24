#!/bin/bash
# Start the Research Agent FastAPI server

# Change to the server directory
cd "$(dirname "$0")"

# Start the server
echo "Starting Research Agent API on http://localhost:8004"
echo "To stop: ./stop_server.sh or press Ctrl+C"
echo ""

mamba run -n agentic-ai python -m uvicorn research_service:app \
    --host 0.0.0.0 \
    --port 8004 \
    --reload \
    --log-level info
