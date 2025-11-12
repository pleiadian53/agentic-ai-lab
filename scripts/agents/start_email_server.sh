#!/bin/bash

# Email Agent Server Startup Script
# Can be run from anywhere in the project
# Usage: ./scripts/agents/start_email_server.sh [OPTIONS]
#
# Options:
#   --port PORT     Specify port (default: 8000)
#   --no-reload     Disable auto-reload
#   --help          Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PORT=8000
RELOAD_FLAG="--reload"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD_FLAG=""
            shift
            ;;
        --help)
            echo "Email Agent Server Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT     Specify port (default: 8000)"
            echo "  --no-reload     Disable auto-reload"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Email Agent Server Startup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Find project root (directory containing pyproject.toml)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${GREEN}📁 Project root: ${PROJECT_ROOT}${NC}"

# Navigate to email_agent directory
EMAIL_AGENT_DIR="${PROJECT_ROOT}/tool_use/email_agent"

if [ ! -d "$EMAIL_AGENT_DIR" ]; then
    echo -e "${RED}❌ Error: email_agent directory not found at ${EMAIL_AGENT_DIR}${NC}"
    exit 1
fi

cd "$EMAIL_AGENT_DIR"
echo -e "${GREEN}📂 Working directory: ${EMAIL_AGENT_DIR}${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    if [ -f "env.template" ]; then
        echo -e "${YELLOW}   Creating from template...${NC}"
        cp env.template .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}   Please edit ${EMAIL_AGENT_DIR}/.env to add your API keys${NC}"
    else
        echo -e "${RED}❌ Error: env.template not found${NC}"
        exit 1
    fi
    echo ""
fi

# Check if M3_EMAIL_SERVER_API_URL is set in .env
if ! grep -q "M3_EMAIL_SERVER_API_URL" .env; then
    echo -e "${YELLOW}📝 Adding M3_EMAIL_SERVER_API_URL to .env...${NC}"
    echo "" >> .env
    echo "# Email server URL" >> .env
    echo "M3_EMAIL_SERVER_API_URL=http://localhost:${PORT}" >> .env
    echo -e "${GREEN}✅ Updated .env${NC}"
    echo ""
fi

# Check if server directory exists
if [ ! -d "server" ]; then
    echo -e "${RED}❌ Error: server directory not found${NC}"
    exit 1
fi

# Check if email_service.py exists
if [ ! -f "server/email_service.py" ]; then
    echo -e "${RED}❌ Error: server/email_service.py not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📧 Starting email service on http://localhost:${PORT}${NC}"
echo -e "${YELLOW}   Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start the server
cd server
exec uvicorn email_service:app --port ${PORT} ${RELOAD_FLAG} --timeout-keep-alive 1200
