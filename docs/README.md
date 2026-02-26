# Documentation Index

Welcome to the Agentic AI documentation! This guide is organized by topic for easy navigation.

## 📁 Documentation Structure

### 🔧 [Installation & Setup](./installation/)

Getting started with the project environment and dependencies.

- **[Environment Setup](./installation/ENVIRONMENT_SETUP.md)** - Complete environment configuration guide
- **[Editable Install](./installation/EDITABLE_INSTALL.md)** - How to install in development mode
- **[Mamba vs Pip](./installation/MAMBA_VS_PIP.md)** - Package manager comparison
- **[Setup Checklist](./installation/SETUP_CHECKLIST.md)** - Step-by-step setup verification
- **[GitHub Setup](./installation/GITHUB_SETUP.md)** - Repository and Git configuration
- **[Install Quickstart](./installation/INSTALL_QUICKSTART.md)** - Quick installation guide
- **[Setup README](./installation/SETUP_README.md)** - Mamba/conda setup guide

**Start here if:** You're setting up the project for the first time.

---

### 🎯 [Agentic Patterns](./patterns/)

Design patterns for building intelligent agents.

- **[Agentic Patterns Overview](./patterns/AGENTIC_PATTERNS.md)** - All implemented and planned patterns
- **[Reflection Pattern](./patterns/RESEARCH_AGENT_GUIDE.md)** - Draft-Reflect-Revise workflow
- **[Enhanced Reflection Prompt](./patterns/ENHANCED_REFLECTION_PROMPT.md)** - Structured critique framework

**Start here if:** You want to understand or implement agentic design patterns.

---

### 🔄 [Workflows](./workflows/)

Specific workflow implementations and guides.

- **[Driver Script Guide](./workflows/DRIVER_SCRIPT_GUIDE.md)** - How to use CLI workflow tools
- **[Output Strategy](./workflows/OUTPUT_STRATEGY.md)** - Where outputs are saved and why

**Start here if:** You want to run or customize existing workflows.

---

### 🏗️ [Architecture](./architecture/)

Project structure, organization, and roadmap.

- **[Agentic Roadmap](./architecture/AGENTIC_ROADMAP.md)** - Project vision and future plans
- **[Test Organization](./architecture/TEST_ORGANIZATION.md)** - Testing structure and conventions

**Start here if:** You want to understand the project structure or contribute.

---

### 📚 [Libraries](./libraries/)

Documentation for external libraries and tools used in the project.

- **[Agent & LLM Tools](./libraries/AGENT_LLM_TOOLS.md)** - LLM provider libraries (aisuite, etc.)

**Start here if:** You need reference documentation for dependencies.

---

### 💾 [Data Management](./data_management/)

Guidelines for organizing, documenting, and versioning datasets.

- **[Data Management Guidelines](./data_management/guidelines.md)** - Complete data organization policy
- **[Data Patterns](./data_management/data_patterns.md)** - ML Agent data documentation patterns

**Start here if:** You're working with datasets or need to understand data organization.

---

### 📖 [Tutorials](./tutorials/)

Learning guides and usage examples.

- **[Learning Guide](./tutorials/LEARNING_GUIDE.md)** - Comprehensive system overview and learning path
- **[Usage Guide](./tutorials/USAGE_GUIDE.md)** - Research agent usage examples
- **[FastAPI Tool Use Tutorial](./tutorials/fastapi_tool_use_tutorial.md)** - Building tool-enabled agents with FastAPI

**Start here if:** You want to learn how to use the system.

---

### 👨‍💻 [Development](./development/)

Developer guides and collaboration standards.

- **[Codex Collaboration Guide](./development/AGENTS.md)** - How to work with Codex in this repo

**Start here if:** You're contributing code or working with AI assistants.

---

### 🗂️ Documentation Meta

- **[Directory Structure](./STRUCTURE.md)** - Full tree view of `docs/`
- **[Documentation Example](./DOCUMENTATION_GUIDES_EXAMPLE.md)** - Doc structure example from a reference project

---

### 🔍 [RAG](./RAG/)

Retrieval-Augmented Generation techniques and reference docs.

- **[ANN](./RAG/ANN/)** - Approximate nearest neighbor search
- **[Semantic Search Beyond Text](./RAG/semantic_search_beyond_text/)** - Multimodal and cross-modal search
- **[Sentence Transformers](./RAG/sentence_transformer/)** - Sentence embedding models

---

### 🕸️ [Knowledge Graphs](./knowledge_graph/)

