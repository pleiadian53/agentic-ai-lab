# AISuite vs. Raw OpenAI API: Tool Calling Differences

## TL;DR

**AISuite** (used in M4 notebook):
- ✅ Automatically generates JSON schemas from Python functions
- ✅ You only need the function implementation
- ✅ Pass function objects directly to `tools=`

**Raw OpenAI API** (what the architecture docs explain):
- ⚠️ Requires manual JSON schema definition
- ⚠️ You need both function AND schema
- ⚠️ Pass schema dictionaries to `tools=`

## The M4 Notebook Approach (AISuite)

### What You See in the Code

```python
from aisuite import Client

def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Searches arXiv for research papers."""
    # Implementation...
    return results

# Usage - Just pass the function!
client = Client()
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=[arxiv_search_tool],  # Function object, not schema!
    tool_choice="auto",
    max_turns=5,
)
```

### What AISuite Does Behind the Scenes

AISuite automatically:

1. **Inspects the function signature**
   ```python
   def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
   ```
   → Extracts: `query` (required), `max_results` (optional, default=5)

2. **Reads the docstring**
   ```python
   """Searches arXiv for research papers."""
   ```
   → Uses as function description

3. **Parses type hints**
   ```python
   query: str  → "type": "string"
   max_results: int  → "type": "integer"
   ```

4. **Generates JSON schema**
   ```python
   {
       "type": "function",
       "function": {
           "name": "arxiv_search_tool",
           "description": "Searches arXiv for research papers.",
           "parameters": {
               "type": "object",
               "properties": {
                   "query": {"type": "string"},
                   "max_results": {"type": "integer"}
               },
               "required": ["query"]
           }
       }
   }
   ```

5. **Sends to LLM**

## The Raw OpenAI API Approach

### What You Must Do Manually

```python
from openai import OpenAI

# 1. Define the function
def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Searches arXiv for research papers."""
    # Implementation...
    return results

# 2. MANUALLY define the schema
arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Searches for research papers on arXiv by query string.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for research papers."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

# 3. Pass the schema (not the function!)
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=[arxiv_tool_def],  # Schema dictionary, not function!
)

# 4. Manually route tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "arxiv_search_tool":
            args = json.loads(tool_call.function.arguments)
            result = arxiv_search_tool(**args)  # Execute function
```

## Why `research_tools.py` Has Both

Looking at `eval/M4/research_tools.py`:

```python
# The function (implementation)
def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Searches arXiv for research papers."""
    # ... implementation ...
    return results

# The schema (explicit definition)
arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Searches for research papers on arXiv by query string.",
        # ... schema ...
    }
}

# The mapping
tool_mapping = {
    "arxiv_search_tool": arxiv_search_tool
}
```

**Why all three?**

1. **Function** - Required for execution (both approaches need this)
2. **Schema** - For educational purposes and raw API compatibility
3. **Mapping** - For manual tool call routing (raw API approach)

**In the M4 notebook, only the function is actually used** because AISuite handles the rest!

## Comparison Table

| Aspect | AISuite | Raw OpenAI API |
|--------|---------|----------------|
| **Schema generation** | Automatic | Manual |
| **What you pass to `tools=`** | Function objects | Schema dictionaries |
| **Type hints required?** | Yes (for auto-generation) | No (but recommended) |
| **Docstrings used?** | Yes (for descriptions) | No (manual descriptions) |
| **Tool call routing** | Automatic (with `max_turns`) | Manual |
| **Code verbosity** | Low | High |
| **Control over schema** | Limited | Full |

## When to Use Each

### Use AISuite When:
- ✅ You want rapid development
- ✅ Your function signatures are clear
- ✅ You're okay with auto-generated descriptions
- ✅ You want automatic multi-turn handling
- ✅ You're building prototypes or educational projects

### Use Raw OpenAI API When:
- ✅ You need precise control over descriptions
- ✅ You want to optimize token usage
- ✅ You need custom parameter constraints (enums, patterns, etc.)
- ✅ You're building production systems
- ✅ You need to support multiple LLM providers without abstraction

