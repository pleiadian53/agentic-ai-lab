# Nexus Research Agent Tests

This directory contains tests for the Nexus Research Agent system.

## Test Files

### `test_research_tools.py`

**Purpose**: Validates all research tool schemas for OpenAI API compatibility.

**What it tests**:
- Tool schema structure (type, function, parameters)
- Parameter definitions (properties, required fields)
- JSON Schema compliance for optional parameters
- Detection of invalid type annotations (e.g., `typing.Optional[str]`)

**Tools validated**:
1. **Tavily Search** - General web search
2. **arXiv Search** - Academic papers (physics, CS, math)
3. **Wikipedia Search** - Encyclopedia summaries
4. **Europe PMC Search** - Biomedical literature
5. **Reddit Search** - Community discussions and insights
6. **Semantic Scholar Search** - AI-ranked academic papers

**Usage**:
```bash
# Run from project root
mamba run -n agentic-ai python tests/nexus/test_research_tools.py

# Expected output: All 6 tools should pass validation
```

**When to run**:
- After modifying tool definitions in `src/nexus/agents/research/tools.py`
- Before deploying changes to the web server
- When debugging OpenAI API schema errors
- As part of CI/CD pipeline (future)

**Common issues detected**:
- Invalid type annotations (e.g., `"type": "Optional[str]"`)
- Missing required fields in schema
- Incorrect parameter structure
- Type mismatches for optional parameters

## Running Tests

### Individual Test
```bash
python tests/nexus/test_research_tools.py
```

### All Nexus Tests (future)
```bash
pytest tests/nexus/
```

## Adding New Tests

When adding new test files:

1. **Create the test file** in `tests/nexus/`
2. **Add proper imports** using the robust project root finder:
   ```python
   import sys
   from pathlib import Path
   
   def _find_project_root(marker_name: str = "agentic-ai-lab") -> Path:
       """Find project root by searching for directory name or markers."""
       current = Path(__file__).resolve()
       for parent in [current] + list(current.parents):
           if parent.name == marker_name:
               return parent
       for parent in [current] + list(current.parents):
           if any((parent / m).exists() for m in ['.git', 'pyproject.toml']):
               return parent
       raise RuntimeError("Could not find project root")
   
   PROJECT_ROOT = _find_project_root()
   sys.path.insert(0, str(PROJECT_ROOT))
   ```
3. **Document the test** in this README
4. **Update** `src/nexus/docs/TESTING.md` with high-level overview

## Test Organization

```
tests/nexus/
├── README.md                    # This file - detailed test documentation
├── __init__.py                  # Package marker
├── test_research_tools.py       # Tool schema validation
└── (future tests)
    ├── test_agents.py           # Agent behavior tests
    ├── test_pipeline.py         # End-to-end pipeline tests
    └── test_pdf_generation.py   # PDF/LaTeX generation tests
```

## Best Practices

1. **Keep tests focused** - One test file per component/feature
2. **Use descriptive names** - `test_<component>_<feature>.py`
3. **Add docstrings** - Explain what the test validates
4. **Make tests runnable** - Should work from project root
5. **Document failures** - Clear error messages for debugging
6. **Update docs** - Keep this README and `src/nexus/docs/TESTING.md` in sync

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`, ensure:
- You're running from project root
- The path manipulation code is present
- The conda environment is activated

### Schema Validation Failures
If tool validation fails:
1. Check the error message for the specific tool and property
2. Review `src/nexus/agents/research/tools.py`
3. Ensure optional parameters use `["string", "null"]` not `"string"`
4. Restart the web server after fixes

## Related Documentation

- **High-level testing overview**: `src/nexus/docs/TESTING.md`
- **Tool definitions**: `src/nexus/agents/research/tools.py`
- **Agent architecture**: `src/nexus/agents/research/docs/MULTIAGENT_WORKFLOW_TUTORIAL.md`