Neo4j, Cypher, and knowledge graph construction docs.

---

### 🔢 [Multi-Vector Retrieval](./multivector_retrieval/)

- **[Multi-Vector Text Retrieval](./multivector_retrieval/01_multivector_text_retrieval.md)**
- **[Clustering in High Dimensions](./multivector_retrieval/02_clustering_in_high_dimensions.md)**

---

### 🤗 [HuggingFace](./huggingface/)

- **[Model Download Troubleshooting](./huggingface/model_download_troubleshooting.md)**

---

### 🔌 [Responses API](./responses_api/)

OpenAI Responses API reference and usage notes.

---

### 🚀 [Applications](./applications/)

Shareable documentation for active applications.

- **[Nexus](./applications/nexus/README.md)** - Research agent: architecture, integration roadmap, KG integration
  - **[Architecture](./applications/nexus/architecture.md)** - System design overview
  - **[Installation](./applications/nexus/installation.md)** - Setup and dependencies
  - **[Troubleshooting](./applications/nexus/troubleshooting.md)** - Common issues
  - **[Multi-Agent Workflow Tutorial](./applications/nexus/MULTIAGENT_WORKFLOW_TUTORIAL.md)** - Building multi-agent pipelines
  - **[Tool Orchestration Design](./applications/nexus/TOOL_ORCHESTRATION_DESIGN.md)** - How tools are selected and invoked
  - **[Tool Calling Reference](./applications/nexus/tool_calling/)** - Architecture, patterns, and AISuite vs raw API
- **[Chart Agent](./applications/chart_agent/README.md)** - AI-powered data visualization with reflection
  - **[Architecture](./applications/chart_agent/ARCHITECTURE.md)** - System and component design
  - **[LLM Insight Strategy](./applications/chart_agent/LLM_INSIGHT_STRATEGY.md)** - How insights are derived
  - **[Frontend Options](./applications/chart_agent/frontend/)** - Swagger, React, Streamlit, cURL

---

### 📦 [Products](./products/)

Documentation for graduated, stable products.

---

## 🚀 Quick Start Paths

### For New Users

1. [Install Quickstart](./installation/INSTALL_QUICKSTART.md) or [Setup README](./installation/SETUP_README.md)
2. [Learning Guide](./tutorials/LEARNING_GUIDE.md)
3. [Usage Guide](./tutorials/USAGE_GUIDE.md)
4. [Agentic Patterns Overview](./patterns/AGENTIC_PATTERNS.md)

### For Contributors

1. [Editable Install](./installation/EDITABLE_INSTALL.md)
2. [Test Organization](./architecture/TEST_ORGANIZATION.md)
3. [Agentic Roadmap](./architecture/AGENTIC_ROADMAP.md)
4. [Agentic Patterns](./patterns/AGENTIC_PATTERNS.md)

### For Pattern Developers

1. [Agentic Patterns Overview](./patterns/AGENTIC_PATTERNS.md)
2. [Reflection Pattern Guide](./patterns/RESEARCH_AGENT_GUIDE.md)
3. [Enhanced Reflection Prompt](./patterns/ENHANCED_REFLECTION_PROMPT.md)
4. [Test Organization](./architecture/TEST_ORGANIZATION.md)

---

## 📖 Documentation by Workflow

### Chart Generation Workflow

- [Driver Script Guide](./workflows/DRIVER_SCRIPT_GUIDE.md) - Chart workflow CLI
- [Enhanced Reflection Prompt](./patterns/ENHANCED_REFLECTION_PROMPT.md) - Chart critique framework
- [Output Strategy](./workflows/OUTPUT_STRATEGY.md) - Where charts are saved

### Research Agent Workflow (Reflection Pattern)

- [Research Agent Guide](./patterns/RESEARCH_AGENT_GUIDE.md) - Complete guide
- [Agentic Patterns](./patterns/AGENTIC_PATTERNS.md) - Pattern comparison
- [Driver Script Guide](./workflows/DRIVER_SCRIPT_GUIDE.md) - CLI usage

---

## 🔍 Find Documentation By Topic

### Installation & Environment
- Environment setup → [installation/ENVIRONMENT_SETUP.md](./installation/ENVIRONMENT_SETUP.md)
- Package managers → [installation/MAMBA_VS_PIP.md](./installation/MAMBA_VS_PIP.md)
- Editable mode → [installation/EDITABLE_INSTALL.md](./installation/EDITABLE_INSTALL.md)
- Quick install → [installation/INSTALL_QUICKSTART.md](./installation/INSTALL_QUICKSTART.md)
- Mamba setup → [installation/SETUP_README.md](./installation/SETUP_README.md)

