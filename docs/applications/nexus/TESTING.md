# Nexus Research Agent - Testing Guide

This document provides an overview of testing infrastructure for the Nexus Research Agent.

## Test Organization

```
tests/nexus/
├── README.md                    # Detailed test documentation
├── test_research_tools.py       # Tool schema validation
└── (future tests)
```

## Available Tests

### 1. Tool Schema Validation (`test_research_tools.py`)

**Purpose**: Validates that all research tool schemas are compatible with OpenAI's function calling API.

**Location**: `tests/nexus/test_research_tools.py`

**Run**:
```bash
mamba run -n agentic-ai python tests/nexus/test_research_tools.py
```

**What it validates**:
- All 6 research tools (Tavily, arXiv, Wikipedia, Europe PMC, Reddit, Semantic Scholar)
- JSON Schema structure compliance
- Optional parameter definitions (must use `["string", "null"]` not `"Optional[str]"`)
- Required fields and parameter types

**When to run**:
- After modifying `src/nexus/agents/research/tools.py`
- Before restarting the web server with tool changes
- When debugging OpenAI API schema errors
- Before committing tool definition changes

**Expected output**:
```
============================================================
SUMMARY
============================================================
  ✅ PASS: Tavily Search
  ✅ PASS: arXiv Search
  ✅ PASS: Wikipedia Search
  ✅ PASS: Europe PMC Search
  ✅ PASS: Reddit Search
  ✅ PASS: Semantic Scholar Search

  Total: 6/6 tools passed

  🎉 All tools validated successfully!
```

## Common Testing Scenarios

### Scenario 1: Tool Schema Error

**Problem**: Getting OpenAI API error like:
```
Error code: 400 - {'error': {'message': "Invalid schema for function 'reddit_search_tool': 
'typing.Optional[str]' is not valid under any of the given schemas."}}
```

**Solution**:
1. Run tool validation test:
   ```bash
   python tests/nexus/test_research_tools.py
   ```
2. Fix any failing tools in `src/nexus/agents/research/tools.py`
3. Restart the web server to load new schemas
4. Re-run validation to confirm fix

### Scenario 2: Adding a New Tool

**Steps**:
1. Add tool function to `src/nexus/agents/research/tools.py`
2. Add tool definition dict (e.g., `new_tool_def`)
3. Add to `TOOL_DEFINITIONS` list
4. Add to `TOOL_REGISTRY` dict
5. **Run validation test** to ensure schema is correct
6. Restart server and test in web UI

### Scenario 3: Server Not Picking Up Changes

**Problem**: Made changes to tool definitions but still getting old errors.

**Cause**: Web server has old code loaded in memory.

**Solution**:
1. Find server process: `ps aux | grep nexus`
2. Kill it: `kill <PID>` or Ctrl+C in terminal
3. Restart: `mamba run -n agentic-ai python -m nexus.agents.research.server.app`
4. Verify with validation test

## Future Tests (Planned)

### Agent Behavior Tests
- Test individual agents (Planner, Researcher, Writer, Editor)
- Validate agent outputs and error handling
- Test tool calling behavior

### Pipeline Tests
- End-to-end research report generation
- Format decision logic (markdown vs LaTeX vs PDF)
- Report length configurations
- Context and style guidance

### PDF Generation Tests
- LaTeX compilation
- Equation rendering
- Automatic error fixing
- PDF metadata

### Integration Tests
- Web server API endpoints
- CLI interface
- Report manifest management
- File organization

## Test Development Guidelines

### Writing New Tests

1. **Location**: Place in `tests/nexus/`
2. **Naming**: Use `test_<component>.py` convention
3. **Imports**: Use robust project root finder (same pattern as `src/nexus/core/config.py`):
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
4. **Documentation**: 
   - Add docstring to test file
   - Update `tests/nexus/README.md`
   - Update this file (`TESTING.md`)

### Test Structure

```python
#!/usr/bin/env python3
"""
Brief description of what this test validates.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Your imports
from src.nexus.agents.research.something import something

def test_something():
    """Test specific functionality."""
    # Test implementation
    pass

if __name__ == "__main__":
    sys.exit(test_something())
```

### Best Practices

1. **Make tests runnable** - Should work from project root
2. **Clear output** - Use emojis and formatting for readability
3. **Helpful errors** - Provide actionable error messages
4. **Fast execution** - Keep tests quick (< 30 seconds)
5. **No external dependencies** - Mock API calls when possible
6. **Document failures** - Explain what went wrong and how to fix

## Continuous Integration (Future)

When CI/CD is set up:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Conda
        uses: conda-incubator/setup-miniconda@v2
      - name: Install dependencies
        run: |
          mamba env create -f environment.yml
          mamba activate agentic-ai
      - name: Run tests
        run: |
          python tests/nexus/test_research_tools.py
          # Add more tests as they're created
```

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Fix**: Ensure you're running from project root and path manipulation is correct.

### Schema Validation Failures

**Error**: Tool validation fails with type errors

**Fix**: 
- Check `src/nexus/agents/research/tools.py`
- Optional parameters should use `["string", "null"]` not `"string"`
- Restart server after fixing

### Test Not Finding Tools

**Error**: Cannot import tool definitions

**Fix**: Verify conda environment is activated: `mamba activate agentic-ai`

## Related Documentation

- **Detailed test docs**: `tests/nexus/README.md`
- **Tool definitions**: `src/nexus/agents/research/tools.py`
- **Tool orchestration**: `src/nexus/agents/research/docs/TOOL_ORCHESTRATION_DESIGN.md`
- **Troubleshooting**: `src/nexus/docs/troubleshooting.md`

## Quick Reference

```bash
# Activate environment
mamba activate agentic-ai

# Run tool validation
python tests/nexus/test_research_tools.py

# Start web server
python -m nexus.agents.research.server.app

# Run CLI test
nexus-research "test topic" --model openai:gpt-4o --length brief

# Check server process
ps aux | grep nexus
```
