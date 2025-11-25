# Nexus Research Agent 🔬✨

**Production-ready multi-agent research system** with comprehensive report generation, PDF export with LaTeX equation rendering, and intelligent tool integration.

## Overview

The Nexus Research Agent is an enhanced, production-ready evolution of the original research agent prototype (now in `multiagent/research_agent/` and `legacy/prototype/`). It provides a robust, well-tested platform for generating comprehensive research reports with beautiful formatting and professional output.

## Key Features

### **Multi-Agent Pipeline** 🤖
- **Planning Agent**: Generates structured, step-by-step research plans
- **Research Agent**: Executes searches across multiple sources
- **Writer Agent**: Drafts comprehensive, well-structured reports
- **Editor Agent**: Refines for clarity, accuracy, and professional quality
- **Executor Agent**: Orchestrates the workflow with intelligent routing

### **Tool Integration** 🔧
- **Tavily Search**: Real-time web search with quality filtering
- **arXiv**: Academic papers and preprints
- **PubMed & Europe PMC**: Biomedical literature
- **Wikipedia**: Background knowledge and context

### **PDF Generation** 📄
- **LaTeX Equation Rendering**: Beautiful mathematical typography using pandoc
- **Professional Formatting**: Publication-quality PDFs
- **Automatic Generation**: Seamless markdown → PDF conversion

### **Report Configuration** ⚙️
- **Length Options**: Brief (2-3 pages), Standard (5-10 pages), Comprehensive (15-25 pages), Technical Paper (25-40 pages)
- **Context Guidance**: Style templates and domain-specific instructions
- **Model Selection**: Support for GPT-4, GPT-5, and other models via aisuite

### **Output Management** 📁
- **Standardized Paths**: `output/research_reports/<topic_slug>/`
- **Manifest Tracking**: Automatic metadata for all reports
- **Smart Slugs**: Intelligent topic-based file organization
- **Version Control**: Timestamped reports with full history

### **Interfaces** 🖥️
- **CLI**: Command-line interface for scripting and automation
- **Web UI**: Interactive form-based interface with real-time progress
- **Python API**: Programmatic access for integration

## Project Structure

```
src/nexus/agents/research/
├── agents.py              # Agent implementations (Planner, Research, Writer, Editor)
├── tools.py               # Tool definitions (Tavily, arXiv, PubMed, Wikipedia)
├── pipeline.py            # Workflow orchestration and execution
├── run.py                 # CLI entry point
├── manifest.py            # Report metadata tracking
├── slug_utils.py          # Topic slug generation
├── pdf_utils.py           # PDF generation with LaTeX support
├── server/                # Web interface
│   ├── app.py            # FastAPI server entry point
│   ├── research_service.py  # Main API service
│   ├── config.py         # Configuration and paths
│   ├── schemas.py        # Pydantic models
│   └── templates/        # HTML templates
└── docs/                  # Documentation
    ├── REPORT_LENGTH_CONFIGURATION.md
    └── QUICKSTART.md
```

## Quick Start

### Installation

```bash
# Activate the environment
mamba activate agentic-ai

# Install the package (if not already installed)
pip install -e .
```

### CLI Usage

```bash
# Basic usage (markdown only)
nexus-research "Physics-Informed Neural Networks for PDEs" --model openai:gpt-4o

# Generate with PDF (recommended for equations)
nexus-research "quantum error correction codes" --model openai:gpt-4o --pdf

# Specify report length
nexus-research "CRISPR gene editing" --length comprehensive --pdf

# Add context/style guidance
nexus-research "protein folding" \
  --model openai:gpt-4o \
  --length standard \
  --context "Follow Nature journal style. Focus on AlphaFold 3." \
  --pdf

# Output: output/research_reports/<topic_slug>/report_YYYY-MM-DD_HH-MM.md
```

**CLI Options:**
- `--model`: Model to use (default: `openai:gpt-4o-mini`)
- `--length`: Report length - `brief`, `standard`, `comprehensive`, `technical-paper`
- `--context`: Additional context or style guidance
- `--pdf`: Generate PDF with LaTeX equation rendering

### Web Interface

```bash
# Activate environment first
mamba activate agentic-ai

# Start the server
nexus-research-server

# Visit http://localhost:8004
```

**Alternative methods:**
```bash
# Using the start script (auto-activates environment)
./scripts/start_research_server.sh

# Or run directly with Python
python -m nexus.agents.research.server.app
```

**Stopping the server:**
```bash
# Using the stop script (graceful shutdown)
./scripts/stop_research_server.sh

# Or manually
lsof -ti:8004 | xargs kill -9
```

**Web Features:**
- Interactive form for research requests
- Real-time generation progress
- Automatic PDF generation with LaTeX equations
- Download markdown and PDF reports
- Browse previous reports
- View manifest metadata

### Python API

```python
from nexus.agents.research.pipeline import generate_research_report

# Basic usage
result = generate_research_report(
    topic="Quantum Computing trends 2025",
    model="openai:gpt-4o"
)

print(result["final_report"])
print(f"Generated in {result['generation_time']:.1f}s")

# With configuration
result = generate_research_report(
    topic="Machine Learning for Drug Discovery",
    model="openai:gpt-4o",
    report_length="comprehensive",
    context="Focus on recent breakthroughs in 2024-2025. Include case studies."
)
```

## Output Structure

Reports are saved in a standardized structure:

```
output/research_reports/
└── <topic_slug>/
    ├── report_2025-11-22_15-30.md   # Markdown report
    ├── report_2025-11-22_15-30.pdf  # PDF with rendered equations
    └── manifest.json                 # Metadata and tracking
```

