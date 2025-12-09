# Tool Use Tutorial: Building an Agentic Chatbot

This tutorial walks through the key components of the L3 chatbot, explaining how Claude's tool use capability works and how to implement an agentic loop.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tool Functions](#tool-functions)
3. [Tool Schema Definition](#tool-schema-definition)
4. [Tool Mapping and Execution](#tool-mapping-and-execution)
5. [The Agentic Loop: `process_query()`](#the-agentic-loop-process_query)
6. [Common Pitfalls](#common-pitfalls)

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────▶│   Claude    │────▶│   Tools     │
│   Query     │     │   (LLM)     │     │  (Python)   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          │   tool_use         │
                          │◀───────────────────│
                          │                    │
                          │   tool_result      │
                          │───────────────────▶│
                          │                    │
                          ▼                    │
                    ┌─────────────┐            │
                    │   Final     │◀───────────┘
                    │  Response   │
                    └─────────────┘
```

The flow:
1. User sends a query
2. Claude decides whether to use tools or respond directly
3. If tools are needed, Claude returns `tool_use` blocks
4. We execute the tools and return `tool_result` blocks
5. Claude processes results and either calls more tools or gives a final response

---

## Tool Functions

### `search_papers(topic, max_results=5)`

Searches arXiv for papers matching a topic and saves metadata to JSON.

```python
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    # Use arxiv client to search
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    # Create directory structure: papers/<topic>/papers_info.json
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    # Save paper metadata (title, authors, summary, pdf_url, published)
    # Returns list of paper IDs
```

**Key points:**
- Creates organized directory structure by topic
- Persists results to JSON for later retrieval
- Returns paper IDs that can be used with `extract_info`

### `extract_info(paper_id)`

Retrieves saved information about a specific paper.

```python
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
    # Searches all topic directories in papers/
    # Returns JSON string with paper details or error message
```

**Key points:**
- Searches across all saved topics
- Returns JSON string (tools should return strings for Claude)

---

## Tool Schema Definition

Claude needs to know what tools are available and how to call them. This is done via JSON Schema:

```python
tools = [
    {
        "name": "search_papers",
        "description": "Search for papers on arXiv based on a topic and store their information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for"
                }, 
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to retrieve",
                    "default": 5
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "extract_info",
        "description": "Search for information about a specific paper across all topic directories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The ID of the paper to look for"
                }
            },
            "required": ["paper_id"]
        }
    }
]
```

**Schema components:**
- `name`: Unique identifier Claude uses to call the tool
- `description`: Helps Claude understand when to use the tool
- `input_schema`: JSON Schema defining parameters
  - `properties`: Parameter definitions with types and descriptions
  - `required`: List of mandatory parameters
  - `default`: Optional default values

---

## Tool Mapping and Execution

We need to map tool names to actual Python functions:

```python
mapping_tool_function = {
    "search_papers": search_papers,
    "extract_info": extract_info
}

def execute_tool(tool_name, tool_args):
    """Execute a tool by name with given arguments."""
    
    # Call the function with unpacked arguments
    result = mapping_tool_function[tool_name](**tool_args)

    # Normalize result to string (required for tool_result)
    if result is None:
        result = "The operation completed but didn't return any results."
    elif isinstance(result, list):
        result = ', '.join(result)
    elif isinstance(result, dict):
        result = json.dumps(result, indent=2)
    else:
        result = str(result)
    
    return result
```

**Key points:**
- `**tool_args` unpacks the dictionary into keyword arguments
- Results must be converted to strings for the API
- Handle edge cases (None, lists, dicts)

---

## The Agentic Loop: `process_query()`

This is the core of the chatbot—the agentic loop that handles iterative tool use.

```python
def process_query(query):
    """Process a user query with tool use support."""
    
    # Initialize conversation with user query
    messages = [{'role': 'user', 'content': query}]
    
    # First API call
    response = client.messages.create(
        max_tokens=2024,
        model='claude-sonnet-4-20250514', 
        tools=tools,
        messages=messages
    )
    
    # Agentic loop: continue while Claude wants to use tools
    while response.stop_reason == "tool_use":
        tool_results = []
        
        # Process all content blocks in the response
        for content in response.content:
            if content.type == 'text' and content.text:
                print(content.text)  # Claude's reasoning/explanation
            
            elif content.type == 'tool_use':
                # Execute the tool
                tool_name = content.name
                tool_args = content.input
                tool_id = content.id
                
                print(f"Calling tool {tool_name} with args {tool_args}")
                result = execute_tool(tool_name, tool_args)
                
                # Collect tool result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result
                })
        
        # Add assistant's response (with tool_use blocks) to history
        messages.append({'role': 'assistant', 'content': response.content})
        
        # Add all tool results as a user message
        messages.append({'role': 'user', 'content': tool_results})
        
        # Get next response from Claude
        response = client.messages.create(
            max_tokens=2024,
            model='claude-sonnet-4-20250514', 
            tools=tools,
            messages=messages
        )
    
    # Print final text response
    for content in response.content:
        if content.type == 'text':
            print(content.text)