## The Documentation Context

The **TOOL_CALLING_ARCHITECTURE.md** document explains the **raw OpenAI API approach** because:

1. **It's the underlying mechanism** - Understanding this helps you understand what AISuite does
2. **It's more universal** - Works with any LLM provider
3. **It's more explicit** - Shows exactly what the LLM sees
4. **It's educational** - Helps you understand the full picture

But in the **M4 notebook**, you're using **AISuite's automatic approach**, which is simpler!

## Example: Both Approaches Side-by-Side

### AISuite (M4 Notebook Style)

```python
from aisuite import Client

def search_papers(query: str, year: int = 2024) -> list[dict]:
    """
    Searches for academic papers.
    
    Args:
        query: Search keywords
        year: Publication year filter
    """
    # Implementation...
    return results

# That's it! Just use it:
client = Client()
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=[{"role": "user", "content": "Find papers on quantum computing"}],
    tools=[search_papers],  # Pass function directly
    max_turns=3
)
```

### Raw OpenAI API

```python
from openai import OpenAI
import json

def search_papers(query: str, year: int = 2024) -> list[dict]:
    """Searches for academic papers."""
    # Implementation...
    return results

search_papers_def = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Searches for academic papers with optional year filter",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for papers"
                },
                "year": {
                    "type": "integer",
                    "description": "Publication year filter",
                    "default": 2024
                }
            },
            "required": ["query"]
        }
    }
}

tool_mapping = {"search_papers": search_papers}

client = OpenAI()
messages = [{"role": "user", "content": "Find papers on quantum computing"}]

# First call
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=[search_papers_def]  # Pass schema
)

# Manual tool call handling
while response.choices[0].message.tool_calls:
    messages.append(response.choices[0].message)
    
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute function
        function_to_call = tool_mapping[function_name]
        result = function_to_call(**function_args)
        
        # Add result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
    
    # Next turn
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[search_papers_def]
    )
```

**Much more code for the same result!**

## AISuite's Magic: Introspection

AISuite uses Python's introspection capabilities:

```python
import inspect

def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Searches arXiv for research papers."""
    pass

# What AISuite does internally:
sig = inspect.signature(arxiv_search_tool)
doc = inspect.getdoc(arxiv_search_tool)

for param_name, param in sig.parameters.items():
    print(f"Parameter: {param_name}")
    print(f"  Type: {param.annotation}")
    print(f"  Default: {param.default}")

# Output:
# Parameter: query
#   Type: <class 'str'>
#   Default: <class 'inspect._empty'>
# Parameter: max_results
#   Type: <class 'int'>
#   Default: 5
```

This is why **type hints and docstrings matter** when using AISuite!

## Summary

### In M4 Notebook (AISuite):
```python
# You only need this:
def my_tool(param: str) -> dict:
    """Does something."""
    return result

# AISuite handles the rest!
tools=[my_tool]
```

### In Raw OpenAI API:
```python
# You need all three:
def my_tool(param: str) -> dict:
    return result

my_tool_def = {"type": "function", ...}  # Schema
tool_mapping = {"my_tool": my_tool}      # Mapping

# And manual routing!
tools=[my_tool_def]
```

### The Documentation:
- **TOOL_CALLING_ARCHITECTURE.md** explains the **raw API approach** (the underlying mechanism)
- **M4 notebook** uses the **AISuite approach** (automatic and simpler)
- Both are valid, but AISuite abstracts away the complexity!

## Key Takeaway

**You're correct!** In the M4 notebook with AISuite:
- ✅ You don't need explicit `arxiv_tool_def` dictionaries
- ✅ You don't need `tool_mapping`
- ✅ You just pass function objects directly

**But understanding the raw API approach helps you:**
- Understand what AISuite does behind the scenes
- Debug issues when auto-generation doesn't work as expected
- Optimize descriptions for better LLM performance
- Work with other frameworks or raw APIs when needed
