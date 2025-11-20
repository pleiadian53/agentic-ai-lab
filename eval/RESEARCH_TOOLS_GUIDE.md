# Research Tools Guide

Production-ready research tools for agentic workflows.

## Overview

This module provides enhanced, production-ready implementations of research tools designed for integration with `tool_use/research_agent`. It includes advanced features beyond the educational M4 notebook version.

## Files

- **`eval/research_tools.py`** - Production version (use this for integration)
- **`eval/M4/research_tools.py`** - Educational version (for notebook demonstrations)

## Key Enhancements

### Production Features

| Feature | M4 Version | Production Version |
|---------|------------|-------------------|
| **Retry Logic** | ❌ No | ✅ Automatic retry with backoff |
| **Caching** | ❌ No | ✅ LRU cache for Wikipedia |
| **Logging** | ❌ No | ✅ Structured logging |
| **Error Handling** | ⚠️ Basic | ✅ Comprehensive |
| **Rate Limiting** | ❌ No | ✅ Built-in adapter |
| **Search Options** | ⚠️ Limited | ✅ Extensive |
| **Validation** | ❌ No | ✅ Input validation |
| **Documentation** | ⚠️ Basic | ✅ Extensive with examples |

## Available Tools

### 1. arXiv Search Tool

**Enhanced features:**
- Configurable search fields (all, title, author, abstract, category)
- Multiple sort options (relevance, date)
- Extended metadata (categories, comments, update dates)
- Input validation (max 100 results)
- Retry logic for failed requests

**Basic usage:**
```python
from eval.research_tools import arxiv_search_tool

# Simple search
papers = arxiv_search_tool("quantum computing", max_results=5)

# Title-only search
papers = arxiv_search_tool("BERT", search_field="ti", max_results=10)

# Author search
papers = arxiv_search_tool("Hinton", search_field="au")

# Recent papers
papers = arxiv_search_tool(
    "machine learning",
    sort_by="submittedDate",
    max_results=10
)

# Category search
papers = arxiv_search_tool("cs.AI", search_field="cat")
```

**Return format:**
```python
[
    {
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "published": "2024-01-15",
        "updated": "2024-01-20",
        "url": "https://arxiv.org/abs/2401.12345",
        "summary": "Abstract text...",
        "link_pdf": "https://arxiv.org/pdf/2401.12345",
        "categories": ["cs.AI", "cs.LG"],
        "comment": "10 pages, 5 figures"
    }
]
```

### 2. Tavily Search Tool

**Enhanced features:**
- Search depth control (basic/advanced)
- Topic filtering (general/news)
- Time-based filtering (last N days)
- Direct answer extraction
- Image search support
- Score-based ranking

**Basic usage:**
```python
from eval.research_tools import tavily_search_tool

# Simple search
results = tavily_search_tool("latest AI developments")

# News search (last 7 days)
news = tavily_search_tool(
    "quantum computing breakthrough",
    topic="news",
    days=7,
    max_results=10
)

# Deep search with answer
results = tavily_search_tool(
    "What is CRISPR?",
    search_depth="advanced",
    include_answer=True
)

# Search with images
results = tavily_search_tool(
    "Mars rover images",
    include_images=True
)
```

**Return format:**
```python
[
    {
        "answer": "Direct answer to the query..."  # If include_answer=True
    },
    {
        "title": "Result Title",
        "content": "Content snippet...",
        "url": "https://example.com",
        "score": 0.95
    },
    {
        "image_url": "https://example.com/image.jpg"  # If include_images=True
    }
]
```

### 3. Wikipedia Search Tool

**Enhanced features:**
- LRU caching (128 entries)
- Auto-suggestion for misspellings
- Disambiguation handling
- Configurable summary length
- Better error messages

**Basic usage:**
```python
from eval.research_tools import wikipedia_search_tool

# Simple search
result = wikipedia_search_tool("Machine learning")

# Brief summary
result = wikipedia_search_tool("Python programming", sentences=3)

# Detailed summary
result = wikipedia_search_tool("Quantum mechanics", sentences=10)

# Disable auto-suggest
result = wikipedia_search_tool("AI", auto_suggest=False)
```

