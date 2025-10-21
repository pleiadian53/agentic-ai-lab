# utils.py API Reference

Core utility functions for the reflection package.

## Data Loading & Preparation

### `load_and_prepare_data(csv_path: str) -> pd.DataFrame`

Load CSV file and derive date-based features.

**Parameters:**
- `csv_path` (str): Path to CSV file

**Returns:**
- `pd.DataFrame`: DataFrame with additional date columns

**Derived Columns:**
- `quarter` (int): Quarter of year (1-4)
- `month` (int): Month (1-12)
- `year` (int): Year (YYYY)

**Example:**
```python
df = utils.load_and_prepare_data('coffee_sales.csv')
print(df.columns)
# ['date', 'time', 'cash_type', 'card', 'price', 'coffee_name', 
#  'quarter', 'month', 'year']
```

**Notes:**
- Handles missing/invalid dates gracefully with `errors='coerce'`
- Only processes if 'date' column exists
- Returns original DataFrame if no date column

---

### `make_schema_text(df: pd.DataFrame) -> str`

Generate human-readable schema description from DataFrame.

**Parameters:**
- `df` (pd.DataFrame): Input DataFrame

**Returns:**
- `str`: Multi-line schema description

**Example:**
```python
schema = utils.make_schema_text(df)
print(schema)
# - date: datetime64[ns]
# - time: object
# - cash_type: object
# - price: float64
# - coffee_name: object
# - quarter: int64
# - month: int64
# - year: int64
```

**Use Case:**
- Include in LLM prompts to describe available data
- Documentation generation
- Data validation

---

## LLM Interaction

### `get_response(model: str, prompt: str) -> str`

Unified interface for calling OpenAI or Anthropic models.

**Parameters:**
- `model` (str): Model name (e.g., "gpt-5.0-mini", "claude-3-5-sonnet-20241022")
- `prompt` (str): User prompt/instruction

**Returns:**
- `str`: Model's text response

**Supported Models:**
- **OpenAI**: Any model containing "gpt", "o1", "o4", etc.
- **Anthropic**: Any model containing "claude" or "anthropic"

**Example:**
```python
# OpenAI
response = utils.get_response(
    model="gpt-5.0-mini",
    prompt="Explain the reflection pattern"
)

# Anthropic
response = utils.get_response(
    model="claude-3-5-sonnet-20241022",
    prompt="Explain the reflection pattern"
)
```

**Implementation:**
```python
def get_response(model: str, prompt: str) -> str:
    if "claude" in model.lower() or "anthropic" in model.lower():
        # Anthropic Claude format
        message = anthropic_client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        return message.content[0].text
    else:
        # Default to OpenAI format
        response = openai_client.responses.create(
            model=model,
            input=prompt,
        )
        return response.output_text
```

**Notes:**
- Automatically detects provider based on model name
- Uses environment variables for API keys
- Max tokens: 1000 for Anthropic (configurable in code)

---

### `image_anthropic_call(model_name: str, prompt: str, media_type: str, b64: str) -> str`

Call Anthropic Claude with text + image input.

**Parameters:**
- `model_name` (str): Claude model (e.g., "claude-3-5-sonnet-20241022")
- `prompt` (str): Text prompt
- `media_type` (str): MIME type (e.g., "image/png", "image/jpeg")
- `b64` (str): Base64-encoded image data

**Returns:**
- `str`: Concatenated text from all response blocks

**Example:**
```python
media_type, b64 = utils.encode_image_b64('chart.png')

feedback = utils.image_anthropic_call(
    model_name="claude-3-5-sonnet-20241022",
    prompt="Critique this chart and suggest improvements",
    media_type=media_type,
    b64=b64
)
```

**Configuration:**
- `max_tokens`: 2000
- `temperature`: 0 (deterministic)
- System message: Enforces JSON-only output

**System Prompt:**
```
You are a careful assistant. Respond with a single valid JSON object only.
Do not include markdown, code fences, or commentary outside JSON.
```

---

### `image_openai_call(model_name: str, prompt: str, media_type: str, b64: str) -> str`

Call OpenAI GPT with text + image input.

**Parameters:**
- `model_name` (str): GPT model (e.g., "gpt-5.0-mini", "gpt-4o")
- `prompt` (str): Text prompt
- `media_type` (str): MIME type
- `b64` (str): Base64-encoded image data

**Returns:**
- `str`: Model's text response

**Example:**
```python
media_type, b64 = utils.encode_image_b64('chart.png')

feedback = utils.image_openai_call(
    model_name="gpt-5.0-mini",
    prompt="Analyze this chart",
    media_type=media_type,
    b64=b64
)
```

**Implementation:**
```python
def image_openai_call(model_name: str, prompt: str, media_type: str, b64: str) -> str:
    data_url = f"data:{media_type};base64,{b64}"
    resp = openai_client.responses.create(
        model=model_name,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": data_url},
            ],
        }],
    )
    return (resp.output_text or "").strip()
```

---

## Display & Formatting

### `print_html(content: Any, title: str | None = None, is_image: bool = False) -> None`

Display content in a styled card in Jupyter notebooks.

