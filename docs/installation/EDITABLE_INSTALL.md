# Editable Install Guide

This guide explains how to install the `agentic-ai` package in editable mode for development.

## Why Editable Install?

Installing in editable mode (`pip install -e .`) provides several benefits:

- **Clean Imports** - Use absolute imports like `from reflection.chart_workflow import workflow`
- **Run Anywhere** - Execute scripts from any directory
- **Better Testing** - pytest works seamlessly without path hacks
- **IDE Support** - Better autocomplete and go-to-definition
- **CLI Commands** - Install command-line tools like `run-chart-workflow`
- **Standard Practice** - Follows Python packaging best practices

## Installation Steps

### 1. Activate Your Mamba Environment

```bash
mamba activate agentic-ai
```

### 2. Install in Editable Mode

From the project root directory:

```bash
# Basic installation
pip install -e .

# With development dependencies (recommended)
pip install -e ".[dev]"

# With all optional dependencies
pip install -e ".[all]"
```

### 3. Verify Installation

```bash
# Check package is installed
pip list | grep agentic-ai

# Test imports from anywhere
cd ~
python -c "from reflection.chart_workflow import workflow; print('Success!')"

# Test CLI command
run-chart-workflow --help
```

## What Gets Installed

### Core Packages
- `reflection/` - All workflow modules (chart, SQL, research, viz)
- `src/` - Research agent backend
- `scripts/` - Utility scripts

### CLI Commands
- `run-chart-workflow` - Chart generation workflow CLI

### Dependencies
All dependencies from `requirements.txt` are automatically installed.

## Usage After Installation

### Clean Imports

Before editable install:
```python
import sys
sys.path.insert(0, '/path/to/project')
from reflection.chart_workflow.workflow import run_reflection_workflow
```

After editable install:
```python
from reflection.chart_workflow.workflow import run_reflection_workflow
```

### Run Scripts Anywhere

```bash
# Before: Must be in project root
cd /Users/pleiadian53/work/agentic-ai-lab
python scripts/run_chart_workflow.py data/file.csv

# After: Run from anywhere
cd ~/Documents
run-chart-workflow ~/work/agentic-ai-lab/data/file.csv
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/chart_workflow/test_iterative_refinement.py

# Run with coverage
pytest --cov=reflection --cov-report=html
```

## Backward Compatibility

The `requirements.txt` file is preserved for backward compatibility:

```bash
# Traditional pip install (still works)
pip install -r requirements.txt

# Mamba/conda install (still works)
mamba env create -f environment.yml
```

Both methods work, but editable install is recommended for development.

## Troubleshooting

### Import Errors After Installation

If you get import errors, try:

```bash
# Reinstall in editable mode
pip install -e . --force-reinstall --no-deps

# Or uninstall and reinstall
pip uninstall agentic-ai
pip install -e .
```

### CLI Command Not Found

Make sure your mamba environment is activated:

```bash
mamba activate agentic-ai
which run-chart-workflow
```

### Changes Not Reflected

Editable install means changes to `.py` files are immediately available.
No need to reinstall unless you:
- Change `pyproject.toml`
- Add new packages to the project structure
- Modify entry points (CLI commands)

## Development Workflow

1. Activate environment: `mamba activate agentic-ai`
2. Install editable: `pip install -e ".[dev]"`
3. Make changes to code
4. Run tests: `pytest`
5. Changes are immediately available (no reinstall needed)

## Additional Tools

The `[dev]` extras include:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **ruff** - Fast linting
- **mypy** - Type checking
- **ipython** - Enhanced REPL

Usage:

```bash
# Format code
black reflection/ src/ scripts/

# Lint code
ruff check reflection/ src/ scripts/

# Type check
mypy reflection/ src/ scripts/

# Interactive Python with better features
ipython
```

## Questions?

See the main `README.md` or `SETUP_README.md` for more information.
