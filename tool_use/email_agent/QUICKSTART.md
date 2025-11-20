# Email Agent Quick Start Guide

This guide walks you through setting up and running the email agent demo from scratch.

## Prerequisites

- Python 3.10+ with `agentic-ai` conda/mamba environment activated
- Project installed in editable mode: `pip install -e .`
- API keys for OpenAI or other LLM providers

## Step-by-Step Setup

### 1. Set Up Environment Variables

The email agent will automatically use API keys from the **project root `.env` file** (`agentic-ai-lab/.env`).

If you need email-agent-specific settings, you can optionally create a local `.env`:

```bash
# Optional: Create local .env for email-agent-specific settings
cd tool_use/email_agent
cp env.template .env
```

**Required setting** (add to project root `.env` or local `.env`):

```bash
M3_EMAIL_SERVER_API_URL=http://localhost:8000
```

Your OpenAI API key from the project root `.env` will be automatically used! ✅

### 2. Start the Email Server

The email server must be running before you can use the notebook or LLM service.

**Terminal 1 - Email Server (Easy Way):**

```bash
# Activate environment
mamba activate agentic-ai

# From project root, run the startup script
./scripts/agents/start_email_agent.sh --email-only
```

**Alternative - Manual Start:**

```bash
# Navigate to server directory
cd tool_use/email_agent/server

# Start the email service
uvicorn email_service:app --reload --timeout-keep-alive 1200
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal running!** The server needs to stay active.

### 3. Verify Server is Running

In a new terminal:

```bash
mamba activate agentic-ai
curl http://localhost:8000/emails
```

You should see a JSON response with preloaded emails.

### 4. (Optional) Start the LLM Service

If you want to use the REST API for the LLM agent:

**Terminal 2 - LLM Service (Easy Way):**

```bash
# Activate environment
mamba activate agentic-ai

# From project root, run the startup script
./scripts/agents/start_email_agent.sh --llm-only
```

**Alternative - Manual Start:**

```bash
# Navigate to server directory
cd tool_use/email_agent/server

# Start the LLM service on a different port
uvicorn llm_service:app --port 8001 --reload --timeout-keep-alive 1200
```

### 5. Run the Notebook

Now you can run the notebook:

```bash
# Activate environment
mamba activate agentic-ai

# Start Jupyter from the project root
cd /Users/pleiadian53/work/agentic-ai-lab
jupyter lab tool_use/email_agent/notebooks/email_agent_demo.ipynb
```

Or from the notebooks directory:

```bash
cd /Users/pleiadian53/work/agentic-ai-lab/tool_use/email_agent/notebooks
jupyter lab email_agent_demo.ipynb
```

## Troubleshooting

### Error: "Invalid URL 'None/send'"

**Problem**: The `M3_EMAIL_SERVER_API_URL` environment variable is not set.

**Solution**:
1. Make sure `.env` file exists in `tool_use/email_agent/`
2. Add this line to `.env`:
   ```
   M3_EMAIL_SERVER_API_URL=http://localhost:8000
   ```
3. Restart your Jupyter kernel (Kernel → Restart Kernel)
4. Re-run the import cell

### Error: "Connection refused"

**Problem**: The email server is not running.

**Solution**: Start the email server (see Step 2 above)

### Error: "ModuleNotFoundError: No module named 'tool_use'"

**Problem**: Package not installed in editable mode.

**Solution**:
```bash
mamba activate agentic-ai
cd /Users/pleiadian53/work/agentic-ai-lab
pip install -e .
```

Then restart your Jupyter kernel.

### Server Already Running

If you see "Address already in use":

```bash
# Find the process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn email_service:app --port 8001
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Jupyter Notebook (email_agent_demo.ipynb)              │
│ - Interactive demos                                     │
│ - Direct Python calls to tools                          │
│ - LLM orchestration                                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ├─→ Imports utils.py (email_agent/)
                      ├─→ Imports tool_use.email_tools
                      └─→ Imports tool_use.display_functions
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│ Email Server (email_service.py) - Port 8000            │
│ - FastAPI REST API                                      │
│ - SQLite database (emails.db)                           │
│ - CRUD operations for emails                            │
└─────────────────────────────────────────────────────────┘
                      ↑
                      │ HTTP requests
                      │
┌─────────────────────────────────────────────────────────┐
│ Email Tools (tool_use/email_tools.py)                  │
│ - Python functions wrapping REST endpoints              │
│ - Used by LLM as tools                                  │
└─────────────────────────────────────────────────────────┘
                      ↑
                      │
┌─────────────────────────────────────────────────────────┐
│ LLM (via AISuite)                                       │
│ - Receives natural language requests                    │
│ - Selects and calls appropriate tools                   │
│ - Returns results                                       │
└─────────────────────────────────────────────────────────┘
```

## What Each Component Does

### Email Server (`email_service.py`)
- **Purpose**: Simulated email backend
- **Technology**: FastAPI + SQLite + SQLAlchemy
- **Endpoints**: `/send`, `/emails`, `/emails/{id}`, `/search`, etc.
- **Must be running**: Yes, before using notebook

### Email Tools (`email_tools.py`)
- **Purpose**: Python functions that wrap REST API calls
- **Used by**: LLM as callable tools
- **Examples**: `send_email()`, `list_all_emails()`, `search_emails()`

### Utils (`utils.py`)
- **Purpose**: Helper functions for testing and display
- **Used by**: Notebook for manual testing
- **Examples**: `test_send_email()`, `reset_database()`

### Display Functions (`display_functions.py`)
- **Purpose**: Pretty-print LLM responses and tool calls
- **Used by**: Notebook for visualization
- **Examples**: `pretty_print_chat_completion()`

### Notebook (`email_agent_demo.ipynb`)
- **Purpose**: Interactive demonstration and learning
- **Shows**: Tool use pattern, LLM orchestration, multi-step workflows

## Usage Patterns

### Pattern 1: Manual Testing (Cell 4)
```python
# Test individual endpoints
new_email_id = utils.test_send_email()
_ = utils.test_get_email(new_email_id['id'])
```

### Pattern 2: Direct Tool Usage (Cell 6)
```python
# Call tools directly
new_email = email_tools.send_email("test@example.com", "Subject", "Body")
content = email_tools.get_email(new_email['id'])
```

### Pattern 3: LLM Orchestration (Cell 14)
```python
# Let LLM decide which tools to use
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    tools=[
        email_tools.search_unread_from_sender,
        email_tools.mark_email_as_read,
        email_tools.send_email
    ],
    max_turns=5
)
```

## Next Steps

1. ✅ Complete this setup guide
2. ✅ Run through the notebook cells in order
3. ✅ Experiment with different prompts
4. ✅ Try adding new tools
5. ✅ Explore the web UI (`static/ui_all.html`)

## Summary

The email agent demonstrates the **tool use pattern**:
1. **Define tools** as Python functions with clear docstrings
2. **Expose tools** to the LLM via AISuite
3. **Give natural language instructions** to the LLM
4. **LLM orchestrates** tool calls to complete tasks
5. **Observe results** and iterate

This pattern enables LLMs to perform complex, multi-step tasks by breaking them down into tool calls!