**Manifest Contents:**
```json
{
  "topic_directory": "physics_informed_neural_networks",
  "created_at": "2025-11-22T15:30:00",
  "reports": [
    {
      "filename": "report_2025-11-22_15-30.md",
      "pdf_filename": "report_2025-11-22_15-30.pdf",
      "topic": "Physics-Informed Neural Networks for PDEs",
      "model": "openai:gpt-4o",
      "report_length": "standard",
      "generated_at": "2025-11-22T15:30:00",
      "generation_time_seconds": 263.3,
      "word_count": 2816,
      "plan_steps": 18
    }
  ]
}
```

## Report Lengths

| Length | Pages | Word Count | Use Case |
|--------|-------|------------|----------|
| **brief** | 2-3 | ~800-1200 | Quick overviews, summaries |
| **standard** | 5-10 | ~2500-4000 | Balanced depth and breadth |
| **comprehensive** | 15-25 | ~6000-10000 | In-depth analysis |
| **technical-paper** | 25-40 | ~10000-16000 | Publication-quality reports |

## PDF Generation

### LaTeX Equation Rendering

The Nexus Research Agent uses **pandoc with XeLaTeX** for professional PDF generation with proper mathematical typography:

**Before (weasyprint):**
```
\mathbf{u}(\mathbf{x}, t; \mathbf{\theta})  ← Raw LaTeX!
```

**After (pandoc):**
```
**u**(x, t; θ)  ← Beautiful rendered equations!
```

### Dependencies

PDF generation requires:
- `pandoc` (3.8+) - Installed via conda
- `pypandoc` - Python wrapper
- Automatically configured in `environment.yml`

## Configuration

### Environment Variables

Required API keys in `.env`:
```bash
OPENAI_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here  # Optional
GOOGLE_API_KEY=your-key-here     # Optional
```

### Model Support

Supported via `aisuite`:
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-5, gpt-5.1, o1, o4-mini
- **Anthropic**: claude-sonnet-4, claude-opus-4 (if configured)
- **Google**: gemini-2.5-flash (if configured)

## Advanced Features

### Context Guidance

Provide style templates and domain-specific instructions:

```bash
nexus-research "tumor growth modeling" \
  --context "Follow PLOS Computational Biology style. \
             Include: Abstract, Introduction, Methods, Results, Discussion. \
             Focus on reaction-diffusion PDEs. \
             Reference papers from 2024-2025."
```

### Manifest Tracking

Every report is automatically tracked:
- Generation timestamp
- Model used
- Report length
- Generation time
- Word count
- Plan steps executed
- PDF generation status

### Smart Slugs

Topic slugs are intelligently generated:
- Lowercase with underscores
- Stopwords removed
- Abbreviations preserved
- Consistent and readable

Examples:
- "Physics-Informed Neural Networks" → `physics_informed_neural_networks`
- "CRISPR Gene Editing in 2025" → `crispr_gene_editing_2025`
- "Quantum Error Correction Codes" → `quantum_error_correction_codes`

## Comparison with Legacy

### Nexus (Production) vs Legacy (Experimental)

| Feature | Nexus | Legacy |
|---------|-------|--------|
| **Status** | Production-ready | Experimental |
| **Location** | `src/nexus/` | `multiagent/`, `legacy/` |
| **CLI** | ✅ `nexus-research` | ❌ Manual scripts |
| **Web UI** | ✅ Port 8004 | ✅ Port 8000 |
| **PDF Generation** | ✅ LaTeX rendering | ❌ Not implemented |
| **Report Lengths** | ✅ 4 options | ❌ Fixed |
| **Context Guidance** | ✅ Yes | ❌ No |
| **Manifest Tracking** | ✅ Automatic | ❌ No |
| **Output Path** | ✅ Standardized | ❌ Variable |
| **Package Structure** | ✅ Proper package | ❌ Scripts |
| **Documentation** | ✅ Comprehensive | ⚠️ Basic |
| **Testing** | ✅ Tested | ⚠️ Minimal |

**Recommendation**: Use **Nexus** for production work. Use **Legacy** for experimentation and learning.

## Troubleshooting

### PDF Generation Issues

**Equations show raw LaTeX:**
```bash
# Verify pandoc is installed
mamba run -n agentic-ai which pandoc

# Check pypandoc
python -c "import pypandoc; print(pypandoc.get_pandoc_version())"
```

**PDF not generated:**
- Check server logs for errors
- Verify `--pdf` flag is used (CLI) or checkbox is checked (Web)
- Ensure pandoc is installed: `mamba install -c conda-forge pandoc`

### Output Path Issues

**Reports in wrong location:**
```python
# Verify configuration
from nexus.core.config import NexusConfig
print(NexusConfig.RESEARCH_REPORTS_DIR)
# Should output: /path/to/agentic-ai-lab/output/research_reports
```

### API Key Issues

**Missing API keys:**
- Create `.env` file in project root
- Add required keys (see Configuration section)
- Restart server if running

## Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **Report Configuration**: `docs/REPORT_LENGTH_CONFIGURATION.md`
- **Server Setup**: `server/QUICKSTART.md`
- **Main README**: `/README.md`

## Contributing

The Nexus Research Agent is part of the larger `agentic-ai-lab` project. Contributions are welcome!

**Priority Areas:**
- Additional tool integrations (Google Scholar, Semantic Scholar)
- Enhanced PDF formatting options
- Real-time progress tracking improvements
- Additional report templates
- Performance optimizations

## License

See repository license file for details.
