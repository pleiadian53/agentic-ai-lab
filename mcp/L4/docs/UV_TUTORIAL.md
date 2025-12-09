# UV Tutorial: The Fast Python Package Manager

`uv` is an extremely fast Python package and project manager written in Rust by [Astral](https://astral.sh) (the creators of Ruff). It's designed as a drop-in replacement for `pip`, `pip-tools`, `virtualenv`, and more.

## Table of Contents

1. [Why uv?](#why-uv)
2. [Installation](#installation)
3. [Core Commands](#core-commands)
4. [Project Workflow](#project-workflow)
5. [uv vs mamba/conda](#uv-vs-mambaconda)
6. [Using uv with MCP](#using-uv-with-mcp)

---

## Why uv?

| Feature | uv | pip | mamba/conda |
|---------|-----|-----|-------------|
| Speed | 10-100x faster | Baseline | ~2-5x faster than pip |
| Lockfiles | ✅ Built-in | ❌ Needs pip-tools | ✅ conda-lock |
| Virtual envs | ✅ Built-in | ❌ Needs virtualenv | ✅ Built-in |
| Python management | ✅ Can install Python | ❌ | ✅ |
| Binary packages | ❌ PyPI only | ❌ PyPI only | ✅ conda-forge |

**Key advantages:**

- **Speed**: Resolves and installs packages 10-100x faster than pip
- **All-in-one**: Replaces pip, pip-tools, virtualenv, pyenv in a single tool
- **Lockfiles**: Generates reproducible `uv.lock` files
- **Compatibility**: Works with existing `requirements.txt` and `pyproject.toml`

---

## Installation

### macOS/Linux

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using Homebrew
brew install uv

# Using pip (if you already have Python)
pip install uv
```

### Verify Installation

```bash
uv --version
# uv 0.5.x
```

---

## Core Commands

### Project Initialization

```bash
# Initialize a new project (creates pyproject.toml)
uv init

# Initialize with a specific Python version
uv init --python 3.11
```

This creates:

- `pyproject.toml` - Project metadata and dependencies
- `.python-version` - Pinned Python version
- `hello.py` - Sample script

### Virtual Environment Management

```bash
# Create a virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.11

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Dependency Management

```bash
# Add a dependency
uv add requests

# Add multiple dependencies
uv add numpy pandas matplotlib

# Add with version constraint
uv add "requests>=2.28.0"

# Add development dependency
uv add --dev pytest black ruff

# Remove a dependency
uv remove requests

# Sync environment with lockfile
uv sync
```

### Running Scripts

```bash
# Run a Python script (auto-creates venv if needed)
uv run script.py

# Run with arguments
uv run script.py --arg1 value1

# Run a module
uv run -m pytest

# Run in a specific directory
uv --directory path/to/project run script.py
```

### pip-Compatible Commands

```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Install a package
uv pip install requests

# List installed packages
uv pip list

# Freeze dependencies
uv pip freeze > requirements.txt

# Compile requirements (like pip-tools)
uv pip compile requirements.in -o requirements.txt
```

---

## Project Workflow

### Typical Workflow

```bash
# 1. Create project directory
mkdir my_project && cd my_project

# 2. Initialize project
uv init

# 3. Create virtual environment
uv venv

# 4. Activate environment
source .venv/bin/activate

# 5. Add dependencies
uv add fastapi uvicorn

# 6. Run your code
uv run main.py
```

### Project Structure After `uv init`

```
my_project/
├── .python-version    # Python version pin
├── .venv/             # Virtual environment (after uv venv)
├── pyproject.toml     # Project config and dependencies
├── uv.lock            # Lockfile (after uv add)
└── hello.py           # Sample script
```

### Example `pyproject.toml`

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "black>=23.0",
]
```

---

## uv vs mamba/conda

### When to Use uv

- Pure Python projects
- Fast iteration during development
- CI/CD pipelines (speed matters)
- Projects using only PyPI packages
- MCP server development

### When to Use mamba/conda

- Need binary/compiled packages (numpy with MKL, CUDA, etc.)
- System-level dependencies (weasyprint, pandoc, etc.)
- Cross-platform reproducibility
- Scientific computing with complex dependencies
- Need to manage Python version alongside system libs

### Can You Use Both?

**Yes!** A common pattern:

```bash
# Use mamba for the base environment with system deps
mamba activate agentic-ai

# Use uv for fast package operations within that env
uv pip install some-package
```

### Using mamba Instead of uv for L4

The L4 notebook uses `uv` because:

1. It's lightweight and fast for simple projects
2. MCP tutorials target a broad audience (uv is easier to install)
3. The dependencies are pure Python (mcp, arxiv)

**You can absolutely use mamba instead:**

```bash
# Instead of uv workflow:
cd L4/mcp_project
uv init
uv venv
source .venv/bin/activate
uv add mcp arxiv

# Use mamba workflow:
cd L4/mcp_project
mamba activate agentic-ai  # Your existing env already has mcp, arxiv
# No additional setup needed!
```

---

## Using uv with MCP

### The Inspector Command Explained

```bash
npx @modelcontextprotocol/inspector uv run research_server.py
```

Let's break this down:

| Part | What it does |
|------|--------------|
| `npx` | Node.js package runner (runs npm packages without installing globally) |
| `@modelcontextprotocol/inspector` | The MCP Inspector package |
| `uv run research_server.py` | Command passed to Inspector to start your server |

The Inspector:

1. Starts a web UI for testing MCP servers
2. Spawns your server using the command you provide (`uv run research_server.py`)
3. Connects to your server via stdio transport
4. Lets you interactively test tools, resources, and prompts

### Alternative: Using mamba with Inspector

```bash
# If you prefer mamba over uv:
npx @modelcontextprotocol/inspector mamba run -n agentic-ai python research_server.py

# Or if already activated:
mamba activate agentic-ai
npx @modelcontextprotocol/inspector python research_server.py
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Initialize project | `uv init` |
| Create venv | `uv venv` |
| Activate venv | `source .venv/bin/activate` |
| Add package | `uv add <package>` |
| Add dev package | `uv add --dev <package>` |
| Remove package | `uv remove <package>` |
| Run script | `uv run <script.py>` |
| Sync deps | `uv sync` |
| Install from requirements | `uv pip install -r requirements.txt` |

---

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
- [uv vs pip comparison](https://docs.astral.sh/uv/pip/compatibility/)
