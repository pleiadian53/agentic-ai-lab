# Research Agent Web Service - Quick Start Guide

Get your Research Agent web service up and running in minutes!

## Prerequisites

1. **Environment**: Ensure you're in the `agentic-ai` conda environment
2. **Dependencies**: Install FastAPI and related packages
3. **API Keys**: Set up your OpenAI and Tavily API keys

## Installation

### Step 1: Activate Environment

```bash
mamba activate agentic-ai
```

### Step 2: Install Dependencies

```bash
pip install fastapi uvicorn jinja2 python-multipart markdown
```

### Step 3: Set API Keys

Create or update `.env` in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Starting the Server

### Option 1: Using the Startup Script (Recommended)

```bash
cd multiagent/research_agent/server
./start_server.sh
```

### Option 2: Manual Start

```bash
cd multiagent/research_agent/server
python -m uvicorn research_service:app --host 0.0.0.0 --port 8004 --reload
```

## Stopping the Server

### Graceful Shutdown (Recommended)

```bash
cd multiagent/research_agent/server
./stop_server.sh
```

This script will:
- Find the process running on port 8004
- Attempt graceful shutdown (SIGTERM)
- Force kill if necessary (SIGKILL)
- Verify the server stopped

### Alternative: Manual Stop

Press `Ctrl+C` in the terminal where the server is running.

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Research Agent API...
INFO:     ✓ AISuite client initialized
INFO:     ✓ Project root: /path/to/agentic-ai-lab
INFO:     ✓ Output directory: /path/to/agentic-ai-lab/output/research_reports
INFO:     Research Agent API ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8004
```

## Using the Web Interface

### 1. Open Your Browser

Navigate to: `http://localhost:8004`

### 2. Generate a Report

Fill in the form:
- **Research Topic**: e.g., "Recent advances in CRISPR gene editing"
- **Model**: Choose from:
  - Development: GPT-4o Mini, GPT-5.1 Codex Mini
  - Production: GPT-4o, GPT-5, O4 Mini
  - Premium: GPT-5.1, GPT-5.1 Codex, GPT-5 Pro, GPT-5 Codex
- **Report Length**: Brief (2-3 pages), Standard (5-10 pages), Comprehensive (15-25 pages), or Technical Paper (25-40 pages)
- **Context** (optional): e.g., "Follow Nature Methods style. Focus on clinical applications." (dates auto-added if not specified)

Click **"Generate Report"** and wait (typically 2-5 minutes).

### 3. View Your Report

Once generated, you'll be redirected to a beautifully formatted HTML view with:
- Markdown content rendered as styled HTML
- Download button for the original markdown file
- Navigation back to home

### 4. Browse Previous Reports

The home page lists all previously generated reports with:
- Topic name
- Creation date and time
- File size
- View and Download buttons

## API Usage

### Generate Report via API

```bash
curl -X POST http://localhost:8004/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Quantum error correction advances",
    "model": "openai:gpt-4o-mini",
    "context": "Focus on surface codes and topological methods"
  }'
```

### List All Reports

```bash
curl http://localhost:8004/api/reports
```

### Get Specific Report

```bash
curl http://localhost:8004/api/reports/quantum_error_correction/report_2025-11-21_14-30.md
```

### Download Report

```bash
curl -O http://localhost:8004/download/quantum_error_correction/report_2025-11-21_14-30.md
```

## What Happens Behind the Scenes

When you generate a report, the system:

1. **Planner Agent** creates a research plan (e.g., "Search arXiv for papers", "Draft introduction", etc.)
2. **Executor Agent** routes each step to the appropriate specialist:
   - **Research Agent**: Searches arXiv, Europe PMC, Tavily, Wikipedia
   - **Writer Agent**: Drafts sections with engaging narratives
   - **Editor Agent**: Refines for clarity and accuracy
3. **Final Report** is saved to `output/research_reports/{topic}/report_{timestamp}.md`

## Output Location

Reports are saved in:

```
output/research_reports/
├── quantum_error_correction/
│   ├── report_2025-11-21_14-30.md
│   └── report_2025-11-21_16-45.md
├── crispr_gene_editing/
│   └── report_2025-11-20_10-15.md
└── ...
```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8004
lsof -i :8004

# Kill the process
kill -9 <PID>
```

### Module Not Found

```bash
# Ensure you're in the right environment
mamba activate agentic-ai

# Reinstall dependencies
pip install fastapi uvicorn jinja2 markdown
```

### API Keys Not Working

```bash
# Check .env file exists in project root
ls -la .env

# Verify keys are set
cat .env | grep API_KEY
```

## Next Steps

- **Customize**: Edit `config.py` to change output directories, ports, etc.
- **Extend**: Add new tools in `tools.py` for additional data sources
- **Deploy**: Use production ASGI server like Gunicorn for deployment
- **Integrate**: Call the API from other applications or scripts

## Support

For detailed documentation, see:
- `server/README.md` - Full API documentation
- `docs/MULTIAGENT_WORKFLOW_TUTORIAL.md` - How the multi-agent system works
- Main `README.md` - Package overview and CLI usage

Happy researching! 🔬
