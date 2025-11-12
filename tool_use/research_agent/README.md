# Research Agent

A modular research agent that uses LLM tool calling to generate, reflect on, and format research reports.

## Features

- ✅ **Parallel Tool Execution**: Execute multiple tool calls concurrently for 2-4x speedup
- ✅ **Robust Error Handling**: Automatic retries for JSON parsing errors
- ✅ **Modular Design**: Reusable components for different workflows
- ✅ **Multiple Interfaces**: Command-line script, Python API, and Jupyter notebook helpers
- ✅ **Comprehensive Workflow**: Research → Reflect → Rewrite → Format to HTML

## Quick Start

### Command Line

```bash
# Simple usage
python run_research_workflow.py "quantum computing applications"

# With custom output directory
python run_research_workflow.py --topic "CRISPR gene editing" --output-dir ./my_reports

# Disable parallel execution
python run_research_workflow.py "climate change" --no-parallel
```

### Jupyter Notebook

```python
# Import helpers
from notebook_helpers import quick_research, save_research_results

# Run complete workflow
results = quick_research("extraterrestrial life")

# Save results
save_research_results(results, "extraterrestrial_life_2024")
```

### Python API

```python
from research_agent import (
    generate_research_report_with_tools,
    reflection_and_rewrite,
    convert_report_to_html
)

# Step 1: Generate research report
report = generate_research_report_with_tools(
    "Radio observations of recurrent novae",
    parallel=True  # Use parallel tool execution
)

# Step 2: Reflect and rewrite
reflection_result = reflection_and_rewrite(report)
print(reflection_result["reflection"])
print(reflection_result["revised_report"])

# Step 3: Convert to HTML
html = convert_report_to_html(reflection_result["revised_report"])
```

## Module Structure

```
research_agent/
├── research_agent.py          # Core agent functions
├── parallel_tools.py          # Parallel tool execution
├── research_tools.py          # Tool definitions (arXiv, Tavily)
├── inspect_utils.py           # Visualization and inspection
├── notebook_helpers.py        # Jupyter notebook convenience functions
├── run_research_workflow.py   # Command-line driver script
├── unittests.py              # Test functions
└── README.md                 # This file
```

## Key Components

### 1. Research Agent (`research_agent.py`)

Core functions with robust error handling:

- `generate_research_report_with_tools()` - Generate report with tool use
- `reflection_and_rewrite()` - Reflect and improve report (with JSON retry logic)
- `convert_report_to_html()` - Convert to styled HTML

### 2. Parallel Tool Executor (`parallel_tools.py`)

Execute LLM-instructed tool calls concurrently:

```python
from parallel_tools import ParallelToolExecutor

executor = ParallelToolExecutor(tool_mapping, max_workers=5)
results = executor.execute_tool_calls(tool_calls, verbose=True)
```

**Performance:**
- Sequential: 5-15 seconds for 3 tools
- Parallel: 3-5 seconds for 3 tools (2-4x faster)

### 3. Inspection Utils (`inspect_utils.py`)

Visualization and analysis tools:

```python
import inspect_utils

# Inspect reflection output
inspect_utils.inspect_reflection_output(result)

# Compare reports
inspect_utils.compare_reports(original, result)

# Display formatted report
inspect_utils.display_research_report(report, title="My Research")

# Show tool usage stats
inspect_utils.show_tool_usage_stats(messages)
```

### 4. Notebook Helpers (`notebook_helpers.py`)

One-line workflows for notebooks:

```python
from notebook_helpers import quick_research, research_and_compare

# Complete workflow in one call
results = quick_research("quantum computing")

# With comparison view
results = research_and_compare("CRISPR applications")
```

## Error Handling

### JSON Parsing Errors

The `reflection_and_rewrite()` function includes automatic retry logic:

```python
reflection_result = reflection_and_rewrite(
    report,
    max_retries=3  # Retry up to 3 times if JSON parsing fails
)
```

**How it works:**
1. First attempt with standard prompt
2. If JSON parsing fails, retry with stricter instructions
3. Up to `max_retries` attempts
4. Raises descriptive exception if all retries fail

### Tool Execution Errors

Parallel executor handles errors gracefully:

```python
# Individual tool errors don't crash the entire workflow
results = executor.execute_tool_calls(tool_calls)

# Check for errors
for result in results:
    if result["error"]:
        print(f"Tool {result['call'].function.name} failed: {result['error']}")
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### Model Selection

```python
# Use different models for different steps
report = generate_research_report_with_tools(
    prompt,
    model="gpt-4o"  # More capable for complex research
)

reflection = reflection_and_rewrite(
    report,
    model="gpt-4o-mini"  # Faster/cheaper for reflection
)

html = convert_report_to_html(
    report,
    model="gpt-4o"  # Better HTML generation
)
```

## Examples

### Example 1: Basic Research

```python
from research_agent import generate_research_report_with_tools

report = generate_research_report_with_tools(
    "What are the latest developments in quantum error correction?"
)
print(report)
```

### Example 2: Complete Workflow with Inspection

```python
from research_agent import *
import inspect_utils

# Generate
report = generate_research_report_with_tools("extraterrestrial life")

# Reflect
result = reflection_and_rewrite(report)
inspect_utils.inspect_reflection_output(result)

# Convert
html = convert_report_to_html(result["revised_report"])

# Save
with open("report.html", "w") as f:
    f.write(html)
```

### Example 3: Batch Processing

```python
topics = [
    "quantum computing applications",
    "CRISPR gene editing advances",
    "climate change mitigation strategies"
]

for topic in topics:
    print(f"\nProcessing: {topic}")
    report = generate_research_report_with_tools(topic, parallel=True)
    # Process report...
```

## Performance Tips

1. **Use parallel execution** (default) for 2-4x speedup
2. **Choose appropriate models**: `gpt-4o` for research, `gpt-4o-mini` for reflection
3. **Adjust max_turns** based on complexity: 5-10 for simple topics, 15-20 for complex
4. **Monitor rate limits**: arXiv has 3-second rate limit (handled automatically)

## Troubleshooting

### "Invalid JSON" Errors

The function now retries automatically, but if you still see errors:

```python
# Increase retries
result = reflection_and_rewrite(report, max_retries=5)

# Or use a more capable model
result = reflection_and_rewrite(report, model="gpt-4o")
```

### Rate Limit Errors

```python
# arXiv rate limiting is automatic, but you can adjust:
# In research_tools.py, modify:
_ARXIV_RATE_LIMIT_SECONDS = 5  # Increase wait time
```

### Max Turns Reached

```python
# Increase max turns for complex topics
report = generate_research_report_with_tools(
    prompt,
    max_turns=20  # Default is 10
)
```

## Testing

```python
# Run unit tests
import unittests

unittests.test_generate_research_report_with_tools(generate_research_report_with_tools)
unittests.test_reflection_and_rewrite(reflection_and_rewrite)
unittests.test_convert_report_to_html(convert_report_to_html)
```

## License

Part of the agentic-ai-public project.
