# API Reference

Technical documentation for all functions and modules in the reflection package.

## Modules

### [utils.md](utils.md)
Core utility functions for data loading, visualization, and LLM interaction.

### [visualization.md](visualization.md)
Chart generation and reflection workflow functions.

## Quick Reference

### Data Handling
- `load_and_prepare_data()` - Load CSV and derive date features
- `make_schema_text()` - Generate human-readable schema

### LLM Interaction
- `get_response()` - Unified interface for OpenAI/Anthropic
- `image_anthropic_call()` - Claude with image input
- `image_openai_call()` - GPT with image input

### Display & Formatting
- `print_html()` - Styled output for Jupyter notebooks
- `ensure_execute_python_tags()` - Normalize code blocks

### Image Processing
- `encode_image_b64()` - Convert image to base64

## Usage Patterns

### Basic Workflow

```python
from reflection import utils

# 1. Load data
df = utils.load_and_prepare_data('data.csv')

# 2. Generate code
code = utils.get_response(
    model="gpt-5.0-mini",
    prompt="Create a bar chart..."
)

# 3. Display results
utils.print_html(code, title="Generated Code")
```

### Image-Based Reflection

```python
# Encode image
media_type, b64 = utils.encode_image_b64('chart.png')

# Get reflection
feedback = utils.image_anthropic_call(
    model_name="claude-3-5-sonnet-20241022",
    prompt="Critique this chart...",
    media_type=media_type,
    b64=b64
)
```

## See Also

- [Design Documentation](../design/)
- [Usage Guides](../guides/)
- [Examples](../examples/)
