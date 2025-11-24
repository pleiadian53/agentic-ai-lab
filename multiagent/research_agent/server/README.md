# Research Agent Web Service

FastAPI-based web service for generating, viewing, and downloading AI-powered research reports using a multi-agent system.

## Features

- **🎯 Research Report Generation**: Generate comprehensive research reports on any topic
- **📊 Multi-Agent Architecture**: Leverages Planner, Research, Writer, and Editor agents
- **🌐 Web Interface**: Beautiful, responsive UI for browsing and viewing reports
- **📥 Download Support**: Download reports as Markdown files
- **🔍 Multiple Data Sources**: arXiv, Europe PMC, Tavily web search, Wikipedia
- **🤖 Model Selection**: Support for GPT-4o, GPT-5, and other OpenAI models

## Architecture

```
multiagent/research_agent/server/
├── research_service.py    # FastAPI application
├── config.py              # Configuration and path management
├── schemas.py             # Pydantic request/response models
├── templates/             # Jinja2 HTML templates
│   ├── index.html        # Home page with report list
│   └── report.html       # Report viewing page
├── static/               # Static assets (CSS, JS, images)
└── start_server.sh       # Server startup script
```

## Installation

### Prerequisites

```bash
# Ensure you're in the agentic-ai environment
mamba activate agentic-ai

# Install additional dependencies
pip install fastapi uvicorn jinja2 python-multipart markdown
```

### Environment Variables

Ensure these are set in your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key  # For web search
```

## Usage

### Starting the Server

```bash
# From the server directory
cd multiagent/research_agent/server
./start_server.sh

# Or manually
python -m uvicorn research_service:app --host 0.0.0.0 --port 8004 --reload
```

The server will start on `http://localhost:8004`

### Stopping the Server

```bash
# Graceful shutdown
./stop_server.sh

# Or press Ctrl+C in the terminal running the server
```

### Web Interface

1. **Home Page** (`http://localhost:8004`):
   - Form to generate new research reports
   - List of previously generated reports
   - Model selection (GPT-4o Mini, GPT-4o, O4 Mini, GPT-5 Codex Mini)

2. **Report View** (`/view/{topic}/{filename}`):
   - Beautifully formatted HTML rendering of the markdown report
   - Download button for the original markdown file
   - Navigation back to home

3. **Download** (`/download/{topic}/{filename}`):
   - Direct download of markdown file

### API Endpoints

#### Generate Report

```bash
POST /api/generate
Content-Type: application/json

{
  "topic": "Recent advances in quantum error correction",
  "model": "openai:gpt-4o-mini",
  "context": "Focus on papers from 2024-2025"
}
```

**Response:**
```json
{
  "success": true,
  "topic": "quantum_error_correction",
  "report_path": "output/research_reports/quantum_error_correction/report_2025-11-21.md",
  "report_content": "# Research Report...",
  "execution_history": [...]
}
```

#### List Reports

```bash
GET /api/reports
```

**Response:**
```json
{
  "reports": [
    {
      "topic": "quantum_error_correction",
      "report_path": "quantum_error_correction/report_2025-11-21.md",
      "created": 1700000000.0,
      "size_kb": 45.2
    }
  ],
  "total": 1
}
```

#### Get Specific Report

```bash
GET /api/reports/{topic}/{filename}
```

**Response:**
```json
{
  "success": true,
  "topic": "quantum_error_correction",
  "report_content": "# Research Report...",
  "created": 1700000000.0,
  "size_kb": 45.2,
  "download_url": "/download/quantum_error_correction/report_2025-11-21.md"
}
```

#### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Research Agent API",
  "version": "1.0.0"
}
```

## Configuration

Edit `config.py` to customize:

- **Output Directory**: `OUTPUT_DIR = PROJECT_ROOT / "output" / "research_reports"`
- **Server Port**: `PORT = 8004`
- **CORS Origins**: `CORS_ORIGINS = ["*"]`
- **Default Model**: `DEFAULT_MODEL = "openai:gpt-4o-mini"`

## Multi-Agent Workflow

When you submit a research topic, the system:

1. **Planner Agent**: Creates a step-by-step research plan
2. **Executor Agent**: Routes each step to the appropriate specialist:
   - **Research Agent**: Searches arXiv, Europe PMC, web, Wikipedia
   - **Writer Agent**: Drafts sections with engaging narratives
   - **Editor Agent**: Refines for clarity, accuracy, and style
3. **Final Report**: Saved as Markdown in `output/research_reports/{topic}/`

## Output Structure

```
output/research_reports/
├── quantum_error_correction/
│   ├── report_2025-11-21_14-30.md
│   └── report_2025-11-21_16-45.md
├── crispr_gene_editing/
│   └── report_2025-11-20_10-15.md
└── ...
```

## Development

### Running Tests

```bash
# Test the API
curl http://localhost:8004/health

# Generate a report via API
curl -X POST http://localhost:8004/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "CRISPR gene editing advances",
    "model": "openai:gpt-4o-mini"
  }'
```

### Debugging

- Logs are output to console with INFO level
- Check `uvicorn` logs for request/response details
- Inspect `output/research_reports/` for generated files

## Comparison with chart_agent

| Feature | chart_agent | research_agent |
|---------|-------------|----------------|
| **Purpose** | Generate data visualizations | Generate research reports |
| **Input** | Dataset + question | Research topic |
| **Output** | PDF/PNG charts | Markdown reports |
| **Agents** | Planner, Critic, Executor | Planner, Research, Writer, Editor, Executor |
| **Port** | 8003 | 8004 |
| **Tools** | Matplotlib, Seaborn | arXiv, Europe PMC, Tavily, Wikipedia |

## Troubleshooting

### Server won't start
- Check if port 8004 is already in use: `lsof -i :8004`
- Ensure you're in the correct conda environment
- Verify all dependencies are installed

### Reports not generating
- Check API keys are set in `.env`
- Review logs for error messages
- Ensure internet connection for API calls

### Template not found
- Verify `templates/` directory exists
- Check `TEMPLATES_DIR` path in `config.py`

## Future Enhancements

- [ ] Add PDF export for reports
- [ ] Implement report comparison view
- [ ] Add citation export (BibTeX, RIS)
- [ ] Support for custom research tools
- [ ] Real-time progress updates via WebSocket
- [ ] Report versioning and history
- [ ] Collaborative annotations

## License

Part of the agentic-ai-lab project.
