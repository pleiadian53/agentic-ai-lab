# Lesson 3: Chatbot Example with Tool Use

This lesson introduces a chatbot that uses Claude's tool use capability to search and retrieve information from arXiv papers.

## Overview

The chatbot demonstrates:
- **Tool definitions**: Defining tools with JSON schemas for Claude
- **Tool execution**: Mapping tool calls to Python functions
- **Agentic loop**: Processing queries with iterative tool use until completion

## Prerequisites

- Python 3.10+
- Anthropic API key in `.env` file (or parent directory)
- Dependencies: `anthropic`, `arxiv`, `python-dotenv`

## Quick Start

1. Ensure your `.env` file contains:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Open `L3.ipynb` and run all cells

3. Interact with the chatbot:
   ```
   Query: Search for 2 papers on "LLM interpretability"
   ```

## Project Structure

```
L3/
├── L3.ipynb              # Main notebook
├── README.md             # This file
├── docs/
│   └── TOOL_USE_TUTORIAL.md  # Detailed code walkthrough
└── papers/               # Generated paper info (created at runtime)
    └── <topic>/
        └── papers_info.json
```

## Tools Available

| Tool | Description |
|------|-------------|
| `search_papers` | Search arXiv for papers on a topic, save metadata to JSON |
| `extract_info` | Retrieve saved information about a specific paper by ID |

## Example Queries

- "Search for 3 papers on transformer architectures"
- "What is paper 2401.05779v4 about?"
- "Find papers about diffusion models and tell me about the first one"

## Documentation

See [docs/TOOL_USE_TUTORIAL.md](docs/TOOL_USE_TUTORIAL.md) for a detailed walkthrough of the code.

## Next Steps

- **L4**: Extract tools into an MCP server
- **L5**: Create an MCP client to connect to the server
