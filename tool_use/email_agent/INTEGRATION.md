# Email Agent Integration with Tool Use Package

## Overview

The **Email Agent** is a self-contained application that demonstrates the **tool use pattern** for agentic workflows. It showcases how an LLM can be equipped with tools to perform complex, multi-step email management tasks.

## Architecture

### Self-Contained + Shared Infrastructure

The email agent follows a hybrid architecture:

```
┌─────────────────────────────────────────────────────────┐
│ Email Agent (Self-Contained Application)                │
│                                                          │
│  ├── server/          Backend services (FastAPI)        │
│  ├── notebooks/       Educational demos                 │
│  ├── static/          Web UI                            │
│  └── utils.py         Agent-specific utilities          │
└─────────────────────────────────────────────────────────┘
                           ↓ imports from
┌─────────────────────────────────────────────────────────┐
│ Tool Use Package (Shared Infrastructure)                │
│                                                          │
│  ├── email_tools.py        Email operation tools        │
│  ├── display_functions.py  Visualization utilities      │
│  ├── client.py             ToolClient wrapper           │
│  └── __init__.py           Package exports              │
└─────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. **Agent-Specific Email Tools**

The `email_tools.py` module is part of the email_agent package:

- **Self-contained**: Each agent manages its own tools
- **Clear ownership**: Tools belong to the email_agent
- **Scalable**: Pattern works for multiple agents

```python
# In email_agent/server/llm_service.py
from email_agent import email_tools

# Use tools
tools=[
    email_tools.list_all_emails,
    email_tools.send_email,
    # ...
]
```

### 2. **Shared Display Functions**

The `display_functions.py` module is shared across all tool use examples:

```python
# In email_agent/server/llm_service.py
from tool_use.display_functions import pretty_print_chat_completion_html
```

This ensures consistent visualization across different applications.

### 3. **Self-Contained Server**

The FastAPI servers (`email_service.py`, `llm_service.py`) are specific to the email agent and remain in `email_agent/server/`. They:

- Provide REST API endpoints for email operations
- Expose LLM agent as a service
- Manage SQLite database for email storage

### 4. **Optional ToolClient Usage**

While the server uses raw `aisuite.Client()`, notebooks and examples can use the higher-level `ToolClient`:

```python
# In notebooks
from tool_use import ToolClient
from email_agent import email_tools

client = ToolClient(model="openai:gpt-4o")
response = client.chat(
    prompt="Check unread emails from boss@email.com",
    tools=[email_tools.search_unread_from_sender],
    max_turns=10
)
```

## Running the Email Agent

### Quick Start

```bash
# 1. Install dependencies
pip install -r tool_use/email_agent/requirements.txt

# 2. Set up environment
cp tool_use/email_agent/env.template tool_use/email_agent/.env
# Edit .env with your API keys

# 3. Start email server
cd tool_use/email_agent/server
uvicorn email_service:app --timeout-keep-alive 1200

# 4. (Optional) Start LLM service
cd tool_use/email_agent/server
uvicorn llm_service:app --port 8001 --timeout-keep-alive 1200

# 5. Use notebook or web UI
jupyter lab tool_use/email_agent/notebooks/email_agent_demo.ipynb
# OR open tool_use/email_agent/static/ui_all.html
```

## Integration Points

### For Other Applications

Other applications in the `tool_use` package can leverage email functionality:

```python
# In another application
from tool_use import ToolClient
from tool_use.email_agent import email_tools

# Use email tools alongside other tools
client = ToolClient()
response = client.chat(
    prompt="Check my emails",
    tools=[email_tools.list_unread_emails],
    max_turns=5
)
```

### For Research Agent Enhancement

The email agent demonstrates patterns that can enhance the research agent:

```python
# In enhanced research agent
from tool_use import ToolClient, email_tools
from tool_use import research_tools  # Future

client = ToolClient()
response = client.chat(
    prompt="Research AI safety and email summary to team@work.com",
    tools=[
        research_tools.search_web,
        research_tools.search_arxiv,
        email_tools.send_email
    ],
    max_turns=15
)
```

## Benefits of This Architecture

### ✅ Modularity
- Email agent can be run independently
- Tools can be used by other applications
- Clear separation of concerns

### ✅ Reusability
- Email tools available to all applications
- Display functions shared across examples
- ToolClient provides consistent interface

### ✅ Maintainability
- Single source of truth for tools
- Centralized infrastructure updates
- Clear dependency hierarchy

### ✅ Educational Value
- Shows complete application structure
- Demonstrates tool use patterns
- Provides working example for learning

## File Organization

```
tool_use/
├── __init__.py                    # Exports: ToolClient, tools, email_tools
├── client.py                      # ToolClient, ToolRegistry
├── tools.py                       # General tools (time, weather, QR, files)
├── email_tools.py                 # Email operation tools
├── display_functions.py           # Visualization utilities
├── utils.py                       # General utilities
│
├── examples/                      # Simple, focused examples
│   ├── basic_tool_usage.py
│   ├── multi_tool_workflow.py
│   └── ...
│
└── email_agent/                   # Complete application
    ├── server/                    # Backend services
    │   ├── email_service.py       # Email REST API
    │   ├── llm_service.py         # LLM agent service
    │   ├── email_models.py        # Database models
    │   ├── email_schema.py        # Pydantic schemas
    │   └── email_database.py      # Database setup
    ├── notebooks/                 # Educational demos
    │   └── email_agent_demo.ipynb
    ├── static/                    # Web UI
    │   └── ui_all.html
    ├── utils.py                   # Agent-specific utilities
    ├── emails.db                  # SQLite database
    ├── requirements.txt           # Dependencies
    ├── env.template               # Environment template
    ├── README.md                  # Usage guide
    └── INTEGRATION.md             # This file
```

## Next Steps

### For Users
1. Follow the Quick Start guide above
2. Explore the notebook for interactive learning
3. Try the web UI for visual interaction
4. Experiment with custom prompts

### For Developers
1. Study the tool definitions in `email_tools.py`
2. Examine the LLM service integration in `llm_service.py`
3. Understand the ToolClient usage patterns
4. Consider building similar applications for other domains

## Comparison: Simple Example vs. Complete Application

### Simple Example (`examples/basic_tool_usage.py`)
- **Purpose**: Demonstrate a single concept
- **Scope**: 50-100 lines of code
- **Dependencies**: Minimal (ToolClient + 1-2 tools)
- **Use Case**: Learning, quick prototyping

### Email Agent (`email_agent/`)
- **Purpose**: Production-ready application
- **Scope**: Complete system with backend, frontend, database
- **Dependencies**: Full stack (FastAPI, SQLAlchemy, etc.)
- **Use Case**: Real-world deployment, comprehensive learning

Both leverage the same shared infrastructure (`ToolClient`, `email_tools`, `display_functions`), demonstrating the power of modular design.

## Summary

The email agent is a **reference implementation** that shows how to build a complete, production-ready application using the tool use pattern. It balances self-containment (can run independently) with integration (leverages shared infrastructure), making it both a learning resource and a template for building similar applications.
