# Nexus: Superintelligent Research Platform

**Version:** 0.1.0  
**Status:** Active Development

## Overview

Nexus is a unified platform for orchestrating multiple AI agents to conduct scientific research, data analysis, and knowledge synthesis. It aims to accelerate scientific discovery by combining specialized agents into coordinated workflows.

## Architecture

```
nexus/
├── core/          # Shared infrastructure
├── agents/        # Individual AI agents
├── workflows/     # Multi-agent pipelines
├── templates/     # Paper style transfer
├── knowledge/     # Knowledge management
├── server/        # Web interface
├── cli/           # Command-line interface
└── docs/          # Documentation
```

## Agents

- **Research Agent**: Literature review and comprehensive report generation
- **Chart Agent**: Data visualization and analysis
- **SQL Agent**: Database querying and data retrieval
- **Splice Agent**: Genomic sequence analysis
- **ML Agent**: Machine learning and predictions
- **Email Agent**: Communication and collaboration

## Key Features

### 🎯 Multi-Agent Orchestration
Coordinate multiple agents to work together on complex research tasks.

### 📄 Paper-Based Style Transfer
Generate reports matching the style of template papers (e.g., Nature, Science, arXiv).

### 🧠 Knowledge Graph Integration
Build and query a knowledge graph across all research activities.

### 🔬 Experimental Results Aggregation
Synthesize experimental results from credible sources.

### 🖥️ Unified Interfaces
Single CLI and web UI for all agents and workflows.

## Quick Start

### Installation

```bash
# Create and activate conda environment
mamba env create -f environment.yml
mamba activate agentic-ai

# Install the package in development mode
pip install -e .
```

See [Installation Guide](docs/installation.md) for detailed setup instructions including LaTeX engine configuration.

## Usage

### Web Interface (Recommended)

The easiest way to use the Research Agent is through the web interface:

```bash
# Start the server
nexus-research-server

# Or using the start script
./scripts/start_research_server.sh

# Visit http://localhost:8004
```

**Features:**
- 📝 Interactive form for research topics
- 📊 Real-time progress updates
- 📄 Automatic PDF generation with LaTeX equations
- 📚 Browse and download previous reports
- 🎨 Clean, modern interface

**Stopping the server:**
```bash
./scripts/stop_research_server.sh
```

### Command Line Interface

**Basic research report:**
```bash
# Generate a research report on a topic
nexus-research "quantum computing advances in 2024-2026"
```

**With PDF output:**
```bash
# Generate report with PDF (includes LaTeX equations)
nexus-research "CRISPR gene editing applications" --pdf
```

**Specify model:**
```bash
# Use GPT-4o for higher quality
nexus-research "protein folding with AlphaFold" \
  --model openai:gpt-4o \
  --pdf
```

**Output location:**
```bash
# Reports are saved to: output/research_reports/<topic>/
# - report_YYYY-MM-DD_HH-MM.md  (Markdown)
# - report_YYYY-MM-DD_HH-MM.pdf (PDF, if --pdf flag used)
# - manifest.json (Metadata)
```

### Python API

```python
from nexus.agents.research.pipeline import ResearchPipeline

# Create pipeline
pipeline = ResearchPipeline(
    model="openai:gpt-4o-mini",
    generate_pdf=True
)

# Generate research report
result = pipeline.run(
    topic="advances in quantum error correction",
    max_sections=5
)

print(f"Report saved to: {result['report_path']}")
if result['pdf_path']:
    print(f"PDF saved to: {result['pdf_path']}")
```

## Documentation

### Core Documentation
- [Installation Guide](docs/installation.md) - Setup, dependencies, and LaTeX configuration
- [Research Agent README](agents/research/README.md) - Detailed usage and API reference
- [Architecture Overview](docs/README.md) - System design and vision

### Planned Documentation
- Multi-agent workflows (coming soon)
- Paper style transfer system (coming soon)
- Knowledge graph integration (coming soon)

## Development Status

### ✅ Completed
- **Research Agent** - Multi-agent pipeline (Planner → Researcher → Writer → Editor)
- **Web Interface** - FastAPI server with real-time progress (port 8004)
- **CLI Tools** - `nexus-research` and `nexus-research-server` commands
- **PDF Generation** - LaTeX equation rendering with Tectonic
- **Tool Integration** - Tavily, arXiv, PubMed, Europe PMC, Wikipedia
- **Manifest System** - Smart organization and tracking

### 🚧 In Progress
- **Enhanced Web UI** - Cost estimation, better UX, granular progress
- **Style Transfer** - Generate reports matching example paper styles
- **Paper2Code Integration** - Learn by implementing research papers

### 📋 Planned
- **GitHub Discovery** - Find and analyze paper implementations
- **Multi-agent Orchestration** - Coordinate Research, Chart, SQL agents
- **Knowledge Graph** - Cross-research knowledge synthesis
- **Additional Agents** - Email, Citation, Experiment agents
- **Uncertainty Quantification** - Confidence scores and reliability metrics

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.

## License

See [LICENSE](../../LICENSE) for details.
