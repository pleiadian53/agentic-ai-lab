# FastAPI Tool Use Service Tutorial

A comprehensive guide to building FastAPI services that enable LLM tool use for agentic workflows.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Common Patterns](#common-patterns)
4. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
5. [Real-World Examples](#real-world-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What is a Tool Use Service?

A **tool use service** is a FastAPI application that:
1. Exposes REST API endpoints for client requests
2. Integrates with an LLM (via AISuite or similar)
3. Provides "tools" (Python functions) that the LLM can invoke
4. Returns structured responses to the client

### Architecture

```
┌─────────────┐      HTTP Request       ┌──────────────────┐
│   Client    │ ───────────────────────> │  FastAPI Server  │
│ (Web/Notebook)│                        │  (llm_service)   │
└─────────────┘                          └────────┬─────────┘
                                                  │
                                                  │ LLM Call
                                                  ▼
                                         ┌──────────────────┐
                                         │   LLM Provider   │
                                         │ (OpenAI/Claude)  │
                                         └────────┬─────────┘
                                                  │
                                                  │ Tool Calls
                                                  ▼
                                         ┌──────────────────┐
                                         │   Tool Layer     │
                                         │ (email_tools.py) │
                                         └────────┬─────────┘
                                                  │
                                                  │ API Calls
                                                  ▼
                                         ┌──────────────────┐
                                         │  Backend Service │
                                         │ (email_service)  │
                                         └──────────────────┘
```

---

## Core Concepts

### 1. FastAPI Application

The central object that handles HTTP requests and responses.

```python
from fastapi import FastAPI

app = FastAPI(title="My Service")
```

**Key Points:**
- `FastAPI()` creates the application instance
- `title` appears in auto-generated API docs
- The `app` object is used to register routes and middleware

### 2. CORS Middleware

**CORS (Cross-Origin Resource Sharing)** controls which external domains can access your API.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allowed domains
    allow_credentials=True,                   # Allow cookies/auth
    allow_methods=["*"],                      # Allow all HTTP methods
    allow_headers=["*"],                      # Allow all headers
)
```

**Why It's Needed:**
- Browsers block cross-origin requests by default for security
- Your web UI (e.g., React app on port 3000) needs permission to call your API (e.g., port 8001)
- Without CORS, you'll get "blocked by CORS policy" errors

**Security Levels:**
- **Development:** `allow_origins=["*"]` (allow all domains)
- **Production:** `allow_origins=["https://myapp.com"]` (specific domains only)

### 3. Pydantic Models

**Pydantic** validates and structures incoming/outgoing data.

```python
from pydantic import BaseModel

class PromptInput(BaseModel):
    prompt: str
    max_tokens: int = 1000  # Optional with default
```

**Benefits:**
- Automatic validation (rejects invalid requests)
- Type checking and IDE autocomplete
- Auto-generated API documentation
- Clear data contracts

**Example:**
```python
# Valid request
{"prompt": "Check my emails"}  # ✅

# Invalid request
{"message": "Check my emails"}  # ❌ Missing 'prompt' field
{"prompt": 123}                 # ❌ Wrong type (not string)
```

### 4. Endpoint Registration

Endpoints are functions decorated with HTTP method decorators.

```python
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    return {"result": "success"}
```

**HTTP Methods:**
- `@app.get()` - Retrieve data (e.g., list emails)
- `@app.post()` - Create/submit data (e.g., send prompt)
- `@app.patch()` - Partial update (e.g., mark as read)
- `@app.delete()` - Delete data (e.g., delete email)

### 5. Tool Use Pattern

The LLM is given a list of Python functions it can call.

```python
response = client.chat.completions.create(
    model="openai:gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    tools=[
        email_tools.send_email,
        email_tools.list_emails,
        email_tools.delete_email
    ],
    max_turns=10
)
```

**How It Works:**
1. LLM reads the function signatures and docstrings
2. LLM decides which tools to call based on the prompt
3. AISuite executes the function calls
4. Results are passed back to the LLM
5. LLM generates a final response

---

## Common Patterns

### Pattern 1: Basic Service Structure

```python
# 1. Imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aisuite as ai

# 2. Initialize clients
client = ai.Client()

