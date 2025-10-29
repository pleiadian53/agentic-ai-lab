# Environment Setup Checklist

Quick verification checklist for the DeepLearning.AI Agentic AI course environment.

## Pre-Setup Requirements

- [ ] **Python 3.10+** installed
  ```bash
  python3 --version  # Should show 3.10.x or higher
  ```
  - ⚠️ **Current system**: Python 3.9.13 (needs upgrade)
  - **Action**: Install Python 3.11 via `brew install python@3.11` or pyenv

## Setup Steps

- [ ] **Virtual environment created**
  ```bash
  python3.11 -m venv .venv
  ```

- [ ] **Virtual environment activated**
  ```bash
  source .venv/bin/activate
  which python  # Should show .venv/bin/python
  ```

- [ ] **Dependencies installed**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Jupyter kernel configured** (optional)
  ```bash
  python -m ipykernel install --user --name=agentic-ai
  ```

## Verification Tests

Run these commands to verify your setup:

### 1. Check Installed Packages
```bash
pip list | grep -E "(aisuite|openai|fastapi|jupyter|pandas)"
```

Expected packages:
- aisuite (0.1.11)
- openai
- fastapi
- jupyter-server
- pandas
- anthropic
- mistralai
- tavily-python (>=0.7.12)

### 2. Test Core Imports
```bash
python -c "
import openai
import fastapi
import jupyter_server
import pandas
import aisuite
print('✅ All core packages imported successfully')
"
```

### 3. Test Notebook Support
```bash
jupyter --version
```

Should show versions for:
- jupyter_core
- jupyter-notebook
- jupyter_server

### 4. Check API Keys (if configured)
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'TAVILY_API_KEY']
for key in keys:
    status = '✅' if os.getenv(key) else '❌'
    print(f'{status} {key}')
"
```

## Environment Configuration

- [ ] **.env file created** with API keys
  ```bash
  touch .env
  ```

- [ ] **API keys configured** (at minimum):
  - `OPENAI_API_KEY` - For GPT models
  - `TAVILY_API_KEY` - For web search (optional but recommended)
  - `ANTHROPIC_API_KEY` - For Claude models (optional)
  - `MISTRAL_API_KEY` - For Mistral models (optional)

## Application Tests

- [ ] **FastAPI server starts**
  ```bash
  uvicorn main:app --reload
  # Should start on http://127.0.0.1:8000
  ```

- [ ] **Jupyter notebooks open**
  ```bash
  jupyter notebook
  # Should open browser with notebook interface
  ```

- [ ] **Can run course notebooks**
  - Open `M2_UGL_1.ipynb`
  - Select kernel: "Python (agentic-ai)"
  - Run first cell to verify imports

## Package Categories Verification

### Agent & LLM Tools
- [ ] aisuite==0.1.11
- [ ] anthropic
- [ ] docstring-parser
- [ ] markdown
- [ ] mistralai
- [ ] openai
- [ ] qrcode
- [ ] tavily-python>=0.7.12
- [ ] textstat
- [ ] vertexai

### Web Framework & API
- [ ] fastapi
- [ ] pydantic
- [ ] pydantic[email]
- [ ] python-dotenv
- [ ] python-multipart
- [ ] requests
- [ ] sqlalchemy
- [ ] uvicorn

### Notebook Experience
- [ ] ipywidgets
- [ ] jupyter_server
- [ ] nbclassic
- [ ] notebook

### Data Analysis
- [ ] duckdb
- [ ] matplotlib
- [ ] pandas
- [ ] seaborn
- [ ] tabulate
- [ ] tinydb

### ML/NLP
- [ ] jinja2
- [ ] psycopg2-binary
- [ ] scikit-learn
- [ ] wikipedia

### Additional
- [ ] pdfminer.six
- [ ] pymupdf

## Common Issues & Solutions

### Issue: Python version too old
**Solution**: Upgrade to Python 3.10+
```bash
brew install python@3.11
# or
pyenv install 3.11.7 && pyenv local 3.11.7
```

### Issue: Package installation fails
**Solution**: Install system dependencies
```bash
brew install postgresql pkg-config freetype
```

### Issue: Virtual environment not activating
**Solution**: Check shell and path
```bash
which python  # Should be in .venv
source .venv/bin/activate
```

### Issue: Jupyter kernel not found
**Solution**: Reinstall kernel
```bash
python -m ipykernel install --user --name=agentic-ai --force
```

## Quick Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Deactivate
deactivate

# Install/update packages
pip install -r requirements.txt

# Start FastAPI
uvicorn main:app --reload

# Start Jupyter
jupyter notebook

# Run automated setup
./scripts/install/setup-venv.sh
```

## Ready to Go? ✅

If all items are checked, you're ready to:
1. 🚀 Start the course labs
2. 📓 Open and run Jupyter notebooks
3. 🔧 Develop and test agentic workflows
4. 📚 Follow the learning roadmap in `AGENTIC_ROADMAP.md`

---

**Last Updated**: October 20, 2024
**Course**: DeepLearning.AI - Agentic AI
