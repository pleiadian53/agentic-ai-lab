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

### 📦 Personal/Local Scripts (Not in Git)

Some scripts are user-specific and excluded from version control via `.gitignore`:

- **`sync_work.py`** - Personal backup script with Dropbox paths
- **`sync_work.sh`** - Bash version of sync script
- **`SYNC_SETUP.md`** - Setup documentation for sync scripts

These scripts contain user-specific directory paths and configurations. If you want to use them:
1. Create your own versions with your paths
2. They won't be tracked by git (intentionally)
3. See the script headers for usage instructions

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

## Server Management Scripts

### start_research_server.sh

Start the Nexus Research Agent web server.

**Usage:**
```bash
./scripts/start_research_server.sh
```

**What it does:**
- Checks if port 8004 is in use and stops existing server
- Activates the `agentic-ai` conda environment
- Starts the FastAPI server on http://localhost:8004
- Displays server status and URLs

**Features:**
- Auto-stops conflicting servers
- Shows API documentation URLs
- Press Ctrl+C to stop

### Stop Server

The stop script is located in the server directory:

**Location:** `src/nexus/agents/research/server/stop_server.sh`

**Usage:**
```bash
./src/nexus/agents/research/server/stop_server.sh
```

**What it does:**
- Finds process using port 8004
- Tries graceful shutdown first (TERM signal)
- Forces shutdown if needed (kill -9)
- Verifies server stopped successfully

## Utility Scripts

### md_to_pdf.py

Convert Markdown documents to professional PDFs using Pandoc and XeLaTeX.

**Usage:**
```bash
# Basic conversion
python scripts/md_to_pdf.py docs/README.md

# With custom title and author
python scripts/md_to_pdf.py docs/README.md \
    --title "Nexus Research Agent" \
    --author "Agentic AI Lab"

# Specify output path
python scripts/md_to_pdf.py docs/README.md -o output/documentation.pdf

# Generate LaTeX only (for debugging)
python scripts/md_to_pdf.py docs/README.md --latex-only
```

**Requirements:**
- Pandoc: `brew install pandoc`
- XeLaTeX: See `src/nexus/agents/research/docs/installation/LATEX_SETUP.md`
- pypandoc (optional): `pip install pypandoc`

**Features:**
- 📑 Automatic table of contents
- 🔢 Numbered sections
- 🔗 Clickable hyperlinks
- 📄 Professional formatting
- ⚡ Works with or without pypandoc

**Examples:**
```bash
# Convert Nexus README
python scripts/md_to_pdf.py src/nexus/README.md

# Convert research report
python scripts/md_to_pdf.py output/research_reports/my_report/report.md \
    --title "Research Report" --author "Nexus Agent"

# Debug LaTeX issues
python scripts/md_to_pdf.py docs/ARCHITECTURE.md --latex-only
```

## Quick Reference

```bash
# Setup environment (first time)
./scripts/install/setup-mamba.sh

# Start research server
./scripts/start_research_server.sh

# Stop research server
./src/nexus/agents/research/server/stop_server.sh

# Convert markdown to PDF
python scripts/md_to_pdf.py docs/README.md

# Activate environment manually
conda activate agentic-ai          # For mamba/conda
source .venv/bin/activate          # For venv
```

---

**See also**: `docs/ENVIRONMENT_SETUP.md` for detailed setup instructions.
