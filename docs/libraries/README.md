# Project Libraries Documentation

This directory contains detailed documentation for all libraries used in the Agentic AI project.

## Documents

- **[DEPENDENCIES.md](DEPENDENCIES.md)** - Complete list of all dependencies with explanations
- **[AGENT_LLM_TOOLS.md](AGENT_LLM_TOOLS.md)** - Agent and LLM-specific libraries
- **[WEB_FRAMEWORK.md](WEB_FRAMEWORK.md)** - Web framework and API libraries
- **[DATA_SCIENCE.md](DATA_SCIENCE.md)** - Data analysis and visualization libraries
- **[JUPYTER.md](JUPYTER.md)** - Jupyter notebook environment libraries

## Quick Reference

### By Category

| Category | Key Libraries | Purpose |
|----------|---------------|---------|
| **Agent/LLM** | aisuite, openai, anthropic, mistralai | LLM integration and agent frameworks |
| **Web Framework** | FastAPI, uvicorn, pydantic | API development and validation |
| **Notebooks** | jupyter, ipywidgets | Interactive development |
| **Data Science** | pandas, matplotlib, seaborn | Data analysis and visualization |
| **Database** | sqlalchemy, duckdb, tinydb | Data persistence |
| **Search/Tools** | tavily-python, wikipedia | External data sources |

### Installation

All libraries are defined in `environment.yml` and installed via:

```bash
./scripts/install/setup-mamba.sh
```

Or manually:

```bash
mamba env create -f environment.yml
conda activate agentic-ai
```

## Adding New Libraries

When adding new libraries:

1. Add to `environment.yml` (conda packages) or pip section
2. Update the relevant documentation file in this directory
3. Run `mamba env update -f environment.yml --prune`
4. Document the purpose and usage

## See Also

- [Environment Setup Guide](../ENVIRONMENT_SETUP.md)
- [Mamba vs Pip Comparison](../MAMBA_VS_PIP.md)
- [Setup Checklist](../SETUP_CHECKLIST.md)