### Learning & Tutorials
- System overview → [tutorials/LEARNING_GUIDE.md](./tutorials/LEARNING_GUIDE.md)
- Usage examples → [tutorials/USAGE_GUIDE.md](./tutorials/USAGE_GUIDE.md)

### Agentic AI Concepts
- Design patterns → [patterns/AGENTIC_PATTERNS.md](./patterns/AGENTIC_PATTERNS.md)
- Reflection pattern → [patterns/RESEARCH_AGENT_GUIDE.md](./patterns/RESEARCH_AGENT_GUIDE.md)
- Structured critique → [patterns/ENHANCED_REFLECTION_PROMPT.md](./patterns/ENHANCED_REFLECTION_PROMPT.md)

### Running Workflows
- CLI tools → [workflows/DRIVER_SCRIPT_GUIDE.md](./workflows/DRIVER_SCRIPT_GUIDE.md)
- Output locations → [workflows/OUTPUT_STRATEGY.md](./workflows/OUTPUT_STRATEGY.md)

### Project Structure
- Roadmap → [architecture/AGENTIC_ROADMAP.md](./architecture/AGENTIC_ROADMAP.md)
- Testing → [architecture/TEST_ORGANIZATION.md](./architecture/TEST_ORGANIZATION.md)

### Libraries & Tools
- LLM providers → [libraries/AGENT_LLM_TOOLS.md](./libraries/AGENT_LLM_TOOLS.md)

### Data Management
- Data guidelines → [data_management/guidelines.md](./data_management/guidelines.md)
- Data patterns → [data_management/data_patterns.md](./data_management/data_patterns.md)

### Development & Collaboration
- Codex guide → [development/AGENTS.md](./development/AGENTS.md)

### Documentation
- Organization → [DOCUMENTATION_ORGANIZATION.md](./DOCUMENTATION_ORGANIZATION.md)
- Structure → [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md)

---

## 📝 Documentation Standards

All documentation in this project follows these standards:

- **Markdown format** - Easy to read and version control
- **Topic-based organization** - Related docs grouped together
- **Clear examples** - Code snippets and command examples
- **Cross-references** - Links to related documentation
- **Status indicators** - ✅ Complete, 🚧 In Progress, ⏳ Planned

---

## 🤝 Contributing to Documentation

When adding new documentation:

1. **Choose the right directory:**
   - Installation/setup → `installation/`
   - Tutorials/learning → `tutorials/`
   - Design patterns → `patterns/`
   - Workflow guides → `workflows/`
   - Architecture/structure → `architecture/`
   - Library references → `libraries/`
   - Data management → `data_management/`
   - Developer guides → `development/`

2. **Follow naming conventions:**
   - Use UPPERCASE for main docs (e.g., `PATTERN_NAME.md`)
   - Be descriptive (e.g., `ENHANCED_REFLECTION_PROMPT.md`)

3. **Update this index:**
   - Add your new doc to the appropriate section
   - Include a brief description
   - Add cross-references if relevant

4. **Include:**
   - Clear title and overview
   - Code examples
   - Links to related docs
   - Status indicators

---

## 📊 Documentation Status

| Category | Docs | Status |
|----------|------|--------|
| Installation | 7 | ✅ Complete |
| Tutorials | 2 | ✅ Complete |
| Patterns | 3 | ✅ Complete (1 pattern), 🚧 More planned |
| Workflows | 2 | ✅ Complete |
| Architecture | 2 | ✅ Complete |
| Libraries | 1 | 🚧 In Progress |
| Data Management | 2 | ✅ Complete |
| Development | 1 | ✅ Complete |

**Last Updated:** November 7, 2024

---

## 🔗 External Resources

- **Main README:** `README.md` (project root)
- **Installation Guide:** [./installation/INSTALL_QUICKSTART.md](./installation/INSTALL_QUICKSTART.md)
- **Learning Guide:** [./tutorials/LEARNING_GUIDE.md](./tutorials/LEARNING_GUIDE.md)

---

## 💡 Tips

- **Use search:** Most IDEs support full-text search across docs
- **Check cross-references:** Docs link to related content
- **Start with overviews:** Pattern and workflow overviews provide context
- **Follow quick start paths:** Curated learning paths above

---

**Need help?** Check the [Setup Checklist](./installation/SETUP_CHECKLIST.md) or [Agentic Patterns Overview](./patterns/AGENTIC_PATTERNS.md).
