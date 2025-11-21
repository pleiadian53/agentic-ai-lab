# Market Research Multi-Agent System

A linear/sequential multi-agent system for automated marketing campaign generation. This package coordinates four specialized agents to create executive-ready campaign reports.

## Overview

This system demonstrates a **linear communication pattern** where agents execute in a fixed sequence, each passing its output to the next agent:

```
Market Research → Graphic Designer → Copywriter → Packaging
```

### Agents

1. **Market Research Agent** 🕵️‍♂️
   - Scans web for fashion trends using Tavily search
   - Matches trends with internal product catalog
   - Recommends products for campaign

2. **Graphic Designer Agent** 🎨
   - Generates visual concept from trend insights
   - Creates DALL-E 3 prompt and caption
   - Produces campaign image

3. **Copywriter Agent** ✍️
   - Analyzes image + trends (multimodal)
   - Creates short, elegant marketing quote
   - Provides justification for messaging

4. **Packaging Agent** 📦
   - Refines trend summary for executives
   - Assembles polished markdown report
   - Combines all assets into final deliverable

## Installation

This package is part of the `agentic-ai-lab` repository. Install dependencies:

```bash
pip install aisuite openai tavily-python pillow python-dotenv pandas
```

### Model Support

The package automatically handles both **Chat Completions API** and **Responses API** models:

**Chat API Models** (default):
- `gpt-4o`, `gpt-4o-mini`
- `gpt-4.1`, `gpt-4-turbo`

**Responses API Models** (GPT-5 series):
- `gpt-5.1`, `gpt-5.1-codex`
- `gpt-5.1-codex-mini` (fast code + vision)
- `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
- `gpt-5-pro`

The `llm_client` module automatically routes requests to the correct API based on the model name.

**Note**: You can optionally use the `openai:` prefix (e.g., `openai:gpt-5.1`) for compatibility with aisuite's multi-provider format, but it's not required.

## Configuration

Create a `.env` file with your API keys:

```bash
# Required
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

# Optional (for DeepLearning.AI courses)
DLAI_TAVILY_BASE_URL=https://...
```

## Usage

### Command Line

Run the full pipeline from the command line:

```bash
# Basic usage
python run_campaign.py

# Use specific model (GPT-5)
python run_campaign.py --model gpt-5.1

# Use GPT-5 Codex (best for code + vision)
python run_campaign.py --model gpt-5.1-codex

# Custom output path
python run_campaign.py --output my_campaign.md

# Quiet mode
python run_campaign.py --quiet
```

### Python API

Use as a library in your code:

```python
import aisuite
from market_research import run_campaign_pipeline

# Initialize client
client = aisuite.Client()

# Run full pipeline
results = run_campaign_pipeline(
    client=client,
    model="gpt-4o-mini",  # or gpt-5.1, gpt-5.1-codex, etc.
    verbose=True
)

# Access results
print(f"Report: {results['markdown_path']}")
print(f"Image: {results['visual']['image_path']}")
print(f"Quote: {results['quote_result']['quote']}")
```

### Individual Agents

You can also use agents individually:

```python
import aisuite
from market_research import (
    market_research_agent,
    graphic_designer_agent,
    copywriter_agent,
    packaging_agent
)

client = aisuite.Client()

# Step 1: Market research
trends = market_research_agent(client, model="gpt-4o-mini")

# Step 2: Generate visual
visual = graphic_designer_agent(client, trend_insights=trends)

# Step 3: Create copy
copy = copywriter_agent(
    client,
    image_path=visual["image_path"],
    trend_summary=trends
)

# Step 4: Package report
report_path = packaging_agent(
    client,
    trend_summary=trends,
    image_url=visual["image_path"],
    quote=copy["quote"],
    justification=copy["justification"]
)
```

## Architecture

### Communication Pattern

This system uses a **linear/sequential pattern**:

- **Advantages**:
  - Simple, predictable flow
  - Easy to debug and trace
  - Clear dependencies between steps
  - Suitable for well-defined workflows

- **Trade-offs**:
  - No parallelization
  - No dynamic routing
  - Fixed agent order
  - Limited flexibility

### Module Structure

```
market_research/
├── __init__.py           # Package exports
├── agents.py             # Agent implementations
├── pipeline.py           # Orchestration logic
├── tools.py              # External tool integrations
├── llm_client.py         # Unified chat/responses API client
├── inventory_utils.py    # Product catalog utilities
├── run_campaign.py       # CLI driver script
└── README.md             # This file
```

### LLM Client Module

The `llm_client.py` module provides unified access to both Chat Completions and Responses APIs:

```python
from market_research import call_llm_text, call_llm_json

