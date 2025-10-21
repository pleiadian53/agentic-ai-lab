#!/bin/bash
# Environment Setup Script for Agentic AI Course
# Usage: ./setup.sh

set -e  # Exit on error

echo "🚀 Agentic AI Environment Setup"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is below required $REQUIRED_VERSION"
    echo ""
    echo "Please upgrade Python first. Options:"
    echo "  1. brew install python@3.11"
    echo "  2. pyenv install 3.11.7 && pyenv local 3.11.7"
    echo ""
    echo "See docs/ENVIRONMENT_SETUP.md for detailed instructions."
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION meets requirements"
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists at .venv"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf .venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
echo "   (This may take a few minutes...)"
pip install -r requirements.txt --quiet

echo ""
echo "✅ Installation complete!"
echo ""

# Verify key packages
echo "🔍 Verifying key packages..."
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

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment: source .venv/bin/activate"
echo "  2. Create .env file with your API keys (see docs/ENVIRONMENT_SETUP.md)"
echo "  3. Run the app: uvicorn main:app --reload"
echo "  4. Or start Jupyter: jupyter notebook"
echo ""
echo "📖 See docs/ENVIRONMENT_SETUP.md for more details"