**Parameters:**
- `content` (Any): Content to display (DataFrame, Series, str, or image path)
- `title` (str | None): Optional title for the card
- `is_image` (bool): If True, treat `content` as image file path

**Returns:**
- None (displays HTML via IPython.display)

**Content Type Handling:**

| Type | Condition | Rendering |
|------|-----------|-----------|
| Image | `is_image=True` | Base64-encoded `<img>` |
| DataFrame | `isinstance(content, pd.DataFrame)` | HTML table |
| Series | `isinstance(content, pd.Series)` | DataFrame table |
| String | `isinstance(content, str)` | `<pre><code>` |
| Other | Default | `str(content)` in `<pre><code>` |

**Examples:**

```python
# Display DataFrame
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
utils.print_html(df, title="Sample Data")

# Display code
code = "import pandas as pd\ndf = pd.read_csv('data.csv')"
utils.print_html(code, title="Generated Code")

# Display image
utils.print_html("chart.png", title="Chart V1", is_image=True)

# Display text
utils.print_html("Processing complete!", title="Status")
```

**Styling:**
- Gradient border (blue to purple)
- Rounded corners
- Drop shadow
- Responsive tables
- Syntax-highlighted code blocks

**See Also:**
- [Styling System Design](../design/styling-system.md)

---

### `ensure_execute_python_tags(text: str) -> str`

Normalize code to be wrapped in `<execute_python>` tags.

**Parameters:**
- `text` (str): Code text (may or may not have tags/fences)

**Returns:**
- `str`: Code wrapped in `<execute_python>` tags

**Behavior:**
1. Strips leading/trailing whitespace
2. Removes markdown code fences (` ```python ` or ` ``` `)
3. Adds `<execute_python>` tags if not present

**Example:**
```python
# Input with markdown fences
code = """```python
import pandas as pd
df = pd.read_csv('data.csv')
```"""

normalized = utils.ensure_execute_python_tags(code)
print(normalized)
# <execute_python>
# import pandas as pd
# df = pd.read_csv('data.csv')
# </execute_python>

# Input already with tags
code = "<execute_python>\nprint('hello')\n</execute_python>"
normalized = utils.ensure_execute_python_tags(code)
# Returns unchanged

# Plain code
code = "print('hello')"
normalized = utils.ensure_execute_python_tags(code)
# <execute_python>
# print('hello')
# </execute_python>
```

**Use Case:**
- Normalize LLM outputs before extraction
- Ensure consistent code block format

---

## Image Processing

### `encode_image_b64(path: str) -> tuple[str, str]`

Convert image file to base64 encoding.

**Parameters:**
- `path` (str): Path to image file

**Returns:**
- `tuple[str, str]`: (media_type, base64_string)
  - `media_type`: MIME type (e.g., "image/png", "image/jpeg")
  - `base64_string`: Base64-encoded image data

**Example:**
```python
media_type, b64 = utils.encode_image_b64('chart.png')
print(media_type)  # "image/png"
print(b64[:50])    # "iVBORw0KGgoAAAANSUhEUgAAA..."

# Use with LLM
feedback = utils.image_anthropic_call(
    model_name="claude-3-5-sonnet-20241022",
    prompt="Analyze this chart",
    media_type=media_type,
    b64=b64
)
```

**MIME Type Detection:**
- Uses `mimetypes.guess_type()` to detect type
- Falls back to "image/png" if detection fails
- Supports: PNG, JPEG, GIF, WebP, etc.

**Implementation:**
```python
def encode_image_b64(path: str) -> tuple[str, str]:
    mime, _ = mimetypes.guess_type(path)
    media_type = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return media_type, b64
```

---

## Environment & Configuration

### Global Variables

```python
# API Keys (loaded from .env)
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# API Clients
openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = Anthropic(api_key=anthropic_api_key)
```

**Setup:**
1. Create `.env` file in project root
2. Add API keys:
   ```env
   OPENAI_API_KEY=sk-proj-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Import utils (automatically loads environment)

---

## Dependencies

```python
# Standard Library
import os
import re
import json
import base64
import mimetypes
from pathlib import Path

# Third-Party
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from html import escape
from IPython.display import HTML, display
```

**Installation:**
```bash
mamba env create -f environment.yml
mamba activate agentic-ai
```

---

## Error Handling

### Missing API Keys

```python
# If API key not found, client initialization may fail
openai_client = OpenAI()  # Raises OpenAIError if no key
```

**Solution:**
- Ensure `.env` file exists with valid keys
- Check environment variables: `echo $OPENAI_API_KEY`

### Invalid Image Path

```python
media_type, b64 = utils.encode_image_b64('nonexistent.png')
# Raises FileNotFoundError
```

**Solution:**
- Verify file exists before encoding
- Use try/except for robust error handling

### Malformed Code Blocks

```python
# LLM returns code without tags
code = "import pandas as pd"
normalized = utils.ensure_execute_python_tags(code)
# Automatically adds tags
```

**Solution:**
- Always use `ensure_execute_python_tags()` before extraction
- Validates and normalizes LLM outputs

---

## See Also

- [Styling System Design](../design/styling-system.md)
- [Getting Started Guide](../guides/getting-started.md)
- [Reflection Pattern Guide](../guides/reflection-pattern.md)
