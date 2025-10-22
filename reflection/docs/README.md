# Reflection Package Documentation

Production-ready package for implementing the **Reflection Pattern** in agentic AI workflows.

## Overview

The reflection pattern enables AI agents to critique and improve their own outputs through iterative refinement. This package provides a complete framework for building reflection-based workflows, with a focus on automated data visualization and chart generation.

**Key Features:**
- 🎨 **Automatic prompt generation** - Dataset-aware visualization suggestions
- 🔄 **Multi-modal reflection** - LLMs critique visual outputs and suggest improvements
- 📊 **Production-ready CLI** - Command-line tool for chart generation
- 🧪 **Comprehensive testing** - Test suite with simple and complex datasets
- 📦 **Modular design** - Reusable components for custom workflows

## Documentation Structure

### 📚 [API Reference](api/)
Technical documentation of all functions, classes, and modules.

**Available:**
- **[utils.md](api/utils.md)** - Core utility functions (data loading, LLM interaction, display)

**Planned (to be created):**
- **chart_workflow.md** - Chart workflow package API documentation

### 📖 Guides
Step-by-step tutorials and how-to guides.

**Planned (to be created):**
- **Getting Started** - Quick start guide for new users
- **Chart Generation** - Building chart workflows with the reflection pattern
- **Reflection Pattern** - Implementing reflection in custom workflows

### 💡 Examples
Real-world examples and use cases.

**Planned (to be created):**
- **Basic Reflection** - Simple reflection workflow example
- **Multi-Model Comparison** - Comparing different LLM models in reflection

### 🏗️ [Design](design/)
Architecture and design decisions.

**Available:**
- **[Styling System](design/styling-system.md)** - Custom HTML/CSS styling for Jupyter notebooks

**Planned (to be created):**
- **Architecture** - Overall package architecture and design philosophy

## Quick Start

### Using the CLI (Recommended)

```bash
# Activate environment
mamba activate agentic-ai

# Auto-generate visualization from dataset
python scripts/run_chart_workflow.py data/your_data.csv

# Or provide custom instruction
python scripts/run_chart_workflow.py data/your_data.csv \
  "Create a bar chart comparing sales by region"
```

### Using the Python API

```python
from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow

# Configure workflow
config = ChartWorkflowConfig(
    generation_model="gpt-4o-mini",
    reflection_model="gpt-4o",
    output_dir="charts/"
)

# Run workflow (auto-generates prompt if instruction=None)
artifacts = run_reflection_workflow(
    dataset="data/sales.csv",
    instruction=None,  # Auto-generate from dataset
    config=config
)

print(f"V1 chart: {artifacts.chart_v1}")
print(f"V2 chart: {artifacts.chart_v2}")
print(f"Feedback: {artifacts.feedback}")
```

## Key Concepts

### Reflection Pattern
1. **Generate** - Create initial output (V1)
2. **Execute** - Run the generated code
3. **Reflect** - Critique the output
4. **Refine** - Generate improved version (V2)

### Multi-Modal Workflow
- Text-based code generation
- Image-based reflection
- Iterative improvement

## Packages & Modules

### chart_workflow - Production Chart Generation Package

Refactored, production-ready package for reflection-based chart generation.

**Modules:**
- `workflow.py` - Main orchestration and reflection loop
- `prompting.py` - Auto-generate dataset-specific visualization prompts
- `llm.py` - LLM interaction (OpenAI, Anthropic)
- `data.py` - Data loading and schema extraction
- `execution.py` - Safe Python code execution

**Features:**
- ✅ Automatic prompt generation based on dataset characteristics
- ✅ Domain-aware (detects genomic data, temporal data, etc.)
- ✅ Multi-modal reflection (LLM critiques visual charts)
- ✅ Iterative refinement (V1 → Reflect → V2)
- ✅ Support for CSV and TSV files

**CLI Tool:**
```bash
python scripts/run_chart_workflow.py <dataset> [instruction] [options]
```

### M2_UGL_1 - Educational Notebooks

Original educational notebooks demonstrating the reflection pattern:
- `M2_UGL_1.ipynb` - Interactive chart generation workflow
- `utils.py` - Core utilities (data loading, LLM calls, display)

**Note:** The `chart_workflow` package is the refactored, production version of concepts from these notebooks.

## Testing

Comprehensive test suite located in `../../tests/chart_workflow/`:

**Quick validation:**
```bash
./tests/chart_workflow/scripts/test_simple_workflow.sh
```

**Comprehensive suite (7 test cases):**
```bash
python tests/chart_workflow/scripts/test_chart_workflow.py
```

**Preview auto-generated prompts:**
```bash
python tests/chart_workflow/scripts/test_prompt_generation.py
```

See [Testing Guide](../../tests/chart_workflow/docs/TESTING_GUIDE.md) for details.

## Contributing

When adding new features:
1. Update relevant API documentation in `api/`
2. Add examples to `examples/`
3. Update guides if workflow changes
4. Document design decisions in `design/`
5. Add tests to `../../tests/chart_workflow/`

## Recent Updates

### Version 0.1.0 (October 2025)

**New Features:**
- ✅ `chart_workflow` package - Production-ready chart generation
- ✅ Automatic prompt generation - Dataset-aware visualization suggestions
- ✅ Multi-modal reflection - LLM critiques visual outputs
- ✅ CLI tool - `scripts/run_chart_workflow.py`
- ✅ Comprehensive testing - Simple and complex dataset validation
- ✅ TSV support - Auto-detection of file format

**Tested On:**
- Simple datasets: Coffee sales (temporal, categorical)
- Complex datasets: Genomic splice sites (2.8M rows, 14 columns)

## See Also

- [Main Project Documentation](../../docs/)
- [Testing Guide](../../tests/chart_workflow/docs/TESTING_GUIDE.md)
- [Test Quick Start](../../tests/chart_workflow/docs/QUICKSTART.md)
- [Agentic AI Roadmap](../../docs/AGENTIC_ROADMAP.md)
- [Library Documentation](../../docs/libraries/)
