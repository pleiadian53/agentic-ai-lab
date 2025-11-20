# Migration Guide - Moving Splice Agent to New Project

This guide explains how to copy `splice_agent` to a new project directory while maintaining full functionality.

## 🎯 Goal

Move `splice_agent` from `agentic-ai-lab/splice_agent/` to a new standalone project (e.g., `bio-agentic-ai/splice_agent/` or `splice-agentic-ai/`).

## 📋 Prerequisites

- Python 3.9+
- Git (for version control)
- OpenAI API key

## 🚀 Migration Steps

### Step 1: Copy the Directory

```bash
# Option A: Copy to sibling directory
cp -r agentic-ai-lab/splice_agent /path/to/bio-agentic-ai/splice_agent

# Option B: Create new standalone project
mkdir splice-agentic-ai
cp -r agentic-ai-lab/splice_agent splice-agentic-ai/
```

### Step 2: Verify Structure

```bash
cd /path/to/new/location/splice_agent
ls -la

# You should see:
# - README.md
# - QUICKSTART.md
# - requirements.txt
# - .env.example
# - __init__.py
# - data_access.py
# - planning.py
# - llm_client.py
# - utils.py
# - splice_analysis.py
# - server/
# - examples/
# - data/
# - docs/
# - tests/
```

### Step 3: Set Up Environment

```bash
# Create new conda environment
mamba create -n splice-agent python=3.11
mamba activate splice-agent

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy and edit .env file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 5: Add Your Data

```bash
# Copy your splice site dataset to data/
cp /path/to/your/splice_sites_enhanced.tsv data/

# Or create a symlink
ln -s /path/to/your/data/splice_sites_enhanced.tsv data/
```

### Step 6: Test Installation

```bash
# Test Python import
python -c "from splice_agent import create_dataset; print('✓ Import successful')"

# Test API server
cd server
python splice_service.py

# In another terminal:
curl http://localhost:8004/health
# Should return: {"status":"healthy",...}
```

### Step 7: Run Examples

```bash
# Run quick start
python examples/quick_start.py

# Run full analysis
python -m splice_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis high_alternative_splicing
```

## ✅ Verification Checklist

- [ ] All files copied successfully
- [ ] Python environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API key
- [ ] Data files added to `data/` directory
- [ ] Python imports work (`from splice_agent import ...`)
- [ ] API server starts (`python server/splice_service.py`)
- [ ] Health check passes (`curl http://localhost:8004/health`)
- [ ] Examples run successfully (`python examples/quick_start.py`)

## 🔧 Customization

### Update Project Name

If you want to rename the package:

```bash
# 1. Rename directory
mv splice_agent your_new_name

# 2. Update imports in all Python files
find . -name "*.py" -type f -exec sed -i '' 's/splice_agent/your_new_name/g' {} +

# 3. Update __init__.py docstring
# Edit __init__.py and update the package description
```

### Add to Git

```bash
# Initialize git repository
git init

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Environment
.env
.env.local

# Data (optional - you may want to track small datasets)
data/*.tsv
data/*.csv
data/*.parquet

# Output
output/
*.pdf
*.png

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# Initial commit
git add .
git commit -m "Initial commit: Splice Agent standalone application"
```

### Connect to GitHub

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/splice-agentic-ai.git
git branch -M main
git push -u origin main
```

## 🎨 Extending Functionality

### Add New Analysis Template

Edit `splice_analysis.py`:

```python
ANALYSIS_TEMPLATES = {
    # ... existing templates ...
    
    "your_new_analysis": {
        "title": "Your Analysis Title",
        "description": "Description of what this analyzes",
        "data_query": """
            SELECT ...
            FROM splice_sites
            WHERE ...
        """,
        "chart_prompt": """
{context}

Create a chart showing...

CHART REQUIREMENTS:
- X-axis: ...
- Y-axis: ...
- ...
"""
    }
}
```

### Add New API Endpoint

Edit `server/splice_service.py`:

```python
@app.post("/your_endpoint")
async def your_endpoint(request: YourRequest):
    """Your endpoint description."""
    # Your logic here
    return YourResponse(...)
```

### Add New Data Source

Edit `data_access.py`:

```python
class YourDataset(ChartDataset):
    """Support for your data format."""
    
    def __init__(self, path: str):
        # Your initialization
        pass
    
    def get_schema_description(self) -> str:
        # Return schema description
        pass
    
    # Implement other required methods...
```

## 📦 Distribution

### Create Python Package

```bash
# Create setup.py
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="splice-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9",
)
EOF

# Install in development mode
pip install -e .
```

### Create Docker Container

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8004

CMD ["python", "server/splice_service.py"]
EOF

# Build and run
docker build -t splice-agent .
docker run -p 8004:8004 -e OPENAI_API_KEY=sk-... splice-agent
```

## 🔄 Keeping Up-to-Date

If you want to pull updates from the original `chart_agent`:

```bash
# Add original repo as remote
git remote add upstream https://github.com/original/agentic-ai-lab.git

# Fetch updates
git fetch upstream

# Merge specific files (be careful with conflicts)
git checkout upstream/main -- chart_agent/data_access.py
# Review changes and commit
```

## 🐛 Troubleshooting

### Import Errors After Migration

```bash
# Make sure you're in the right directory
cd /path/to/new/location

# Reinstall in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/new/location:$PYTHONPATH
```

### API Server Won't Start

```bash
# Check if port is in use
lsof -i :8004

# Use different port
# Edit server/splice_service.py or set in .env:
SPLICE_AGENT_PORT=8005
```

### Data Not Found

```bash
# Check paths are relative to project root
# NOT absolute paths
# Good: data/splice_sites_enhanced.tsv
# Bad: /full/path/to/data/splice_sites_enhanced.tsv
```

## 📚 Next Steps

1. **Customize for your needs** - Add domain-specific analyses
2. **Add tests** - Create unit tests in `tests/`
3. **Document your changes** - Update README.md
4. **Share with team** - Push to GitHub
5. **Deploy** - Set up production environment

## 🤝 Contributing Back

If you make improvements that could benefit others:

1. Fork the original `agentic-ai-lab` repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- **Original Chart Agent**: See `../chart_agent/README.md`
- **Splice Agent Issues**: Open issue in your new repository
- **Questions**: Check documentation or ask in discussions

---

**Success!** Your Splice Agent is now a standalone application ready for bio-agentic AI research! 🧬🚀
