# Agentic AI Workflows & Patterns

A comprehensive and **evolving collection** of **agentic AI workflows** demonstrating various design patterns including reflection, iterative refinement, tool-using agents, and multiagent systems. This repository includes multiple production-ready implementations for research, data visualization, SQL generation, and more.

> **Note**: This repository is actively expanding to cover additional agentic workflow patterns including multiagent collaboration, hierarchical agents, and advanced orchestration patterns.

## 🎯 What's Inside

This repository showcases **practical agentic AI patterns** with working implementations:

### **1. Chart Agent** 📊
Production-ready data visualization agent with FastAPI service, iterative refinement, and reflection.
- **Location**: `chart_agent/`
- **Features**:
  - **FastAPI REST API** with Swagger UI (`http://localhost:8003/docs`)
  - LLM-driven code-as-plan chart generation
  - Iterative refinement with convergence detection
  - DuckDB-based data access (TSV, CSV, Parquet)
  - Multiple model support (GPT-4, GPT-5, o1, etc.)
  - Reflection pattern for code improvement
  - Comprehensive documentation and examples
- **Server**: `chart_agent/server/chart_service.py`
- **Examples**: `chart_agent/examples/`
- **Docs**: `chart_agent/docs/`

### **2. Splice Agent** 🧬
Specialized genomics agent for splice site analysis using agentic workflows.
- **Location**: `splice_agent/`
- **Features**:
  - **Domain-specific analysis templates** for splice sites
  - Biological context and genomic feature analysis
  - FastAPI service with splice-specific endpoints (`http://localhost:8004/docs`)
  - Template-based and exploratory analysis modes
  - Built on chart_agent core engine
  - Genomic data visualization and insights
- **Server**: `splice_agent/server/splice_service.py`
- **Examples**: `splice_agent/examples/`
- **Docs**: `splice_agent/docs/`

### **3. SQL Agent Workflow** 🗄️
Natural language to SQL with adaptive iteration based on model strength.
- **Location**: `reflection/sql_agent/`
- **Features**:
  - Adaptive iteration (strong models: 1-2 iterations, weak models: 3-5)
  - Convergence detection and regression handling
  - Model-aware configuration (GPT-4 vs GPT-3.5 vs custom)
  - Event-sourced transaction database
- **Analysis**: `reflection/sql_agent/ADAPTIVE_ITERATION_ANALYSIS.md`
- **Notebook**: `reflection/sql_agent/sql.ipynb`

### **4. Research Agent** 🔬
Multi-step research workflow with planning, execution, and reflection.
- **Location**: `reflection/research_agent/`, `src/`
- **Features**:
  - FastAPI web app with Postgres backend
  - Tool-using agents (Tavily, arXiv, Wikipedia)
  - Planner → Research → Writer → Editor pipeline
  - Live task progress tracking
  - Docker deployment (single container)
