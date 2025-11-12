"""
Configuration module for the email agent.

This module provides centralized configuration management for the email agent,
including environment variables, paths, and shared settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
EMAIL_AGENT_DIR = Path(__file__).parent
PROJECT_ROOT = EMAIL_AGENT_DIR.parent.parent  # agentic-ai-public/
SERVER_DIR = EMAIL_AGENT_DIR / "server"
NOTEBOOKS_DIR = EMAIL_AGENT_DIR / "notebooks"
STATIC_DIR = EMAIL_AGENT_DIR / "static"

# Load environment variables from project root first, then local
# This allows reusing the main project .env file
load_dotenv(PROJECT_ROOT / ".env")  # Load from project root
load_dotenv(EMAIL_AGENT_DIR / ".env", override=True)  # Override with local if exists

# Email server configuration
EMAIL_SERVER_URL = os.getenv("M3_EMAIL_SERVER_API_URL", "http://localhost:8000")
EMAIL_SERVER_HOST = os.getenv("EMAIL_SERVER_HOST", "0.0.0.0")
EMAIL_SERVER_PORT = int(os.getenv("EMAIL_SERVER_PORT", "8000"))

# LLM service configuration
LLM_SERVER_HOST = os.getenv("LLM_SERVER_HOST", "0.0.0.0")
LLM_SERVER_PORT = int(os.getenv("LLM_SERVER_PORT", "8001"))

# LLM provider API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Default LLM model
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "openai:gpt-4o")

# Database configuration
DATABASE_PATH = EMAIL_AGENT_DIR / "emails.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# User email (for agent context)
USER_EMAIL = os.getenv("USER_EMAIL", "you@email.com")


def validate_config():
    """
    Validate that required configuration is present.
    
    Raises:
        ValueError: If required configuration is missing
    """
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not MISTRAL_API_KEY:
        raise ValueError(
            "At least one LLM provider API key must be set. "
            "Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or MISTRAL_API_KEY "
            "in your .env file."
        )


def get_config_summary():
    """
    Get a summary of the current configuration.
    
    Returns:
        dict: Configuration summary with sensitive values masked
    """
    return {
        "email_server_url": EMAIL_SERVER_URL,
        "email_server_port": EMAIL_SERVER_PORT,
        "llm_server_port": LLM_SERVER_PORT,
        "default_model": DEFAULT_MODEL,
        "database_path": str(DATABASE_PATH),
        "openai_configured": bool(OPENAI_API_KEY),
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "mistral_configured": bool(MISTRAL_API_KEY),
        "user_email": USER_EMAIL,
    }


if __name__ == "__main__":
    # Print configuration summary when run directly
    import json
    print("Email Agent Configuration:")
    print(json.dumps(get_config_summary(), indent=2))
