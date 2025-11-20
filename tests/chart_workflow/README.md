# Chart Workflow Tests

Test suite for the reflection-based chart generation workflow.

## Overview

This test suite validates the `reflection/chart_workflow` package, which implements the reflection design pattern for iterative chart generation and refinement.

## Directory Structure

```
tests/chart_workflow/
├── README.md                           # This file
├── scripts/                            # Test scripts
│   ├── test_chart_workflow.py          # Comprehensive test suite (7 cases)
│   ├── test_simple_workflow.sh         # Quick validation (2 cases)
│   ├── test_auto_prompt.sh             # Test auto-generated prompts
│   ├── test_prompt_generation.py       # Preview auto-generated prompts
│   └── run_prompt_test.sh              # Wrapper for prompt generation test
├── docs/                               # Documentation
│   ├── QUICKSTART.md                   # Quick start guide
│   └── TESTING_GUIDE.md                # Comprehensive guide
└── outputs/                            # Test results (gitignored)
    ├── quick_test/                     # Quick test outputs
    ├── comprehensive/                  # Comprehensive test outputs
    └── auto_prompt_test/               # Auto-prompt test outputs
```

## What Gets Tested

### Reflection Pattern Workflow

```
1. Generate V1 → Initial chart from natural language
2. Execute V1 → Create chart_v1.png
3. Reflect → Multi-modal LLM critiques visual output
4. Refine V2 → Generate improved code
5. Execute V2 → Create chart_v2.png
```

### Test Datasets

**Simple**: Coffee sales (temporal, categorical, ~1K rows)  
**Complex**: Genomic splice sites (multi-dimensional, ~10K rows)

### Test Cases

**Quick Test** (2 cases):
1. Coffee sales - Quarterly comparison
2. Splice sites - Type distribution

**Comprehensive Test** (7 cases):
1. Coffee sales - Quarterly comparison
2. Coffee sales - Revenue trend
3. Coffee sales - Product distribution
4. Splice sites - Type distribution
5. Splice sites - Strand distribution
6. Splice sites - Positional analysis
7. Splice sites - Gene biotype ranking

## Quick Start

### Prerequisites

```bash
# 1. Activate environment
mamba activate agentic-ai

# 2. Ensure API keys are set
cat .env | grep OPENAI_API_KEY

# 3. Navigate to project root
cd /Users/pleiadian53/work/agentic-ai-lab
```

### Run Quick Test

```bash
./tests/chart_workflow/scripts/test_simple_workflow.sh
```

**Duration**: ~2-3 minutes  
**Output**: `tests/chart_workflow/outputs/quick_test/`

### Run Comprehensive Test

```bash
python tests/chart_workflow/scripts/test_chart_workflow.py
```

**Duration**: ~7-10 minutes  
**Output**: `tests/chart_workflow/outputs/comprehensive/`

### Test Auto-Generated Prompts

The workflow can automatically generate visualization instructions based on dataset characteristics.

**Preview prompts** (no API calls):
```bash
./tests/chart_workflow/scripts/run_prompt_test.sh
```

**Test full workflow** with auto-generated prompts:
```bash
./tests/chart_workflow/scripts/test_auto_prompt.sh
```

**Duration**: ~3-5 minutes  
**Output**: `tests/chart_workflow/outputs/auto_prompt_test/`

This tests:
- Auto-generated prompt for genomic data (splice sites)
- User-specified prompt for comparison
- Verifies prompts are dataset-specific and sensible

## Expected Results

Each test produces two charts:
- **`*_v1.png`** - Initial generation (before reflection)
- **`*_v2.png`** - Refined version (after reflection)

### Quality Improvements (V1 → V2)

**Visual Design**:
- ✅ Better color choices
- ✅ Clearer labels
- ✅ Improved legends
- ✅ Better axis formatting

**Data Representation**:
- ✅ More appropriate chart type
- ✅ Correct aggregations
- ✅ Proper scaling
- ✅ Meaningful groupings

**Publication Quality**:
- ✅ Professional appearance
- ✅ High resolution (300 DPI)
- ✅ Clear without explanation
- ✅ Suitable for papers/presentations

## Reviewing Results

### Compare Charts

```bash
# View all outputs
ls -R tests/chart_workflow/outputs/

# Open specific charts
open tests/chart_workflow/outputs/quick_test/coffee_sales/coffee_q1_comparison_v1.png
open tests/chart_workflow/outputs/quick_test/coffee_sales/coffee_q1_comparison_v2.png
```

### Evaluation Criteria

When reviewing charts, assess:

1. **Technical Correctness**
   - [ ] Code executes without errors
   - [ ] Data loaded correctly
   - [ ] Calculations accurate

2. **Visual Quality**
   - [ ] Colors distinct and accessible
   - [ ] Labels readable
   - [ ] Legend present (when needed)
   - [ ] Axes properly formatted

3. **Reflection Effectiveness**
   - [ ] Feedback identifies real issues
   - [ ] Feedback is actionable
   - [ ] V2 addresses feedback
   - [ ] V2 shows improvement

4. **Publication Readiness**
   - [ ] Professional appearance
   - [ ] High resolution
   - [ ] Clear without explanation

## Troubleshooting

### Environment Not Activated

**Error**: `command not found` or `ModuleNotFoundError`

**Solution**:
```bash
mamba activate agentic-ai
```

### API Key Missing

**Error**: `OpenAIError: The api_key client option must be set`

**Solution**:
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# If missing, copy from example
cp .env.example .env
# Edit .env and add your actual API key
```

### Wrong Directory

**Error**: `FileNotFoundError: No such file or directory`

**Solution**:
```bash
# Run from project root
cd /Users/pleiadian53/work/agentic-ai-lab
./tests/chart_workflow/scripts/test_simple_workflow.sh
```

## Cleaning Up

Remove test outputs:

```bash
# Remove all outputs
rm -rf tests/chart_workflow/outputs/*

# Remove specific test outputs
rm -rf tests/chart_workflow/outputs/quick_test
rm -rf tests/chart_workflow/outputs/comprehensive
```

## Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference guide
- **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Comprehensive testing guide

## Related

- **Package**: [reflection/chart_workflow](../../reflection/chart_workflow/)
- **Package Docs**: [reflection/docs](../../reflection/docs/)
- **Original Notebook**: [reflection/M2_UGL_1/M2_UGL_1.ipynb](../../reflection/M2_UGL_1/M2_UGL_1.ipynb)
- **CLI Tool**: [scripts/run_chart_workflow.py](../../scripts/run_chart_workflow.py)

## Notes

- Test outputs are gitignored to keep repository clean
- Tests use latest models (gpt-5.0-mini, o4-mini)
- Each test is independent and can be run separately
- Tests validate refactored package extracted from educational notebook
