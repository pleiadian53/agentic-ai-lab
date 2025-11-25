# Nexus Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip or conda package manager
- Git (for cloning the repository)

## Installation Methods

### Method 1: Mamba/Conda Environment (Recommended)

This project uses **mamba** (or conda) for environment management and **poetry/pip** for package installation.

```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-ai-lab.git
cd agentic-ai-lab

# Create and activate the environment from environment.yml
mamba env create -f environment.yml
mamba activate agentic-ai

# Install the package in editable mode
pip install -e .
```

**Benefits**:
- Consistent environment across team
- All system dependencies included
- Code changes take effect immediately
- Perfect for development

### Method 2: Poetry (Alternative)

If you prefer poetry for dependency management:

```bash
# Install with poetry
poetry install

# Activate the virtual environment
poetry shell

# Or run commands directly
poetry run nexus-research --help
```

### Method 3: Standard pip Install

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

### Method 4: Install with Optional Dependencies

```bash
# Install with development tools
pip install -e ".[dev]"

# Install with all optional dependencies
pip install -e ".[dev,test,docs]"
```

## Verify Installation

After installation, verify that Nexus is properly installed:

```bash
# Test imports
python -c "from nexus.core.config import NexusConfig; print('✓ Nexus installed successfully')"

# Test CLI
nexus-research --help

# Or using Python module
python -m nexus.cli.research --help
```

## Configuration

### API Keys

Set up your API keys as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="your-key-here"

# Anthropic (optional)
export ANTHROPIC_API_KEY="your-key-here"

# Google (optional)
export GOOGLE_API_KEY="your-key-here"
```

Or create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

### Directory Structure

After installation, Nexus will create the following directories:

```
agentic-ai-lab/
├── output/
│   ├── nexus/           # Nexus platform outputs
│   └── research_reports/ # Research agent reports
├── data/                # Data files
└── src/nexus/
    ├── templates/papers/ # Template papers
    └── ...
```

## Dependencies

### Core Dependencies

Automatically installed with Nexus:

- **aisuite** - Multi-provider LLM client
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **jinja2** - Template engine
- **markdown** - Markdown processing
- **weasyprint** - PDF generation
- **beautifulsoup4** - HTML parsing
- **requests** - HTTP client

### Optional Dependencies

Install as needed:

- **pypandoc** - Alternative PDF generation
- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Linting
- **mkdocs** - Documentation generation

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'nexus'`:

```bash
# Make sure you're in the project root
cd /path/to/agentic-ai-lab

# Reinstall in editable mode
pip install -e .

# Or set PYTHONPATH temporarily
export PYTHONPATH=/path/to/agentic-ai-lab/src
```

### LaTeX Engine Setup (For Equation Rendering in PDFs)

The Research Agent generates reports with mathematical equations in LaTeX format. To render these properly in PDFs, you need a LaTeX engine.

> **Note:** This is for Nexus Research Agent only. If you're using `scripts/sync_work.py` for backup/mobile reading, see `scripts/SYNC_SETUP.md` for different requirements.

#### Option 1: Tectonic (Recommended - Already Included)

Tectonic is a modern, self-contained LaTeX engine that's already included in the conda environment:

```bash
# Verify Tectonic is installed
mamba run -n agentic-ai tectonic --version

# If not installed, add it:
mamba install -n agentic-ai -c conda-forge tectonic
```

**Benefits**:
- ✅ Self-contained - downloads packages automatically
- ✅ Fast - single-pass compilation
- ✅ No system dependencies required
- ✅ Works across all platforms

#### Option 2: System-Wide LaTeX (Alternative)

If you prefer a full LaTeX distribution:

**macOS**:
```bash
# Install MacTeX (full) or BasicTeX (minimal)
brew install --cask mactex        # Full (~4GB)
# OR
brew install --cask basictex      # Minimal (~100MB)

# Add to PATH
export PATH="/Library/TeX/texbin:$PATH"
```

**Ubuntu/Debian**:
```bash
# Install TeX Live
sudo apt-get install texlive-xetex texlive-latex-extra texlive-fonts-recommended
```

**Windows**:
```bash
# Install MiKTeX
# Download from: https://miktex.org/download
```

