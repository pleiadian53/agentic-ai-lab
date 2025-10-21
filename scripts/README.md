# Scripts Directory

This directory contains helper scripts organized by purpose to keep the project root clean.

## Directory Structure

```
scripts/
├── README.md           # This file
├── install/            # Environment setup scripts
│   ├── setup.sh        # Mamba environment setup (primary)
│   └── archive/        # Old/deprecated scripts
├── dev/                # Development workflow scripts (future)
└── utils/              # General utility scripts (future)
```

## Scripts by Category

### Installation Scripts (`install/`)

Environment setup and dependency installation.

### setup.sh

Creates a mamba environment with all dependencies.

**Usage:**
```bash
./scripts/install/setup.sh
mamba activate agentic-ai
```

**What it does:**
- Checks for mamba installation
- Creates `agentic-ai` environment from `environment.yml`
- Installs all conda and pip dependencies (~46 packages)
- Configures Jupyter kernel
- Verifies installation

**Requirements:**
- Miniforge (includes mamba)
- Install: `brew install --cask miniforge`
- `environment.yml` in project root

**Features:**
- Detects existing environment and prompts for recreation
- Verifies key packages after installation
- Provides clear next steps

### 🔧 dev/

Development workflow and testing scripts (to be added as needed).

Examples of scripts that could go here:
- Database reset/migration scripts
- Test data generation
- Development server launchers
- Code formatting/linting runners

### 🛠️ utils/

General utility scripts for maintenance and operations (to be added as needed).

Examples of scripts that could go here:
- Backup scripts
- Log analysis
- Performance profiling
- Cleanup utilities

## Adding New Scripts

When adding new scripts:

1. **Choose the right category**:
   - `install/` - Setup and installation
   - `dev/` - Development workflows
   - `utils/` - General utilities

2. **Make scripts executable**:
   ```bash
   chmod +x scripts/category/your-script.sh
   ```

3. **Add documentation**:
   - Update this README
   - Add usage comments in the script
   - Update relevant docs in `docs/`

4. **Follow naming conventions**:
   - Use kebab-case: `setup-mamba.sh`, `reset-db.sh`
   - Be descriptive: `generate-test-data.sh` not `gen.sh`
   - Include extension: `.sh`, `.py`, etc.

## Script Standards

All scripts should:
- ✅ Include a header comment explaining purpose
- ✅ Use `set -e` for bash scripts (exit on error)
- ✅ Provide helpful error messages
- ✅ Be executable (`chmod +x`)
- ✅ Work from any directory (use `cd "$(dirname "$0")"` if needed)

## Quick Reference

```bash
# Setup environment (first time)
./scripts/install/setup-mamba.sh

# Or with pip/venv
./scripts/install/setup-venv.sh

# Activate environment
conda activate agentic-ai          # For mamba/conda
source .venv/bin/activate          # For venv
```

---

**See also**: `docs/ENVIRONMENT_SETUP.md` for detailed setup instructions.
