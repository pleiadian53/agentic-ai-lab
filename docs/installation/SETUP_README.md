# Quick Setup Guide

This is the quick-start guide for setting up your local environment for the DeepLearning.AI Agentic AI course.

## 🚀 Recommended: Mamba/Conda Setup

**We recommend using mamba/conda** as it:
- ✅ Handles Python version automatically (no upgrade needed!)
- ✅ Faster and more reliable dependency resolution
- ✅ Better for ML/data science projects

### Quick Start with Mamba

```bash
# 1. Install miniforge (includes mamba)
brew install miniforge
conda init zsh
# Restart terminal

# 2. Run automated setup
./scripts/install/setup-mamba.sh

# 3. Activate environment
conda activate agentic-ai

# 4. Verify
python --version  # Should show 3.11.x
```

**That's it!** Python 3.11 is installed automatically by mamba.

## 📖 Alternative: Pip/Venv Setup

If you prefer traditional pip/venv:

### ⚠️ Important: Python Version

**You need Python 3.10 or higher**. Your system currently has Python 3.9.13.

**Upgrade Python First:**

```bash
# Option 1: Homebrew
brew install python@3.11

# Option 2: pyenv
brew install pyenv
pyenv install 3.11.7
cd /Users/pleiadian53/work/agentic-ai-lab
pyenv local 3.11.7
```

### Automated Setup

After upgrading Python:

```bash
./scripts/install/setup-venv.sh
```

### Manual Setup

```bash
# 1. Create virtual environment
python3.11 -m venv .venv

# 2. Activate it
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure Jupyter (optional)
python -m ipykernel install --user --name=agentic-ai
```

## 🔑 Configure API Keys

Create a `.env` file:

```bash
touch .env
```

Add your keys:
```env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here  # Optional
ANTHROPIC_API_KEY=your_key_here  # Optional
```

## ✅ Verify Setup

```bash
# Activate environment
source .venv/bin/activate

# Test imports
python -c "import openai, fastapi, jupyter_server; print('✅ Setup successful!')"

# Start the app
uvicorn main:app --reload

# Or start Jupyter
jupyter notebook
```

## 📚 Documentation

- **Detailed Setup**: `docs/ENVIRONMENT_SETUP.md`
- **Checklist**: `docs/SETUP_CHECKLIST.md`
- **Learning Roadmap**: `docs/AGENTIC_ROADMAP.md`
- **Status**: `dev/SETUP_STATUS.md`

## 🆘 Need Help?

See `docs/ENVIRONMENT_SETUP.md` for:
- Detailed installation instructions
- Troubleshooting guide
- IDE integration
- Common issues and solutions

---

**Ready to start?** Follow the steps above, then check out the learning roadmap! 🎓
