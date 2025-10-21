#!/bin/bash
# Mamba/Conda Environment Setup Script for Agentic AI Course
# Usage: ./setup-mamba.sh

set -e  # Exit on error

echo "🚀 Agentic AI Environment Setup (Mamba/Conda)"
echo "=============================================="
echo ""

# Check if mamba is installed
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    echo "✅ Using mamba (faster)"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
    echo "✅ Using conda"
else
    echo "❌ Neither mamba nor conda found!"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "Option 1: Install Miniforge (includes mamba):"
    echo "  brew install miniforge"
    echo "  conda init zsh"
    echo "  # Restart your terminal"
    echo ""
    echo "Option 2: Install Miniconda, then mamba:"
    echo "  brew install miniconda"
    echo "  conda init zsh"
    echo "  # Restart terminal, then:"
    echo "  conda install -n base -c conda-forge mamba"
    echo ""
    echo "Option 3: Install Mambaforge directly:"
    echo "  curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-arm64.sh"
    echo "  bash Mambaforge-MacOSX-arm64.sh"
    echo ""
    exit 1
fi

echo "Using: $CONDA_CMD"
echo ""

# Check if environment already exists
if $CONDA_CMD env list | grep -q "^agentic-ai "; then
    echo "⚠️  Environment 'agentic-ai' already exists"
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        $CONDA_CMD env remove -n agentic-ai -y
    else
        echo "Updating existing environment..."
        $CONDA_CMD env update -n agentic-ai -f environment.yml --prune
        echo ""
        echo "✅ Environment updated!"
        echo ""
        echo "To activate: conda activate agentic-ai"
        exit 0
    fi
fi

# Create environment from environment.yml
echo "📦 Creating environment from environment.yml..."
echo "   (This may take a few minutes...)"
$CONDA_CMD env create -f environment.yml

echo ""
echo "✅ Environment created successfully!"
echo ""

# Activate and verify
echo "🔍 Verifying installation..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate agentic-ai

# Verify key packages
python -c "
import sys
packages = ['openai', 'fastapi', 'jupyter_server', 'pandas', 'aisuite']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ❌ {pkg}')
        missing.append(pkg)

if missing:
    print(f'\n⚠️  Some packages failed to import: {missing}')
    sys.exit(1)
else:
    print('\n✅ All key packages verified!')
"

# Install Jupyter kernel
echo ""
echo "📓 Installing Jupyter kernel..."
python -m ipykernel install --user --name=agentic-ai --display-name="Python (agentic-ai)"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment: mamba activate agentic-ai"
echo "  2. Create .env file with your API keys (see docs/ENVIRONMENT_SETUP.md)"
echo "  3. Run the app: uvicorn main:app --reload"
echo "  4. Or start Jupyter: jupyter notebook"
echo ""
echo "📖 See docs/ENVIRONMENT_SETUP.md for more details"
echo ""
echo "💡 Tip: To deactivate, run: mamba deactivate"
