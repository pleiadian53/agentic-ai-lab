# Email Agent Configuration

The email agent uses a centralized configuration system via the `config.py` module. This provides a clean, maintainable way to manage settings across all components.

## Configuration Module

The `config.py` module provides:

- **Centralized settings**: All configuration in one place
- **Environment variable loading**: Automatic `.env` file support
- **Path management**: Consistent path handling across the project
- **Validation**: Ensures required configuration is present
- **Type safety**: Proper types for all configuration values

## Usage

### In Server Code

```python
# Import specific configuration values
from config import (
    DEFAULT_MODEL,
    USER_EMAIL,
    EMAIL_SERVER_URL,
    CORS_ORIGINS,
)

# Use in your code
model = DEFAULT_MODEL  # "openai:gpt-4o"
user = USER_EMAIL      # "you@email.com"
```

### In Notebooks

```python
import sys
from pathlib import Path

# Add email_agent to path
sys.path.insert(0, str(Path.cwd().parent))

# Import configuration
from config import EMAIL_SERVER_URL, DEFAULT_MODEL

print(f"Server: {EMAIL_SERVER_URL}")
print(f"Model: {DEFAULT_MODEL}")
```

### Check Configuration

Run the config module directly to see current settings:

```bash
cd tool_use/email_agent
python config.py
```

Output:
```json
{
  "email_server_url": "http://localhost:8000",
  "email_server_port": 8000,
  "llm_server_port": 8001,
  "default_model": "openai:gpt-4o",
  "database_path": "/path/to/emails.db",
  "openai_configured": true,
  "anthropic_configured": false,
  "mistral_configured": false,
  "user_email": "you@email.com"
}
```

## Available Configuration

### LLM Configuration

- `DEFAULT_MODEL`: Default LLM model (e.g., `"openai:gpt-4o"`)
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `MISTRAL_API_KEY`: Mistral API key

### Server Configuration

- `EMAIL_SERVER_URL`: Email service URL
- `EMAIL_SERVER_HOST`: Email service bind host
- `EMAIL_SERVER_PORT`: Email service port
- `LLM_SERVER_HOST`: LLM service bind host
- `LLM_SERVER_PORT`: LLM service port

### Path Configuration

- `EMAIL_AGENT_DIR`: Root directory of email agent
- `SERVER_DIR`: Server code directory
- `NOTEBOOKS_DIR`: Notebooks directory
- `STATIC_DIR`: Static files directory
- `DATABASE_PATH`: SQLite database file path

### Application Configuration

- `USER_EMAIL`: Default user email address
- `CORS_ORIGINS`: Allowed CORS origins (list)
- `CORS_ALLOW_CREDENTIALS`: Allow credentials in CORS
- `LOG_LEVEL`: Logging level

## Environment Variables

### Loading Priority

The configuration module loads environment variables in this order:

1. **Project root `.env`** (`agentic-ai-public/.env`) - Loaded first
2. **Local `.env`** (`tool_use/email_agent/.env`) - Overrides project root if exists

This allows you to:
- ✅ Reuse API keys from the main project `.env`
- ✅ Override specific settings locally if needed
- ✅ Keep email-agent-specific configuration separate

### Configuration Files

All configuration can be set via environment variables in `.env`:

```bash
# LLM Configuration
DEFAULT_LLM_MODEL=openai:gpt-4o
OPENAI_API_KEY=sk-...

# Server Configuration
EMAIL_SERVER_HOST=0.0.0.0
EMAIL_SERVER_PORT=8000
LLM_SERVER_PORT=8001

# User Configuration
USER_EMAIL=you@email.com

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=DEBUG
```

## Benefits

### Before (Awkward Path Manipulation)

```python
import sys
from pathlib import Path

# Fragile path manipulation
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Hardcoded values
model = "openai:gpt-4.1"
user_email = "you@email.com"
```

### After (Clean Configuration)

```python
from config import DEFAULT_MODEL, USER_EMAIL

# Clean, centralized configuration
model = DEFAULT_MODEL
user_email = USER_EMAIL
```

## Validation

The config module includes validation:

```python
from config import validate_config

try:
    validate_config()
    print("✅ Configuration is valid")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

This ensures at least one LLM provider API key is configured.

## Best Practices

1. **Never hardcode values**: Use config module instead
2. **Use `.env` for secrets**: Don't commit API keys
3. **Validate early**: Call `validate_config()` at startup
4. **Document new settings**: Update this file when adding config
5. **Provide defaults**: All config should have sensible defaults

## Migration Guide

To migrate existing code to use the config module:

1. **Identify hardcoded values**:
   ```python
   # Before
   model = "openai:gpt-4.1"
   ```

2. **Import from config**:
   ```python
   # After
   from config import DEFAULT_MODEL
   model = DEFAULT_MODEL
   ```

3. **Remove path manipulation** (if using editable install):
   ```python
   # Before
   sys.path.insert(0, str(Path(__file__).parent.parent.parent))
   
   # After
   # (Remove - not needed with editable install)
   ```

4. **Update `.env` file**:
   ```bash
   # Add new configuration options
   DEFAULT_LLM_MODEL=openai:gpt-4o
   USER_EMAIL=your@email.com
   ```

## Summary

The configuration module provides:

- ✅ **Centralized management**: One place for all settings
- ✅ **Environment support**: Easy `.env` file integration
- ✅ **Type safety**: Proper types for all values
- ✅ **Validation**: Ensures required config is present
- ✅ **Maintainability**: Easy to update and extend
- ✅ **Clean code**: No more awkward path manipulation

For questions or issues, see `config.py` source code or the main README.