# 3. Create FastAPI app
app = FastAPI(title="My Service")

# 4. Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define schemas
class RequestModel(BaseModel):
    prompt: str

# 6. Define endpoints
@app.post("/endpoint")
async def handler(payload: RequestModel):
    return {"status": "ok"}
```

### Pattern 2: LLM Tool Use Endpoint

```python
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    # 1. Extract user input
    user_prompt = payload.prompt
    
    # 2. Build system prompt
    system_prompt = f"""
    You are an AI assistant that helps with [TASK].
    Available actions: [LIST ACTIONS]
    
    User request: {user_prompt}
    """
    
    # 3. Call LLM with tools
    response = client.chat.completions.create(
        model="openai:gpt-4o-mini",
        messages=[{"role": "user", "content": system_prompt}],
        tools=[tool1, tool2, tool3],
        max_turns=20
    )
    
    # 4. Extract and return result
    result = response.choices[0].message.content
    return {"response": result}
```

### Pattern 3: Database Dependency Injection

```python
from sqlalchemy.orm import Session

# Database session generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use in endpoint
@app.get("/items")
async def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items
```

### Pattern 4: Startup/Shutdown Events

```python
@app.on_event("startup")
async def startup_event():
    """Run when server starts"""
    print("🚀 Server starting...")
    # Initialize database, load models, etc.

@app.on_event("shutdown")
async def shutdown_event():
    """Run when server stops"""
    print("👋 Server shutting down...")
    # Close connections, save state, etc.
```

### Pattern 5: Error Handling

```python
from fastapi import HTTPException

@app.post("/process")
async def process_data(payload: DataInput):
    try:
        result = risky_operation(payload.data)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

---

## Step-by-Step Walkthrough

Let's build a complete tool use service from scratch.

### Step 1: Project Structure

```
my_agent/
├── __init__.py
├── config.py              # Configuration
├── my_tools.py            # Tool functions
└── server/
    ├── __init__.py
    └── llm_service.py     # FastAPI service
```

### Step 2: Define Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
DEFAULT_MODEL = "openai:gpt-4o-mini"

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Application Settings
USER_EMAIL = os.getenv("USER_EMAIL", "user@example.com")
```

### Step 3: Create Tool Functions

```python
# my_tools.py
import requests
import os

BASE_URL = os.getenv("MY_SERVICE_API_URL", "http://localhost:8000")

def get_items() -> list:
    """
    Fetch all items from the service.
    
    Returns:
        List[dict]: A list of items
    """
    response = requests.get(f"{BASE_URL}/items")
    return response.json()

def create_item(name: str, description: str) -> dict:
    """
    Create a new item.
    
    Args:
        name (str): The item name
        description (str): The item description
        
    Returns:
        dict: The created item
    """
    payload = {"name": name, "description": description}
    response = requests.post(f"{BASE_URL}/items", json=payload)
    return response.json()

def delete_item(item_id: int) -> dict:
    """
    Delete an item by ID.
    
    Args:
        item_id (int): The ID of the item to delete
        
    Returns:
        dict: Confirmation message
    """
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    return response.json()
```

**Key Points:**
- Clear, imperative docstrings
- Type hints for all parameters
- Consistent return types
- Each function does one thing

### Step 4: Build the FastAPI Service

```python
# server/llm_service.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aisuite as ai
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
from config import (
    DEFAULT_MODEL,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    USER_EMAIL,
)

# Import tools
from my_agent import my_tools

# Initialize AISuite client
client = ai.Client()

# Create FastAPI app
app = FastAPI(title="My Agent LLM Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request schema
class PromptInput(BaseModel):
    prompt: str

# Define endpoint
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    """
    Handle natural language prompts and execute operations via LLM.
    
    Args:
        payload: PromptInput containing the user's instruction
        
    Returns:
        dict: Contains the LLM's response
    """
    prompt = payload.prompt

    # Build system prompt
    system_prompt = f"""
    You are an AI assistant specialized in managing items.
    You can list, create, and delete items.
    Use the provided tools to interact with the system.
    Never ask the user for confirmation before performing an action.
    
    User request: {prompt}
    """

    # Call LLM with tools
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": system_prompt}],
        tools=[
            my_tools.get_items,
            my_tools.create_item,
            my_tools.delete_item,
        ],
        max_turns=10
    )

    # Extract result
    result = response.choices[0].message.content

    return {"response": result}
