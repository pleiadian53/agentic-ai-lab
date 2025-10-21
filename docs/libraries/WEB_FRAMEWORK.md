# Web Framework & API Libraries

Documentation for web framework and API-related libraries.

## Overview

These libraries power the FastAPI web application, handle HTTP requests, validate data, and manage database connections.

---

## Core Web Framework

### FastAPI

**Modern Python Web Framework**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Agentic AI API")

class ResearchRequest(BaseModel):
    prompt: str
    model: str = "openai:gpt-4"

@app.post("/generate_report")
async def generate_report(request: ResearchRequest):
    """Generate a research report"""
    # Agent logic here
    return {"task_id": "uuid-123", "status": "started"}

@app.get("/task_status/{task_id}")
async def get_status(task_id: str):
    """Get task status"""
    return {"task_id": task_id, "status": "completed"}
```

**Key Features:**
- Automatic API documentation (Swagger/OpenAPI)
- Type validation with Pydantic
- Async/await support
- Dependency injection
- WebSocket support

**Use Cases:**
- REST API endpoints
- Real-time updates via WebSockets
- Background task management
- Request/response validation

**Auto-Generated Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

### uvicorn

**ASGI Server**

```bash
# Development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

```python
# Programmatic usage
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development only
        log_level="info"
    )
```

**Key Features:**
- ASGI server implementation
- Hot reload for development
- Multiple workers for production
- WebSocket support
- HTTP/2 support

**Configuration:**
- `--reload`: Auto-reload on code changes
- `--workers N`: Number of worker processes
- `--log-level`: debug, info, warning, error
- `--ssl-keyfile/--ssl-certfile`: HTTPS support

---

## Data Validation

### Pydantic

**Data Validation with Type Hints**

```python
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

class TaskRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=5000)
    model: str = Field(default="openai:gpt-4")
    max_steps: int = Field(default=10, ge=1, le=50)
    email: Optional[EmailStr] = None
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if 'forbidden' in v.lower():
            raise ValueError('Prompt contains forbidden content')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Research quantum computing",
                "model": "openai:gpt-4",
                "max_steps": 10
            }
        }

class TaskResponse(BaseModel):
    task_id: str
    status: str
    created_at: datetime
    result: Optional[str] = None
```

**Key Features:**
- Type validation
- Custom validators
- JSON schema generation
- Nested models
- Field constraints

**Use Cases:**
- API request/response models
- Configuration management
- Data serialization
- Type safety

---

### pydantic[email]

**Email Validation Extension**

```python
from pydantic import BaseModel, EmailStr

class UserNotification(BaseModel):
    email: EmailStr  # Validates email format
    subject: str
    message: str

# Valid
notification = UserNotification(
    email="user@example.com",
    subject="Task Complete",
    message="Your research is ready"
)

# Invalid - raises ValidationError
try:
    notification = UserNotification(
        email="not-an-email",
        subject="Test",
        message="Test"
    )
except ValidationError as e:
    print(e)
```

**Features:**
- RFC-compliant email validation
- DNS validation (optional)
- Internationalized emails

---

## HTTP & Networking

### requests

**HTTP Library**

```python
import requests

# GET request
response = requests.get(
    "https://api.example.com/data",
    params={"query": "AI"},
    headers={"Authorization": "Bearer token"}
)

# POST request
response = requests.post(
    "https://api.example.com/submit",
    json={"data": "value"},
    timeout=30
)

# Session for connection pooling
session = requests.Session()
session.headers.update({"User-Agent": "AgenticAI/1.0"})

response = session.get("https://arxiv.org/api/query")
```

**Key Features:**
- Simple API
- Session management
- Connection pooling
- Automatic retries (with adapters)
- File uploads/downloads

**Use Cases:**
- Call external APIs (arXiv, PubMed)
- Download research papers
- Web scraping
- API integration

