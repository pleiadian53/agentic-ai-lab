# Mamba/Conda vs Pip/Venv: Setup Comparison

This document explains why we recommend mamba/conda for this project and when you might prefer pip/venv.

## Quick Comparison

| Feature | Mamba/Conda | Pip/Venv |
|---------|-------------|----------|
| **Python Version** | Installs automatically | Must install separately |
| **Speed** | Very fast (mamba) | Slower |
| **Dependency Resolution** | Better (SAT solver) | Basic |
| **Binary Packages** | Pre-compiled | Often needs compilation |
| **Scientific Packages** | Optimized | Standard |
| **Cross-platform** | Excellent | Good |
| **Disk Space** | More (separate envs) | Less (shared libs) |
| **Learning Curve** | Moderate | Easy |

## Why Mamba/Conda for This Project?

### 1. **No Python Version Hassle**

**Mamba/Conda:**
```bash
mamba env create -f environment.yml  # Python 3.11 installed automatically
conda activate agentic-ai
```

**Pip/Venv:**
```bash
# First, upgrade Python manually
brew install python@3.11  # or use pyenv
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. **Better Dependency Resolution**

Mamba/conda uses a SAT solver to resolve dependencies, which is especially important for:
- Scientific packages (numpy, pandas, scipy)
- ML libraries (scikit-learn, tensorflow, pytorch)
- Complex dependency chains

Pip can sometimes install incompatible versions that only fail at runtime.

### 3. **Pre-compiled Binaries**

Many packages (especially scientific ones) are pre-compiled in conda-forge:
- **psycopg2**: No need for PostgreSQL dev headers
- **pymupdf**: No need for system libraries
- **matplotlib**: No need for freetype, libpng, etc.

With pip, these often require system dependencies or compilation.

### 4. **Speed**

**Mamba** is significantly faster than both conda and pip:
- Parallel downloads
- Efficient dependency resolution
- Optimized package extraction

### 5. **Environment Isolation**

Conda environments are completely isolated:
- Separate Python interpreter
- No system Python conflicts
- Can have multiple Python versions simultaneously

## When to Use Pip/Venv

### Good Use Cases for Pip/Venv:

1. **Simple Python-only projects**
   - No scientific/ML dependencies
   - Pure Python packages

2. **CI/CD pipelines**
   - Faster Docker builds (smaller base images)
   - Simpler deployment

3. **Existing pip workflows**
   - Team already uses pip
   - Existing requirements.txt files

4. **Minimal installations**
   - Limited disk space
   - Only need specific packages

5. **Latest package versions**
   - Need bleeding-edge packages
   - Package not yet in conda-forge

## Our Setup: Best of Both Worlds

We provide **both** options:

### Primary: Mamba/Conda
- `environment.yml` - Full environment specification
- `setup-mamba.sh` - Automated setup script
- Recommended for course work

### Fallback: Pip/Venv
- `requirements.txt` - Pip package list
- `setup.sh` - Automated setup script
- For compatibility and CI/CD

## File Comparison

### environment.yml (Mamba/Conda)

```yaml
name: agentic-ai
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas
  - scikit-learn
  - pip:
    - aisuite==0.1.11  # Not in conda-forge
    - tavily-python>=0.7.12
```

**Advantages:**
- Specifies Python version
- Uses conda-forge channel (optimized packages)
- Can mix conda and pip packages
- Environment name included

### requirements.txt (Pip)

```txt
pandas
scikit-learn
aisuite==0.1.11
tavily-python>=0.7.12
```

**Advantages:**
- Simpler format
- Universal (works everywhere)
- Smaller file
- Easier to read

## Migration Between Methods

### From Mamba to Pip

```bash
# Export from conda environment
conda activate agentic-ai
pip freeze > requirements-frozen.txt

# Use in pip
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-frozen.txt
```

### From Pip to Mamba

```bash
# Create environment.yml from requirements.txt
# (Manual process - categorize packages)

# Or use existing environment.yml
mamba env create -f environment.yml
```

## Performance Comparison

### Installation Time (Approximate)

| Method | Time | Notes |
|--------|------|-------|
| Mamba | 2-3 min | Pre-compiled binaries |
| Conda | 5-8 min | Slower solver |
| Pip | 5-10 min | May need compilation |

### Disk Space

| Method | Space | Notes |
|--------|-------|-------|
| Mamba/Conda | ~2-3 GB | Includes Python + packages |
| Pip/Venv | ~500 MB - 1 GB | Uses system Python |

## Recommendations by Use Case

### For This Course (Agentic AI)
**Use: Mamba/Conda** ✅
- Handles Python version automatically
- Better for Jupyter notebooks
- Optimized scientific packages
- Easier for beginners

### For Production Deployment
**Use: Pip/Venv or Docker** ✅
- Smaller Docker images
- Faster CI/CD
- More control over dependencies

### For Team Development
**Use: Both** ✅
- `environment.yml` for development
- `requirements.txt` for CI/CD
- Best of both worlds

## Common Issues

### Mamba/Conda Issues

**Issue**: Package not in conda-forge
**Solution**: Add to pip section in environment.yml

**Issue**: Slow environment creation
**Solution**: Use mamba instead of conda

**Issue**: Environment conflicts
**Solution**: Create separate environments per project

### Pip Issues

**Issue**: Compilation errors
**Solution**: Install system dependencies or use conda

**Issue**: Dependency conflicts
**Solution**: Use pip-tools or poetry for better resolution

**Issue**: Python version mismatch
**Solution**: Use pyenv or upgrade system Python

## Conclusion

For this **Agentic AI course project**, we recommend:

1. **Primary**: Use mamba/conda (`environment.yml`)
   - Easier setup
   - Better for learning
   - Handles Python version

2. **Fallback**: Keep pip/venv (`requirements.txt`)
   - For compatibility
   - For CI/CD
   - For deployment

Both methods are fully supported and documented!

## Resources

- **Mamba**: https://mamba.readthedocs.io/
- **Conda**: https://docs.conda.io/
- **Conda-forge**: https://conda-forge.org/
- **Pip**: https://pip.pypa.io/
- **Venv**: https://docs.python.org/3/library/venv.html

---

**Quick Start**: See `SETUP_README.md` for step-by-step instructions.
