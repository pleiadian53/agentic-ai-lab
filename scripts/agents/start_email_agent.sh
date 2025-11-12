#!/bin/bash

# Email Agent Full Stack Startup Script
# Starts both email service and LLM service
# Can be run from anywhere in the project
# Usage: ./scripts/agents/start_email_agent.sh [OPTIONS]
#
# Options:
#   --email-port PORT    Email service port (default: 8000)
#   --llm-port PORT      LLM service port (default: 8001)
#   --email-only         Start only email service
#   --llm-only           Start only LLM service
#   --no-reload          Disable auto-reload
#   --help               Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
EMAIL_PORT=8000
LLM_PORT=8001
START_EMAIL=true
START_LLM=true
RELOAD_FLAG=""  # Empty by default (reload is uvicorn's default)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --email-port)
            EMAIL_PORT="$2"
            shift 2
            ;;
        --llm-port)
            LLM_PORT="$2"
            shift 2
            ;;
        --email-only)
            START_LLM=false
            shift
            ;;
        --llm-only)
            START_EMAIL=false
            shift
            ;;
        --no-reload)
            RELOAD_FLAG="--no-reload"
            shift
            ;;
        --help)
            echo "Email Agent Full Stack Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --email-port PORT    Email service port (default: 8000)"
            echo "  --llm-port PORT      LLM service port (default: 8001)"
            echo "  --email-only         Start only email service"
            echo "  --llm-only           Start only LLM service"
            echo "  --no-reload          Disable auto-reload"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Start both services"
            echo "  $0 --email-only                 # Start only email service"
            echo "  $0 --email-port 9000            # Custom port for email service"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         📧 Email Agent Full Stack Startup 🤖              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're starting both services
if [ "$START_EMAIL" = true ] && [ "$START_LLM" = true ]; then
    echo -e "${YELLOW}⚠️  Starting both services requires two terminal windows${NC}"
    echo ""
    echo -e "${BLUE}Option 1: Use tmux/screen (recommended)${NC}"
    echo -e "  ${GREEN}# Start email service in background${NC}"
    echo -e "  tmux new-session -d -s email-service '${SCRIPT_DIR}/start_email_server.sh --port ${EMAIL_PORT}'"
    echo -e "  ${GREEN}# Start LLM service in foreground${NC}"
    echo -e "  ${SCRIPT_DIR}/start_email_llm_service.sh --port ${LLM_PORT}"
    echo ""
    echo -e "${BLUE}Option 2: Run in separate terminals${NC}"
    echo -e "  ${GREEN}# Terminal 1${NC}"
    echo -e "  ${SCRIPT_DIR}/start_email_server.sh --port ${EMAIL_PORT}"
    echo -e "  ${GREEN}# Terminal 2${NC}"
    echo -e "  ${SCRIPT_DIR}/start_email_llm_service.sh --port ${LLM_PORT}"
    echo ""
    echo -e "${YELLOW}For now, starting email service only...${NC}"
    echo -e "${YELLOW}Run with --email-only or --llm-only to start individual services${NC}"
    echo ""
    
    # Start email service
    exec "${SCRIPT_DIR}/start_email_server.sh" --port ${EMAIL_PORT} ${RELOAD_FLAG}
    
elif [ "$START_EMAIL" = true ]; then
    # Start email service only
    exec "${SCRIPT_DIR}/start_email_server.sh" --port ${EMAIL_PORT} ${RELOAD_FLAG}
    
elif [ "$START_LLM" = true ]; then
    # Start LLM service only
    exec "${SCRIPT_DIR}/start_email_llm_service.sh" --port ${LLM_PORT} ${RELOAD_FLAG}
    
else
    echo -e "${RED}❌ Error: No service selected${NC}"
    exit 1
fi
