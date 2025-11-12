#!/usr/bin/env python3
"""
Quick configuration checker for the email agent.

Run this script to verify your environment is properly configured.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import (
        PROJECT_ROOT,
        EMAIL_AGENT_DIR,
        EMAIL_SERVER_URL,
        DEFAULT_MODEL,
        OPENAI_API_KEY,
        ANTHROPIC_API_KEY,
        MISTRAL_API_KEY,
        get_config_summary,
        validate_config,
    )
    
    print("=" * 60)
    print("📧 Email Agent Configuration Check")
    print("=" * 60)
    print()
    
    # Check paths
    print("📁 Paths:")
    print(f"  Project Root:    {PROJECT_ROOT}")
    print(f"  Email Agent Dir: {EMAIL_AGENT_DIR}")
    print()
    
    # Check .env files
    print("📄 Environment Files:")
    root_env = PROJECT_ROOT / ".env"
    local_env = EMAIL_AGENT_DIR / ".env"
    
    if root_env.exists():
        print(f"  ✅ Project root .env found: {root_env}")
    else:
        print(f"  ⚠️  Project root .env not found: {root_env}")
    
    if local_env.exists():
        print(f"  ✅ Local .env found: {local_env}")
    else:
        print(f"  ℹ️  Local .env not found (optional): {local_env}")
    print()
    
    # Check API keys
    print("🔑 API Keys:")
    if OPENAI_API_KEY:
        masked = OPENAI_API_KEY[:10] + "..." + OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 14 else "***"
        print(f"  ✅ OpenAI:    {masked}")
    else:
        print(f"  ❌ OpenAI:    Not set")
    
    if ANTHROPIC_API_KEY:
        masked = ANTHROPIC_API_KEY[:10] + "..." + ANTHROPIC_API_KEY[-4:] if len(ANTHROPIC_API_KEY) > 14 else "***"
        print(f"  ✅ Anthropic: {masked}")
    else:
        print(f"  ℹ️  Anthropic: Not set (optional)")
    
    if MISTRAL_API_KEY:
        masked = MISTRAL_API_KEY[:10] + "..." + MISTRAL_API_KEY[-4:] if len(MISTRAL_API_KEY) > 14 else "***"
        print(f"  ✅ Mistral:   {masked}")
    else:
        print(f"  ℹ️  Mistral:   Not set (optional)")
    print()
    
    # Check configuration
    print("⚙️  Configuration:")
    print(f"  Email Server URL: {EMAIL_SERVER_URL}")
    print(f"  Default Model:    {DEFAULT_MODEL}")
    print()
    
    # Validate
    print("🔍 Validation:")
    try:
        validate_config()
        print("  ✅ Configuration is valid!")
    except ValueError as e:
        print(f"  ❌ Configuration error: {e}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Configuration check complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start the email server:")
    print("     cd tool_use/email_agent/server")
    print("     uvicorn email_service:app --reload")
    print()
    print("  2. Open the notebook:")
    print("     jupyter lab notebooks/email_agent_demo.ipynb")
    print()

except ImportError as e:
    print(f"❌ Error importing config module: {e}")
    print()
    print("Make sure you're running from the email_agent directory:")
    print("  cd tool_use/email_agent")
    print("  python check_config.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
