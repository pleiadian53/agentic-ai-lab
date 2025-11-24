# Nexus Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip or conda package manager
- Git (for cloning the repository)

## Installation Methods

### Method 1: Mamba/Conda Environment (Recommended)

This project uses **mamba** (or conda) for environment management and **poetry/pip** for package installation.

```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-ai-lab.git
cd agentic-ai-lab

# Create and activate the environment from environment.yml
mamba env create -f environment.yml
mamba activate agentic-ai

# Install the package in editable mode
pip install -e .
```

**Benefits**:
- Consistent environment across team
- All system dependencies included
- Code changes take effect immediately
- Perfect for development

### Method 2: Poetry (Alternative)

If you prefer poetry for dependency management:

```bash
# Install with poetry
poetry install

# Activate the virtual environment
poetry shell

# Or run commands directly
poetry run nexus-research --help
```

### Method 3: Standard pip Install

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

### Method 4: Install with Optional Dependencies

```bash
# Install with development tools
pip install -e ".[dev]"

# Install with all optional dependencies
pip install -e ".[dev,test,docs]"
```

## Verify Installation

After installation, verify that Nexus is properly installed:

```bash
# Test imports
python -c "from nexus.core.config import NexusConfig; print('✓ Nexus installed successfully')"

# Test CLI
nexus-research --help

# Or using Python module
python -m nexus.cli.research --help
```

## Configuration

### API Keys

Set up your API keys as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="your-key-here"

# Anthropic (optional)
export ANTHROPIC_API_KEY="your-key-here"

# Google (optional)
export GOOGLE_API_KEY="your-key-here"
```

Or create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

### Directory Structure

After installation, Nexus will create the following directories:

```
agentic-ai-lab/
├── output/
│   ├── nexus/           # Nexus platform outputs
│   └── research_reports/ # Research agent reports
├── data/                # Data files
└── src/nexus/
    ├── templates/papers/ # Template papers
    └── ...
```

## Dependencies

### Core Dependencies

Automatically installed with Nexus:

- **aisuite** - Multi-provider LLM client
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **jinja2** - Template engine
- **markdown** - Markdown processing
- **weasyprint** - PDF generation
- **beautifulsoup4** - HTML parsing
- **requests** - HTTP client

### Optional Dependencies

Install as needed:

- **pypandoc** - Alternative PDF generation
- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Linting
- **mkdocs** - Documentation generation

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'nexus'`:

```bash
# Make sure you're in the project root
cd /path/to/agentic-ai-lab

# Reinstall in editable mode
pip install -e .

# Or set PYTHONPATH temporarily
export PYTHONPATH=/path/to/agentic-ai-lab/src
```

### WeasyPrint Issues

WeasyPrint requires system dependencies:

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Ubuntu/Debian**:
```bash
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Windows**:
```bash
# Use GTK+ runtime
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

### Permission Errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Uninstallation

To uninstall Nexus:

```bash
pip uninstall nexus-ai
```

Note: This removes the package but keeps your configuration and output files.

## Updating

To update Nexus after pulling new changes:

```bash
# Pull latest changes
git pull

# Reinstall (if dependencies changed)
pip install -e .

# Or just continue using (if only code changed)
# Editable install automatically uses latest code
```

## Next Steps

After installation:

1. [Quick Start Guide](getting_started.md) - Your first research task
2. [Architecture Overview](architecture.md) - Understanding Nexus
3. [Agent Documentation](agents/overview.md) - Available agents

## Support

For issues and questions:

- Check [Troubleshooting](#troubleshooting) section
- Review [GitHub Issues](https://github.com/yourusername/agentic-ai-lab/issues)
- Consult [Documentation](README.md)