**Best Practices:**
```python
# Use sessions for multiple requests
with requests.Session() as session:
    session.headers.update({"User-Agent": "..."})
    r1 = session.get(url1)
    r2 = session.get(url2)

# Set timeouts
response = requests.get(url, timeout=10)

# Handle errors
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise for 4xx/5xx
except requests.RequestException as e:
    print(f"Request failed: {e}")
```

---

## Configuration Management

### python-dotenv

**Environment Variable Management**

```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
DEBUG = os.getenv("DEBUG", "False") == "True"

# .env file format
"""
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
DATABASE_URL=postgresql://user:pass@localhost/db
DEBUG=True
"""
```

**Key Features:**
- Load .env files
- Override system environment
- Multiple .env files
- Variable expansion

**Best Practices:**
```python
# Use with Pydantic for type-safe config
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "sqlite:///./app.db"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## File Handling

### python-multipart

**Multipart Form Data Parser**

```python
from fastapi import FastAPI, File, UploadFile, Form

app = FastAPI()

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    """Upload a file with metadata"""
    contents = await file.read()
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "description": description
    }

@app.post("/upload_multiple")
async def upload_multiple(
    files: list[UploadFile] = File(...)
):
    """Upload multiple files"""
    return [
        {"filename": f.filename, "size": len(await f.read())}
        for f in files
    ]
```

**Key Features:**
- Stream large files
- Multiple file uploads
- Form data parsing
- Memory efficient

---

## Database

### SQLAlchemy

**SQL Toolkit and ORM**

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create engine
engine = create_engine("sqlite:///./app.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define models
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String, unique=True, index=True)
    prompt = Column(String)
    status = Column(String)
    result = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Use in FastAPI
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks")
def create_task(request: TaskRequest, db: Session = Depends(get_db)):
    task = Task(
        task_id=str(uuid.uuid4()),
        prompt=request.prompt,
        status="pending"
    )
    db.add(task)
    db.commit()
    return task
```

**Key Features:**
- ORM (Object-Relational Mapping)
- Multiple database support
- Migrations (with Alembic)
- Connection pooling
- Query builder

**Supported Databases:**
- SQLite (development)
- PostgreSQL (production)
- MySQL/MariaDB
- Oracle
- Microsoft SQL Server

---

## Text Processing

### markdown

**Markdown to HTML Conversion**

```python
import markdown

# Basic conversion
md_text = """
# Research Report

## Summary
This is a **bold** statement.

- Point 1
- Point 2

[Link](https://example.com)
"""

html = markdown.markdown(md_text)

# With extensions
html = markdown.markdown(
    md_text,
    extensions=[
        'extra',      # Tables, fenced code, etc.
        'codehilite', # Syntax highlighting
        'toc',        # Table of contents
        'nl2br'       # Newline to <br>
    ]
)

# Custom configuration
md = markdown.Markdown(
    extensions=['extra', 'codehilite'],
    extension_configs={
        'codehilite': {
            'linenums': True,
            'guess_lang': False
        }
    }
)
html = md.convert(md_text)
```

**Key Features:**
- Standard markdown syntax
- Extensions (tables, code highlighting, etc.)
- Safe HTML output
- Custom renderers

**Use Cases:**
- Render agent-generated reports
- Convert markdown to HTML for display
- Email formatting
- Documentation generation

---

## Complete FastAPI Application Example

```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI(
    title="Agentic AI API",
    description="Research agent API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ResearchRequest(BaseModel):
    prompt: str
    model: str = "openai:gpt-4"

class TaskResponse(BaseModel):
    task_id: str
    status: str

# Endpoints
@app.post("/generate_report", response_model=TaskResponse)
async def generate_report(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a research task"""
    task = create_task(db, request)
    background_tasks.add_task(run_agent, task.task_id)
    return TaskResponse(task_id=task.task_id, status="started")

@app.get("/task_status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    """Get task status"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## See Also

- [Complete Dependencies](DEPENDENCIES.md)
- [Agent & LLM Tools](AGENT_LLM_TOOLS.md)
- [Environment Setup](../ENVIRONMENT_SETUP.md)
