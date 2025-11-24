#!/usr/bin/env python3
"""
Nexus Research Agent Web Server

Entry point for the research agent web interface.
Provides a FastAPI-based web UI for submitting research requests,
monitoring progress, and downloading reports.

Usage:
    nexus-research-server

    Or directly:
    python -m nexus.agents.research.server.app

Configuration:
    - Host: 0.0.0.0 (accessible from network)
    - Port: 8004 (default for research agent)
    - Log level: info

Environment Variables:
    - OPENAI_API_KEY: Required for OpenAI models
    - TAVILY_API_KEY: Required for web search
    - ANTHROPIC_API_KEY: Optional for Claude models
    - GOOGLE_API_KEY: Optional for Gemini models
"""

import sys
import uvicorn

from nexus.agents.research.server.research_service import app


def main():
    """
    Start the Nexus Research Agent web server.
    
    The server will be accessible at:
    - Local: http://localhost:8004
    - Network: http://<your-ip>:8004
    
    Press Ctrl+C to stop the server.
    """
    print("=" * 60)
    print("🚀 Starting Nexus Research Agent Web Server")
    print("=" * 60)
    print()
    print("📍 Server will be available at:")
    print("   - Local:   http://localhost:8004")
    print("   - Network: http://0.0.0.0:8004")
    print()
    print("📚 API Documentation:")
    print("   - Swagger UI: http://localhost:8004/docs")
    print("   - ReDoc:      http://localhost:8004/redoc")
    print()
    print("⚙️  Configuration:")
    print("   - Host: 0.0.0.0")
    print("   - Port: 8004")
    print("   - Log level: info")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8004,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print("\n")
        print("=" * 60)
        print(f"❌ Server error: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
