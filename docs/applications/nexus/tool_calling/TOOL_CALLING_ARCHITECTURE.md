# Tool Calling Architecture: Function Implementation vs. Schema Definition

## Overview

When building LLM-powered agents with tool-calling capabilities, you need **two separate but complementary representations** of each tool:

1. **Python Function** (Implementation) - The actual executable code
2. **JSON Schema** (Definition) - The metadata that describes the function to the LLM

This document explains why both are necessary and how they work together.

## The Two Representations

### 1. Python Function (Implementation)

```python
def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches arXiv for research papers matching the given query.
    """
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        # ... parsing logic ...
        return results
    except Exception as e:
        return [{"error": str(e)}]
```

**Purpose**: This is the **actual code** that executes when the tool is called.

**Characteristics**:
- Written in Python
- Contains business logic
- Makes API calls, processes data
- Returns structured results
- Handles errors and edge cases

### 2. JSON Schema (Definition)

```python
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
```

**Purpose**: This is the **metadata** that tells the LLM about the tool.

**Characteristics**:
- Written as JSON/dictionary
- Describes function signature
- Provides semantic descriptions
- Specifies parameter types and constraints
- Indicates required vs. optional parameters

## Why Both Are Necessary

### The LLM Cannot See Your Code

**Key Insight**: The LLM has **no access** to your Python function's implementation. It cannot:
- Read your function signature
- Parse your docstrings
- Inspect parameter types
- Understand what the function does

The LLM only sees what you explicitly tell it through the JSON schema.

### The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Tool Registration                      │
│  You send JSON schema to LLM: "Here are the tools you have" │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    2. LLM Decision Making                    │
│  LLM reads schema and decides: "I need arxiv_search_tool"   │
│  LLM generates: {"name": "arxiv_search_tool",               │
│                  "arguments": {"query": "quantum"}}         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    3. Your Code Execution                    │
│  You receive tool call from LLM                             │
│  You look up function in tool_mapping                       │
│  You execute: arxiv_search_tool(query="quantum")           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    4. Return Results to LLM                  │
│  Your function returns results                              │
│  You send results back to LLM                               │
│  LLM uses results to formulate response                     │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Comparison

| Aspect | Python Function | JSON Schema |
|--------|----------------|-------------|
| **Audience** | Python interpreter | LLM |
| **Purpose** | Execute the tool | Describe the tool |
| **Contains** | Implementation logic | Metadata and documentation |
| **Used by** | Your application code | LLM's decision-making |
| **When** | At execution time | At planning time |
| **Format** | Python code | JSON/dictionary |

## Example: Complete Tool Definition

### Step 1: Implement the Function

```python
def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False) -> list[dict]:
    """
    Perform a search using the Tavily API.
    
    Args:
        query: The search query
        max_results: Number of results to return (default 5)
        include_images: Whether to include image results
        
    Returns:
        List of dictionaries with 'title', 'content', and 'url'
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images
        )
        
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", "")
            })
        
        return results
    except Exception as e:
        return [{"error": str(e)}]
```

### Step 2: Define the Schema

```python
tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",  # Must match function name
        "description": "Performs a general-purpose web search using the Tavily API.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for retrieving information from the web."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image results.",
                    "default": False
                }
            },
            "required": ["query"]  # Only query is required
        }
    }
}
```

### Step 3: Create Tool Mapping

```python
tool_mapping = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool
}
```

**Purpose**: Maps function names (strings) to actual function objects for execution.

### Step 4: Use in Agent

```python
# Send schemas to LLM
tools = [arxiv_tool_def, tavily_tool_def, wikipedia_tool_def]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Research quantum computing"}],
    tools=tools  # LLM sees only the schemas
)

# Execute tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Look up actual function
        function_to_call = tool_mapping[function_name]
        
        # Execute it
        result = function_to_call(**function_args)
```

## Key Design Principles

### 1. Schema Must Match Function Signature

```python
# ✅ GOOD: Schema matches function
def search(query: str, limit: int = 10):
    pass

schema = {
    "name": "search",
    "parameters": {
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 10}
        }
    }
}
```

```python
# ❌ BAD: Schema doesn't match
def search(query: str, limit: int = 10):
    pass

schema = {
    "name": "search",
    "parameters": {
        "properties": {
            "q": {"type": "string"},  # Wrong parameter name!
            "max": {"type": "integer"}  # Wrong parameter name!
        }
    }
}
```

### 2. Descriptions Are Critical

The LLM relies **entirely** on descriptions to understand when to use a tool:

```python
# ❌ BAD: Vague description
"description": "Searches for stuff"

# ✅ GOOD: Specific, actionable description
"description": "Searches for research papers on arXiv by query string. Use this for academic papers in physics, math, CS, and related fields."
```

### 3. Parameter Descriptions Guide LLM Behavior

```python
# ❌ BAD: No context
"query": {
    "type": "string",
    "description": "Query"
}

# ✅ GOOD: Clear guidance
"query": {
    "type": "string",
    "description": "Search keywords for research papers. Can include author names, paper titles, or topic keywords. Example: 'quantum entanglement' or 'author:Einstein'"
}
```

### 4. Specify Required vs. Optional

```python
{
    "parameters": {
        "properties": {
            "query": {"type": "string"},      # Required
            "max_results": {                   # Optional
                "type": "integer",
                "default": 5
            }
        },
        "required": ["query"]  # Explicitly list required params
    }
}
```

