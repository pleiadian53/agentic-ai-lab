# Chart Workflow Testing - Quick Start

## Prerequisites

1. **Activate the environment**:
   ```bash
   mamba activate agentic-ai
   ```

2. **Ensure API keys are set**:
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # If not, copy from example and add your keys
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Quick Test (2 minutes)

Run the quick validation test:

```bash
# From project root
cd /Users/pleiadian53/work/agentic-ai-lab

# Activate environment
mamba activate agentic-ai

# Run quick test
./scripts/test_simple_workflow.sh
```

**What it does**:
- Tests coffee sales dataset (simple)
- Tests splice sites dataset (complex)
- Generates V1 and V2 charts for each
- Saves to `test_outputs/quick_test/`

## Comprehensive Test (10 minutes)

Run all 7 test cases:

```bash
# Activate environment
mamba activate agentic-ai

# Run comprehensive suite
python scripts/test_chart_workflow.py
```

**What it does**:
- 3 coffee sales visualizations
- 4 splice sites visualizations
- Detailed progress reporting
- Saves to `test_outputs/chart_workflow/`

## Manual Test (Custom)

Test with your own dataset and instruction:

```bash
# Activate environment
mamba activate agentic-ai

# Run with custom parameters
python scripts/run_chart_workflow.py \
    "path/to/your/data.csv" \
    "Your visualization instruction" \
    --generation-model "gpt-5.0-mini" \
    --reflection-model "o4-mini" \
    --output-dir "my_charts/"
```

## Reviewing Results

After running tests, compare V1 vs V2 charts:

```bash
# View all generated charts
ls -R test_outputs/

# Open a specific chart
open test_outputs/quick_test/coffee_sales/coffee_q1_comparison_v1.png
open test_outputs/quick_test/coffee_sales/coffee_q1_comparison_v2.png
```

Look for improvements in:
- Color choices
- Label clarity
- Legend quality
- Axis formatting
- Overall professionalism

## Troubleshooting

### Environment not activated
```bash
# Error: command not found or module import error
# Solution: Activate environment first
mamba activate agentic-ai
```

### API key missing
```bash
# Error: OpenAIError: The api_key client option must be set
# Solution: Check .env file
cat .env | grep OPENAI_API_KEY
```

### Module not found
```bash
# Error: ModuleNotFoundError: No module named 'reflection'
# Solution: Run from project root
cd /Users/pleiadian53/work/agentic-ai-lab
python scripts/test_chart_workflow.py
```

## Next Steps

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed documentation.