```

### Step 5: Run the Service

```bash
# Start the service
uvicorn llm_service:app --port 8001 --reload
```

### Step 6: Test the Service

```bash
# Using curl
curl -X POST http://localhost:8001/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all items"}'

# Using Python
import requests

response = requests.post(
    "http://localhost:8001/prompt",
    json={"prompt": "Create an item called 'Test' with description 'Testing'"}
)
print(response.json())
```

---

## Real-World Examples

### Example 1: Email Agent (Simple)

```python
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    prompt = payload.prompt
    
    system_prompt = f"""
    You are an email assistant.
    Help the user manage their emails.
    
    {prompt}
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": system_prompt}],
        tools=[
            email_tools.list_unread_emails,
            email_tools.send_email,
            email_tools.delete_email,
        ],
        max_turns=20
    )
    
    return {"response": response.choices[0].message.content}
```

### Example 2: Research Agent (Advanced)

```python
@app.post("/research")
async def handle_research(payload: ResearchInput):
    """Research agent with web search and document analysis."""
    
    # Build context-rich prompt
    system_prompt = f"""
    You are a research assistant.
    Research topic: {payload.topic}
    Depth level: {payload.depth}
    
    Steps:
    1. Search for relevant information
    2. Analyze and synthesize findings
    3. Generate a comprehensive report
    """
    
    # Call LLM with research tools
    response = client.chat.completions.create(
        model="openai:gpt-4o",  # More capable model
        messages=[{"role": "user", "content": system_prompt}],
        tools=[
            research_tools.web_search,
            research_tools.read_document,
            research_tools.summarize_text,
            research_tools.extract_citations,
        ],
        max_turns=50  # More turns for complex research
    )
    
    # Format response with citations
    result = format_research_report(response)
    
    return {
        "report": result.report,
        "citations": result.citations,
        "metadata": result.metadata
    }
```

### Example 3: Multi-Agent Orchestrator

```python
@app.post("/orchestrate")
async def orchestrate_agents(payload: TaskInput):
    """Orchestrate multiple specialized agents."""
    
    # Determine which agent to use
    agent_type = classify_task(payload.task)
    
    if agent_type == "email":
        tools = email_tools_list
        system_prompt = email_system_prompt
    elif agent_type == "research":
        tools = research_tools_list
        system_prompt = research_system_prompt
    elif agent_type == "data":
        tools = data_tools_list
        system_prompt = data_system_prompt
    else:
        raise HTTPException(400, "Unknown task type")
    
    # Execute with appropriate agent
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": system_prompt}],
        tools=tools,
        max_turns=30
    )
    
    return {
        "agent_used": agent_type,
        "response": response.choices[0].message.content
    }
```

---

## Best Practices

### 1. Configuration Management

✅ **Do:**
```python
# Use environment variables
DEFAULT_MODEL = os.getenv("LLM_MODEL", "openai:gpt-4o-mini")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
```

❌ **Don't:**
```python
# Hardcode sensitive values
DEFAULT_MODEL = "openai:gpt-4o-mini"
API_KEY = "sk-1234567890"  # Never hardcode API keys!
```

### 2. Tool Design

✅ **Do:**
```python
def send_email(recipient: str, subject: str, body: str) -> dict:
    """
    Send an email to a recipient.
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject line
        body (str): Email message body
        
    Returns:
        dict: Confirmation with email ID
    """
    # Implementation
```

❌ **Don't:**
```python
def send_email(data):  # No type hints
    # No docstring
    # Unclear what 'data' contains
    pass
```

### 3. Error Handling

✅ **Do:**
```python
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    try:
        response = client.chat.completions.create(...)
        return {"response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(500, "Failed to process request")
```

❌ **Don't:**
```python
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    response = client.chat.completions.create(...)  # No error handling
    return {"response": response.choices[0].message.content}
```

### 4. CORS Configuration

✅ **Do:**
```python
# Development
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]

# Production
CORS_ORIGINS = ["https://myapp.com", "https://www.myapp.com"]
```

❌ **Don't:**
```python
# Production with wildcard (security risk!)
CORS_ORIGINS = ["*"]
```

### 5. Tool Selection

✅ **Do:**
```python
# Only provide relevant tools
tools=[
    email_tools.list_unread_emails,  # User asked about unread
    email_tools.mark_as_read,        # Related action
]
```

❌ **Don't:**
```python
# Provide all tools regardless of task
tools=[
    email_tools.list_all_emails,
    email_tools.send_email,
    email_tools.delete_email,
    # ... 20 more tools
]  # LLM gets confused with too many options
```

### 6. Prompt Engineering

✅ **Do:**
```python
system_prompt = f"""
You are an email assistant.

