# Async Python Tutorial for MCP Clients

This tutorial explains Python's `async`/`await` syntax as used in the L5 MCP client notebook.

## Table of Contents

1. [Why Async?](#why-async)
2. [Core Concepts](#core-concepts)
3. [Async in the MCP Client](#async-in-the-mcp-client)
4. [Key Patterns](#key-patterns)
5. [Common Pitfalls](#common-pitfalls)

---

## Why Async?

### The Problem: Blocking I/O

In traditional (synchronous) Python:

```python
# This blocks the entire program while waiting for the server
result = server.call_tool("search_papers", {"topic": "AI"})
# Nothing else can happen until the server responds
```

When your code waits for:
- Network requests (API calls, server communication)
- File I/O
- Database queries

...the entire program is **blocked**. Nothing else can run.

### The Solution: Non-blocking I/O

With async Python:

```python
# This "yields" control while waiting, allowing other tasks to run
result = await session.call_tool("search_papers", arguments={"topic": "AI"})
# Other async tasks can execute while we wait for the server
```

The `await` keyword says: "I'm waiting for something. Let other tasks run in the meantime."

### When to Use Async

| Use Case | Sync or Async? |
|----------|----------------|
| CPU-bound work (math, processing) | Sync |
| I/O-bound work (network, files) | Async |
| MCP client-server communication | **Async** |
| Simple scripts | Sync |
| Servers handling many connections | Async |

MCP uses async because client-server communication involves waiting for network responses.

---

## Core Concepts

### 1. `async def` - Defining Coroutines

A function defined with `async def` is a **coroutine**:

```python
# Regular function
def greet(name):
    return f"Hello, {name}"

# Coroutine (async function)
async def greet_async(name):
    return f"Hello, {name}"
```

**Key difference**: Calling a coroutine doesn't execute it immediately:

```python
greet("Alice")        # Returns: "Hello, Alice"
greet_async("Alice")  # Returns: <coroutine object> (NOT executed yet!)
```

### 2. `await` - Running Coroutines

To actually run a coroutine, you must `await` it:

```python
async def main():
    result = await greet_async("Alice")  # NOW it executes
    print(result)  # "Hello, Alice"
```

**Rule**: You can only use `await` inside an `async def` function.

### 3. `asyncio.run()` - The Entry Point

To start the async world from regular Python:

```python
import asyncio

async def main():
    print("Hello from async!")

# This is the bridge from sync to async
asyncio.run(main())
```

### 4. `async with` - Async Context Managers

For resources that need async setup/teardown:

```python
# Sync context manager
with open("file.txt") as f:
    data = f.read()

# Async context manager
async with aiofiles.open("file.txt") as f:
    data = await f.read()
```

In MCP, connections use `async with`:

```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Use the session...
```

---

## Async in the MCP Client

Let's trace through the L5 `mcp_chatbot.py` code:

### Entry Point

```python
async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()

if __name__ == "__main__":
    asyncio.run(main())  # Bridge from sync to async
```

### Connecting to the Server

```python
async def connect_to_server_and_run(self):
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "research_server.py"],
        env=None,
    )
    
    # async with: Opens connection, ensures cleanup on exit
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            self.session = session
            
            # await: Wait for server initialization
            await session.initialize()
            
            # await: Wait for tool list from server
            response = await session.list_tools()
            
            # ... process tools ...
            
            # await: Run the chat loop
            await self.chat_loop()
```

**What's happening:**

1. `stdio_client(server_params)` spawns the server as a subprocess
2. `ClientSession(read, write)` creates a communication channel
3. `await session.initialize()` performs the MCP handshake
4. `await session.list_tools()` requests available tools from server

### Processing Queries

```python
async def process_query(self, query):
    messages = [{'role': 'user', 'content': query}]
    
    # Note: This is NOT async - Anthropic's SDK handles it internally
    response = self.anthropic.messages.create(
        max_tokens=2024,
        model='claude-sonnet-4-20250514',
        tools=self.available_tools,
        messages=messages
    )
    
    # ... process response ...
    
    if content.type == 'tool_use':
        # await: Call tool on the MCP server
        result = await self.session.call_tool(tool_name, arguments=tool_args)
```

**Key insight**: The `await self.session.call_tool(...)` is where async matters most—it's a network call to the MCP server.

### The Chat Loop

```python
async def chat_loop(self):
    while True:
        query = input("\nQuery: ").strip()  # Sync input (blocking)
        
        if query.lower() == 'quit':
            break
        
        await self.process_query(query)  # Async processing
```

---

## Key Patterns

### Pattern 1: Nested `async with`

```python
async with outer_resource() as outer:
    async with inner_resource(outer) as inner:
        await do_something(inner)
# Both resources are properly cleaned up
```

This ensures proper cleanup even if exceptions occur.

### Pattern 2: Sequential Awaits

```python
async def sequential():
    result1 = await task1()  # Wait for task1
    result2 = await task2()  # Then wait for task2
    return result1, result2
```

Tasks run one after another.

### Pattern 3: Concurrent Awaits with `gather`

```python
async def concurrent():
    # Run both tasks at the same time
    result1, result2 = await asyncio.gather(
        task1(),
        task2()
    )
    return result1, result2
```

Tasks run in parallel (useful for independent operations).

### Pattern 4: `nest_asyncio` for Jupyter

```python
import nest_asyncio
nest_asyncio.apply()
```

Jupyter notebooks already run an event loop. `nest_asyncio` allows nested event loops so you can use `asyncio.run()` inside notebooks.

---

## Common Pitfalls

### 1. Forgetting `await`

```python
# WRONG: Returns a coroutine object, not the result
result = session.call_tool("search", {"topic": "AI"})

# CORRECT: Actually executes and returns the result
result = await session.call_tool("search", {"topic": "AI"})
```

### 2. Using `await` Outside `async def`

```python
# WRONG: SyntaxError
def main():
    result = await some_coroutine()

# CORRECT: Must be in async function
async def main():
    result = await some_coroutine()
```

### 3. Blocking Calls in Async Code

```python
# BAD: time.sleep() blocks the entire event loop
async def bad_example():
    time.sleep(5)  # Blocks everything!

# GOOD: asyncio.sleep() yields control
async def good_example():
    await asyncio.sleep(5)  # Other tasks can run
```

### 4. Not Running the Event Loop

```python
# WRONG: Coroutine never executes
async def main():
    print("Hello")

main()  # Just creates a coroutine object

# CORRECT: Actually runs the coroutine
asyncio.run(main())
```

---

## Quick Reference

| Concept | Syntax | Purpose |
|---------|--------|---------|
| Define coroutine | `async def func():` | Create an async function |
| Run coroutine | `await func()` | Execute and wait for result |
| Start event loop | `asyncio.run(main())` | Entry point from sync code |
| Async context | `async with resource:` | Async setup/teardown |
| Concurrent tasks | `await asyncio.gather(a(), b())` | Run multiple coroutines |
| Sleep (non-blocking) | `await asyncio.sleep(n)` | Pause without blocking |

---

## Further Reading

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