**Return format:**
```python
[
    {
        "title": "Machine learning",
        "summary": "Machine learning is a field of study...",
        "url": "https://en.wikipedia.org/wiki/Machine_learning"
    }
]
```

## Utility Functions

### Search All Tools

Search across all tools simultaneously:

```python
from eval.research_tools import search_all

results = search_all("quantum computing", max_results_per_tool=5)

print(f"arXiv papers: {len(results['arxiv'])}")
print(f"Web results: {len(results['tavily'])}")
print(f"Wikipedia: {len(results['wikipedia'])}")
```

### Tool Management

```python
from eval.research_tools import (
    get_tool,
    list_tools,
    get_tool_metadata,
    RESEARCH_TOOLS
)

# List available tools
tools = list_tools()
# ['arxiv_search_tool', 'tavily_search_tool', 'wikipedia_search_tool']

# Get a specific tool
arxiv_tool = get_tool("arxiv_search_tool")
results = arxiv_tool("quantum computing")

# Get tool metadata
metadata = get_tool_metadata("arxiv_search_tool")
print(metadata["best_for"])
# ['research papers', 'academic literature', 'preprints']

# Access tool mapping
for name, func in RESEARCH_TOOLS.items():
    print(f"{name}: {func.__doc__}")
```

## Integration with Research Agent

### Option 1: Direct Import

```python
# In tool_use/research_agent/research_agent.py
from eval.research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool
)

# Use with AISuite
tools = [
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool
]

response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=tools,
    max_turns=5
)
```

### Option 2: Dynamic Loading

```python
from eval.research_tools import RESEARCH_TOOLS

# Get all tools
tools = list(RESEARCH_TOOLS.values())

# Or select specific tools
selected_tools = [
    RESEARCH_TOOLS["arxiv_search_tool"],
    RESEARCH_TOOLS["tavily_search_tool"]
]
```

### Option 3: With Evaluation

Combine with the evaluation package:

```python
from eval.research_tools import tavily_search_tool
from eval import DomainEvaluator, ACADEMIC_DOMAINS

# Search
results = tavily_search_tool("quantum computing research")

# Evaluate sources
evaluator = DomainEvaluator(preferred_domains=ACADEMIC_DOMAINS)
evaluation = evaluator.evaluate_json(results)

print(f"Status: {evaluation.status}")
print(f"Preferred ratio: {evaluation.preferred_ratio:.2%}")
```

## Configuration

### Environment Variables

Required:
```bash
TAVILY_API_KEY=your_tavily_api_key
```

Optional:
```bash
DLAI_TAVILY_BASE_URL=https://custom-tavily-endpoint.com
```

### Logging

Configure logging level:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger("eval.research_tools")
logger.setLevel(logging.INFO)
```

## Error Handling

All tools return `[{"error": "..."}]` on failure:

```python
results = arxiv_search_tool("invalid query")

if results and "error" in results[0]:
    print(f"Search failed: {results[0]['error']}")
else:
    print(f"Found {len(results)} papers")
```

## Performance Considerations

### Caching

Wikipedia searches are cached using `@lru_cache`:

```python
# First call - hits Wikipedia API
result1 = wikipedia_search_tool("Machine learning")

# Second call - returns cached result (instant)
result2 = wikipedia_search_tool("Machine learning")
```

### Rate Limiting

Built-in retry logic with exponential backoff:

```python
# Automatically retries on:
# - 429 (Too Many Requests)
# - 500, 502, 503, 504 (Server errors)

# With backoff: 1s, 2s, 4s
```

### Timeouts

All HTTP requests have 60-second timeout:

```python
# Prevents hanging on slow responses
response = session.get(url, timeout=60)
```

## Advanced Examples

### Multi-source Research

```python
from eval.research_tools import search_all

def research_topic(topic: str):
    """Comprehensive research across all sources."""
    results = search_all(topic, max_results_per_tool=10)
    
    # Process arXiv papers
    papers = [p for p in results["arxiv"] if "error" not in p]
    print(f"Found {len(papers)} academic papers")
    
    # Process web results
    web = [r for r in results["tavily"] if "error" not in r]
    print(f"Found {len(web)} web results")
    
    # Process Wikipedia
    wiki = results["wikipedia"]
    if wiki and "error" not in wiki[0]:
        print(f"Wikipedia summary: {wiki[0]['title']}")
    
    return results