Available actions:
- List unread emails
- Mark emails as read
- Send replies

Current context:
- User email: {USER_EMAIL}
- Timezone: {USER_TIMEZONE}

User request: {prompt}
"""
```

❌ **Don't:**
```python
system_prompt = prompt  # No context or instructions
```

---

## Troubleshooting

### Issue 1: CORS Errors

**Symptom:**
```
Access to fetch at 'http://localhost:8001/prompt' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solution:**
```python
# Add the frontend origin to CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'my_tools'
```

**Solution:**
```python
# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now imports work
from my_agent import my_tools
```

### Issue 3: Pydantic Validation Errors

**Symptom:**
```
422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution:**
```python
# Ensure request matches schema
class PromptInput(BaseModel):
    prompt: str  # Required field

# Client must send:
{"prompt": "your text here"}

# Not:
{"message": "your text here"}  # Wrong field name
```

### Issue 4: Tool Not Being Called

**Symptom:**
LLM responds with text but doesn't call the tool.

**Solution:**
1. Check tool docstring is clear:
```python
def send_email(recipient: str, subject: str, body: str) -> dict:
    """
    Send an email to a recipient.  # Clear, imperative description
    
    Args:
        recipient (str): Email address
        subject (str): Subject line
        body (str): Message content
    """
```

2. Ensure tool is registered:
```python
tools=[
    email_tools.send_email,  # Must be in the list!
]
```

3. Check prompt is clear:
```python
# Good: "Send an email to bob@example.com"
# Bad: "Maybe we should email Bob?"
```

### Issue 5: Server Won't Start

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :8001

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn llm_service:app --port 8002
```

---

## Summary

### Key Takeaways

1. **FastAPI Structure**
   - Initialize app with `FastAPI()`
   - Add CORS middleware for cross-origin access
   - Define Pydantic models for validation
   - Register endpoints with decorators

2. **Tool Use Pattern**
   - Tools are Python functions with clear docstrings
   - LLM decides which tools to call
   - AISuite handles execution and result passing
   - Return structured responses

3. **Best Practices**
   - Use environment variables for configuration
   - Provide clear tool docstrings and type hints
   - Handle errors gracefully
   - Limit CORS origins in production
   - Only provide relevant tools

4. **Common Patterns**
   - Basic service structure
   - LLM tool use endpoint
   - Database dependency injection
   - Startup/shutdown events
   - Error handling

### Next Steps

1. **Study the Examples**
   - Review `email_agent/server/llm_service.py`
   - Review `email_agent/server/email_service.py`
   - Compare patterns across different agents

2. **Build Your Own**
   - Start with the step-by-step walkthrough
   - Add your own tools
   - Test with different prompts
   - Iterate on tool design

3. **Advanced Topics**
   - Authentication and authorization
   - Rate limiting
   - Caching responses
   - Streaming responses
   - Multi-agent orchestration

---

## Additional Resources

### Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AISuite Documentation](https://github.com/andrewyng/aisuite)

### Related Files
- `tool_use/email_agent/server/llm_service.py` - LLM service example
- `tool_use/email_agent/server/email_service.py` - Backend service example
- `tool_use/email_agent/email_tools.py` - Tool functions example
- `tool_use/email_agent/config.py` - Configuration example

### Tools
- [FastAPI CLI](https://fastapi.tiangolo.com/reference/cli/) - Command-line interface
- [Uvicorn](https://www.uvicorn.org/) - ASGI server
- [HTTPie](https://httpie.io/) - API testing tool
- [Postman](https://www.postman.com/) - API development platform

---

**Happy Building! 🚀**
