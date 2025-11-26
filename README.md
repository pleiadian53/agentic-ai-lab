# Nexus: Superintelligent Research System

**Building toward superintelligent AI for scientific discovery** through an evolving collection of agentic workflows and design patterns.

📚 **[Quick Start Guide](QUICKSTART.md)** | 🏗️ **[Architecture](ARCHITECTURE.md)** | 📖 **[Full Documentation](src/nexus/agents/research/README.md)**

---

## Vision

Nexus is our journey toward creating a **superintelligent research expert** - an AI system that combines reflection, tool use, multiagent collaboration, and advanced reasoning to push the boundaries of scientific discovery and exploration into uncharted territories. This repository documents our learning, experimentation, and production implementations as we build toward this ambitious goal.

### What We're Building

**Nexus Research System** - An intelligent, multi-agent research platform that:
- 🔬 Generates comprehensive research reports with publication-quality output
- 🧠 Combines multiple AI agents (Planner, Researcher, Writer, Editor) for intelligent orchestration
- 🔧 Integrates diverse knowledge sources (arXiv, PubMed, Tavily, Wikipedia)
- 📊 Produces beautiful PDFs with LaTeX equation rendering
- 🎯 Adapts to different research domains and complexity levels
- 🚀 Actively evolving with new capabilities (see roadmap below)

### Design Patterns

This repository **illustrates** key agentic AI design patterns through working implementations:
- **Reflection**: Iterative refinement and self-evaluation
- **Tool Use**: Integration with external knowledge and APIs
- **Code-as-Plan**: LLM-driven code generation and execution
- **Multiagent Systems**: Collaborative AI architectures
- **Evaluation**: Quality assessment and convergence detection

Each pattern and agent demonstrates how these principles combine to create **a superintelligent system capable of autonomous scientific discovery**.

> **Note**: This is an actively evolving project. We're continuously learning, experimenting, and integrating new capabilities as we work toward true AI-powered research superintelligence.

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "User Interface"
        CLI[💻 CLI]
        WEB[🌐 Web UI]
    end
    
    subgraph "🎯 Nexus Core Pipeline"
        PLAN[📋 Planner<br/>Strategy]
        RESEARCH[🔍 Researcher<br/>Knowledge]
        WRITE[✍️ Writer<br/>Content]
        EDIT[📝 Editor<br/>Quality]
    end
    
    subgraph "🔧 Knowledge Sources"
        TOOLS[🌐 Tavily • 📚 arXiv<br/>🏥 PubMed • 🔬 Europe PMC<br/>📖 Wikipedia]
    end
    
    subgraph "🤝 Supporting Agents"
        CHART[📊 Chart Agent]
        SQL[🗄️ SQL Agent]
        SPLICE[🧬 Splice Agent]
    end
    
    subgraph "Output"
        PDF[📕 PDF + Equations]
        MD[📝 Markdown]
    end
    
    CLI --> PLAN
    WEB --> PLAN
    PLAN --> RESEARCH
    RESEARCH --> TOOLS
    RESEARCH --> WRITE
    WRITE --> EDIT
    EDIT --> PDF
    EDIT --> MD
    
    CHART -.-> WRITE
    SQL -.-> RESEARCH
    SPLICE -.-> RESEARCH
    
    style PLAN fill:#fff4e1
    style RESEARCH fill:#e1f5ff
    style WRITE fill:#f0e1ff
    style EDIT fill:#e1ffe1
    style PDF fill:#ffe1f0