# Works with both GPT-4 and GPT-5 models
text = call_llm_text(
    client=client,
    model="gpt-5.1",  # or gpt-4o, gpt-5-mini, etc.
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7
)

# Automatic JSON parsing with robust error handling
data = call_llm_json(
    client=client,
    model="gpt-5.1-codex",
    messages=[{"role": "user", "content": "Return JSON: {...}"}],
    temperature=0.0
)
```

**Features**:
- Automatic model routing (chat vs responses API)
- Multimodal message support (images + text)
- Temperature fallback for unsupported models
- Robust JSON parsing with code fence handling
- Message flattening for responses-only models

### Data Flow

```
1. Market Research Agent
   Input: None (uses tools)
   Output: Trend summary (str)
   ↓
2. Graphic Designer Agent
   Input: Trend summary
   Output: {image_path, prompt, caption}
   ↓
3. Copywriter Agent
   Input: Image path + trend summary
   Output: {quote, justification}
   ↓
4. Packaging Agent
   Input: All previous outputs
   Output: Markdown report path
```

## Tools

### tavily_search_tool

Web search for fashion trends:

```python
from market_research import tavily_search_tool

results = tavily_search_tool(
    query="summer sunglasses trends 2025",
    max_results=5,
    include_images=False
)
```

### product_catalog_tool

Access internal product inventory:

```python
from market_research import product_catalog_tool

products = product_catalog_tool(max_items=10)
# Returns: [{'name': 'Aviator', 'item_id': 'SG001', ...}, ...]
```

## Output

The pipeline generates:

1. **Markdown Report** - Executive summary with:
   - Refined trend insights
   - Campaign visual (embedded)
   - Marketing quote
   - Strategic justification
   - Timestamp

2. **Campaign Image** - DALL-E 3 generated PNG

3. **Structured Data** - Python dict with all intermediate results

### Example Output

```markdown
# 🕶️ Summer Sunglasses Campaign – Executive Summary

## 📊 Refined Trend Insights
[Executive-friendly trend analysis]

## 🎯 Campaign Visual
![Campaign Visual](img-xyz.png)

## ✍️ Campaign Quote
"Embrace the summer with timeless aviator elegance."

## ✅ Why This Works
[Strategic justification linking trends, visual, and messaging]

---
*Report generated on 2025-11-20*
```

## Comparison with customer_service

Both packages follow similar patterns but differ in:

| Aspect | customer_service | market_research |
|--------|-----------------|-----------------|
| **Pattern** | Code-as-plan + Tool-based | Linear/Sequential agents |
| **Agents** | Single or tool-based | Four specialized agents |
| **Tools** | Database operations | Web search + catalog |
| **Output** | Execution report | Marketing campaign |
| **Complexity** | Reflection + validation | Fixed pipeline |

## Examples

See the original notebook for interactive examples:
- `/Users/pleiadian53/work/agentic-ai-lab/multiagent/M5_lab2/M5_UGL_2.ipynb`

## Testing

Run a quick test:

```python
import aisuite
from market_research import run_campaign_pipeline

client = aisuite.Client()
results = run_campaign_pipeline(client, verbose=True)
assert "markdown_path" in results
assert "visual" in results
assert "quote_result" in results
print("✅ Pipeline test passed!")
```

## Troubleshooting

### API Key Errors

```
Error: TAVILY_API_KEY not found
```

**Solution**: Add keys to `.env` file

### Import Errors

```
ModuleNotFoundError: No module named 'aisuite'
```

**Solution**: Install dependencies:
```bash
pip install aisuite openai tavily-python pillow python-dotenv pandas
```

### Image Generation Fails

```
Error: DALL-E 3 request failed
```

**Solution**: Check OpenAI API key and quota

## Future Enhancements

Potential improvements:

1. **Parallel Execution** - Run independent agents concurrently
2. **Dynamic Routing** - Choose agents based on context
3. **Reflection Loop** - Add quality checks and refinement
4. **Multi-Modal Input** - Accept user-provided images
5. **A/B Testing** - Generate multiple campaign variants
6. **Cost Tracking** - Monitor API usage and costs

## Related Packages

- `customer_service` - Single-agent and tool-based patterns
- `chart_agent` - Code generation for data visualization
- `splice_agent` - Genomics analysis workflows

## License

Part of the agentic-ai-lab project.

## References

- Original notebook: `multiagent/M5_lab2/M5_UGL_2.ipynb`
- aisuite: https://github.com/andrewyng/aisuite
- OpenAI API: https://platform.openai.com/docs
- Tavily: https://tavily.com