# Use it
results = research_topic("CRISPR gene editing")
```

### Filtered arXiv Search

```python
def find_recent_papers(topic: str, days: int = 30):
    """Find papers submitted in the last N days."""
    from datetime import datetime, timedelta
    
    papers = arxiv_search_tool(
        topic,
        sort_by="submittedDate",
        max_results=50
    )
    
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    recent = [
        p for p in papers
        if "error" not in p and p["published"] >= cutoff
    ]
    
    return recent

# Use it
recent_papers = find_recent_papers("machine learning", days=7)
```

### News Monitoring

```python
def monitor_news(keywords: list[str], days: int = 1):
    """Monitor news for specific keywords."""
    all_news = []
    
    for keyword in keywords:
        news = tavily_search_tool(
            keyword,
            topic="news",
            days=days,
            max_results=5
        )
        all_news.extend([
            {**item, "keyword": keyword}
            for item in news
            if "error" not in item
        ])
    
    return all_news

# Use it
news = monitor_news(
    ["quantum computing", "AI breakthrough", "gene therapy"],
    days=7
)
```

## Comparison: M4 vs Production

### M4 Version (Educational)

**Purpose:** Demonstrate concepts in notebooks

**Features:**
- Simple, readable code
- Minimal dependencies
- Basic error handling
- Good for learning

**Use when:**
- Teaching tool calling concepts
- Demonstrating in notebooks
- Quick prototypes

### Production Version (eval/research_tools.py)

**Purpose:** Production use in research agents

**Features:**
- Robust error handling
- Retry logic and caching
- Extensive configuration
- Logging and monitoring
- Input validation
- Performance optimizations

**Use when:**
- Building production systems
- Integrating with research_agent
- Need reliability and performance
- Require advanced features

## Migration Guide

### From M4 to Production

**Before (M4):**
```python
from eval.M4 import research_tools

papers = research_tools.arxiv_search_tool("quantum computing")
```

**After (Production):**
```python
from eval.research_tools import arxiv_search_tool

# Same interface, enhanced features
papers = arxiv_search_tool("quantum computing")

# Now with advanced options
papers = arxiv_search_tool(
    "quantum computing",
    search_field="ti",
    sort_by="submittedDate",
    max_results=10
)
```

### Backward Compatibility

The production version maintains backward compatibility:

```python
# All M4 calls work without changes
arxiv_search_tool("query", max_results=5)
tavily_search_tool("query", max_results=5, include_images=False)
wikipedia_search_tool("query", sentences=5)
```

## Testing

### Basic Tests

```python
def test_arxiv_search():
    results = arxiv_search_tool("machine learning", max_results=3)
    assert len(results) <= 3
    assert all("title" in r for r in results if "error" not in r)

def test_tavily_search():
    results = tavily_search_tool("Python programming", max_results=3)
    assert len(results) <= 3
    assert all("url" in r for r in results if "error" not in r)

def test_wikipedia_search():
    results = wikipedia_search_tool("Python (programming language)")
    assert len(results) == 1
    assert "summary" in results[0]
```

## Troubleshooting

### Common Issues

**1. TAVILY_API_KEY not found**
```python
# Solution: Set environment variable
import os
os.environ["TAVILY_API_KEY"] = "your_key_here"
```

**2. Wikipedia disambiguation error**
```python
# Problem: Query is ambiguous
results = wikipedia_search_tool("Python")
# Returns: {"error": "Ambiguous query. Options: Python (programming language), ..."}

# Solution: Be more specific
results = wikipedia_search_tool("Python programming language")
```

**3. arXiv timeout**
```python
# Problem: Request times out
# Solution: Already handled with 60s timeout and retry logic
# If persistent, reduce max_results
papers = arxiv_search_tool("query", max_results=5)  # Instead of 100
```

## See Also

- [eval/README.md](./README.md) - Evaluation package documentation
- [eval/INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - Integration patterns
- [eval/docs/AISUITE_VS_RAW_API.md](./docs/AISUITE_VS_RAW_API.md) - Tool calling architecture
- [tool_use/research_agent/README.md](../tool_use/research_agent/README.md) - Research agent documentation