```

**See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and workflows.**

---

## 🎯 Core System: Nexus Research Agent

### **Nexus Research Agent** 🔬✨
**Intelligent research agent** with multi-agent pipeline, PDF generation, and LaTeX equation rendering. *Active development - see roadmap below.*

- **Location**: `src/nexus/agents/research/`
- **Current Features**:
  - **CLI & Web Interface** - Both command-line and web UI (port 8004)
  - **Multi-agent pipeline** - Planner → Research → Writer → Editor
  - **Tool integration** - Tavily, arXiv, PubMed, Europe PMC, Wikipedia
  - **PDF generation** - Professional PDFs with LaTeX equation rendering
  - **Report length options** - Brief, standard, comprehensive, technical-paper
  - **Context guidance** - Style templates and domain-specific instructions
  - **Manifest tracking** - Automatic metadata and version tracking
  - **Smart slugs** - Intelligent topic-based file organization
- **CLI**: `nexus-research "your topic" --model gpt-4o --pdf`
- **Web UI**: [http://localhost:8004](http://localhost:8004)
- **Docs**: `src/nexus/agents/research/README.md`
- **Output**: `output/research_reports/<topic>/`

**Example Reports** 📊:

> 📖 **Dual-Format Reports**: LaTeX reports include both a GitHub-friendly Markdown preview (equations as images) and a publication-quality PDF. Click "Read on GitHub" for instant viewing or "Download PDF" for the full experience.

- **[All-Atom Biomolecular Design](output/research_reports/all_atom_biomolecular_design/)** - Cutting-edge 2025 AI/ML for molecular design (3,849 words, 25 steps, gpt-5.1)
  - Covers RFdiffusion3, Boltz-2, AlphaFold3 breakthroughs
  - Diffusion models, transformer architectures, drug discovery applications
  - Demonstrates multi-source synthesis (arXiv, PubMed, web)
  - [📖 Read on GitHub](output/research_reports/all_atom_biomolecular_design/report_2025-11-25_23-30.md) | [⬇️ Download PDF](https://github.com/pleiadian53/agentic-ai-lab/raw/main/output/research_reports/all_atom_biomolecular_design/report_2025-11-25_23-30.pdf) | [📝 LaTeX Source](output/research_reports/all_atom_biomolecular_design/report_2025-11-25_23-30.tex)

- **[AGI Consciousness & Sentience](output/research_reports/consciousness_sentience_agi/)** - Methodological approaches to consciousness detection (3,833 words, 26 steps, gpt-5.1)
  - Focuses on technical frameworks: IIT, Global Workspace Theory, Active Inference
  - Empirical tests and measurement approaches
  - Multi-source research with Reddit community insights
  - [📖 Read on GitHub](output/research_reports/consciousness_sentience_agi/report_2025-11-25_23-04.md) | [⬇️ Download PDF](https://github.com/pleiadian53/agentic-ai-lab/raw/main/output/research_reports/consciousness_sentience_agi/report_2025-11-25_23-04.pdf) | [📝 LaTeX Source](output/research_reports/consciousness_sentience_agi/report_2025-11-25_23-04.tex)

- **[Quantum Entanglement & Bell's Theorem](output/research_reports/quantum_entanglement_bell_theorem/)** - Brief technical report with LaTeX equations (709 words, 12 steps, gpt-4o)
  - Publication-quality PDF with proper mathematical notation
  - Demonstrates equation rendering capabilities
  - [⬇️ Download PDF](https://github.com/pleiadian53/agentic-ai-lab/raw/main/output/research_reports/quantum_entanglement_bell_theorem/report_2025-11-23_17-27.pdf)

- **[Einstein's Field Equations](output/research_reports/einstein_field_equations_gravity/)** - Physics report with tensor notation (gpt-4o)
  - Full LaTeX compilation with variable definitions and physical interpretations
  - [⬇️ Download PDF](https://github.com/pleiadian53/agentic-ai-lab/raw/main/output/research_reports/einstein_field_equations_gravity/report_2025-11-23_17-37.pdf)

**Roadmap** 🚀:
- [ ] **Style Transfer** - Use example papers (e.g., `data/papers/OpenSpliceAI.pdf`) as style templates
- [ ] **Paper2Code Integration** - Learn by doing: generate code prototypes alongside research reports
- [ ] **GitHub Discovery** - Find and analyze paper implementations, suggest extensions
- [ ] **Enhanced Web UI** - Progress tracking, cost estimation, improved aesthetics
- [ ] **Uncertainty Quantification** - Confidence scores and source reliability metrics
- [ ] **Interactive Refinement** - Iterative report improvement with user feedback

---

## 🤝 Supporting Agents

These general-purpose agents enhance Nexus's research capabilities:

### **Chart Agent** 📊
**Visual presentation of research insights** - Helps Nexus present ideas and data visually.

- **Location**: `chart_agent/`
- **Role**: Generate publication-quality visualizations for research reports
- **Features**:
  - FastAPI REST API (`http://localhost:8003/docs`)
  - LLM-driven code-as-plan chart generation
  - Iterative refinement with reflection
  - DuckDB-based data access (TSV, CSV, Parquet)
  - Multiple model support (GPT-4, GPT-5, o1)
