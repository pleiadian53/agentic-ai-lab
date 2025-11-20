# Quick Start: Editable Install

## One-Time Setup

```bash
# 1. Activate your mamba environment
mamba activate agentic-ai

# 2. Install in editable mode with dev tools
pip install -e ".[dev]"

# 3. Verify installation
run-chart-workflow --help
```

## What This Gives You

✅ **Clean imports** - No more `sys.path` hacks  
✅ **CLI commands** - `run-chart-workflow` available everywhere  
✅ **Better testing** - `pytest` works seamlessly  
✅ **IDE support** - Autocomplete and go-to-definition  
✅ **Live changes** - Edit code, no reinstall needed  

## Usage Examples

### Run Chart Workflow from Anywhere

```bash
cd ~/Documents
run-chart-workflow ~/work/agentic-ai-lab/data/coffee_sales.csv
```

### Import Modules Cleanly

```python
# Before editable install
import sys
sys.path.insert(0, '/path/to/project')
from reflection.chart_workflow.workflow import run_reflection_workflow

# After editable install
from reflection.chart_workflow.workflow import run_reflection_workflow
```

### Run Tests

```bash
# From anywhere
pytest

# Specific test
pytest tests/chart_workflow/test_iterative_refinement.py

# With coverage
pytest --cov=reflection --cov-report=html
```

## Development Tools

```bash
# Format code
black reflection/ src/ scripts/

# Lint code
ruff check reflection/ src/ scripts/

# Type check
mypy reflection/
```

## Backward Compatibility

Old methods still work:

```bash
# Traditional pip install
pip install -r requirements.txt

# Mamba environment
mamba env create -f environment.yml
```

## Full Documentation

See `docs/EDITABLE_INSTALL.md` for complete guide.

## Questions?

- Main README: `README.md`
- Setup guide: `SETUP_README.md`
- Editable install: `docs/EDITABLE_INSTALL.md`
