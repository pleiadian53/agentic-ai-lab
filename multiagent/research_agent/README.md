# Research Agent Package

A modular, multi-agent research system refactored from `GL-M5.ipynb`.

## Features
- **Planning Agent**: Generates step-by-step research plans.
- **Research Agent**: Executes search tasks (Arxiv, Tavily, Wikipedia).
- **Executor Agent**: Orchestrates the workflow.
- **Dual-Path API Support**:
  - **Standard**: Uses `aisuite` (Chat Completions) for GPT-4 and compatible models.
  - **Next-Gen**: Uses native `openai` Responses API for GPT-5 (`gpt-5*`, `codex`) models.

## Structure
- `tools.py`: Tool definitions and implementations.
- `agents.py`: Agent logic (Planner, Research, Writer, Editor, Executor).
- `pipeline.py`: High-level workflow.
- `run.py`: CLI entry point.

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