## Common Patterns

### Pattern 1: Simple Tool

```python
# Function
def get_weather(location: str) -> dict:
    return {"temp": 72, "condition": "sunny"}

# Schema
weather_tool_def = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or zip code"
                }
            },
            "required": ["location"]
        }
    }
}
```

### Pattern 2: Tool with Optional Parameters

```python
# Function
def search_papers(query: str, year: int | None = None, max_results: int = 10) -> list:
    # Implementation
    pass

# Schema
search_tool_def = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Search academic papers with optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords"
                },
                "year": {
                    "type": "integer",
                    "description": "Filter by publication year (optional)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}
```

### Pattern 3: Tool with Enums

```python
# Function
def analyze_sentiment(text: str, language: str = "en") -> dict:
    # Implementation
    pass

# Schema
sentiment_tool_def = {
    "type": "function",
    "function": {
        "name": "analyze_sentiment",
        "description": "Analyze sentiment of text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze"
                },
                "language": {
                    "type": "string",
                    "description": "Language code",
                    "enum": ["en", "es", "fr", "de"],
                    "default": "en"
                }
            },
            "required": ["text"]
        }
    }
}
```

## Best Practices

### 1. Keep Schemas in Sync with Functions

When you modify a function signature, **always update the schema**:

```python
# Before
def search(query: str):
    pass

# After: Added new parameter
def search(query: str, filters: dict | None = None):
    pass

# Don't forget to update schema!
schema["parameters"]["properties"]["filters"] = {
    "type": "object",
    "description": "Optional filters for search results"
}
```

### 2. Use Type Hints in Functions

```python
# ✅ GOOD: Clear types
def search(query: str, max_results: int = 5) -> list[dict]:
    pass

# ❌ BAD: No type hints
def search(query, max_results=5):
    pass
```

### 3. Validate Schema Against OpenAPI Spec

The schema format follows [OpenAPI 3.0 specification](https://spec.openapis.org/oas/v3.0.0):

- `type`: "string", "integer", "number", "boolean", "object", "array"
- `description`: Human-readable explanation
- `enum`: List of allowed values
- `default`: Default value if not provided
- `required`: Array of required parameter names

### 4. Test Both Representations

```python
# Test function execution
result = arxiv_search_tool(query="quantum computing")
assert "title" in result[0]

# Test schema validity
import jsonschema
jsonschema.validate(instance=arxiv_tool_def, schema=openapi_schema)

# Test schema-function alignment
function_params = inspect.signature(arxiv_search_tool).parameters
schema_params = arxiv_tool_def["function"]["parameters"]["properties"]
assert set(function_params.keys()) == set(schema_params.keys())
```

### 5. Document Both

```python
def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches arXiv for research papers matching the given query.
    
    This function is used by the LLM agent to search for academic papers
    in physics, mathematics, computer science, and related fields.
    
    Args:
        query: Search keywords for research papers
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of dictionaries containing paper metadata:
        - title: Paper title
        - authors: List of author names
        - published: Publication date
        - url: Abstract URL
        - summary: Paper abstract
        - link_pdf: PDF download link
        
    Example:
        >>> results = arxiv_search_tool("quantum entanglement", max_results=3)
        >>> print(results[0]["title"])
    """
    # Implementation...
```

## Common Pitfalls

### ❌ Pitfall 1: Mismatched Names

```python
# Function name
def search_arxiv(query: str):
    pass

# Schema name (WRONG!)
schema = {
    "name": "arxiv_search"  # Doesn't match!
}

# Tool mapping won't work
tool_mapping = {
    "arxiv_search": search_arxiv  # LLM calls "arxiv_search", but key is wrong
}
```

### ❌ Pitfall 2: Missing Required Parameters

```python
# Function requires both
def search(query: str, database: str):
    pass

# Schema only marks one as required
schema = {
    "required": ["query"]  # Missing "database"!
}

# Result: LLM might not provide database, causing errors
```

### ❌ Pitfall 3: Poor Descriptions

```python
# Too vague
"description": "Does a search"

# Too technical
"description": "Executes HTTP GET request to arXiv API endpoint with query parameter"

# Just right ✅
"description": "Searches for research papers on arXiv by query string. Use this for academic papers in physics, math, CS, and related fields."
```

### ❌ Pitfall 4: Forgetting Tool Mapping

```python
# Defined function and schema, but forgot mapping
def my_tool():
    pass

my_tool_def = {...}

# Missing!
# tool_mapping = {"my_tool": my_tool}

# Result: Runtime error when LLM tries to call the tool
```

## Summary

### The Function (Implementation)
- **What**: Executable Python code
- **For**: Your application
- **Contains**: Business logic, API calls, error handling
- **Used**: At execution time

### The Schema (Definition)
- **What**: JSON metadata
- **For**: The LLM
- **Contains**: Function signature, descriptions, constraints
- **Used**: At planning/decision time

### The Mapping
- **What**: Dictionary linking names to functions
- **For**: Your orchestration code
- **Contains**: `{function_name: function_object}`
- **Used**: To route LLM's tool calls to actual code

### Why Both?
Because **the LLM cannot see your code**. It needs explicit metadata to understand:
- What tools are available
- What each tool does
- What parameters each tool needs
- When to use each tool

The schema is the **contract** between your code and the LLM.

## Further Reading

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [JSON Schema Documentation](https://json-schema.org/)
- Tool Use course: M4 module on component-level evaluation
