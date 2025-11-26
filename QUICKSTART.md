# Nexus Research System - Quick Start Guide

**Get started with Nexus in 5 minutes!**

---

## 🚀 Installation

### Prerequisites

1. **Miniforge** (includes mamba package manager)
   ```bash
   brew install --cask miniforge
   ```
   Or visit: https://github.com/conda-forge/miniforge

2. **LaTeX Distribution** (for PDF generation with equations)
   - **macOS**: MacTeX or BasicTeX
   - **Linux**: TeX Live
   - **Windows**: MiKTeX or TeX Live
   
   See [LaTeX Setup Guide](#-latex-setup) below for details.

3. **API Keys** (at least one required)
   - OpenAI API key (recommended)
   - Anthropic API key (optional)
   - Google API key (optional)
   - Tavily API key (for web search)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-ai-lab.git
cd agentic-ai-lab

# Run setup script
./scripts/install/setup.sh

# Activate environment
mamba activate agentic-ai

# Install package
pip install -e .
```

### Configure API Keys

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

---

## 🎯 Using Nexus Research Agent

### CLI Usage

**Basic research report:**
```bash
nexus-research "Quantum Computing Applications in Drug Discovery"
```

**With options:**
```bash
nexus-research "CRISPR Gene Editing Advances" \
  --model openai:gpt-4o \
  --length comprehensive \
  --pdf
```

**Available options:**
- `--model`: Model to use (default: `openai:gpt-4o`)
  - `openai:gpt-4o` - Balanced quality (recommended)
  - `openai:gpt-4o-mini` - Fast & cheap (testing)
  - `openai:gpt-5*` - Maximum quality (when available)
- `--length`: Report length
  - `brief` - 2-3 pages
  - `standard` - 5-10 pages (default)
  - `comprehensive` - 15-25 pages
  - `technical-paper` - 25-40 pages
- `--pdf`: Generate PDF (requires LaTeX)
- `--context`: Additional context or style guidance

**Examples:**

```bash
# Quick test with cheap model
nexus-research "Neural Networks" --model openai:gpt-4o-mini --length brief

# Production report with equations
nexus-research "Maxwell's Equations in Electromagnetic Theory" --pdf

# Comprehensive technical paper
nexus-research "Transformer Architecture Evolution" \
  --length technical-paper \
  --context "Follow NeurIPS paper style" \
  --pdf
```

### Web Interface

**Start the server:**
```bash
# From project root
mamba activate agentic-ai
python -m nexus.agents.research.server.app
```

**Access the interface:**
Open http://localhost:8004 in your browser

**Features:**
- 📝 Interactive topic input
- 🎛️ Model and length selection
- ⏱️ Real-time progress tracking
- 📄 Markdown preview
- 📥 PDF download
- 📚 Browse previous reports

---

## 📄 LaTeX Setup

### Why LaTeX?

LaTeX is required for:
- ✅ **Mathematical equations** - Proper rendering of complex formulas
- ✅ **Publication quality** - Professional typesetting
- ✅ **Scientific notation** - Symbols, subscripts, superscripts
- ✅ **Beautiful PDFs** - Publication-ready output

### Installation by Platform

#### macOS

**Option 1: BasicTeX (Recommended - Smaller)**
```bash
brew install --cask basictex

# Add to PATH
eval "$(/usr/libexec/path_helper)"

# Install required packages
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended
sudo tlmgr install collection-latexextra
```

**Option 2: MacTeX (Complete - Larger)**
```bash
brew install --cask mactex-no-gui
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra
```

#### Windows

**Option 1: MiKTeX**
1. Download from https://miktex.org/download
2. Run installer
3. Add to PATH during installation

**Option 2: TeX Live**
1. Download from https://www.tug.org/texlive/
2. Run installer
3. Add `C:\texlive\2024\bin\windows` to PATH

### Verify Installation

```bash
# Check if xelatex is available
which xelatex

# Test compilation
xelatex --version
```

### Troubleshooting

**LaTeX not found:**
```bash
# macOS - Add to PATH
export PATH="/Library/TeX/texbin:$PATH"

# Linux - Usually automatic
# Windows - Check PATH includes TeX bin directory
```

**Missing packages:**
```bash
# macOS/Linux
sudo tlmgr install <package-name>

# Windows (MiKTeX) - Packages install automatically on first use
```

**Compilation errors:**
- Check `output/research_reports/<topic>/` for `.log` files
- Common issues: Missing fonts, special characters, complex equations
- See `src/nexus/agents/research/docs/installation/LATEX_SETUP.md` for detailed troubleshooting

---

## 📊 Output Structure

Generated reports are saved in:
```
output/research_reports/<topic-slug>/
├── report_YYYY-MM-DD_HH-MM.md      # Markdown source
├── report_YYYY-MM-DD_HH-MM.pdf     # PDF output (if --pdf used)
├── report_YYYY-MM-DD_HH-MM.tex     # LaTeX source (if applicable)
└── manifest.json                    # Metadata and tracking
```

**Manifest contains:**
- Topic and generation timestamp
- Model used and parameters
- Format decision and reasoning
- Word count and plan steps
- Source tracking

---

## 🎨 Example Workflows

### 1. Quick Research (Testing)

```bash
# Use cheap model for quick testing
nexus-research "Quantum Entanglement" \
  --model openai:gpt-4o-mini \
  --length brief
```

**Output:** Markdown report in ~30 seconds, minimal cost

### 2. Math-Heavy Topic (Production)

```bash
# Physics/Math topics need LaTeX
nexus-research "Schrödinger Equation and Wave Mechanics" \
  --model openai:gpt-4o \
  --length standard \
  --pdf
```

**Output:** PDF with properly rendered equations

### 3. Comprehensive Review (Publication)

```bash
# Detailed technical paper
nexus-research "Deep Learning for Protein Structure Prediction" \
  --model openai:gpt-4o \
  --length comprehensive \
  --context "Follow Nature Methods style, include recent AlphaFold advances" \
  --pdf
```

**Output:** 15-25 page technical paper with citations

### 4. Domain-Specific Research

```bash
# Computational biology
nexus-research "CRISPR-Cas9 Off-Target Effects and Mitigation Strategies" \
  --length technical-paper \
  --pdf

# AI/ML research
nexus-research "Transformer Attention Mechanisms: A Comprehensive Survey" \
  --context "Focus on recent innovations since 2023" \
  --pdf
```

---

## 🤝 Using Supporting Agents

### Chart Agent (Visualizations)

```bash
# Start Chart Agent server
python -m chart_agent.server.chart_service

# Access at http://localhost:8003/docs
```

**Integration:** Can be called by Nexus to generate figures

### SQL Agent (Data Queries)

```python
from reflection.sql_agent import sql_workflow

# Natural language to SQL
result = sql_workflow.execute("Show top 10 customers by revenue")
```

**Integration:** Enables Nexus to query research databases

### Splice Agent (Genomics)

```bash
# Start Splice Agent server
python -m splice_agent.server.splice_service

# Access at http://localhost:8004/docs
```

**Integration:** Specialized genomics analysis for biology research

---

## 🔧 Configuration

### Model Selection Strategy

| Use Case | Model | Cost | Quality | Speed |
|----------|-------|------|---------|-------|
| Testing/Drafts | `gpt-4o-mini` | $ | Good | Fast |
| Production | `gpt-4o` | $$$ | Excellent | Medium |
| Critical Research | `gpt-5*` | $$$$ | Best | Slower |

### Report Length Guidelines

| Length | Pages | Use Case | Time | Cost |
|--------|-------|----------|------|------|
| `brief` | 2-3 | Quick overview, testing | ~1 min | $ |
| `standard` | 5-10 | General research | ~2-3 min | $$ |
| `comprehensive` | 15-25 | Detailed review | ~5-7 min | $$$ |
| `technical-paper` | 25-40 | Publication-ready | ~10-15 min | $$$$ |

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Configuration
DEBUG=false
LOG_LEVEL=INFO
```

---

## 📚 Next Steps

### Learn More

- **Architecture:** See `ARCHITECTURE.md` for system design
- **Full Documentation:** `src/nexus/agents/research/README.md`
- **LaTeX Details:** `src/nexus/agents/research/docs/installation/LATEX_SETUP.md`
- **API Reference:** Start web server and visit `/docs`

### Explore Example Reports

The repository includes 4 example reports demonstrating Nexus capabilities:

**1. All-Atom Biomolecular Design** (`output/research_reports/all_atom_biomolecular_design/`)
- Cutting-edge 2025 AI/ML for molecular design (3,849 words, 25 steps, gpt-5.1)
- Covers RFdiffusion3, Boltz-2, AlphaFold3 breakthroughs
- Diffusion models, transformer architectures, drug discovery applications
- Demonstrates multi-source synthesis (arXiv, PubMed, web)

**2. AGI Consciousness & Sentience** (`output/research_reports/consciousness_sentience_agi/`)
- Methodological approaches to consciousness detection (3,833 words, 26 steps, gpt-5.1)
- Focuses on technical frameworks: IIT, Global Workspace Theory, Active Inference
- Empirical tests and measurement approaches
- Multi-source research with Reddit community insights

**3. Quantum Entanglement & Bell's Theorem** (`output/research_reports/quantum_entanglement_bell_theorem/`)
- Brief 709-word technical report with LaTeX equations (gpt-4o)
- Publication-quality PDF with proper mathematical notation
- Shows equation rendering capabilities

**4. Einstein's Field Equations** (`output/research_reports/einstein_field_equations_gravity/`)
- Physics report with tensor notation and LaTeX compilation (gpt-4o)
- Variable definitions and physical interpretations
- Demonstrates advanced equation handling

```bash
# Browse all example reports
ls output/research_reports/

# View example PDFs
open output/research_reports/all_atom_biomolecular_design/report_*.pdf
open output/research_reports/consciousness_sentience_agi/report_*.pdf
open output/research_reports/quantum_entanglement_bell_theorem/report_*.pdf

# Read the markdown source
cat output/research_reports/all_atom_biomolecular_design/report_*.md
```

### Customize

- **Style Transfer:** Add example papers to `data/papers/`
- **Templates:** Modify templates in `src/nexus/templates/`
- **Prompts:** Adjust prompts in `src/nexus/agents/research/format_decision.py`

### Get Help

- **Issues:** Check `dev/nexus/` for troubleshooting guides
- **Logs:** Check `output/logs/` for detailed logs
- **Community:** (Add your community links here)

---

## 🚀 Roadmap Features

Coming soon:
- [ ] **Style Transfer** - Use example papers as templates
- [ ] **Paper2Code** - Generate implementations alongside research
- [ ] **GitHub Discovery** - Find and analyze paper repositories
- [ ] **Enhanced Web UI** - Progress tracking, cost estimation
- [ ] **Interactive Refinement** - Iterative improvement with feedback

---

## ⚡ Tips & Tricks

### Performance

```bash
# Use cheaper model for initial drafts
nexus-research "Topic" --model openai:gpt-4o-mini

# Then refine with better model
nexus-research "Topic" --model openai:gpt-4o --pdf
```

### Cost Optimization

- Start with `brief` length for testing
- Use `gpt-4o-mini` for non-critical reports
- Save `gpt-5*` for publication-ready work

### Quality

- Provide specific context for better results
- Math/science topics benefit from `--pdf` flag
- Longer reports have more depth but cost more

### Troubleshooting

**LaTeX compilation fails:**
```bash
# Check LaTeX installation
which xelatex

# View compilation logs
cat output/research_reports/<topic>/report_*.log
```

**API errors:**
```bash
# Verify API keys
echo $OPENAI_API_KEY

# Check .env file
cat .env
```

**Import errors:**
```bash
# Reinstall package
pip install -e .

# Verify installation
python -c "import nexus; print(nexus.__file__)"
```

---

**Ready to generate your first research report?** 🚀

```bash
nexus-research "Your Fascinating Topic Here" --pdf
```
