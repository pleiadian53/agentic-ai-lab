#!/bin/bash
# Agentic AI Environment Setup
# Creates and configures the agentic-ai conda environment using mamba

set -e

echo "🚀 Agentic AI Environment Setup"
echo "================================"
echo ""

# Initialize conda/mamba if not already available
if ! command -v mamba &> /dev/null; then
    # Try to source conda initialization
    if [ -f "$HOME/miniforge3-new/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniforge3-new/etc/profile.d/conda.sh"
    elif [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniforge3/etc/profile.d/conda.sh"
    else
        echo "❌ Error: mamba not found"
        echo ""
        echo "Please install Miniforge first:"
        echo "  https://github.com/conda-forge/miniforge"
        echo ""
        echo "Or run: brew install --cask miniforge"
        exit 1
    fi
fi

# Verify mamba is now available
if ! command -v mamba &> /dev/null; then
    echo "❌ Error: Could not initialize mamba"
    echo ""
    echo "Please ensure Miniforge is properly installed and initialized."
    echo "Run: conda init zsh"
    exit 1
fi

echo "✅ Using mamba $(mamba --version)"
echo ""

# Check if environment already exists
if mamba env list | grep -q "^agentic-ai "; then
    echo "⚠️  Environment 'agentic-ai' already exists"
    read -p "Do you want to remove and recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        mamba env remove -n agentic-ai -y
    else
        echo "Keeping existing environment. Run 'mamba activate agentic-ai' to use it."
        exit 0
    fi
fi

# Create environment
echo "📦 Creating environment from environment.yml..."
echo "   (This may take a few minutes...)"
echo ""

mamba env create -f environment.yml

# Verify installation
echo ""
echo "🔍 Verifying installation..."

# Activate environment and check key packages
eval "$(conda shell.bash hook)"
conda activate agentic-ai

# Check key packages
PACKAGES=("openai" "fastapi" "jupyter_server" "pandas" "aisuite")
for pkg in "${PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        echo "  ✅ $pkg"
    else
        echo "  ❌ $pkg (failed to import)"
    fi
done

echo ""
echo "✅ All key packages verified!"

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
echo ""
