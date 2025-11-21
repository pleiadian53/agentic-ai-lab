# OpenAI Responses API Integration Guide for GPT-5 Models

## Problem Statement
GPT-5 models (e.g., `gpt-5.1`, `gpt-5.1-codex`) utilize the new OpenAI Responses API (`client.responses.create`), which differs significantly from the Chat Completions API (`client.chat.completions.create`) used by GPT-4 models. 

Key differences include:
1. **Endpoint**: `client.responses.create` vs `client.chat.completions.create`.
2. **Tool Definition**: Simplified schema (no nested `function` object required in some contexts, though native format is preferred for compatibility).
3. **Response Structure**: Different object hierarchy for accessing content and tool calls.
4. **Library Support**: `aisuite` currently supports Chat Completions but not the experimental Responses API.

## Solution Overview

We implemented a **dual-path architecture** in `agents.py` and `llm_client.py` that dynamically routes requests based on the model name.

### 1. Model Detection & Routing
We detect the provider and API type based on the model prefix/name.

```python
def _uses_responses_api(model: str) -> bool:
    """Check if model requires OpenAI Responses API (e.g. gpt-5.1)."""
    return model.startswith("gpt-5") or "codex" in model
```

### 2. Tool Schema Transformation
The Responses API accepts a list of tools with a **flattened schema**. Unlike the Chat API which nests `name` and `parameters` under a `function` object, the Responses API expects them at the top level.

**Standard Chat API Format:**
```json
{
  "type": "function",
  "function": {
    "name": "search_tool",
    "description": "...",
    "parameters": { ... }
  }
}
```

**Responses API Format (Corrected):**
```json
{
    "type": "function",
    "name": "search_tool",
    "description": "...",
    "parameters": { ... }
}
```

Implementation:
```python
responses_tools = []
for tool_def in tools_list:
    func = tool_def["function"]
    responses_tools.append({
        "type": "function",
        "name": func["name"],        # Top-level name
        "description": func["description"],
        "parameters": func.get("parameters", {})
    })
```

### 3. Direct API Call & Conversation Loop
For GPT-5 models, we use the native `openai` client with a stateful conversation loop.

**Key Concept**: Instead of stringifying the history, we pass a list of `input_items`. When a tool is called, we append the `function_call` object and the `function_call_output` object to this list and call the API again.

```python
if use_responses_api:
    openai_client = openai.OpenAI()
    
    # Initialize conversation state
    input_items = list(messages)
    
    while True:
        response = openai_client.responses.create(
            model=openai_model,
            input=input_items,  # Pass list directly
            tools=responses_tools,
            tool_choice="auto"
        )
        
        # Check for tool calls
        tool_calls_found = []
        if hasattr(response, 'output'):
            for item in response.output:
                if hasattr(item, 'type') and item.type == 'function_call':
                    tool_calls_found.append(item)
        
        if tool_calls_found:
            for tool_call in tool_calls_found:
                # Execute tool...
                result = execute_tool(tool_call)
                
                # 1. Add function_call to history
                input_items.append(tool_call)
                
                # 2. Add result as function_call_output
                input_items.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result)
                })
            continue # Loop back to model
        
        # No tools, break and return text
        break
```

### 4. Response Parsing
The `response` object does **NOT** have a top-level `tool_calls` attribute. Instead, tool calls are located inside the `response.output` list as items of type `function_call`.

**Handling Tool Calls:**
```python
# Iterate through output items to find tool calls
if hasattr(response, 'output'):
    for item in response.output:
        if hasattr(item, 'type') and item.type == 'function_call':
             tool_name = item.name
             tool_args = json.loads(item.arguments)
             # Execute tool...
```

**Handling Content:**
Content is also found in `response.output` items, typically where `item.type` is NOT `function_call` (e.g., content objects).

```python
# Extract text from output items
texts = []
if hasattr(response, 'output'):
    for item in response.output:
        if hasattr(item, 'content'):
            if isinstance(item.content, str):
                texts.append(item.content)
            elif hasattr(item.content, 'text'):
                texts.append(item.content.text)
response_text = "\n".join(texts)
```

### 5. Troubleshooting & Gotchas

**Missing "reasoning" component error (400)**
If you receive an error like: `Missing required "reasoning" component for function call item`, it means you added a `function_call` item to the history but omitted the `reasoning` item that preceded it.

**Solution**: Always append the **entire** `response.output` to your conversation history, not just the tool calls. This ensures that reasoning items (which justify the tool usage) stay paired with their function calls.

```python
# ✅ Correct:
input_items.extend(response.output)

# ❌ Incorrect (causes 400 error):
for item in response.output:
    if item.type == 'function_call':
        input_items.append(item)
```

## Implementation Details

### File: `llm_client.py`
- **`_normalize_model_name`**: logic to strip `openai:` prefix.
- **`call_llm_text` / `call_llm_json`**: Routing logic.

### File: `agents.py`
- **`market_research_agent`**: Implements the correct flattened tool schema construction and `response.output` iteration parsing logic.

## Status
- **Tool Adherence**: Verified working with `gpt-5.1-codex-mini`. The model correctly identifies the need for tools and executes them when provided with the flattened schema.
- **Parsing**: The `response.output` iteration correctly identifies `function_call` items.

## Usage Example

```python
from market_research.llm_client import call_llm_text

# Automatically routes to Responses API
response = call_llm_text(client, model="gpt-5.1-codex", messages=[...])
```