```

### Step-by-Step Breakdown

#### 1. Initialize the Conversation

```python
messages = [{'role': 'user', 'content': query}]
```

The messages list maintains the full conversation history. Each message has:
- `role`: Either `'user'` or `'assistant'`
- `content`: String or list of content blocks

#### 2. First API Call

```python
response = client.messages.create(
    max_tokens=2024,
    model='claude-sonnet-4-20250514', 
    tools=tools,          # Pass tool definitions
    messages=messages
)
```

Claude receives the query and tool definitions. It decides whether to:
- Respond directly (`stop_reason == "end_turn"`)
- Use tools (`stop_reason == "tool_use"`)

#### 3. Check Stop Reason

```python
while response.stop_reason == "tool_use":
```

The `stop_reason` tells us why Claude stopped generating:
- `"end_turn"`: Claude finished responding
- `"tool_use"`: Claude wants to call one or more tools
- `"max_tokens"`: Hit the token limit

#### 4. Process Response Content

```python
for content in response.content:
    if content.type == 'text' and content.text:
        print(content.text)
    elif content.type == 'tool_use':
        # Handle tool call
```

A response can contain multiple content blocks:
- `text`: Claude's explanation or reasoning
- `tool_use`: A tool call with `id`, `name`, and `input`

#### 5. Handle Multiple Tool Calls

```python
tool_results = []
for content in response.content:
    if content.type == 'tool_use':
        # ... execute tool ...
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_id,
            "content": result
        })
```

**Critical**: Claude can call multiple tools in one response. You must:
1. Execute ALL tools
2. Return ALL results in a single user message
3. Match each result to its `tool_use_id`

#### 6. Update Message History

```python
# Add assistant's full response
messages.append({'role': 'assistant', 'content': response.content})

# Add tool results as user message
messages.append({'role': 'user', 'content': tool_results})
```

The message structure must be:
```
user → assistant (with tool_use) → user (with tool_result) → assistant → ...
```

#### 7. Continue the Loop

```python
response = client.messages.create(...)
```

Claude receives the tool results and either:
- Calls more tools (loop continues)
- Provides final response (loop exits)

---

## Common Pitfalls

### 1. Not Handling Multiple Tool Calls

**Wrong:**
```python
for content in response.content:
    if content.type == 'tool_use':
        result = execute_tool(...)
        messages.append({'role': 'user', 'content': [tool_result]})
        response = client.messages.create(...)  # Called inside loop!
```

**Right:**
```python
tool_results = []
for content in response.content:
    if content.type == 'tool_use':
        tool_results.append(...)

messages.append({'role': 'assistant', 'content': response.content})
messages.append({'role': 'user', 'content': tool_results})  # All results together
response = client.messages.create(...)  # Called once after loop
```

### 2. Missing tool_use_id Matching

Each `tool_result` must reference the correct `tool_use_id`:

```python
{
    "type": "tool_result",
    "tool_use_id": content.id,  # Must match the tool_use block's id
    "content": result
}
```

### 3. Not Including Assistant Message

Before sending tool results, you must include the assistant's message that contained the tool calls:

```python
messages.append({'role': 'assistant', 'content': response.content})  # Don't forget!
messages.append({'role': 'user', 'content': tool_results})
```

### 4. Tool Results Must Be Strings

The `content` field in `tool_result` must be a string:

```python
# Wrong
{"content": {"key": "value"}}

# Right
{"content": '{"key": "value"}'}
```

---

## Summary

The key components of an agentic chatbot with tool use:

1. **Tool Functions**: Python functions that perform actions
2. **Tool Schemas**: JSON Schema definitions for Claude
3. **Tool Mapping**: Dictionary connecting names to functions
4. **Agentic Loop**: 
   - Check `stop_reason == "tool_use"`
   - Execute ALL requested tools
   - Return ALL results with matching IDs
   - Continue until `stop_reason != "tool_use"`

This pattern forms the foundation for MCP (Model Context Protocol), where tools are exposed via a standardized server interface rather than being defined inline.
