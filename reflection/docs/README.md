# Reflection Package Documentation

Educational package for implementing the **Reflection Pattern** in agentic AI workflows.

## Overview

The reflection pattern enables AI agents to critique and improve their own outputs through iterative refinement. This package provides utilities and examples for building reflection-based workflows, particularly focused on data visualization tasks.

## Documentation Structure

### 📚 [API Reference](api/)
Technical documentation of all functions, classes, and modules.

- [utils.md](api/utils.md) - Core utility functions
- [visualization.md](api/visualization.md) - Chart generation and reflection

### 📖 [Guides](guides/)
Step-by-step tutorials and how-to guides.

- [Getting Started](guides/getting-started.md) - Quick start guide
- [Chart Generation](guides/chart-generation.md) - Building chart workflows
- [Reflection Pattern](guides/reflection-pattern.md) - Implementing reflection

### 💡 [Examples](examples/)
Real-world examples and use cases.

- [Basic Reflection](examples/basic-reflection.md) - Simple reflection workflow
- [Multi-Model Comparison](examples/multi-model-comparison.md) - Compare different models

### 🏗️ [Design](design/)
Architecture and design decisions.

- [Architecture](design/architecture.md) - Package architecture
- [Styling System](design/styling-system.md) - Custom HTML/CSS styling

## Quick Start

```python
from reflection import utils

# Load data
df = utils.load_and_prepare_data('data.csv')

# Display with custom styling
utils.print_html(df.head(), title="Sample Data")

# Generate chart code
code = generate_chart_code(
    instruction="Create a bar chart of sales by month",
    model="gpt-5.0-mini",
    out_path="chart.png"
)
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

## Modules

### M2_UGL_1 - Chart Generation with Reflection
Implements the reflection pattern for data visualization:
- Generate matplotlib code from natural language
- Execute and visualize results
- Reflect on chart quality
- Refine and regenerate

## Contributing

When adding new features:
1. Update relevant API documentation
2. Add examples to `examples/`
3. Update guides if workflow changes
4. Document design decisions in `design/`

## See Also

- [Main Project Documentation](../../docs/)
- [Agentic AI Roadmap](../../docs/AGENTIC_ROADMAP.md)
- [Library Documentation](../../docs/libraries/)