#### Verifying LaTeX Installation

Test that LaTeX compilation works:

```bash
# Test with Tectonic (in conda environment)
mamba run -n agentic-ai tectonic --help

# Test with system LaTeX
xelatex --version
# OR
pdflatex --version
```

### PDF Generation Troubleshooting

#### Issue: PDF Shows Raw LaTeX Code

**Symptoms**: PDF displays `\documentclass`, `\begin{document}`, etc. instead of rendered content.

**Cause**: LaTeX engine not available or not being used correctly.

**Solution**:
1. Verify Tectonic is installed:
   ```bash
   mamba list -n agentic-ai | grep tectonic
   ```

2. If missing, install it:
   ```bash
   mamba install -n agentic-ai -c conda-forge tectonic
   ```

3. Restart the research server:
   ```bash
   ./scripts/stop_research_server.sh
   ./scripts/start_research_server.sh
   ```

4. Check server logs for:
   ```
   Detected LaTeX format, using LaTeX compiler...
   ✓ PDF generated using Tectonic: ...
   ```

#### Issue: Tectonic Compilation Fails

**Symptoms**: Error message "Tectonic compilation failed"

**Solutions**:

1. **Check internet connection** - Tectonic downloads packages on first use
2. **Clear Tectonic cache**:
   ```bash
   rm -rf ~/.cache/Tectonic
   ```
3. **Try manual compilation**:
   ```bash
   # Test with a simple LaTeX file
   echo '\documentclass{article}\begin{document}Hello\end{document}' > test.tex
   mamba run -n agentic-ai tectonic test.tex
   ```

#### Issue: Equations Not Rendering

**Symptoms**: Equations appear as plain text or show errors

**Common Causes**:
1. Missing LaTeX packages (Tectonic auto-downloads these)
2. Invalid LaTeX syntax in equations
3. Using markdown converter instead of LaTeX compiler

**Solutions**:

1. **Verify format detection**:
   - Check that report starts with `\documentclass`
   - Server logs should show "Detected LaTeX format"

2. **Test equation syntax**:
   ```latex
   % Inline math
   $E = mc^2$
   
   % Display math
   $$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
   ```

3. **Check server logs** for compilation errors:
   ```bash
   # View logs in real-time
   tail -f /path/to/server/logs
   ```

#### Issue: "xelatex not found" Error

**Cause**: System LaTeX not in PATH (only relevant if not using Tectonic)

**Solution**:
```bash
# macOS - Add MacTeX to PATH
export PATH="/Library/TeX/texbin:$PATH"
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc

# Linux - Install TeX Live
sudo apt-get install texlive-xetex

# Verify
which xelatex
```

#### Testing PDF Generation

Test the complete pipeline:

```bash
# Generate a test report with equations
nexus-research "quantum mechanics and Schrödinger equation" \
  --length brief \
  --pdf

# Check the output
ls -lh output/research_reports/*/report_*.pdf
```

**Expected output**:
- PDF file created successfully
- Equations rendered properly (not raw LaTeX)
- Professional formatting with proper fonts

### WeasyPrint Issues (Fallback for Markdown PDFs)

WeasyPrint is used for markdown-to-PDF conversion (without equations). It requires system dependencies:

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Ubuntu/Debian**:
```bash
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Windows**:
```bash
# Use GTK+ runtime
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

### Permission Errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Uninstallation

To uninstall Nexus:

```bash
pip uninstall nexus-ai
```

Note: This removes the package but keeps your configuration and output files.

## Updating

To update Nexus after pulling new changes:

```bash
# Pull latest changes
git pull

# Reinstall (if dependencies changed)
pip install -e .

# Or just continue using (if only code changed)
# Editable install automatically uses latest code
```

## Next Steps

After installation:

1. [Quick Start Guide](getting_started.md) - Your first research task
2. [Architecture Overview](architecture.md) - Understanding Nexus
3. [Agent Documentation](agents/overview.md) - Available agents

## Support

For issues and questions:

- Check [Troubleshooting](#troubleshooting) section
- Review [GitHub Issues](https://github.com/yourusername/agentic-ai-lab/issues)
- Consult [Documentation](README.md)
