# Environment Setup Guide

This guide covers the local development environment setup for the DeepLearning.AI Agentic AI course labs.

## Recommended Approach: Mamba/Conda 🚀

**We recommend using mamba (or conda) for environment management** as it:
- ✅ Handles Python version automatically
- ✅ Resolves dependencies more reliably
- ✅ Works better with scientific/ML packages
- ✅ Faster than pip (especially mamba)
- ✅ Isolates environments completely

**Quick Start with Mamba:**
```bash
# If you have mamba/conda installed:
./scripts/install/setup-mamba.sh

# Or manually:
mamba env create -f environment.yml
mamba activate agentic-ai
```

See [Mamba/Conda Setup](#mambaconda-setup-recommended) below for details.

**Alternative:** If you prefer pip, see [Pip/Venv Setup](#pipvenv-setup-alternative) below.

---

## Prerequisites

### Python Version Requirement
- **Required**: Python 3.10 or higher
- **Current System**: Python 3.9.13 ⚠️

### Action Required: Upgrade Python

You need to upgrade to Python 3.10+ before proceeding. Here are the recommended options:

#### Option 1: Install Python 3.11 via Homebrew (Recommended for macOS)
```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version

# Create an alias (optional, add to ~/.zshrc)
alias python3=python3.11
```

#### Option 2: Use pyenv for Python Version Management
```bash
# Install pyenv if not already installed
brew install pyenv

# Install Python 3.11
pyenv install 3.11.7

# Set as local version for this project
cd /Users/pleiadian53/work/agentic-ai-lab
pyenv local 3.11.7

# Verify
python --version
```

#### Option 3: Download from python.org
Visit https://www.python.org/downloads/ and install Python 3.11+

---

## Mamba/Conda Setup (Recommended)

### Why Mamba/Conda?

- **No Python version hassle**: Automatically installs Python 3.11
- **Better dependency resolution**: Handles complex scientific packages
- **Faster**: Mamba is significantly faster than pip
- **Reproducible**: Cross-platform environment files
- **Isolated**: Complete environment isolation

### Install Mamba/Conda

If you don't have mamba or conda installed:

#### Option 1: Miniforge (Recommended - includes mamba)

```bash
# Install via Homebrew
brew install miniforge

# Initialize for zsh
conda init zsh

# Restart your terminal
```

#### Option 2: Mambaforge (Direct install)

```bash
# Download and install
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh
bash Mambaforge-MacOSX-arm64.sh

# Follow prompts, then restart terminal
```

#### Option 3: Add mamba to existing conda

```bash
# If you already have conda
conda install -n base -c conda-forge mamba
```

### Create Environment

#### Automated Setup (Recommended)

```bash
# Navigate to project
cd /Users/pleiadian53/work/agentic-ai-lab

# Run setup script
./scripts/install/setup-mamba.sh
```

The script will:
1. Check for mamba/conda
2. Create environment from `environment.yml`
3. Install all dependencies
4. Configure Jupyter kernel
5. Verify installation

#### Manual Setup

```bash
# Create environment from environment.yml
mamba env create -f environment.yml

# Activate environment
mamba activate agentic-ai

# Verify installation
python --version  # Should show 3.11.x

# Install Jupyter kernel
python -m ipykernel install --user --name=agentic-ai --display-name="Python (agentic-ai)"
```

### Managing the Environment

```bash
# Activate environment
mamba activate agentic-ai

# Deactivate
mamba deactivate

# Update environment (after changing environment.yml)
mamba env update -f environment.yml --prune

# Remove environment
mamba env remove -n agentic-ai

# List all environments
conda env list

# Export environment (for sharing)
conda env export > environment-lock.yml
```

### Verify Installation

```bash
# Activate environment
mamba activate agentic-ai

# Check installed packages
mamba list

# Test key imports
python -c "import openai, fastapi, jupyter_server, pandas, aisuite; print('✅ All packages working!')"
```

---

## Pip/Venv Setup (Alternative)

If you prefer traditional pip and venv, or need compatibility with existing workflows:

### Prerequisites

You need Python 3.10+ installed (see [Prerequisites](#prerequisites) above).

### Virtual Environment Setup

Once you have Python 3.10+, follow these steps:

### 1. Create Virtual Environment

```bash
# Navigate to project directory
cd /Users/pleiadian53/work/agentic-ai-lab

# Create virtual environment (use python3.11 or your installed version)
python3.11 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Verify you're in the virtual environment
which python
# Should show: /Users/pleiadian53/work/agentic-ai-lab/.venv/bin/python
```

### 2. Upgrade pip

```bash
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- **Agent & LLM Tools**: aisuite, anthropic, openai, mistralai, tavily-python, etc.
- **Web Framework**: FastAPI, uvicorn, pydantic, sqlalchemy
- **Notebook Experience**: jupyter, ipywidgets, notebook
- **Data Analysis**: pandas, matplotlib, seaborn, duckdb
- **ML/NLP Tools**: scikit-learn, wikipedia, textstat

### 4. Verify Installation

```bash
# Check installed packages
pip list

# Test key imports
python -c "import openai; import fastapi; import jupyter_server; print('✅ Core packages imported successfully')"
```

---

## IDE/Jupyter Integration (Optional)

### Link Virtual Environment to Jupyter

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Install ipykernel
pip install ipykernel

# Add the virtual environment as a Jupyter kernel
python -m ipykernel install --user --name=agentic-ai --display-name="Python (agentic-ai)"
```

### VS Code Setup

If using VS Code:
1. Open Command Palette (`Cmd+Shift+P`)
2. Select "Python: Select Interpreter"
3. Choose `.venv/bin/python`

### PyCharm Setup

If using PyCharm:
1. Go to Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Browse to `.venv/bin/python`

---

## Environment Variables

Create a `.env` file in the project root for API keys:

```bash
# Copy template (if exists) or create new
touch .env
```

Add your API keys:
```env
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Mistral
MISTRAL_API_KEY=your_mistral_key_here

# Tavily (Web Search)
TAVILY_API_KEY=your_tavily_key_here

# Google Vertex AI (if using)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

**Note**: The `.env` file should already be in `.gitignore` to prevent committing secrets.

---

## Running the Application

### Start FastAPI Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload

# Or specify host and port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Jupyter Notebooks
```bash
# Activate virtual environment
source .venv/bin/activate

# Start Jupyter
jupyter notebook

# Or use Jupyter Lab
jupyter lab
```

---

## Troubleshooting

### Issue: `pip install` fails for some packages

**Solution**: Some packages may require system dependencies:

```bash
# For psycopg2-binary (PostgreSQL)
brew install postgresql

# For matplotlib
brew install pkg-config freetype

# For vertexai
pip install --upgrade google-cloud-aiplatform
```

### Issue: Import errors after installation

**Solution**: Ensure you're using the correct Python interpreter:
```bash
# Check which Python you're using
which python

# Should point to .venv/bin/python
# If not, reactivate the virtual environment
deactivate
source .venv/bin/activate
```

### Issue: Jupyter kernel not found

**Solution**: Reinstall the kernel:
```bash
source .venv/bin/activate
python -m ipykernel install --user --name=agentic-ai --display-name="Python (agentic-ai)" --force
```

---

## Quick Reference Commands

```bash
# Activate environment
source .venv/bin/activate

# Deactivate environment
deactivate

# Update dependencies
pip install -r requirements.txt --upgrade

# Freeze current environment
pip freeze > requirements-frozen.txt

# Run tests (when added)
pytest -v

# Start development server
uvicorn main:app --reload
```

---

## Next Steps

After completing the setup:

1. ✅ Verify Python 3.10+ is installed
2. ✅ Create and activate virtual environment
3. ✅ Install all dependencies from requirements.txt
4. ✅ Configure API keys in .env
5. ✅ Link environment to your IDE/Jupyter
6. 🚀 Start exploring the course labs!

Refer to `AGENTIC_ROADMAP.md` for the learning path and enhancement ideas.
