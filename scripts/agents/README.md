# Agent Startup Scripts

Convenient scripts to start agent services from anywhere in the project.

## Email Agent Scripts

### Quick Start

**Start email service only** (most common):
```bash
./scripts/agents/start_email_agent.sh --email-only
```

**Start LLM service only** (requires email service running):
```bash
./scripts/agents/start_email_agent.sh --llm-only
```

### Individual Service Scripts

#### Email Service
```bash
./scripts/agents/start_email_server.sh
```

**Options:**
- `--port PORT` - Specify port (default: 8000)
- `--no-reload` - Disable auto-reload
- `--help` - Show help message

**Examples:**
```bash
# Start on default port 8000
./scripts/agents/start_email_server.sh

# Start on custom port
./scripts/agents/start_email_server.sh --port 9000

# Production mode (no auto-reload)
./scripts/agents/start_email_server.sh --no-reload
```

#### LLM Service
```bash
./scripts/agents/start_email_llm_service.sh
```

**Options:**
- `--port PORT` - Specify port (default: 8001)
- `--no-reload` - Disable auto-reload
- `--help` - Show help message

**Examples:**
```bash
# Start on default port 8001
./scripts/agents/start_email_llm_service.sh

# Start on custom port
./scripts/agents/start_email_llm_service.sh --port 9001
```

### Full Stack Script

```bash
./scripts/agents/start_email_agent.sh
```

**Options:**
- `--email-port PORT` - Email service port (default: 8000)
- `--llm-port PORT` - LLM service port (default: 8001)
- `--email-only` - Start only email service
- `--llm-only` - Start only LLM service
- `--no-reload` - Disable auto-reload
- `--help` - Show help message

**Examples:**
```bash
# Start email service only
./scripts/agents/start_email_agent.sh --email-only

# Start LLM service only
./scripts/agents/start_email_agent.sh --llm-only

# Custom ports
./scripts/agents/start_email_agent.sh --email-only --email-port 9000
```

## Features

✅ **Run from anywhere** - No need to navigate to deep directories  
✅ **Auto-configuration** - Creates `.env` if missing  
✅ **Port customization** - Specify custom ports  
✅ **Color output** - Easy to read status messages  
✅ **Error checking** - Validates environment before starting  
✅ **Help messages** - Built-in documentation

## Typical Workflow

### Development

**Terminal 1 - Email Service:**
```bash
./scripts/agents/start_email_agent.sh --email-only
```

**Terminal 2 - LLM Service:**
```bash
./scripts/agents/start_email_agent.sh --llm-only
```

**Terminal 3 - Jupyter:**
```bash
jupyter lab tool_use/email_agent/notebooks/
```

### Testing

```bash
# Start email service
./scripts/agents/start_email_server.sh

# In another terminal, test the API
curl http://localhost:8000/emails
```

## Comparison with Old Method

### Before ❌
```bash
cd /Users/pleiadian53/work/agentic-ai-lab/tool_use/email_agent/server
uvicorn email_service:app --reload --timeout-keep-alive 1200
```

**Issues:**
- Long path to navigate
- Easy to forget flags
- No environment validation
- No helpful output

### After ✅
```bash
./scripts/agents/start_email_agent.sh --email-only
```

**Benefits:**
- Run from project root
- Auto-configuration
- Validates environment
- Color-coded output
- Built-in help

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
./scripts/agents/start_email_server.sh --port 9000
```

### Environment Issues

The scripts will automatically:
- Create `.env` from template if missing
- Add `M3_EMAIL_SERVER_API_URL` if not present
- Validate required files exist

### Import Errors

If you see import errors, ensure the project is installed in editable mode:

```bash
cd /path/to/agentic-ai-lab
pip install -e .
```

## Adding More Agent Scripts

To add scripts for other agents (ml_agent, research_agent), follow this pattern:

```bash
scripts/agents/
├── start_email_server.sh
├── start_email_llm_service.sh
├── start_email_agent.sh
├── start_ml_agent.sh          # Future
├── start_research_agent.sh    # Future
└── README.md
```

Each script should:
1. Find project root automatically
2. Validate environment
3. Provide helpful output
4. Support common options (--port, --no-reload, --help)
