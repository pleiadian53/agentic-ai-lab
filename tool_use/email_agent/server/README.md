# Email Agent Server

This directory contains the FastAPI server components for the email agent.

## Components

### `email_service.py`
The main email backend service that provides REST API endpoints for email operations.

**Endpoints:**
- `GET /` - Serves the email UI interface
- `GET /emails` - List all emails
- `GET /emails/unread` - List unread emails
- `GET /emails/{id}` - Get specific email
- `GET /emails/search?q=...` - Search emails
- `GET /emails/filter` - Filter emails by criteria
- `POST /send` - Send a new email
- `PATCH /emails/{id}/read` - Mark email as read
- `PATCH /emails/{id}/unread` - Mark email as unread
- `DELETE /emails/{id}` - Delete an email
- `GET /reset_database` - Reset database to initial state

**Start the server:**
```bash
cd tool_use/email_agent/server
uvicorn email_service:app --reload --timeout-keep-alive 1200
```

### `llm_service.py`
The LLM orchestration service that handles natural language requests and executes email tools.

**Endpoints:**
- `POST /prompt` - Send a natural language prompt to the LLM agent

**Start the service:**
```bash
cd tool_use/email_agent/server
uvicorn llm_service:app --port 8001 --reload --timeout-keep-alive 1200
```

## Template System

The server uses a **priority-based template search** system:

### Search Priority

1. **`server/templates/`** (highest priority)
   - Server-specific templates
   - Overrides shared templates
   - Create this directory to customize server UI

2. **`../static/`** (fallback)
   - Shared templates across the email agent
   - Default location for `ui_all.html`

### How It Works

```python
# Template search paths (in order):
_TEMPLATE_SEARCH_PATHS = [
    "server/templates/",  # Check here first
    "../static/",         # Fallback to shared templates
]
```

When you request a template (e.g., `ui_all.html`):
1. Server looks in `server/templates/ui_all.html` first
2. If not found, looks in `../static/ui_all.html`
3. Uses the first match found

### Creating Custom Templates

To override the default UI:

```bash
# Create templates directory
mkdir -p server/templates

# Copy and customize the template
cp ../static/ui_all.html server/templates/ui_all.html

# Edit your custom version
nano server/templates/ui_all.html
```

Your custom template will now be used instead of the shared one!

### Benefits

- ✅ **Flexibility**: Override specific templates without modifying shared files
- ✅ **Separation**: Server-specific UI separate from shared resources
- ✅ **Fallback**: Graceful degradation to shared templates
- ✅ **No duplication**: Only customize what you need

## Database

The email service uses SQLite for data storage:

- **Location**: `../emails.db` (in email_agent directory)
- **Schema**: Defined in `email_models.py`
- **ORM**: SQLAlchemy

### Reset Database

```bash
curl http://localhost:8000/reset_database
```

Or from Python:
```python
from utils import reset_database
reset_database()
```

## Configuration

The servers use the centralized configuration from `../config.py`:

```python
from config import (
    EMAIL_SERVER_URL,
    DEFAULT_MODEL,
    USER_EMAIL,
    CORS_ORIGINS,
)
```

See `../CONFIGURATION.md` for details.

## Development

### Running Both Services

**Terminal 1 - Email Service:**
```bash
cd tool_use/email_agent/server
uvicorn email_service:app --reload --timeout-keep-alive 1200
```

**Terminal 2 - LLM Service:**
```bash
cd tool_use/email_agent/server
uvicorn llm_service:app --port 8001 --reload --timeout-keep-alive 1200
```

### Testing Endpoints

```bash
# List all emails
curl http://localhost:8000/emails

# Search emails
curl "http://localhost:8000/emails/search?q=lunch"

# Send email
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"test@example.com","subject":"Test","body":"Hello"}'

# Test LLM service
curl -X POST http://localhost:8001/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt":"List all unread emails"}'
```

### Auto-Reload

Both services use `--reload` flag for development:
- ✅ Automatically restart when code changes
- ✅ No need to manually restart after edits
- ⚠️ Don't use in production (use `--workers` instead)

## Production Deployment

For production, use multiple workers and remove `--reload`:

```bash
# Email service (production)
uvicorn email_service:app --host 0.0.0.0 --port 8000 --workers 4

# LLM service (production)
uvicorn llm_service:app --host 0.0.0.0 --port 8001 --workers 2
```

## Troubleshooting

### Template Not Found

**Error:** `jinja2.exceptions.TemplateNotFound: 'ui_all.html'`

**Solution:** Ensure `../static/ui_all.html` exists or create `server/templates/ui_all.html`

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'config'`

**Solution:** Install the project in editable mode:
```bash
cd /path/to/agentic-ai-lab
pip install -e .
```

## Architecture

```
server/
├── email_service.py      # Email backend API
├── llm_service.py        # LLM orchestration
├── email_database.py     # Database connection
├── email_models.py       # SQLAlchemy models
├── email_schema.py       # Pydantic schemas
├── templates/            # Server-specific templates (optional)
│   └── ui_all.html      # Custom UI (overrides ../static/)
└── README.md            # This file

../
├── static/              # Shared templates (fallback)
│   └── ui_all.html     # Default UI
├── config.py           # Centralized configuration
└── utils.py            # Utility functions
```

## See Also

- `../QUICKSTART.md` - Getting started guide
- `../CONFIGURATION.md` - Configuration documentation
- `../INTEGRATION.md` - Architecture overview
- `../notebooks/` - Jupyter notebook demos
