# MCP Inspector & FastMCP Tutorial

This tutorial covers two essential tools for MCP development:

1. **MCP Inspector**: Interactive debugging tool for testing MCP servers
2. **FastMCP**: High-level Python framework for building MCP servers

## Table of Contents

1. [MCP Inspector](#mcp-inspector)
   - [What is MCP Inspector?](#what-is-mcp-inspector)
   - [Installation & Launch](#installation--launch)
   - [Inspector Interface](#inspector-interface)
   - [Testing Your Server](#testing-your-server)
2. [FastMCP](#fastmcp)
   - [What is FastMCP?](#what-is-fastmcp)
   - [Core Concepts](#core-concepts)
   - [Building a Server](#building-a-server)
   - [Tools, Resources, and Prompts](#tools-resources-and-prompts)
3. [Putting It Together](#putting-it-together)

---

# MCP Inspector

## What is MCP Inspector?

The MCP Inspector is an interactive developer tool for testing and debugging MCP servers. It provides a web-based UI that lets you:

- Connect to any MCP server
- List and test tools
- Browse and read resources
- Test prompt templates
- View server logs and notifications

Think of it as "Postman for MCP"—a way to manually test your server before integrating it with an LLM client.

## Installation & Launch

### Prerequisites

- **Node.js**: Required to run the Inspector (it's a TypeScript application)
  
  ```bash
  # Check if installed
  node --version
  
  # Install on macOS
  brew install node
  ```

### Basic Usage

The Inspector runs via `npx` (no global installation needed):

```bash
npx @modelcontextprotocol/inspector <command-to-start-server>
```

Here `npx` is the **Node.js package runner** (it comes with `node`/`npm`). It is *not* a package manager itself; instead, it temporarily downloads and runs the `@modelcontextprotocol/inspector` npm package without requiring a global install, then passes the rest of the command (`<command-to-start-server>`) as the way to start your MCP server.

### Examples

**Python server with uv:**

```bash
npx @modelcontextprotocol/inspector uv run research_server.py
```

**Python server with mamba/conda:**

```bash
# If environment is activated:
npx @modelcontextprotocol/inspector python research_server.py

# Explicit environment:
npx @modelcontextprotocol/inspector mamba run -n agentic-ai python research_server.py
```

**TypeScript/Node server:**

```bash
npx @modelcontextprotocol/inspector node path/to/server/index.js
```

**NPM package server:**

```bash
npx @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /path/to/dir
```

**PyPI package server:**

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-git --repository ~/code/repo
```

### What Happens When You Launch

1. Inspector starts a web server (typically on port 6274)
2. Opens a proxy server for MCP communication (port 6277)
3. Spawns your MCP server using the command you provided
4. Connects to your server via stdio transport
5. Displays the web UI in your browser

```
$ npx @modelcontextprotocol/inspector uv run research_server.py

MCP Inspector is up and running at http://localhost:6274
```

## Inspector Interface

The Inspector UI has several key sections:

### Server Connection Pane

- **Transport**: Select stdio (local) or SSE (remote)
- **Command**: The command to run your server (e.g., `uv`)
- **Arguments**: Arguments for the command (e.g., `run research_server.py`)
- **Environment**: Set environment variables for your server

### Tools Tab

- Lists all tools exposed by your server
- Shows tool schemas (parameters, types, descriptions)
- Provides input forms to test tools with custom arguments
- Displays tool execution results

### Resources Tab

- Lists all available resources
- Shows resource metadata (MIME types, descriptions)
- Allows reading resource contents
- Supports testing resource subscriptions

### Prompts Tab

- Displays available prompt templates
- Shows prompt arguments and descriptions
- Enables testing prompts with custom arguments
- Previews generated messages

### Notifications Pane

- Shows server logs
- Displays notifications from the server
- Useful for debugging server behavior

## Testing Your Server

### Step-by-Step Workflow

1. **Launch Inspector with your server:**
   
   ```bash
   cd mcp_project
   npx @modelcontextprotocol/inspector uv run research_server.py
   ```

2. **Open the Inspector UI** (click the URL shown in terminal)

3. **Connect to your server:**
   - Verify Command: `uv`
   - Verify Arguments: `run research_server.py`
   - Click "Connect"

4. **Test a tool:**
   - Go to "Tools" tab
   - Click on `search_papers`
   - Enter a topic: `"machine learning"`
   - Click "Run Tool"
   - View the results

5. **Check the output:**
   - Tool results appear in the response pane
   - Check the `papers/` directory for saved JSON files

---

# FastMCP

## What is FastMCP?

FastMCP is a high-level Python framework for building MCP servers. It handles all the protocol complexity, letting you focus on writing Python functions.

**Key benefits:**

- **Decorator-based**: Use `@mcp.tool()` to expose functions as tools
- **Auto-schema generation**: Generates JSON schemas from type hints and docstrings
- **Transport handling**: Manages stdio, SSE, and other transports
- **Minimal boilerplate**: A complete server in ~10 lines of code

### History

- FastMCP was created by [Jeremiah Lowin](https://github.com/jlowin)
- FastMCP 1.0 was incorporated into the official MCP Python SDK
- FastMCP 2.0 is the actively maintained, production-ready framework

## Core Concepts

### MCP Primitives

MCP servers can expose three types of capabilities:

| Primitive | Purpose | Example |
|-----------|---------|---------|
| **Tools** | Actions the LLM can invoke | Search papers, send email, query database |
| **Resources** | Data the LLM can read | Config files, documentation, API responses |
| **Prompts** | Reusable prompt templates | System prompts, task templates |

### How FastMCP Maps Python to MCP

```python
@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results (default: 5)
    """
    # Implementation...
```

FastMCP automatically extracts:

- **Tool name**: `search_papers` (from function name)
- **Description**: From the docstring's first line
- **Input schema**: From type hints (`topic: str`, `max_results: int`)
- **Parameter descriptions**: From docstring's Args section

## Building a Server

### Minimal Example

```python
from mcp.server.fastmcp import FastMCP

# Create server instance
mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

### Server Initialization Options

```python
# Basic
mcp = FastMCP("server-name")

# With configuration
mcp = FastMCP(
    name="research-server",
    version="1.0.0",
)
```

### Running the Server

```python
if __name__ == "__main__":
    # stdio transport (for local use, Claude Desktop, Inspector)
    mcp.run(transport='stdio')
    
    # SSE transport (for remote/web use)
    # mcp.run(transport='sse', port=8000)
```

## Tools, Resources, and Prompts

### Tools

Tools are functions the LLM can call to perform actions:

```python
@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve
        
    Returns:
        List of paper IDs found in the search
    """
    # Your implementation here
    client = arxiv.Client()
    search = arxiv.Search(query=topic, max_results=max_results)
    return [paper.get_short_id() for paper in client.results(search)]
```

**Best practices:**

- Use clear, descriptive function names
- Add comprehensive docstrings (LLM uses these!)
- Use type hints for all parameters
- Return strings or JSON-serializable objects

### Resources

Resources expose data that the LLM can read:

```python
# Static resource
@mcp.resource("resource://config")
def get_config() -> dict:
    """Provides the application's configuration."""
    return {"version": "1.0", "author": "MyTeam"}

# Dynamic resource template
@mcp.resource("papers://{paper_id}")
def get_paper(paper_id: str) -> str:
    """Get information about a specific paper."""
    # Load paper info from storage
    return json.dumps(paper_info)
```

**Resource URIs:**

- Static: `resource://config` → always calls `get_config()`
- Template: `papers://{paper_id}` → `papers://2401.05779` calls `get_paper("2401.05779")`

### Prompts

Prompts are reusable templates:

```python
@mcp.prompt()
def research_prompt(topic: str) -> str:
    """Generate a research prompt for a given topic."""
    return f"""You are a research assistant. 
    
Please search for papers about: {topic}

For each paper found:
1. Summarize the key findings
2. Note the methodology
3. Identify potential applications
"""
```

---

# Putting It Together

## Complete L4 Server Example

```python
# research_server.py
import arxiv
import json
import os
from typing import List
from mcp.server.fastmcp import FastMCP

PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = client.results(search)
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")
    
    try:
        with open(file_path, "r") as f:
            papers_info = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}
    
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        papers_info[paper.get_short_id()] = {
            'title': paper.title,
            'authors': [a.name for a in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
    
    with open(file_path, "w") as f:
        json.dump(papers_info, f, indent=2)
    
    return paper_ids

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found
    """
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    papers_info = json.load(f)
                    if paper_id in papers_info:
                        return json.dumps(papers_info[paper_id], indent=2)
    
    return f"No information found for paper {paper_id}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

## Testing Workflow

```bash
# 1. Navigate to project
cd mcp/L4/mcp_project

# 2. Set up environment (choose one)
# Option A: uv
uv init && uv venv && source .venv/bin/activate && uv add mcp arxiv

# Option B: mamba (if deps already installed)
mamba activate agentic-ai

# 3. Launch Inspector
npx @modelcontextprotocol/inspector uv run research_server.py
# OR
npx @modelcontextprotocol/inspector python research_server.py

# 4. Open browser to http://localhost:6274

# 5. Test tools in the Inspector UI
```

---

## Resources

### MCP Inspector

- [Official Documentation](https://modelcontextprotocol.io/docs/tools/inspector)
- [GitHub Repository](https://github.com/modelcontextprotocol/inspector)
- [Debugging Guide](https://modelcontextprotocol.io/docs/tools/debugging)

### FastMCP

- [FastMCP Documentation](https://gofastmcp.com/)
- [GitHub Repository](https://github.com/jlowin/fastmcp)
- [Tutorial: Create MCP Server](https://gofastmcp.com/tutorials/create-mcp-server)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### MCP Protocol

- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Quickstart](https://modelcontextprotocol.io/quickstart/server)
