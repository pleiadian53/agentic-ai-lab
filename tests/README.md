# Tests Directory

Organized test suites for the agentic-ai project, structured by topic.

## Directory Structure

```
tests/
├── README.md                    # This file
├── chart_workflow/              # Chart generation reflection pattern tests
│   ├── scripts/                 # Test scripts
│   │   ├── test_chart_workflow.py      # Comprehensive test suite
│   │   └── test_simple_workflow.sh     # Quick validation test
│   ├── docs/                    # Test documentation
│   │   ├── QUICKSTART.md        # Quick start guide
│   │   └── TESTING_GUIDE.md     # Comprehensive testing guide
│   └── outputs/                 # Test outputs (gitignored)
│       ├── quick_test/
│       └── comprehensive/
└── [future test topics]/        # Additional test suites
```

## Test Topics

### 1. Chart Workflow Tests

**Location**: `tests/chart_workflow/`

**Purpose**: Test the reflection-based chart generation workflow

**What it tests**:
- Reflection pattern implementation
- Multi-modal LLM integration
- Chart quality improvement (V1 → V2)
- Simple and complex datasets

**Quick Start**:
```bash
# Activate environment
mamba activate agentic-ai

# Run quick test
./tests/chart_workflow/scripts/test_simple_workflow.sh

# Or comprehensive test
python tests/chart_workflow/scripts/test_chart_workflow.py
```

**Documentation**: See [chart_workflow/docs/](chart_workflow/docs/)

## Organization Principles

### Topic-Based Structure

Each test topic gets its own directory with:
- **`scripts/`** - Executable test scripts
- **`docs/`** - Test-specific documentation
- **`outputs/`** - Test results (gitignored)
- **`fixtures/`** - Test data (if needed)

### Why This Structure?

✅ **Organized** - Tests grouped by functionality  
✅ **Self-contained** - Each topic has its own docs and scripts  
✅ **Scalable** - Easy to add new test topics  
✅ **Clear** - Purpose of each test is obvious  
✅ **Maintainable** - Easy to find and update tests

## Running Tests

### Prerequisites

All tests require:
1. **Environment activation**:
   ```bash
   mamba activate agentic-ai
   ```

2. **API keys configured**:
   ```bash
   # Ensure .env file exists with valid keys
   cat .env | grep OPENAI_API_KEY
   ```

3. **Run from project root**:
   ```bash
   cd /Users/pleiadian53/work/agentic-ai-lab
   ```

### Chart Workflow Tests

**Quick validation** (2 test cases, ~2-3 minutes):
```bash
./tests/chart_workflow/scripts/test_simple_workflow.sh
```

**Comprehensive suite** (7 test cases, ~7-10 minutes):
```bash
python tests/chart_workflow/scripts/test_chart_workflow.py
```

**Manual testing**:
```bash
python scripts/run_chart_workflow.py \
    "dataset.csv" \
    "Your instruction"
```

## Test Outputs

All test outputs are saved to topic-specific directories:

```
tests/
└── chart_workflow/
    └── outputs/
        ├── quick_test/
        │   ├── coffee_sales/
        │   │   ├── *_v1.png
        │   │   └── *_v2.png
        │   └── splice_sites/
        │       ├── *_v1.png
        │       └── *_v2.png
        └── comprehensive/
            ├── test_case_1/
            ├── test_case_2/
            └── ...
```

**Note**: Test outputs are gitignored to keep the repository clean.

## Adding New Test Topics

To add a new test topic:

1. **Create directory structure**:
   ```bash
   mkdir -p tests/new_topic/{scripts,docs,outputs,fixtures}
   ```

2. **Add test scripts** to `scripts/`

3. **Document tests** in `docs/`

4. **Update this README** with new topic

5. **Add to `.gitignore`**:
   ```
   tests/new_topic/outputs/
   ```

## Cleaning Up Test Outputs

Remove all test outputs:
```bash
rm -rf tests/*/outputs/*
```

Remove specific topic outputs:
```bash
rm -rf tests/chart_workflow/outputs/*
```

## See Also

- [Chart Workflow Tests](chart_workflow/docs/QUICKSTART.md)
- [Main Scripts](../scripts/) - Production scripts
- [Development Notes](../dev/) - Development documentation
