# Agentic AI Workflows & Patterns

A comprehensive and **evolving collection** of **agentic AI workflows** demonstrating various design patterns including reflection, iterative refinement, tool-using agents, and multiagent systems. This repository includes multiple production-ready implementations for research, data visualization, SQL generation, and more.

> **Note**: This repository is actively expanding to cover additional agentic workflow patterns including multiagent collaboration, hierarchical agents, and advanced orchestration patterns.

## 🎯 What's Inside

This repository showcases **practical agentic AI patterns** with working implementations:

### **1. Chart Generation Workflow** 📊
Automated data visualization with iterative refinement and reflection.
- **Location**: `reflection/chart_workflow/`
- **Features**:
  - Iterative refinement with convergence detection (V1 → V2 → ... → Vn)
  - Auto-generated visualization prompts from data schemas
  - Code persistence (saves final refined Python code)
  - Configurable max iterations with early stopping
  - Cost optimization: 25-50% savings via smart stopping
- **CLI**: `scripts/run_chart_workflow.py`
- **Tests**: `tests/chart_workflow/`

### **2. SQL Agent Workflow** 🗄️
Natural language to SQL with adaptive iteration based on model strength.
- **Location**: `reflection/sql_agent/`
- **Features**:
  - Adaptive iteration (strong models: 1-2 iterations, weak models: 3-5)
  - Convergence detection and regression handling
  - Model-aware configuration (GPT-4 vs GPT-3.5 vs custom)
  - Event-sourced transaction database
- **Analysis**: `reflection/sql_agent/ADAPTIVE_ITERATION_ANALYSIS.md`
- **Notebook**: `reflection/sql_agent/sql.ipynb`

### **3. Research Agent** 🔬
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

### **4. Visualization Agent** 📈
Advanced data visualization with multiple chart types and layouts.
- **Location**: `reflection/viz_agent/`
- **Features**: Multi-panel figures, exploratory analysis, custom styling

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
├─ reflection/                  # Main workflows directory
│  ├─ chart_workflow/          # Chart generation with iterative refinement
│  │  ├─ workflow.py           # Core workflow logic with iteration loop
│  │  ├─ execution.py          # Code execution and validation
│  │  ├─ llm.py                # LLM integration for generation and reflection
│  │  ├─ prompting.py          # Auto-prompt generation from data
│  │  └─ data.py               # Data loading and preprocessing
│  ├─ sql_agent/               # SQL generation with adaptive iteration
│  │  ├─ sql.ipynb             # Interactive notebook
│  │  ├─ adaptive_sql_workflow.py  # Adaptive iteration implementation
│  │  ├─ ADAPTIVE_ITERATION_ANALYSIS.md  # Analysis and recommendations
│  │  └─ utils.py              # Database utilities
│  ├─ research_agent/          # Multi-step research workflow
│  └─ viz_agent/               # Advanced visualization agent
├─ scripts/                     # CLI tools
│  ├─ run_chart_workflow.py    # Chart generation CLI
│  └─ install/                 # Setup scripts
├─ tests/                       # Comprehensive test suites
│  ├─ chart_workflow/          # Chart workflow tests
│  │  ├─ test_iterative_refinement.py  # 6 iteration tests
│  │  └─ test_code_persistence.py      # 6 code saving tests
│  └─ sql_agent/               # SQL workflow tests
├─ src/                         # Research agent backend
│  ├─ planning_agent.py        # Planner and executor agents
│  ├─ agents.py                # Research, writer, editor agents
│  └─ research_tools.py        # Tavily, arXiv, Wikipedia tools
├─ docs/                        # Documentation
│  ├─ ENVIRONMENT_SETUP.md     # Environment configuration
│  ├─ SETUP_CHECKLIST.md       # Setup verification
│  └─ libraries/               # Library documentation
├─ data/                        # Sample datasets
├─ main.py                      # FastAPI app for research agent
├─ environment.yml              # Conda environment spec
├─ requirements.txt             # Python dependencies
├─ Dockerfile                   # Docker configuration
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

### 📊 Quick Start: Chart Workflow

Generate visualizations with iterative refinement:

```bash
# Activate environment
mamba activate agentic-ai

# Run with default settings (2 iterations, stop on convergence)
python3 scripts/run_chart_workflow.py data/your_data.csv

# Run with custom settings
python3 scripts/run_chart_workflow.py data/your_data.csv \
  --max-iterations 4 \
  --output-dir outputs/ \
  --image-basename my_chart

# With custom instruction
python3 scripts/run_chart_workflow.py data/your_data.csv \
  "Create a bar chart showing sales by category"
```

**Output:**
- `my_chart_v1.png`, `my_chart_v2.png`, ... (iterative charts)
- `my_chart_final.py` (final refined code)
- Per-iteration feedback and convergence detection

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

### October 2024: Iterative Refinement & Code Persistence

**Chart Workflow Enhancements:**
- ✅ Configurable `max_iterations` with early stopping on convergence
- ✅ Save final refined code to disk (`--no-save-final-code` to disable)
- ✅ Per-iteration tracking and summary output
- ✅ Backward compatible with existing code
- ✅ Cost savings: 25-50% for strong models via early stopping

**SQL Agent Analysis:**
- ✅ Adaptive iteration based on model strength (GPT-4 vs GPT-3.5 vs custom)
- ✅ Convergence detection and regression handling
- ✅ Comprehensive analysis document with cost/quality tradeoffs
- ✅ Role assignment importance analysis for prompts

**Testing Infrastructure:**
- ✅ `test_iterative_refinement.py` - 6 test cases for iteration features
- ✅ `test_code_persistence.py` - 6 test cases for code saving
- ✅ `test_adaptive_vs_fixed.py` - SQL workflow comparisons
- ✅ `test_role_importance.py` - Prompt engineering analysis

All tests pass successfully with comprehensive coverage.

---

## 📚 Learning Resources

### Documentation
- `LEARNING_GUIDE.md` - Comprehensive guide to agentic AI patterns
- `AGENTS.md` - Agent architecture and design patterns
- `docs/ENVIRONMENT_SETUP.md` - Environment configuration guide
- `docs/SETUP_CHECKLIST.md` - Setup verification checklist
- `reflection/sql_agent/ADAPTIVE_ITERATION_ANALYSIS.md` - Adaptive iteration deep dive

### Example Datasets
- `reflection/M2_UGL_1/coffee_sales.csv` - Simple temporal data
- `data/splice_sites_enhanced.tsv` - Complex genomic data (2.8M rows)

### Interactive Notebooks
- `reflection/sql_agent/sql.ipynb` - SQL generation with reflection
- `reflection/C1M2_Assignment.ipynb` - Course assignments
- `reflection/C1M2_Assignment_Solution.ipynb` - Solutions

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

- `SETUP_README.md` - Detailed setup instructions
- `LEARNING_GUIDE.md` - Agentic AI concepts and patterns
- `AGENTS.md` - Agent architecture guide
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