- **Web UI**: [http://localhost:8000/](http://localhost:8000/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### **5. Visualization Agent** 📈
Advanced data visualization with multiple chart types and layouts.
- **Location**: `reflection/viz_agent/`
- **Features**: Multi-panel figures, exploratory analysis, custom styling

### **6. Legacy Workflows** 📚
Earlier implementations and learning materials (superseded by chart_agent/splice_agent):
- **Chart Workflow**: `reflection/chart_workflow/` - Original chart generation prototype
- **Note**: Use `chart_agent/` and `splice_agent/` for production work

## 🚀 Key Features Across All Workflows

* **Reflection Pattern**: Iterative refinement with LLM-based evaluation
* **Convergence Detection**: Smart stopping when output stabilizes
* **Cost Optimization**: Early stopping saves 25-50% on API calls
* **Model-Aware**: Adapts iteration count based on model capability
* **Code Persistence**: Saves generated code for reuse and debugging
* **Comprehensive Testing**: Full test suites for all major features
* **Production-Ready**: CLI tools, error handling, logging

---

## 🗺️ Roadmap: Planned Workflow Patterns

This repository is actively expanding to include additional agentic design patterns:

### **Coming Soon:**

**Multiagent Workflows** 🤝
- Agent collaboration and coordination patterns
- Hierarchical agent architectures (supervisor → workers)
- Parallel agent execution with result aggregation
- Agent communication protocols and message passing
- Consensus mechanisms and conflict resolution

**Advanced Orchestration** 🎭
- Dynamic workflow routing based on task complexity
- Conditional branching and decision trees
- State machines for complex multi-step processes
- Error recovery and fallback strategies
- Workflow versioning and A/B testing

**Specialized Agents** 🎯
- Code generation and debugging agents
- Data analysis and insight extraction agents
- Document processing and summarization agents
- API integration and tool-calling agents
- Domain-specific agents (legal, medical, financial)

**Performance & Optimization** ⚡
- Caching strategies for repeated queries
- Batch processing for high-throughput scenarios
- Cost tracking and budget management
- Latency optimization techniques
- Model selection and routing strategies

### **Contribution Ideas:**

Have a workflow pattern you'd like to see? Contributions are welcome! See the [Contributing](#-contributing) section for details.

---

## 📁 Project Structure

```
.
├─ chart_agent/                 # Production chart generation agent
│  ├─ server/                   # FastAPI service (port 8003)
│  │  ├─ chart_service.py       # Main API service
│  │  ├─ config.py              # Configuration
│  │  └─ schemas.py             # Pydantic models
│  ├─ examples/                 # Example scripts and notebooks
│  ├─ docs/                     # Comprehensive documentation
│  ├─ data_access.py            # DuckDB dataset loading
│  ├─ planning.py               # LLM-based code generation
│  ├─ llm_client.py             # OpenAI API client
│  └─ utils.py                  # Utility functions
│
├─ splice_agent/                # Genomics splice site analysis agent
│  ├─ server/                   # FastAPI service (port 8004)
│  │  ├─ splice_service.py      # Splice-specific API
│  │  ├─ config.py              # Configuration
│  │  └─ schemas.py             # Pydantic models
│  ├─ examples/                 # Splice analysis examples
│  ├─ docs/                     # Documentation
│  ├─ splice_analysis.py        # Domain-specific templates
│  ├─ data_access.py            # Dataset loading (from chart_agent)
│  ├─ planning.py               # Code generation (from chart_agent)
│  └─ llm_client.py             # LLM client (from chart_agent)
│
├─ reflection/                  # Reflection pattern implementations
│  ├─ chart_workflow/           # Original chart generation prototype
│  ├─ sql_agent/                # SQL generation with adaptive iteration
│  ├─ research_agent/           # Multi-step research workflow
│  └─ viz_agent/                # Advanced visualization agent
│
├─ multiagent/                  # Multiagent collaboration patterns
│  └─ customer_service/         # Customer service multiagent system
│
├─ tool_use/                    # Tool-using agent patterns
│
├─ docs/                        # Global documentation
│  ├─ architecture/             # System architecture
│  ├─ tutorials/                # Learning guides
│  ├─ installation/             # Setup guides
│  └─ libraries/                # Library documentation
│
├─ data/                        # Sample datasets
├─ tests/                       # Test suites
├─ scripts/                     # CLI tools and utilities
├─ environment.yml              # Mamba environment spec
├─ pyproject.toml               # Poetry project configuration
└─ README.md                    # This file
```

---

## Quick Start

### 🚀 Local Development Setup (Recommended)

For the best development experience, set up a local Python environment with mamba:

```bash
./scripts/install/setup.sh
mamba activate agentic-ai
```

**Prerequisites:** Miniforge (includes mamba)
- Install: `brew install --cask miniforge` or visit https://github.com/conda-forge/miniforge

**See**: 
* `SETUP_README.md` for detailed setup instructions
* `docs/libraries/` for complete library documentation

### 📊 Quick Start: Chart Agent

**Option 1: FastAPI Service (Recommended)**

```bash
# Activate environment
mamba activate agentic-ai

# Start the Chart Agent API server
cd chart_agent/server
python chart_service.py

# Visit Swagger UI at http://localhost:8003/docs
# Or use the API:
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/your_data.csv",
    "user_request": "Show top 10 categories by sales",
    "model": "gpt-4o-mini"
  }'
```

**Option 2: Python API**

```python
from chart_agent import create_dataset, generate_chart_code

# Load dataset
dataset = create_dataset("data/your_data.csv")

# Generate chart
result = generate_chart_code(
    dataset=dataset,
    user_request="Create a bar chart showing sales by category",
    model="gpt-4o-mini"
)

# Access generated code and chart
print(result["code"])
result["chart"].show()
```

**Option 3: CLI Examples**

```bash
# Run example scripts
python chart_agent/examples/quick_start.py
python chart_agent/examples/analyze_splice_sites.py
```

### 🧬 Quick Start: Splice Agent

Genomics-specific analysis with domain templates:

```bash
# Start the Splice Agent API server
cd splice_agent/server
python splice_service.py

# Visit Swagger UI at http://localhost:8004/docs

# List available analyses
curl http://localhost:8004/analyses

# Run template-based analysis
curl -X POST http://localhost:8004/analyze/template \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites.tsv",
    "analysis_type": "high_alternative_splicing",
    "model": "gpt-4o-mini"
  }'

# Run exploratory analysis
curl -X POST http://localhost:8004/analyze/exploratory \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites.tsv",
    "research_question": "What genes show tissue-specific splicing patterns?",
    "model": "gpt-4o-mini"
  }'
```

### 🗄️ Quick Start: SQL Agent

Generate SQL queries from natural language:

```bash
# Open the interactive notebook
jupyter notebook reflection/sql_agent/sql.ipynb

# Or use the adaptive workflow programmatically
python3 -c "from reflection.sql_agent.adaptive_sql_workflow import *"
```

### 🐳 Docker Setup (Research Agent)

For the research agent web app, see [Docker Setup](#build--run-localdev) below.

---

## Prerequisites

### For Local Development

* **Python 3.10+** (automatically handled by mamba/conda)
* **API keys** in `.env` file (see [Environment Setup](#environment-variables))

See `docs/ENVIRONMENT_SETUP.md` for complete setup guide.

### For Docker

* **Docker** (Desktop on Windows/macOS, or engine on Linux).
* API keys stored in a `.env` file:

  ```
  OPENAI_API_KEY=your-open-api-key
  TAVILY_API_KEY=your-tavily-api-key
  ```

* Python deps are installed by Docker from `requirements.txt`:

  * `fastapi`, `uvicorn`, `sqlalchemy`, `python-dotenv`, `jinja2`, `requests`, `wikipedia`, etc.
  * Plus any libs used by your `aisuite` client.

---

## Environment variables

The app **reads only `DATABASE_URL`** at startup.

* The container’s entrypoint sets a sane default for local dev:

  ```
  postgresql://app:local@127.0.0.1:5432/appdb
  ```
* To use Tavily:

  * Provide `TAVILY_API_KEY` (via `.env` or `-e`).

Optional (if you want to override defaults done by the entrypoint):

* `POSTGRES_USER` (default `app`)
* `POSTGRES_PASSWORD` (default `local`)
* `POSTGRES_DB` (default `appdb`)

---

## Build & Run (local/dev)

### 1) Build

```bash
docker build -t fastapi-postgres-service .
```

### 2) Run (foreground)

```bash
docker run --rm -it  -p 8000:8000  -p 5432:5432  --name fpsvc  --env-file .env  fastapi-postgres-service
```

You should see logs like:

```
🚀 Starting Postgres cluster 17/main...
✅ Postgres is ready
CREATE ROLE
CREATE DATABASE
🔗 DATABASE_URL=postgresql://app:local@127.0.0.1:5432/appdb
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3) Open the app

* UI: [http://localhost:8000/](http://localhost:8000/)
* Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API quickstart

### Kick off a run

```bash
curl -X POST http://localhost:8000/generate_report \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Large Language Models for scientific discovery", "model":"openai:gpt-4o"}'
# -> {"task_id": "UUID..."}
```

### Poll progress

```bash
curl http://localhost:8000/task_progress/<TASK_ID>
```

### Final status + report

```bash
curl http://localhost:8000/task_status/<TASK_ID>
```

---

## Troubleshooting

**I open [http://localhost:8000](http://localhost:8000) and see nothing / errors**

* Confirm `templates/index.html` exists inside the container:

  ```bash
  docker exec -it fpsvc bash -lc "ls -l /app/templates && ls -l /app/static || true"
  ```
* Watch logs while you load the page:

  ```bash
  docker logs -f fpsvc
  ```

**Container asks for a Postgres password on startup**

* The entrypoint uses **UNIX socket + peer auth** for admin tasks (no password).
  Ensure you’re not calling `psql -h 127.0.0.1 -U postgres` in the script—use:

  ```bash
  su -s /bin/bash postgres -c "psql -c '...'"
  ```

**`DATABASE_URL not set` error**

* The entrypoint exports a default DSN. If you overrode it, ensure it’s valid:

  ```
  postgresql://<user>:<password>@<host>:<port>/<database>
  ```

**Tables disappear on restart**

* In your `main.py` you call `Base.metadata.drop_all(...)` on startup.
  Comment it out or guard with an env flag:

  ```python
  if os.getenv("RESET_DB_ON_STARTUP") == "1":
      Base.metadata.drop_all(bind=engine)
  ```

**Tavily / arXiv / Wikipedia errors**

* Provide `TAVILY_API_KEY` and ensure network access, provide in the root dir and `.env` file as follows:
```
# OpenAI API Key
OPENAI_API_KEY=your-open-api-key
TAVILY_API_KEY=your-tavily-api-key
```

* Wikipedia rate limits sometimes; try later or handle exceptions gracefully.

---

## Development tips

* **Hot reload** (optional): For dev, you can run Uvicorn with `--reload` if you mount your code:

  ```bash
  docker run --rm -it -p 8000:8000 -p 5432:5432 \
    -v "$PWD":/app \
    --name fpsvc fastapi-postgres-service \
    bash -lc "pg_ctlcluster \$(psql -V | awk '{print \$3}' | cut -d. -f1) main start && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
  ```

* **Connect to DB from host:**

  ```bash
  psql "postgresql://app:local@localhost:5432/appdb"
  ```

---

## 🆕 Recent Updates

### November 2024: Production Agent Services

**Chart Agent (NEW):**
- ✅ Production-ready FastAPI service with Swagger UI (port 8003)
- ✅ DuckDB-based data access for TSV, CSV, Parquet files
- ✅ LLM-driven code-as-plan chart generation
- ✅ Reflection pattern for iterative code improvement
- ✅ Multi-model support (GPT-4, GPT-5, o1, etc.)
- ✅ Comprehensive documentation and examples
- ✅ Supersedes `reflection/chart_workflow/`

**Splice Agent (NEW):**
- ✅ Domain-specific genomics analysis agent
- ✅ FastAPI service with splice-specific endpoints (port 8004)
- ✅ Predefined analysis templates for splice sites
- ✅ Exploratory analysis mode for custom research questions
- ✅ Built on chart_agent core engine
- ✅ Biological context and genomic feature analysis

**Model Support Updates:**
- ✅ GPT-5 series support (gpt-5, gpt-5-mini, gpt-5-pro, gpt-5-codex)
- ✅ GPT-5.1 series support (gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-mini)
- ✅ Responses API support for all models
- ✅ Updated model recommendations for fast prototyping

### October 2024: Iterative Refinement & Code Persistence

**Chart Workflow Enhancements:**
- ✅ Configurable `max_iterations` with early stopping on convergence
- ✅ Save final refined code to disk
- ✅ Per-iteration tracking and summary output
- ✅ Cost savings: 25-50% for strong models via early stopping

**SQL Agent Analysis:**
- ✅ Adaptive iteration based on model strength
- ✅ Convergence detection and regression handling
- ✅ Comprehensive analysis document with cost/quality tradeoffs

---

## 📚 Learning Resources

### Documentation

**Agent Documentation:**
- `chart_agent/README.md` - Chart Agent overview and features
- `chart_agent/docs/` - Comprehensive Chart Agent documentation
- `splice_agent/README.md` - Splice Agent overview and features
- `splice_agent/docs/` - Splice Agent documentation
- `splice_agent/QUICKSTART.md` - 5-minute Splice Agent guide
- `splice_agent/MIGRATION.md` - Moving Splice Agent to new projects

**General Documentation:**
- `LEARNING_GUIDE.md` - Comprehensive guide to agentic AI patterns
- `AGENTS.md` - Agent architecture and design patterns
- `docs/ENVIRONMENT_SETUP.md` - Environment configuration guide
- `docs/SETUP_CHECKLIST.md` - Setup verification checklist
- `reflection/sql_agent/ADAPTIVE_ITERATION_ANALYSIS.md` - Adaptive iteration deep dive

### Example Datasets
- `data/splice_sites_enhanced.tsv` - Complex genomic data (2.8M rows)
- `reflection/M2_UGL_1/coffee_sales.csv` - Simple temporal data

### Example Scripts
- `chart_agent/examples/quick_start.py` - Chart Agent quick examples
- `chart_agent/examples/analyze_splice_sites.py` - Splice site analysis
- `splice_agent/examples/quick_start.py` - Splice Agent examples
- `splice_agent/examples/analyze_splice_sites.py` - Full splice analysis CLI

### Interactive Notebooks
- `reflection/sql_agent/sql.ipynb` - SQL generation with reflection
- `chart_agent/examples/` - Chart Agent notebooks
- `reflection/C1M2_Assignment.ipynb` - Course assignments

---

## 🤝 Contributing

This repository demonstrates practical agentic AI patterns and is **actively expanding**. Contributions are welcome!

**Priority Areas (see [Roadmap](#️-roadmap-planned-workflow-patterns)):**
- **Multiagent workflows** - Collaboration, hierarchical architectures, parallel execution
- **Advanced orchestration** - Dynamic routing, state machines, error recovery
- **Specialized agents** - Code generation, data analysis, document processing
- **Performance optimization** - Caching, batch processing, cost tracking

**Other Contributions:**
- Additional workflow implementations and design patterns
- Performance optimizations and cost reduction strategies
- Enhanced testing and validation
- Documentation improvements
- New example datasets and use cases

**Testing:**
```bash
# Run all tests
pytest tests/

# Run specific workflow tests
pytest tests/chart_workflow/
pytest tests/sql_agent/
```

---

## 📖 Related Documentation

**Agent Documentation:**
- `chart_agent/README.md` - Chart Agent comprehensive guide
- `chart_agent/docs/` - Chart Agent detailed documentation
- `splice_agent/README.md` - Splice Agent comprehensive guide
- `splice_agent/QUICKSTART.md` - Splice Agent quick start
- `splice_agent/MIGRATION.md` - Splice Agent migration guide

**General Documentation:**
- `SETUP_README.md` - Detailed setup instructions
- `LEARNING_GUIDE.md` - Agentic AI concepts and patterns
- `AGENTS.md` - Agent architecture guide
- `docs/` - Global documentation (architecture, tutorials, installation)
- `docs/libraries/` - Library documentation
- `reflection/docs/` - Workflow-specific documentation

---

## 📄 License

See repository license file for details.

---

## 🙏 Acknowledgments

Built with:
- OpenAI GPT models for generation and reflection
- `aisuite` for unified LLM interface
- FastAPI for web services
- Matplotlib/Pandas for data visualization
- SQLite for data storage
- Tavily, arXiv, Wikipedia for research tools

---
