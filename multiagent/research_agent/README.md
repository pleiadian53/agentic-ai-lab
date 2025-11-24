# Research Agent Package

A modular, multi-agent research system refactored from `GL-M5.ipynb`.

## Features
- **Planning Agent**: Generates step-by-step research plans.
- **Research Agent**: Executes search tasks (arXiv, Europe PMC, Tavily, Wikipedia).
- **Writer Agent**: Drafts engaging, well-structured content.
- **Editor Agent**: Refines for clarity, accuracy, and style.
- **Executor Agent**: Orchestrates the workflow with intelligent routing.
- **Web Interface**: FastAPI-based service for browsing and downloading reports.
- **Dual-Path API Support**:
  - **Standard**: Uses `aisuite` (Chat Completions) for GPT-4 and compatible models.
  - **Next-Gen**: Uses native `openai` Responses API for GPT-5 (`gpt-5*`, `codex`) models.

## Structure
- `tools.py`: Tool definitions and implementations (arXiv, Europe PMC, Tavily, Wikipedia).
- `agents.py`: Agent logic (Planner, Research, Writer, Editor, Executor).
- `pipeline.py`: High-level workflow orchestration.
- `run.py`: CLI entry point.
- `server/`: FastAPI web service for report generation and viewing.
  - `research_service.py`: Main FastAPI application.
  - `templates/`: HTML templates for web interface.
  - `config.py`: Configuration and path management.

## Usage

### CLI
Run a research task from the terminal:

```bash
# Default (GPT-4o via aisuite)
python -m multiagent.research_agent.run "Quantum Computing trends 2025"

# GPT-5 (Responses API)
python -m multiagent.research_agent.run "Quantum Computing trends 2025" --model openai:gpt-5.1-codex-mini
```

### Python API

```python
from multiagent.research_agent.pipeline import generate_research_report

# Run with default model
result = generate_research_report("My Topic")
print(result['final_report'])

# Run with GPT-5
result = generate_research_report("My Topic", model="openai:gpt-5.1-codex-mini")
```

### Web Interface

Start the FastAPI web service for a visual interface:

```bash
# From the server directory
cd multiagent/research_agent/server
./start_server.sh

# Or manually
python -m uvicorn research_service:app --host 0.0.0.0 --port 8004 --reload
```

Then open your browser to `http://localhost:8004` to:
- Generate new research reports with a form interface
- Browse previously generated reports
- View reports in beautifully formatted HTML
- Download reports as Markdown files

See `server/README.md` for detailed API documentation and usage examples.
