# MCP Server Installation Guide

This guide covers how to install and configure MCP servers, understand different server types, and discover domain-specific servers.

## Table of Contents

1. [Installation Patterns](#installation-patterns)
2. [TypeScript Servers Explained](#typescript-servers-explained)
3. [Finding Domain-Specific MCP Servers](#finding-domain-specific-mcp-servers)
4. [Configuration Reference](#configuration-reference)

---

## Installation Patterns

MCP servers can be implemented in different languages. The installation steps depend on the implementation.

### Pattern 1: Node.js/TypeScript Servers (Most Common)

Most MCP servers are written in TypeScript and compiled to JavaScript.

**Installation steps:**

```bash
# 1. Clone the repository
git clone https://github.com/example/mcp-server-name.git
cd mcp-server-name

# 2. Install Node.js dependencies
npm install

# 3. Compile TypeScript to JavaScript
npm run build
```

**Run the server:**

```bash
node build/index.js
# or
npm start
```

**Configuration:**

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/absolute/path/to/build/index.js"]
    }
  }
}
```

**Examples:** UniProt, AlphaFold, Filesystem, GitHub, Postgres

---

### Pattern 2: Pre-packaged npm Servers

Official and popular servers are published to npm. No cloning or building needed.

**Run directly with npx:**

```bash
# npx downloads and runs the package temporarily
npx @modelcontextprotocol/server-filesystem /path/to/directory
```

**Or install globally:**

```bash
npm install -g @modelcontextprotocol/server-filesystem
mcp-server-filesystem /path/to/directory
```

**Configuration:**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

The `-y` flag auto-confirms the installation prompt.

**Examples:** @modelcontextprotocol/server-filesystem, @modelcontextprotocol/server-github

---

### Pattern 3: Python Servers (From Source)

Python servers use the `mcp` SDK with FastMCP or low-level implementation.

**Installation steps:**

```bash
# 1. Clone the repository
git clone https://github.com/example/mcp-server-python.git
cd mcp-server-python

# 2. Install dependencies
pip install -r requirements.txt
# or
pip install -e .
```

**Run the server:**

```bash
python server.py
# or with uv
uv run server.py
```

**Configuration:**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "cwd": "/path/to/server/directory"
    }
  }
}
```

**Examples:** Custom servers like our `research_server.py`

---

### Pattern 4: Pre-packaged Python Servers (uvx/pipx)

Some Python servers are published to PyPI and can be run without cloning.

**Run directly with uvx:**

```bash
# uvx downloads and runs the package
uvx mcp-server-fetch
```

**Or install with pip:**

```bash
pip install mcp-server-fetch
mcp-server-fetch
```

**Configuration:**

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

**Examples:** mcp-server-fetch, mcp-server-time

---

## TypeScript Servers Explained

### What is TypeScript?

**TypeScript** is a programming language developed by Microsoft that extends JavaScript with static type checking.

```typescript
// TypeScript: Types are explicit
function greet(name: string): string {
  return `Hello, ${name}`;
}

// JavaScript: No type annotations
function greet(name) {
  return `Hello, ${name}`;
}
```

### Why TypeScript for MCP Servers?

1. **Type Safety**: Catches errors at compile time, not runtime
2. **Better Tooling**: IDEs provide better autocomplete and error detection
3. **MCP SDK**: The official MCP TypeScript SDK is well-maintained
4. **Node.js Ecosystem**: Access to npm's vast package library

### The Build Step

TypeScript cannot run directly—it must be **compiled** to JavaScript:

```
source/           →  npm run build  →  build/
├── index.ts                         ├── index.js
├── tools.ts                         ├── tools.js
└── utils.ts                         └── utils.js
```

This is why TypeScript servers require `npm run build` before running.

### TypeScript vs Python for MCP Servers

| Aspect | TypeScript | Python |
|--------|------------|--------|
| **Build step** | Required (`npm run build`) | Not needed |
| **Runtime** | Node.js | Python interpreter |
| **Package manager** | npm | pip/uv |
| **MCP SDK** | `@modelcontextprotocol/sdk` | `mcp` |
| **Framework** | Low-level SDK | FastMCP (high-level) |
| **Best for** | Web integrations, APIs | ML/AI, scientific computing |

### When to Choose Each

- **TypeScript**: Web APIs, database integrations, existing npm packages
- **Python**: Machine learning models (ESM-2, etc.), scientific computing, data analysis

---

## Finding Domain-Specific MCP Servers

### Official Resources

#### 1. MCP Server Registry (GitHub)

**URL**: https://github.com/modelcontextprotocol/servers

The official list of MCP servers maintained by Anthropic. Includes:
- Reference implementations
- Community contributions
- Categorized by function

#### 2. Awesome MCP Servers

**URL**: https://github.com/punkpeye/awesome-mcp-servers

Community-curated list organized by category:
- Databases
- Developer Tools
- Knowledge & Memory
- Web & Browser
- Science & Research
- And more...

#### 3. MCP Hub / PulseMCP

**URL**: https://www.pulsemcp.com/servers

Searchable directory with:
- Server descriptions
- Installation instructions
- User ratings

#### 4. Smithery

**URL**: https://smithery.ai/

MCP server marketplace with:
- One-click installation
- Server discovery
- Integration guides

---

### Search Strategies for Domain-Specific Servers

#### GitHub Search

```
# Search for MCP servers in a specific domain
"mcp server" bioinformatics
"model context protocol" protein
"fastmcp" genomics
```

#### npm Search

```bash
npm search mcp-server
npm search @modelcontextprotocol
```

#### PyPI Search

```bash
pip search mcp-server  # Note: pip search is often disabled
# Use https://pypi.org/search/?q=mcp instead
```

---

### Domain-Specific Server Examples

#### Bioinformatics / Life Sciences

| Server | Description | Source |
|--------|-------------|--------|
| **UniProt MCP** | Protein database queries | [GitHub](https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server) |
| **AlphaFold MCP** | Protein structure predictions | [GitHub](https://github.com/Augmented-Nature/AlphaFold-MCP-Server) |
| **BioMCP** | General bioinformatics tools | Community |

#### Data & Databases

| Server | Description | Source |
|--------|-------------|--------|
| **Postgres MCP** | PostgreSQL queries | Official |
| **SQLite MCP** | SQLite database access | Official |
| **MongoDB MCP** | MongoDB operations | Community |

#### Research & Knowledge

| Server | Description | Source |
|--------|-------------|--------|
| **arXiv MCP** | Academic paper search | Community |
| **PubMed MCP** | Medical literature | Community |
| **Wikipedia MCP** | Wikipedia queries | Community |

#### Developer Tools

| Server | Description | Source |
|--------|-------------|--------|
| **GitHub MCP** | Repository operations | Official |
| **GitLab MCP** | GitLab integration | Community |
| **Jira MCP** | Issue tracking | Community |

#### Web & APIs

| Server | Description | Source |
|--------|-------------|--------|
| **Fetch MCP** | HTTP requests | Official |
| **Brave Search MCP** | Web search | Official |
| **Puppeteer MCP** | Browser automation | Official |

---

### Building Your Own Domain-Specific Server

If no existing server fits your needs, build your own using:

**Python (recommended for ML/scientific):**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-domain-server")

@mcp.tool()
def my_domain_tool(param: str) -> dict:
    """Description of what this tool does."""
    # Your domain logic here
    return {"result": "..."}

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**TypeScript:**

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-domain-server",
  version: "1.0.0",
}, {
  capabilities: { tools: {} }
});

// Define tools...

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## Configuration Reference

### Full Configuration Options

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",           // Required: executable
      "args": ["path/to/server"],  // Required: command arguments
      "env": {                     // Optional: environment variables
        "API_KEY": "secret",
        "LOG_LEVEL": "debug"
      },
      "cwd": "/working/directory", // Optional: working directory
      "disabled": false            // Optional: skip this server
    }
  }
}
```

### Configuration File Locations

| Client | Config Path |
|--------|-------------|
| **Claude Desktop (macOS)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop (Windows)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | Settings → MCP Servers |
| **Custom Python Client** | Your own `server_config.json` |

### Environment Variable Expansion

Some clients support environment variable expansion:

```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}"
  }
}
```

This pulls `MY_API_KEY` from your shell environment.

---

## Quick Reference

| Server Type | Install | Build | Run | Config Command |
|-------------|---------|-------|-----|----------------|
| npm (published) | — | — | `npx @pkg/server` | `"npx"` |
| npm (source) | `npm install` | `npm run build` | `node build/index.js` | `"node"` |
| Python (published) | — | — | `uvx pkg` | `"uvx"` |
| Python (source) | `pip install -r requirements.txt` | — | `python server.py` | `"python"` |
