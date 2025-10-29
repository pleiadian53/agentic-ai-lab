# Output Strategy: Enhanced Chart Workflow

## Default Output Location

### Production Default: `./charts`

When users run the enhanced chart workflow, outputs are saved to:

```bash
./charts/
├── chart_v1.png          # Initial generation
├── chart_v2.png          # First refinement
├── chart_v3.png          # Second refinement (if applicable)
└── chart_final.py        # Executable Python code
```

**Rationale:**
- ✅ Semantic naming (clearly indicates chart outputs)
- ✅ Relative to current working directory (user controls location)
- ✅ Follows common conventions (`./data`, `./docs`, `./tests`)
- ✅ Easy to find and organize
- ✅ Automatically gitignored

## Usage Examples

### 1. Default Location (Recommended)

```bash
# Outputs to ./charts/
run-enhanced-chart-workflow data/sales.csv
```

**Result:**
```
./charts/
├── chart_v1.png
├── chart_v2.png
└── chart_final.py
```

### 2. Custom Directory

```bash
# Outputs to ./reports/q4_analysis/
run-enhanced-chart-workflow data/sales.csv \
    --output-dir ./reports/q4_analysis \
    --image-basename sales_trends
```

**Result:**
```
./reports/q4_analysis/
├── sales_trends_v1.png
├── sales_trends_v2.png
└── sales_trends_final.py
```

### 3. Absolute Path

```bash
# Outputs to /Users/username/Documents/charts/
run-enhanced-chart-workflow data/sales.csv \
    --output-dir ~/Documents/charts
```

### 4. Project-Specific Organization

```bash
# Organize by project
run-enhanced-chart-workflow data/project_a.csv \
    --output-dir ./charts/project_a \
    --image-basename analysis
```

**Result:**
```
./charts/
├── project_a/
│   ├── analysis_v1.png
│   ├── analysis_v2.png
│   └── analysis_final.py
└── project_b/
    ├── analysis_v1.png
    └── ...
```

## Output Structure

### File Naming Convention

```
{output_dir}/{image_basename}_v{iteration}.png
{output_dir}/{image_basename}_final.py
```

**Components:**
- `output_dir`: Directory path (default: `./charts`)
- `image_basename`: Base name for files (default: `chart`)
- `iteration`: Iteration number (1, 2, 3, ...)

### Example with Custom Names

```bash
run-enhanced-chart-workflow data/sales.csv \
    --output-dir ./reports/2024 \
    --image-basename q4_revenue \
    --max-iterations 3
```

**Output:**
```
./reports/2024/
├── q4_revenue_v1.png
├── q4_revenue_v2.png
├── q4_revenue_v3.png
└── q4_revenue_final.py
```

## Version Control

### Gitignore Configuration

The following directories are automatically excluded from git:

```gitignore
# Chart workflow outputs
charts/
output/

# Test outputs
tests/*/outputs/
```

**Rationale:**
- Generated artifacts should not be committed
- Users can regenerate charts from code
- Keeps repository size manageable
- Prevents merge conflicts on binary files

### Exception: Example Outputs

If you want to commit example outputs for documentation:

```bash
# Create a separate directory for examples
mkdir -p docs/examples/charts
run-enhanced-chart-workflow data/sample.csv \
    --output-dir docs/examples/charts
```

Then add to `.gitignore`:
```gitignore
# Chart workflow outputs
charts/
output/

# But allow documentation examples
!docs/examples/charts/
```

## Test Output Location

Test scripts use a separate, structured location:

```
tests/chart_workflow/outputs/
├── enhanced_prompt_test/
│   ├── basic/
│   ├── extended/
│   └── auto_instruction/
├── iterative_test/
└── code_persistence_test/
```

**Rationale:**
- Isolated from production outputs
- Organized by test type
- Easy to clean up (`rm -rf tests/*/outputs/`)
- Automatically gitignored

## Best Practices

### 1. Use Descriptive Basenames

```bash
# ❌ Generic
run-enhanced-chart-workflow data.csv

# ✅ Descriptive
run-enhanced-chart-workflow data.csv \
    --image-basename customer_segmentation
```

### 2. Organize by Project/Date

```bash
# By project
--output-dir ./charts/project_alpha

# By date
--output-dir ./charts/2024-10-28

# By both
--output-dir ./charts/project_alpha/2024-10-28
```

### 3. Keep Final Code

```bash
# ✅ Save code (default)
run-enhanced-chart-workflow data.csv

# ❌ Skip code (not recommended for reproducibility)
run-enhanced-chart-workflow data.csv --no-save-final-code
```

### 4. Clean Up Old Outputs

```bash
# Remove all generated charts
rm -rf ./charts

# Remove specific project
rm -rf ./charts/old_project

# Keep only final versions
find ./charts -name "*_v[0-9].png" -delete
```

## Comparison: Test vs Production

| Aspect | Test Outputs | Production Outputs |
|--------|-------------|-------------------|
| Location | `tests/chart_workflow/outputs/` | `./charts/` (default) |
| Purpose | Validation, comparison | User deliverables |
| Organization | By test type | By user preference |
| Gitignored | Yes | Yes |
| Cleanup | Frequent | User-managed |

## Migration Path

When moving from experimental to production (`reflection/` → `src/`):

### Current (Experimental)
```python
# reflection/chart_workflow/workflow.py
output_dir = Path(config.output_dir)  # User-specified
```

### Future (Production)
```python
# src/chart_workflow/workflow.py
# Same behavior - no changes needed!
output_dir = Path(config.output_dir)
```

**Output strategy remains consistent across refactoring.**

## Environment-Specific Defaults

For advanced users, you can set environment variables:

```bash
# In .env or shell profile
export CHART_WORKFLOW_OUTPUT_DIR="$HOME/Documents/charts"
export CHART_WORKFLOW_BASENAME="analysis"
```

Then in the driver script (future enhancement):
```python
default=os.getenv("CHART_WORKFLOW_OUTPUT_DIR", "./charts")
```

## Summary

### Default Behavior
- **Location:** `./charts/` (relative to current directory)
- **Files:** `chart_v1.png`, `chart_v2.png`, `chart_final.py`
- **Gitignored:** Yes
- **User control:** Full (via `--output-dir` and `--image-basename`)

### Key Principles
1. **User control first** - Always respect explicit `--output-dir`
2. **Semantic defaults** - `./charts` is clearer than `./output`
3. **Relative paths** - User chooses where to run the command
4. **Gitignore by default** - Generated artifacts excluded
5. **Consistent structure** - Same pattern for tests and production

### Quick Reference

```bash
# Default
run-enhanced-chart-workflow data.csv
# → ./charts/chart_v1.png, chart_v2.png, chart_final.py

# Custom directory
run-enhanced-chart-workflow data.csv --output-dir ./my_charts
# → ./my_charts/chart_v1.png, ...

# Custom basename
run-enhanced-chart-workflow data.csv --image-basename sales
# → ./charts/sales_v1.png, sales_v2.png, sales_final.py

# Both custom
run-enhanced-chart-workflow data.csv \
    --output-dir ./reports \
    --image-basename q4_analysis
# → ./reports/q4_analysis_v1.png, ...
```