- **Integration**: Can be called by Nexus to create figures and visualizations
- **Docs**: `chart_agent/docs/`

### **SQL Agent** 🗄️
**Dataset querying and analysis** - Helps Nexus query and analyze research datasets.

- **Location**: `reflection/sql_agent/`
- **Role**: Natural language to SQL for data exploration
- **Features**:
  - Adaptive iteration based on model strength
  - Convergence detection and regression handling
  - Event-sourced transaction database
- **Integration**: Enables Nexus to query databases for research data
- **Docs**: `reflection/sql_agent/ADAPTIVE_ITERATION_ANALYSIS.md`

### **Future Supporting Agents** 🔮
Planned general-purpose agents to expand Nexus capabilities:
- **Email Agent** - Send research updates and summaries
- **Code Agent** - Generate and test research code (Paper2Code integration)
- **GitHub Agent** - Discover and analyze paper implementations
- **Citation Agent** - Manage references and bibliography
- **Experiment Agent** - Design and track computational experiments
- **Market Research Agent** - Business and market analysis (to be ported)

---

## 🧬 Domain-Specific Research Agents

Specialized agents for specific research domains (separate projects):

### **Splice Agent** 🧬
**RNA splicing and alternative splicing research** - A complex, dedicated project for computational biology.

- **Project**: [splice-agent](https://github.com/yourusername/splice-agent) (separate repository)
- **Location** (prototype): `splice_agent/`
- **Domain**: RNA splicing, alternative splicing, genomics
- **Complexity**: Full research area requiring dedicated development
- **Features**:
  - Domain-specific analysis templates for splice sites
  - Biological context and genomic feature interpretation
  - Integration with genomics databases
  - Built on chart_agent core engine
- **Status**: Active research project with ongoing development
- **Note**: Due to the complexity of RNA splicing research, this is maintained as a separate project at `/Users/pleiadian53/work/splice-agent`

### **Future Domain-Specific Agents** 🔬
Potential specialized research agents for dedicated domains:
- **Protein Structure Agent** - Protein folding and structure prediction
- **Drug Discovery Agent** - Computational drug design and screening
- **Climate Modeling Agent** - Climate science and environmental research
- **Materials Science Agent** - Computational materials discovery

---

## 📚 Legacy & Learning

### **Legacy Research Agent** 🔬
Original research workflow prototype (now superseded by Nexus).
- **Location**: `multiagent/research_agent/`, `legacy/prototype/`
- **Purpose**: Experimentation, learning, and brainstorming new multiagent features
- **Features**:
  - FastAPI web app with Postgres backend
  - Tool-using agents (Tavily, arXiv, Wikipedia)
  - Live task progress tracking
  - Docker deployment
- **Note**: Use **Nexus Research Agent** for production work

### **6. Visualization Agent** 📈
Advanced data visualization with multiple chart types and layouts.
- **Location**: `reflection/viz_agent/`
- **Features**: Multi-panel figures, exploratory analysis, custom styling

### **7. Legacy Workflows** 📚
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
├─ src/nexus/                   # 🎯 CORE: Nexus Research System
│  ├─ agents/research/          # Research agent implementation
│  │  ├─ server/                # FastAPI web interface (port 8004)
│  │  ├─ docs/                  # Documentation and guides
│  │  ├─ pipeline.py            # Multi-agent orchestration
│  │  ├─ agents.py              # Planner, Researcher, Writer, Editor
│  │  ├─ format_decision.py     # Intelligent format selection
│  │  ├─ pdf_utils.py           # LaTeX PDF generation
│  │  ├─ manifest.py            # Report metadata tracking
│  │  └─ run.py                 # CLI entry point
│  ├─ core/                     # Shared Nexus infrastructure
│  │  ├─ config.py              # Centralized configuration
│  │  └─ llm_client.py          # LLM client wrapper
│  └─ templates/                # Report templates and styles
│
├─ chart_agent/                 # 📊 SUPPORTING: Visual presentation
│  ├─ server/                   # FastAPI service (port 8003)
│  ├─ examples/                 # Example scripts and notebooks
│  ├─ docs/                     # Documentation
│  ├─ data_access.py            # DuckDB dataset loading
│  ├─ planning.py               # LLM-based code generation
│  └─ llm_client.py             # OpenAI API client
│
├─ splice_agent/                # 🧬 DOMAIN-SPECIFIC: RNA splicing (prototype)
│  ├─ server/                   # FastAPI service
│  ├─ examples/                 # Splice analysis examples
│  ├─ docs/                     # Documentation
│  └─ splice_analysis.py        # Domain-specific templates
│  # Note: Full project at /Users/pleiadian53/work/splice-agent
│
├─ reflection/                  # 📚 LEARNING: Design pattern examples
│  ├─ sql_agent/                # SQL generation with adaptive iteration
│  ├─ chart_workflow/           # Chart generation prototype
│  ├─ research_agent/           # Research workflow experiments
│  └─ viz_agent/                # Visualization agent
│
├─ multiagent/                  # 📚 LEARNING: Multiagent patterns
│  ├─ research_agent/           # Legacy research agent (superseded by Nexus)
│  └─ customer_service/         # Customer service system
│
├─ eval/                        # 🎯 EVALUATION: Quality assessment & error analysis
│  ├─ metrics/                  # Evaluation metrics and scoring
│  ├─ error_analysis/           # Error pattern analysis
│  ├─ benchmarks/               # Benchmark datasets and tests
│  └─ reports/                  # Evaluation reports and insights
│
├─ legacy/                      # 📚 LEARNING: Historical implementations
│  └─ prototype/                # Early prototypes and experiments
│
├─ output/                      # Generated outputs
│  └─ research_reports/         # Nexus research reports
│
├─ data/                        # Sample datasets and papers
│  └─ papers/                   # Example papers for style transfer
│
├─ dev/                         # Development documentation
│  └─ nexus/                    # Nexus-specific development docs
│
├─ docs/                        # Global documentation
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

### � Quick Start: Nexus Research Agent

**CLI Interface:**

```bash
# Activate environment
mamba activate agentic-ai

# Generate research report (markdown only)
nexus-research "Physics-Informed Neural Networks for PDEs" --model openai:gpt-4o

# Generate with PDF (recommended - beautiful equation rendering)
nexus-research "quantum error correction codes" --model openai:gpt-4o --pdf

# Specify report length
nexus-research "CRISPR gene editing" --length comprehensive --pdf

# Add context/style guidance
nexus-research "protein folding" \
  --model openai:gpt-4o \
  --length standard \
  --context "Follow Nature journal style. Focus on AlphaFold 3." \
  --pdf

# Output location: output/research_reports/<topic_slug>/
```

**Web Interface:**

```bash
# Start the Nexus Research Agent server
nexus-research-server

# Visit web UI at http://localhost:8004
# Features:
# - Interactive form for research requests
# - Real-time generation progress
# - Automatic PDF generation with LaTeX equations
# - Download markdown and PDF reports
# - Browse previous reports
```

**Report Features:**
- ✅ **LaTeX equation rendering** - Beautiful mathematical typography in PDFs
- ✅ **Multiple sources** - Tavily, arXiv, PubMed, Europe PMC, Wikipedia
- ✅ **Configurable length** - Brief (2-3 pages) to Technical Paper (25-40 pages)
- ✅ **Context guidance** - Style templates and domain-specific instructions
- ✅ **Manifest tracking** - Automatic metadata for all reports
- ✅ **Smart organization** - Topic-based file structure

### ��️ Quick Start: SQL Agent

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
