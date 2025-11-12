# 🎓 Comprehensive Learning Guide: Agentic AI Research System

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Component 1: FastAPI Web Framework](#component-1-fastapi-web-framework)
3. [Component 2: PostgreSQL Database](#component-2-postgresql-database)
4. [Component 3: Docker Containerization](#component-3-docker-containerization)
5. [Component 4: Multi-Agent Architecture](#component-4-multi-agent-architecture)
6. [Component 5: Research Tools](#component-5-research-tools)
7. [Hands-On Experiments](#hands-on-experiments)
8. [Learning Path](#learning-path)

---

## System Overview

This is a **Reflective Research Agent** system that orchestrates multiple AI agents to conduct comprehensive research on any topic. Here's the high-level workflow:

```
User Query → Planner Agent → [Research → Write → Edit] → Final Report
                ↓
            Postgres DB (stores task state)
                ↓
            FastAPI (serves progress updates)
                ↓
            Web UI (displays real-time progress)
```

**Key Technologies:**
- **FastAPI**: Modern Python web framework (async, fast, with automatic API docs)
- **PostgreSQL**: Relational database for persistent storage
- **Docker**: Containerization for easy deployment
- **AI Agents**: Specialized agents using OpenAI's API
- **Research Tools**: Tavily (web search), arXiv (papers), Wikipedia

---

## Component 1: FastAPI Web Framework

### What is FastAPI?

FastAPI is a modern, high-performance web framework for building APIs with Python. It's built on:
- **Starlette** (for web routing)
- **Pydantic** (for data validation)
- **ASGI** (Asynchronous Server Gateway Interface)

### How It's Used in This Project

**File: `main.py` (lines 1-228)**

#### 1. Application Setup
```python
# Lines 60-66
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
```

**What this does:**
- Creates a FastAPI application instance
- Adds CORS middleware (allows requests from any origin)
- Mounts static files (CSS, JS, images)
- Sets up Jinja2 templates for HTML rendering

#### 2. API Endpoints

**a) Homepage Endpoint**
```python
# Lines 74-76
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```
- Serves the main UI page
- Uses Jinja2 templating to render HTML

**b) Generate Report Endpoint**
```python
# Lines 84-108
@app.post("/generate_report")
def generate_report(req: PromptRequest):
    task_id = str(uuid.uuid4())
    db = SessionLocal()
    db.add(Task(id=task_id, prompt=req.prompt, status="running"))
    db.commit()
    db.close()
    
    # Create initial plan
    initial_plan_steps = planner_agent(req.prompt)
    
    # Start background thread for actual work
    thread = threading.Thread(
        target=run_agent_workflow, args=(task_id, req.prompt, initial_plan_steps)
    )
    thread.start()
    return {"task_id": task_id}
```

**What this does:**
1. Generates a unique task ID (UUID)
2. Saves task to database with "running" status
3. Calls planner agent to create step-by-step plan
4. Starts background thread to execute the plan
5. Returns task_id immediately (non-blocking)

**c) Progress Endpoint**
```python
# Lines 111-113
@app.get("/task_progress/{task_id}")
def get_task_progress(task_id: str):
    return task_progress.get(task_id, {"steps": []})
```
- Real-time progress updates
- UI polls this endpoint to show live status

**d) Final Status Endpoint**
```python
# Lines 116-126
@app.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": task.status,
        "result": json.loads(task.result) if task.result else None,
    }
```
- Returns final report and history
- Used when workflow is complete

#### 3. Request/Response Models (Pydantic)

```python
# Lines 70-71
class PromptRequest(BaseModel):
    prompt: str
```

**Why Pydantic?**
- Automatic validation (ensures `prompt` is a string)
- Automatic API documentation
- Type safety

### Key FastAPI Concepts to Learn

1. **Path Operations**: `@app.get()`, `@app.post()`, etc.
2. **Dependency Injection**: Not heavily used here, but powerful
3. **Background Tasks**: Threading used here; FastAPI has built-in support
4. **Async/Await**: Not used here; could improve performance
5. **Automatic Docs**: Visit `/docs` for interactive API documentation

---

## Component 2: PostgreSQL Database

### What is PostgreSQL?

PostgreSQL is a powerful, open-source relational database. It's:
- **ACID compliant** (Atomicity, Consistency, Isolation, Durability)
- **Feature-rich** (supports JSON, full-text search, etc.)
- **Reliable** (used by major companies)

### How It's Used in This Project

**File: `main.py` (lines 22-57)**

#### 1. Database Connection Setup

```python
# Lines 22-27
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for Heroku's postgres:// URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

**Connection String Format:**
```
postgresql://username:password@host:port/database
```

Example:
```
postgresql://app:local@127.0.0.1:5432/appdb
```

#### 2. SQLAlchemy ORM Setup

```python
# Lines 33-36
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
```

**What this does:**
- `Base`: Base class for all models
- `engine`: Connection to database
- `SessionLocal`: Factory for creating database sessions

#### 3. Database Model (Table Definition)

```python
# Lines 39-46
class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    prompt = Column(Text)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    result = Column(Text)
```

**This creates a table:**
```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    prompt TEXT,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    result TEXT
);
```

#### 4. Database Operations

**Create table:**
```python
# Lines 54-57
Base.metadata.create_all(bind=engine)
```

**Insert record:**
```python
# Lines 87-90
db = SessionLocal()
db.add(Task(id=task_id, prompt=req.prompt, status="running"))
db.commit()
db.close()
```

**Query record:**
```python
# Lines 118-120
db = SessionLocal()
task = db.query(Task).filter(Task.id == task_id).first()
db.close()
```

**Update record:**
```python
# Lines 200-206
db = SessionLocal()
task = db.query(Task).filter(Task.id == task_id).first()
task.status = "done"
task.result = json.dumps(result)
task.updated_at = datetime.utcnow()
db.commit()
db.close()
```

### Key PostgreSQL Concepts to Learn

1. **Tables**: Structured data storage
2. **Primary Keys**: Unique identifiers
3. **Indexes**: Speed up queries
4. **CRUD Operations**: Create, Read, Update, Delete
5. **Transactions**: `commit()` and `rollback()`
6. **SQLAlchemy ORM**: Python objects ↔ database rows

---

## Component 3: Docker Containerization

### What is Docker?

Docker packages applications with all their dependencies into **containers** - lightweight, portable units that run consistently anywhere.

**Key Concepts:**
- **Image**: Blueprint for container (like a class)
- **Container**: Running instance (like an object)
- **Dockerfile**: Instructions to build image
- **Layers**: Each instruction creates a cached layer

### How It's Used in This Project

**File: `Dockerfile` (25 lines)**

```dockerfile
FROM python:3.11-slim
```
**Base image**: Start with Python 3.11 on lightweight Debian

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
```
**Environment variables:**
- Don't write `.pyc` files (bytecode)
- Show Python output immediately (no buffering)
- Don't cache pip downloads

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    postgresql postgresql-client postgresql-contrib \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
```
**Install system dependencies:**
- `gcc` and `libpq-dev`: Compile Python packages
- `postgresql`: Full Postgres server
- `postgresql-client`: CLI tools (`psql`)
- Clean up to reduce image size

```dockerfile
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
```
**Application setup:**
1. Set working directory to `/app`
2. Copy requirements first (cache optimization)
3. Install Python packages
4. Copy entire application

```dockerfile
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000 5432
CMD ["/entrypoint.sh"]
```
**Startup configuration:**
- Copy entrypoint script
- Make it executable
- Expose ports (8000=FastAPI, 5432=Postgres)
- Run entrypoint on container start

### Entrypoint Script

**File: `docker/entrypoint.sh` (40 lines)**

This script runs when the container starts:

```bash
#!/usr/bin/env bash
set -euo pipefail
```
**Strict mode:**
- `e`: Exit on error
- `u`: Error on undefined variable
- `o pipefail`: Catch errors in pipes

```bash
# Start Postgres
PG_MAJOR="$(psql -V | awk '{print $3}' | cut -d. -f1)"
echo "🚀 Starting Postgres cluster ${PG_MAJOR}/main..."
pg_ctlcluster "${PG_MAJOR}" main start
```
**Start Postgres server:**
- Detect Postgres version
- Start the cluster

```bash
# Wait for Postgres to be ready
for i in $(seq 1 60); do
  if pg_isready -h 127.0.0.1 -p 5432 -U postgres >/dev/null 2>&1; then
    echo "✅ Postgres is ready"
    break
  fi
  sleep 1
done
```
**Health check loop:**
- Try up to 60 times (60 seconds)
- Check if Postgres accepts connections
- Sleep 1 second between attempts

```bash
# Create database user and database
: "${POSTGRES_USER:=app}"
: "${POSTGRES_PASSWORD:=local}"
: "${POSTGRES_DB:=appdb}"

# Create user if doesn't exist
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\""
fi

# Create database if doesn't exist
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};\""
fi
```
**Database initialization:**
- Set default values for user/password/database
- Check if user exists; create if not
- Check if database exists; create if not

```bash
# Set DATABASE_URL for FastAPI
export DATABASE_URL="${DATABASE_URL:-postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/${POSTGRES_DB}}"
echo "🔗 DATABASE_URL=${DATABASE_URL}"

# Start FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
```
**Start application:**
- Export connection string
- Launch FastAPI with uvicorn

### Key Docker Concepts to Learn

1. **Images vs Containers**: Blueprint vs running instance
2. **Layers and Caching**: Speed up builds
3. **Multi-stage builds**: Not used here, but important
4. **Volumes**: Persistent storage (not used here)
5. **Networks**: Container communication
6. **Docker Compose**: Orchestrate multiple containers

---

## Component 4: Multi-Agent Architecture

### What are AI Agents?

An **AI agent** is an AI system that:
- Receives a goal or task
- Can use tools (search, calculation, etc.)
- Makes decisions autonomously
- Produces output

This project uses **specialized agents**:
1. **Planner Agent**: Creates research plan
2. **Research Agent**: Gathers information using tools
3. **Writer Agent**: Drafts reports
4. **Editor Agent**: Refines and improves drafts

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER PROMPT                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              PLANNER AGENT (o4-mini)                     │
│  Creates step-by-step plan (max 7 steps)                │
│  Enforces workflow: Tavily → arXiv → Synthesis → Draft  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │   EXECUTOR AGENT     │
           │  (loops through plan)│
           └──────────┬───────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼              ▼
  ┌─────────┐  ┌──────────┐  ┌──────────┐
  │RESEARCH │  │ WRITER   │  │ EDITOR   │
  │ AGENT   │  │ AGENT    │  │ AGENT    │
  └────┬────┘  └────┬─────┘  └────┬─────┘
       │            │              │
   [Tools]      [Drafting]    [Refining]
       │            │              │
       └────────────┴──────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ FINAL REPORT  │
            │ (Markdown)    │
            └───────────────┘
```

### 1. Planner Agent

**File: `src/planning_agent.py` (lines 27-133)**

```python
def planner_agent(topic: str, model: str = "openai:o4-mini") -> List[str]:
    prompt = f"""
You are a planning agent responsible for organizing a research workflow...

🧠 Available agents:
- Research agent: Web search, arXiv, Wikipedia
- Writer agent: drafts based on research findings
- Editor agent: reviews and improves drafts

🎯 Produce a clear step-by-step research plan as a valid Python list of strings.
Maximum of 7 steps.

Topic: "{topic}"
"""
```

**What it does:**
1. Takes research topic as input
2. Sends prompt to OpenAI's o4-mini model
3. Gets back a list of steps like:
   ```python
   [
       "Research agent: Use Tavily to search for recent papers...",
       "Research agent: Search arXiv for academic papers...",
       "Research agent: Synthesize and rank findings...",
       "Writer agent: Draft structured outline...",
       "Editor agent: Review for coherence...",
       "Writer agent: Generate final Markdown report..."
   ]
   ```
4. Enforces specific steps (Tavily first, arXiv second)

**Key Feature: Robust Parsing**
```python
# Lines 67-91
def _coerce_to_list(s: str) -> List[str]:
    # try strict JSON
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return obj[:7]
    except json.JSONDecodeError:
        pass
    # try Python literal list
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, list):
            return obj[:7]
    except Exception:
        pass
    return []
```
**Why?** LLMs sometimes return invalid JSON or add markdown formatting

### 2. Executor Agent

**File: `src/planning_agent.py` (lines 136-176)**

```python
def executor_agent_step(step_title: str, history: list, prompt: str):
    # Build context from previous steps
    context = f"📘 User Prompt:\n{prompt}\n\n📜 History so far:\n"
    for i, (desc, agent, output) in enumerate(history):
        if "draft" in desc.lower():
            context += f"\n✍️ Draft (Step {i + 1}):\n{output}\n"
        elif "research" in desc.lower():
            context += f"\n🔍 Research (Step {i + 1}):\n{output}\n"
    
    # Select appropriate agent based on step title
    step_lower = step_title.lower()
    if "research" in step_lower:
        content, _ = research_agent(prompt=context + step_title)
        return step_title, "research_agent", content
    elif "write" in step_lower:
        content, _ = writer_agent(prompt=context + step_title)
        return step_title, "writer_agent", content
    elif "edit" in step_lower:
        content, _ = editor_agent(prompt=context + step_title)
        return step_title, "editor_agent", content
```

**What it does:**
1. Takes a single step from the plan
2. Builds **enriched context** with all previous outputs
3. Routes to the appropriate specialized agent
4. Returns the agent's output

**Why context matters:**
- Writer needs research findings
- Editor needs the draft to review
- Each agent builds on previous work

### 3. Research Agent

**File: `src/agents.py` (lines 14-152)**

```python
def research_agent(prompt: str, model: str = "openai:gpt-4.1-mini"):
    full_prompt = f"""
You are an advanced research assistant...

## AVAILABLE RESEARCH TOOLS:
1. tavily_search_tool: General web search
2. arxiv_search_tool: Academic papers
3. wikipedia_search_tool: Encyclopedia

## OUTPUT FORMAT:
1. Summary of Research Approach
2. Key Findings
3. Source Details (URLs, titles, authors)
4. Limitations

USER RESEARCH REQUEST:
{prompt}
"""
    
    tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool]
    
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        tools=tools,
        tool_choice="auto",
        max_turns=5,
        temperature=0.0
    )
```

**Key Features:**
- **Tool calling**: Model decides which tools to use
- **Multi-turn**: Can use multiple tools in sequence
- **Temperature=0**: Deterministic output
- **Tracks tool usage**: Shows which tools were called

**Example output:**
```
🔍 Research Agent Output:

Summary of Research Approach:
Used Tavily to search for recent developments in large language models,
then searched arXiv for academic papers on the topic.

Key Findings:
1. GPT-4 released in March 2023 (Source: OpenAI blog)
2. Recent paper on "Chain of Thought Prompting" shows...

Tools used:
- tavily_search_tool(query="large language models 2024")
- arxiv_search_tool(query="transformer architecture", max_results=5)
```

### 4. Writer Agent

**File: `src/agents.py` (lines 155-246)**

```python
def writer_agent(prompt: str, model: str = "openai:gpt-4.1-mini"):
    system_message = """
You are an expert academic writer...

## REPORT REQUIREMENTS:
- COMPLETE, POLISHED, PUBLICATION-READY report
- Original content with critical analysis
- Length: 1500-3000 words

## MANDATORY STRUCTURE:
1. Title
2. Abstract (100-150 words)
3. Introduction
4. Background/Literature Review
5. Methodology
6. Key Findings/Results
7. Discussion
8. Conclusion
9. References

## CITATION RULES:
- Use numeric inline citations [1], [2]
- Every claim needs a citation
- Complete References section
"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=15000
    )
```

**Why separate Writer Agent?**
- Specialized prompt for academic writing
- Enforces structure and citation standards
- Long output (up to 15,000 tokens)

### 5. Editor Agent

**File: `src/agents.py` (lines 249-296)**

```python
def editor_agent(prompt: str, model: str = "openai:gpt-4.1-mini"):
    system_message = """
You are a professional academic editor...

## Your Editing Process:
1. Analyze overall structure and argument flow
2. Ensure logical progression of ideas
3. Improve clarity and conciseness
4. Verify technical accuracy
5. Enhance readability

## Specific Elements to Address:
- Strengthen thesis statements
- Clarify complex concepts
- Add equations/diagrams where helpful
- Standardize terminology
- Preserve all citations [1], [2]
"""
```

**Why separate Editor Agent?**
- Different mindset: critical review vs. creation
- Focuses on refinement, not generation
- Preserves existing work while improving

### Key Agent Concepts to Learn

1. **Tool Calling**: LLMs can call external functions
2. **Context Management**: Passing history between agents
3. **Prompt Engineering**: Different prompts for different tasks
4. **Temperature**: 0 for deterministic, higher for creative
5. **Max Tokens**: Output length limits
6. **System Messages**: Define agent personality/role

---

## Component 5: Research Tools

### Tool Architecture

Each tool has:
1. **Python function**: Actual implementation
2. **Tool definition**: JSON schema for LLM

**File: `src/research_tools.py` (408 lines)**

### 1. Tavily Search Tool (Web Search)

```python
def tavily_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Perform a search using the Tavily API.
    
    Returns:
        List[dict]: [{'title': ..., 'content': ..., 'url': ...}]
    """
    api_key = os.getenv("TAVILY_API_KEY")
    client = TavilyClient(api_key)
    
    response = client.search(
        query=query, 
        max_results=max_results
    )
    
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "content": r.get("content", ""),
            "url": r.get("url", "")
        })
    return results
```

**Tool Definition:**
```python
tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Performs web search using Tavily API.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}
```

**Why Tavily?**
- Optimized for LLM applications
- Returns clean, relevant content
- Better than scraping Google

### 2. arXiv Search Tool (Academic Papers)

```python
def arxiv_search_tool(query: str, max_results: int = 3) -> List[Dict]:
    """
    Searches arXiv and extracts PDF text.
    
    Returns:
        List[Dict]: [{
            'title': ...,
            'authors': [...],
            'published': '2024-01-15',
            'url': ...,
            'summary': ...,  # First 5000 chars of PDF text
            'link_pdf': ...
        }]
    """
    api_url = f"https://export.arxiv.org/api/query?search_query=all:{query}"
    
    resp = session.get(api_url, timeout=60)
    root = ET.fromstring(resp.content)
    
    out = []
    for entry in root.findall("atom:entry", ns):
        # Extract metadata
        title = entry.findtext("atom:title")
        authors = [a.findtext("atom:name") for a in entry.findall("atom:author")]
        link_pdf = entry.findtext("atom:link[@title='pdf']")
        
        # Download and extract PDF text
        pdf_bytes = fetch_pdf_bytes(link_pdf)
        text = pdf_bytes_to_text(pdf_bytes, max_pages=6)
        
        out.append({
            "title": title,
            "authors": authors,
            "summary": text[:5000],  # First 5000 characters
            "link_pdf": link_pdf
        })
    return out
```

**Advanced Features:**
- **PDF extraction**: Downloads and extracts text from PDFs
- **Two libraries**: PyMuPDF (fast) or pdfminer.six (fallback)
- **Rate limiting**: Sleep 1 second between downloads
- **Error handling**: Graceful degradation

**PDF Text Extraction:**
```python
def pdf_bytes_to_text(pdf_bytes: bytes, max_pages: Optional[int] = None) -> str:
    # Try PyMuPDF first (faster)
    try:
        import fitz  # PyMuPDF
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            out = []
            limit = len(doc) if max_pages is None else min(max_pages, len(doc))
            for i in range(limit):
                out.append(doc.load_page(i).get_text("text"))
            return "\n".join(out)
    except Exception:
        pass
    
    # Fallback to pdfminer.six
    from pdfminer.high_level import extract_text_to_fp
    buf_in = BytesIO(pdf_bytes)
    buf_out = BytesIO()
    extract_text_to_fp(buf_in, buf_out)
    return buf_out.getvalue().decode("utf-8", errors="ignore")
```

### 3. Wikipedia Search Tool

```python
def wikipedia_search_tool(query: str, sentences: int = 5) -> List[Dict]:
    """
    Searches Wikipedia for a summary.
    
    Returns:
        List[Dict]: [{'title': ..., 'summary': ..., 'url': ...}]
    """
    try:
        page_title = wikipedia.search(query)[0]
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=sentences)
        
        return [{
            "title": page.title,
            "summary": summary,
            "url": page.url
        }]
    except Exception as e:
        return [{"error": str(e)}]
```

**Why Wikipedia?**
- Great for background/context
- Reliable for definitions
- Good starting point for research

### How Tools Work with LLMs

**Flow:**
1. Agent sends request to OpenAI with tool definitions
2. OpenAI decides which tools to call (if any)
3. OpenAI returns tool calls like:
   ```json
   {
     "tool_calls": [{
       "function": {
         "name": "tavily_search_tool",
         "arguments": "{\"query\": \"quantum computing\", \"max_results\": 5}"
       }
     }]
   }
   ```
4. Application executes the function
5. Results sent back to OpenAI
6. OpenAI synthesizes final response

**Key advantage**: LLM decides *when* and *which* tools to use

---

## Hands-On Experiments

### Experiment 1: Explore the Database

**Access the running container:**
```bash
docker exec -it fpsvc bash
```

**Connect to Postgres:**
```bash
psql "postgresql://app:local@127.0.0.1:5432/appdb"
```

**SQL queries to try:**
```sql
-- List all tables
\dt

-- See table structure
\d tasks

-- View all tasks
SELECT id, prompt, status, created_at FROM tasks;

-- View a specific task result
SELECT result FROM tasks WHERE id = 'YOUR_TASK_ID';

-- Count tasks by status
SELECT status, COUNT(*) FROM tasks GROUP BY status;
```

### Experiment 2: Test Individual Agents

**Create a test script: `test_agents.py`**
```python
from src.agents import research_agent, writer_agent, editor_agent

# Test research agent
print("=== RESEARCH AGENT ===")
research_output, _ = research_agent(
    "What are the latest developments in quantum computing?"
)
print(research_output)

# Test writer agent
print("\n=== WRITER AGENT ===")
writer_output, _ = writer_agent(
    f"Write a brief report based on: {research_output}"
)
print(writer_output)

# Test editor agent
print("\n=== EDITOR AGENT ===")
editor_output, _ = editor_agent(
    f"Improve this draft: {writer_output}"
)
print(editor_output)
```

**Run it:**
```bash
python test_agents.py
```

### Experiment 3: Monitor Real-Time Progress

**Terminal 1 - Start the app:**
```bash
docker run --rm -it -p 8000:8000 -p 5432:5432 \
  --name fpsvc --env-file .env fastapi-postgres-service
```

**Terminal 2 - Submit a task:**
```bash
# Submit task
TASK_ID=$(curl -X POST http://localhost:8000/generate_report \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Large Language Models"}' | jq -r '.task_id')

echo "Task ID: $TASK_ID"

# Poll progress every 3 seconds
while true; do
  clear
  curl -s "http://localhost:8000/task_progress/$TASK_ID" | jq '.'
  sleep 3
done
```

### Experiment 4: Modify Agent Behavior

**Edit the research agent to be more verbose:**

In `src/agents.py`, modify the system message:
```python
full_prompt = f"""
You are an advanced research assistant...

## OUTPUT FORMAT:
1. **Detailed Research Process**: Explain each step you took
2. **Key Findings**: Organized by subtopic
3. **Source Analysis**: Evaluate credibility of each source
4. **Synthesis**: Connect findings across sources
5. **Gaps**: What information is still missing?

...
"""
```

**Rebuild and test:**
```bash
docker build -t fastapi-postgres-service .
docker run --rm -it -p 8000:8000 -p 5432:5432 \
  --name fpsvc --env-file .env fastapi-postgres-service
```

### Experiment 5: Add Custom Tool

**Create a new tool in `src/research_tools.py`:**
```python
def github_search_tool(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search GitHub repositories.
    """
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
    response = requests.get(url, headers={"Accept": "application/vnd.github+json"})
    data = response.json()
    
    results = []
    for repo in data.get("items", [])[:max_results]:
        results.append({
            "name": repo["full_name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"]
        })
    return results

github_tool_def = {
    "type": "function",
    "function": {
        "name": "github_search_tool",
        "description": "Search GitHub repositories by keywords.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
}
```

**Register it in the research agent (`src/agents.py`):**
```python
from src.research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool,
    github_search_tool  # Add this
)

# In research_agent function:
tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool, github_search_tool]
```

---

## Learning Path

### Week 1: FastAPI Fundamentals
**Goals:**
- Understand HTTP methods (GET, POST)
- Learn path operations and routing
- Understand request/response models

**Resources:**
- FastAPI official tutorial: https://fastapi.tiangolo.com/tutorial/
- Build a simple TODO API

**Practice:**
- Add a new endpoint: `GET /tasks` to list all tasks
- Add endpoint: `DELETE /task/{task_id}` to delete a task

### Week 2: PostgreSQL & SQLAlchemy
**Goals:**
- Understand relational databases
- Learn SQL basics (SELECT, INSERT, UPDATE, DELETE)
- Understand ORMs

**Resources:**
- PostgreSQL tutorial: https://www.postgresql.org/docs/current/tutorial.html
- SQLAlchemy docs: https://docs.sqlalchemy.org/

**Practice:**
- Add a new table for "Users"
- Create one-to-many relationship (User has many Tasks)
- Add filtering: `GET /tasks?status=done`

### Week 3: Docker Fundamentals
**Goals:**
- Understand containers vs VMs
- Learn Dockerfile syntax
- Understand Docker networking

**Resources:**
- Docker Getting Started: https://docs.docker.com/get-started/
- Docker Compose tutorial

**Practice:**
- Modify Dockerfile to use PostgreSQL in separate container
- Create docker-compose.yml with two services
- Add volume for persistent data

### Week 4: AI Agents & Tool Calling
**Goals:**
- Understand LLM function calling
- Learn prompt engineering
- Understand agent workflows

**Resources:**
- OpenAI function calling docs
- LangChain documentation
- Anthropic prompt engineering guide

**Practice:**
- Create a new specialized agent (e.g., "Data Analyst Agent")
- Add a new research tool (e.g., Google Scholar)
- Experiment with different temperature values

### Advanced Topics
- **Async FastAPI**: Convert to async/await for better performance
- **Celery**: Replace threading with proper task queue
- **Redis**: Add caching layer
- **Authentication**: Add JWT-based auth
- **Testing**: Write pytest tests
- **Monitoring**: Add logging and metrics

---

## Additional Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/
- **OpenAI API**: https://platform.openai.com/docs/

### Books
- "FastAPI Beyond CRUD" by Abdulazeez Abdulazeez
- "SQL Antipatterns" by Bill Karwin
- "Docker Deep Dive" by Nigel Poulton
- "Building LLM Apps" by Valentina Alto

### Video Courses
- FastAPI - Full Course (freeCodeCamp on YouTube)
- PostgreSQL Tutorial for Beginners (Programming with Mosh)
- Docker Tutorial for Beginners (TechWorld with Nana)

### Practice Projects
1. **Blog API**: Users, posts, comments (FastAPI + Postgres)
2. **Task Queue System**: Background jobs with Celery
3. **AI Chatbot**: Multi-turn conversation with context
4. **Research Assistant**: Similar to this project but specialized domain

---

## Next Steps

### Option A: Deep Dive with Me (Claude)
I can help you:
- Run the application and explore each component
- Modify code and see results in real-time
- Debug issues as they arise
- Build new features hands-on

### Option B: Conceptual Learning with ChatGPT
Upload the codebase to discuss:
- Architecture patterns and alternatives
- Best practices for each technology
- Design decisions and trade-offs
- Scaling considerations

### Option C: Hybrid Approach (Recommended)
1. Use me for hands-on experimentation
2. Use ChatGPT for deep conceptual questions
3. Use documentation for reference
4. Build your own project to solidify learning

---

## Questions to Explore Further

### FastAPI
- How would you add authentication to this API?
- How could you make this API async for better performance?
- What's the difference between path parameters and query parameters?

### PostgreSQL
- When should you use an index?
- What's the difference between INNER JOIN and LEFT JOIN?
- How do transactions work?

### Docker
- What's the difference between CMD and ENTRYPOINT?
- How do Docker layers work?
- When should you use Docker Compose vs Kubernetes?

### AI Agents
- How do you prevent infinite loops in agent workflows?
- What's the trade-off between temperature and consistency?
- How do you handle tool calling errors?

---

**Happy Learning! 🚀**

Remember: The best way to learn is by doing. Start with simple experiments,
break things, fix them, and gradually build up your understanding.

Feel free to ask me specific questions as you work through each component!
