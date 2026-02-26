# Tool Calling Quick Reference

## TL;DR

**You need TWO things for each tool:**

1. **Python function** (does the work)
2. **JSON schema** (tells LLM about it)

## Minimal Example

```python
# 1. The function (implementation)
def search_papers(query: str, max_results: int = 5) -> list[dict]:
    """Search for academic papers."""
    # ... your code here ...
    return results

# 2. The schema (definition for LLM)
search_papers_def = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Searches for academic papers by query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

# 3. The mapping (connects name to function)
tool_mapping = {
    "search_papers": search_papers
}
```

## Why Both?

| Component | Purpose | Used By |
|-----------|---------|---------|
| **Function** | Executes the tool | Your code |
| **Schema** | Describes the tool | The LLM |
| **Mapping** | Routes calls to functions | Your orchestration |

**Key insight**: The LLM cannot see your Python code. It only sees the schema.

## Schema Template

```python
tool_def = {
    "type": "function",
    "function": {
        "name": "function_name",  # Must match Python function name
        "description": "What this tool does and when to use it",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",  # or "integer", "boolean", "object", "array"
                    "description": "What this parameter is for"
                },
                "param2": {
                    "type": "integer",
                    "description": "Another parameter",
                    "default": 10  # Optional: default value
                }
            },
            "required": ["param1"]  # List required parameters
        }
    }
}
```

## Common Types

```python
"type": "string"    # Text
"type": "integer"   # Whole numbers
"type": "number"    # Decimals
"type": "boolean"   # true/false
"type": "object"    # Dictionary/JSON object
"type": "array"     # List
```

## Checklist

- [ ] Function name matches schema name
- [ ] All function parameters are in schema
- [ ] Required parameters marked in schema
- [ ] Good descriptions for function and all parameters
- [ ] Function added to tool_mapping
- [ ] Schema added to tools list sent to LLM

## Common Mistakes

❌ **Mismatched names**
```python
def my_search():  # Function name
    pass

schema = {"name": "search"}  # Different name - won't work!
```

✅ **Matching names**
```python
def my_search():
    pass

schema = {"name": "my_search"}  # Same name - works!
```

---

❌ **Vague description**
```python
"description": "Does stuff"
```

✅ **Clear description**
```python
"description": "Searches arXiv for research papers. Use for academic papers in physics, math, CS."
```

---

❌ **Missing from mapping**
```python
def my_tool():
    pass

my_tool_def = {...}

# Forgot this!
# tool_mapping = {"my_tool": my_tool}
```

✅ **Complete setup**
```python
def my_tool():
    pass

my_tool_def = {...}

tool_mapping = {"my_tool": my_tool}  # Don't forget!
```

## See Also

- [Full Architecture Guide](./TOOL_CALLING_ARCHITECTURE.md) - Detailed explanation
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
