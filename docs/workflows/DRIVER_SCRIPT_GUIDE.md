# Driver Script Guide: Enhanced Chart Workflow

## Overview

The enhanced chart workflow driver script provides a production-ready CLI tool for generating and refining visualizations using structured reflection.

## Installation

After installing the package in editable mode, the CLI command is automatically available:

```bash
# One-time setup
mamba activate agentic-ai
pip install -e .

# Verify installation
run-enhanced-chart-workflow --help
```

## Quick Start

### Basic Usage

```bash
# Auto-generated instruction
run-enhanced-chart-workflow data/sales.csv

# Custom instruction
run-enhanced-chart-workflow data/sales.csv "Show monthly sales trends"
```

### With Options

```bash
# 3 iterations with custom output directory
run-enhanced-chart-workflow data/sales.csv \
    "Visualize sales by region" \
    --max-iterations 3 \
    --output-dir ./charts \
    --image-basename sales_analysis

# Use Claude for reflection
run-enhanced-chart-workflow data/sales.csv \
    --reflection-model claude-3-5-sonnet-20241022 \
    --verbose
```

## Features

### 1. Enhanced Reflection Prompt (Automatic)

The driver automatically uses the structured critique framework with **no code changes needed**:

- ✅ Chart type appropriateness
- ✅ Perceptual accuracy & truthfulness  
- ✅ Clarity & readability
- ✅ Data-ink ratio (Tufte's principle)
- ✅ Statistical integrity

### 2. Iterative Refinement

Control the number of refinement rounds:

```bash
# No refinement (just initial generation)
--max-iterations 1

# One refinement (default)
--max-iterations 2

# Multiple refinements
--max-iterations 3  # or 4, 5, etc.
```

### 3. Code Persistence

Save the final executable Python code:

```bash
# Save code (default)
run-enhanced-chart-workflow data/sales.csv

# Skip saving code
run-enhanced-chart-workflow data/sales.csv --no-save-final-code
```

Output: `{output_dir}/{image_basename}_final.py`

### 4. Convergence Detection

Automatically stops when no improvements are detected:

```bash
# Stop early when converged (default)
run-enhanced-chart-workflow data/sales.csv --max-iterations 5

# Force all iterations
run-enhanced-chart-workflow data/sales.csv --max-iterations 5 --no-stop-on-convergence
```

### 5. Progress Tracking

```bash
# Detailed progress
run-enhanced-chart-workflow data/sales.csv --verbose

# Show generated code
run-enhanced-chart-workflow data/sales.csv --show-code
```

## Command-Line Options

### Required Arguments

| Argument | Description |
|----------|-------------|
| `dataset` | Path to CSV file to visualize |
| `instruction` | Natural language description (optional, auto-generated if omitted) |

### Model Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--generation-model` | `gpt-4o-mini` | Model for initial code generation |
| `--reflection-model` | `gpt-4o` | Vision model for reflection (gpt-4o, claude-3-5-sonnet-20241022) |

### Output Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--image-basename` | `chart` | Basename for chart files |
| `--output-dir` | `./output` | Output directory |
| `--no-save-final-code` | (save enabled) | Skip saving final code |

### Workflow Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--sample-rows` | `5` | Sample rows in prompts |
| `--max-iterations` | `2` | Maximum refinement iterations |
| `--no-stop-on-convergence` | (stop enabled) | Force all iterations |

### Display Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed progress |
| `--show-code` | Display generated code |

## Output Structure

```
{output_dir}/
├── {basename}_v1.png          # Initial chart
├── {basename}_v2.png          # First refinement
├── {basename}_v3.png          # Second refinement (if max_iterations >= 3)
└── {basename}_final.py        # Executable Python code
```

## Examples

### Example 1: Quick Visualization

```bash
run-enhanced-chart-workflow data/coffee_sales.csv
```

**Output:**
- `./output/chart_v1.png` - Initial chart
- `./output/chart_v2.png` - Refined chart
- `./output/chart_final.py` - Executable code

### Example 2: Production-Quality Chart

```bash
run-enhanced-chart-workflow data/sales_data.csv \
    "Create a professional time series visualization showing quarterly revenue trends" \
    --reflection-model claude-3-5-sonnet-20241022 \
    --max-iterations 3 \
    --output-dir ./reports/charts \
    --image-basename q4_revenue \
    --verbose
```

**Output:**
- `./reports/charts/q4_revenue_v1.png`
- `./reports/charts/q4_revenue_v2.png`
- `./reports/charts/q4_revenue_v3.png`
- `./reports/charts/q4_revenue_final.py`

### Example 3: Exploratory Analysis

```bash
# Let the system auto-generate instruction
run-enhanced-chart-workflow data/customer_data.csv \
    --max-iterations 2 \
    --output-dir ./exploration \
    --show-code
```

## Comparison: Original vs Enhanced

| Feature | `run-chart-workflow` | `run-enhanced-chart-workflow` |
|---------|---------------------|------------------------------|
| Reflection prompt | Generic | Structured (5 dimensions) |
| Progress display | Basic | Detailed with emojis |
| Code preview | No | Optional (`--show-code`) |
| Verbose mode | No | Yes (`--verbose`) |
| Help examples | Minimal | Comprehensive |
| Output summary | Basic | Detailed with insights |

## Testing

Run the quality test suite:

```bash
cd tests/chart_workflow/scripts
python test_enhanced_prompt_quality.py
```

**Output location:** `tests/chart_workflow/outputs/enhanced_prompt_test/`

## Architecture

### Current Structure (Experimental)

```
scripts/
└── run_enhanced_chart_workflow.py  # CLI entry point

reflection/chart_workflow/           # Library code
├── workflow.py                      # Orchestration
├── llm.py                          # Enhanced prompts
├── data.py                         # Data handling
└── ...

pyproject.toml                       # CLI registration
```

### Future Structure (Production)

When the system matures, it will be refactored to:

```
src/chart_workflow/                  # Production package
├── __init__.py
├── workflow.py
├── llm.py
├── cli.py                          # Moved from scripts/
└── ...

scripts/                            # Deprecated or wrapper scripts
```

**Migration trigger:** When API stability, test coverage, and production patterns are complete.

## Troubleshooting

### Command Not Found

```bash
# Reinstall in editable mode
pip install -e .

# Verify
which run-enhanced-chart-workflow
```

### Import Errors

```bash
# Ensure you're in the correct environment
mamba activate agentic-ai

# Verify package installation
pip show agentic-ai
```

### API Key Issues

```bash
# Check .env file exists
ls -la .env

# Verify keys are set
grep -E "OPENAI_API_KEY|ANTHROPIC_API_KEY" .env
```

## Next Steps

1. ✅ **Enhanced Reflection Prompt** (implemented)
2. ⏳ **Data-driven chart type selection** (analyze data structure)
3. ⏳ **Multi-step reasoning chain** (describe → critique → propose)
4. ⏳ **Reference examples** (few-shot learning)
5. ⏳ **Tool use** (query data statistics)

## References

- **Implementation:** `scripts/run_enhanced_chart_workflow.py`
- **Enhanced Prompt:** `docs/ENHANCED_REFLECTION_PROMPT.md`
- **Test Suite:** `tests/chart_workflow/scripts/test_enhanced_prompt_quality.py`
- **Package Config:** `pyproject.toml` (line 124)
