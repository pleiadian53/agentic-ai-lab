#!/bin/bash

# Email Agent Server Startup Script
# This script starts the email service backend

echo "🚀 Starting Email Agent Server..."
echo ""

# Check if we're in the right directory
if [ ! -f "server/email_service.py" ]; then
    echo "❌ Error: Must run this script from the email_agent directory"
    echo "   cd tool_use/email_agent"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from template..."
    cp env.template .env
    echo "✅ Created .env file - please edit it to add your API keys"
    echo ""
fi

# Check if M3_EMAIL_SERVER_API_URL is set in .env
if ! grep -q "M3_EMAIL_SERVER_API_URL" .env; then
    echo "📝 Adding M3_EMAIL_SERVER_API_URL to .env..."
    echo "" >> .env
    echo "# Email server URL" >> .env
    echo "M3_EMAIL_SERVER_API_URL=http://localhost:8000" >> .env
fi

echo "✅ Environment configured"
echo ""
echo "📧 Starting email service on http://localhost:8000"
echo "   Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
cd server
uvicorn email_service:app --reload --timeout-keep-alive 1200
