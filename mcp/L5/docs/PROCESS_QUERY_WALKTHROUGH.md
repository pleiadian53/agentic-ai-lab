# Walkthrough: `process_query()` in MCP Chatbot

This document explains the `process_query` method in `mcp_chatbot.py`, which orchestrates the conversation between the user, Claude, and MCP tools.

## Overview

```
User Query → Claude → [Tool Calls] → MCP Server → [Tool Results] → Claude → Final Response
```

The method implements an **agentic loop**: Claude can request tools multiple times until it has enough information to answer.

---

## Code Walkthrough

### 1. Initialize the Conversation

```python
async def process_query(self, query):
    """Process a user query with tool use support."""
    messages = [{'role': 'user', 'content': query}]
```

- Creates a message list with the user's query
- This list accumulates the full conversation history

### 2. First Call to Claude

```python
    # Send my query to Claude
    response = self.anthropic.messages.create(
        max_tokens=2024,
        model='claude-sonnet-4-20250514',
        tools=self.available_tools,  # Tools discovered from MCP server
        messages=messages
    )
```

- Sends the query to Claude along with available tool definitions
- Claude decides whether to:
  - **Answer directly** → `stop_reason = "end_turn"`
  - **Request tools** → `stop_reason = "tool_use"`

### 3. The Agentic Loop

```python
    # Process until we get a final text response
    while response.stop_reason == "tool_use":
```

- Continues as long as Claude wants to use tools
- May iterate multiple times (e.g., search → extract → extract → ...)

### 4. Collect Tool Requests

```python
        # Collect all tool uses from the response
        tool_results = []

        for content in response.content:
            if content.type == 'text' and content.text:
                print(content.text)  # Claude's intermediate thoughts
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                tool_id = content.id
```

- Claude's response contains multiple content blocks
- `text` blocks: Claude's reasoning (e.g., "Let me search for papers...")
- `tool_use` blocks: Tool call requests with name, arguments, and unique ID

**Example response content:**
```python
[
    TextBlock(type='text', text='I\'ll search for papers on astrobiology.'),
    ToolUseBlock(type='tool_use', id='toolu_01ABC', name='search_papers', input={'topic': 'astrobiology'})
]
```

### 5. Execute Tools via MCP

```python
                print(f"Calling tool {tool_name} with args {tool_args}")
                result = await self.session.call_tool(tool_name, arguments=tool_args)
```

- `self.session` is the MCP `ClientSession` connected to the server
- `call_tool()` sends the request to the MCP server over stdio
- `await` because this is async I/O (waiting for server response)

### 6. Format Tool Results

```python
                # Convert result content to string if needed
                result_content = result.content
                if isinstance(result_content, list):
                    result_content = str(result_content)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,  # Must match the tool_use ID
                    "content": result_content
                })
```

- Each `tool_result` must reference its corresponding `tool_use_id`
- Results are collected into a list (handles multiple simultaneous tool calls)

### 7. Update Conversation History

```python
        # Add assistant message with all tool uses
        messages.append({'role': 'assistant', 'content': response.content})

        # Add user message with ALL tool results together
        messages.append({'role': 'user', 'content': tool_results})
```

**This is the key insight:**

| Message | Role | Content |
|---------|------|---------|
| Original query | `user` | "Find papers on astrobiology" |
| Claude's tool request | `assistant` | `[TextBlock, ToolUseBlock, ToolUseBlock]` |
| Tool results | `user` | `[tool_result, tool_result]` |

The tool results are tagged as `user` messages because:
1. The Anthropic API requires `tool_result` blocks in a `user` message
2. Conceptually, the tools are "responding" to Claude's request

**Critical**: All `tool_result` blocks must be in the **same** user message, immediately after the assistant message containing the `tool_use` blocks.

### 8. Get Next Response

```python
        # Get next response
        response = self.anthropic.messages.create(
            max_tokens=2024,
            model='claude-sonnet-4-20250514',
            tools=self.available_tools,
            messages=messages
        )
```

- Claude now sees the full history including tool results
- May request more tools or provide final answer
- Loop continues if `stop_reason == "tool_use"`

### 9. Print Final Response

```python
    # Print final text response
    for content in response.content:
        if content.type == 'text':
            print(content.text)
```

- When Claude is done with tools, it returns a text response
- `stop_reason` will be `"end_turn"` or `"max_tokens"`

---

## Message Flow Example

**User asks:** "Find papers on astrobiology and summarize the first one"

### Round 1: Search

```
messages = [
    {'role': 'user', 'content': 'Find papers on astrobiology...'}
]
↓ Claude responds with tool_use
messages = [
    {'role': 'user', 'content': 'Find papers on astrobiology...'},
    {'role': 'assistant', 'content': [TextBlock("I'll search..."), ToolUseBlock(search_papers)]},
    {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': '...', 'content': '["2004.11312v3", ...]'}]}
]
```

### Round 2: Extract

```
↓ Claude responds with tool_use for extract_info
messages = [
    ... previous messages ...,
    {'role': 'assistant', 'content': [TextBlock("Now extracting..."), ToolUseBlock(extract_info)]},
    {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': '...', 'content': '{"title": "...", ...}'}]}
]
```

### Round 3: Final Answer

```
↓ Claude responds with text (stop_reason = "end_turn")
→ Print final response
```

---

## Why `async`?

The method is `async` because:

1. **`await self.session.call_tool(...)`** - MCP communication is async I/O
2. **Non-blocking** - While waiting for the MCP server, other tasks could run
3. **Required by MCP SDK** - `ClientSession.call_tool()` is an async method

Note: `self.anthropic.messages.create()` is synchronous in this code. For fully async, you'd use `await self.anthropic.messages.create()` with the async client.

---

## Error Handling

The current implementation catches errors in `chat_loop()`:

```python
except Exception as e:
    print(f"\nError: {str(e)}")
```

Common errors:
- **400 Invalid Request**: Tool results don't match tool uses (the bug we fixed)
- **Connection Error**: MCP server not running
- **Timeout**: Server taking too long

---

## Summary

| Step | What Happens |
|------|--------------|
| 1 | User query → messages list |
| 2 | Send to Claude with tool definitions |
| 3 | Loop while Claude wants tools |
| 4 | Parse tool requests from response |
| 5 | Execute each tool via MCP session |
| 6 | Collect all results with matching IDs |
| 7 | Append assistant message + user message (results) |
| 8 | Send updated history to Claude |
| 9 | Print final text response |
