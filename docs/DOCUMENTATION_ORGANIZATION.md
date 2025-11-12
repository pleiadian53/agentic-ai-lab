# Documentation Organization

**Last Updated**: November 7, 2024

---

## Overview

This document describes the organization of documentation in the agentic-ai-public project. All documentation follows a clear hierarchy to keep the project root clean and make information easy to find.

**Core Principle**: Only `README.md` lives in the project root. All other documentation is organized under `docs/` by topic and scope.

---

## Directory Structure

```
agentic-ai-public/
├── README.md                          # Main project README (ONLY doc in root)
│
├── docs/
│   ├── README.md                      # Documentation index
│   ├── DOCUMENTATION_ORGANIZATION.md  # This file
│   ├── DOCUMENTATION_STRUCTURE.md     # Technical structure guide
│   ├── DOCUMENTATION_GUIDES_EXAMPLE.md # Example from another project
│   │
│   ├── installation/                  # Setup & environment
│   │   ├── ENVIRONMENT_SETUP.md
│   │   ├── EDITABLE_INSTALL.md
│   │   ├── MAMBA_VS_PIP.md
│   │   ├── SETUP_CHECKLIST.md
│   │   ├── GITHUB_SETUP.md
│   │   ├── INSTALL_QUICKSTART.md      # ✅ Moved from root
│   │   └── SETUP_README.md            # ✅ Moved from root
│   │
│   ├── tutorials/                     # User guides & learning
│   │   ├── LEARNING_GUIDE.md          # ✅ Moved from root
│   │   └── USAGE_GUIDE.md             # ✅ Moved from root
│   │
│   ├── patterns/                      # Agentic design patterns
│   │   ├── AGENTIC_PATTERNS.md
│   │   ├── RESEARCH_AGENT_GUIDE.md
│   │   └── ENHANCED_REFLECTION_PROMPT.md
│   │
│   ├── workflows/                     # Workflow guides
│   │   ├── DRIVER_SCRIPT_GUIDE.md
│   │   └── OUTPUT_STRATEGY.md
│   │
│   ├── architecture/                  # Project structure
│   │   ├── AGENTIC_ROADMAP.md
│   │   └── TEST_ORGANIZATION.md
│   │
│   ├── libraries/                     # External library docs
│   │   └── AGENT_LLM_TOOLS.md
│   │
│   ├── data_management/               # Data organization
│   │   └── guidelines.md
│   │
│   └── development/                   # Developer documentation
│       └── AGENTS.md                  # ✅ Moved from root (Codex collaboration guide)
│
├── tool_use/                          # Package-level docs
│   ├── docs/
│   │   ├── README.md                  # Tool use index
│   │   └── data_patterns.md           # Data documentation patterns
│   │
│   ├── email_agent/
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   └── ...
│   │
│   └── ml_agent/
│       ├── README.md
│       ├── QUICKSTART.md
│       ├── data/
│       │   └── README.md
│       └── ...
│
└── (other packages)/
    └── docs/                          # Package-specific docs
```

---

## Documentation Levels

### Level 1: Project Root
**Location**: `/`  
**Purpose**: Only the main README.md  
**Rule**: Keep this directory clean - no other documentation files

**Allowed**:
- ✅ `README.md` - Main project overview

**Not Allowed**:
- ❌ Any other `.md` files
- ❌ Documentation directories

### Level 2: Global Documentation (`docs/`)
**Location**: `/docs/<topic>/`  
**Purpose**: Project-wide documentation organized by topic  
**Scope**: Applies to entire project

**Categories**:
- **installation/** - Setup, environment, dependencies
- **tutorials/** - Learning guides, usage examples
- **patterns/** - Agentic design patterns
- **workflows/** - Workflow guides and strategies
- **architecture/** - Project structure, roadmap
- **libraries/** - External library documentation
- **data_management/** - Data organization policies
- **development/** - Developer guides, collaboration

### Level 3: Package Documentation
**Location**: `<package>/docs/<topic>/`  
**Purpose**: Package-specific documentation  
**Scope**: Applies to specific package

**Example**: `tool_use/docs/`
- Cross-agent patterns
- Package architecture
- Integration guides

### Level 4: Agent/Module Documentation
**Location**: `<package>/<agent>/*.md`  
**Purpose**: Agent-specific guides  
**Scope**: Single agent or module

**Example**: `tool_use/ml_agent/`
- `README.md` - Complete guide
- `QUICKSTART.md` - Quick setup
- `data/README.md` - Data catalog

---

## Documentation Categories

### Installation & Setup
**Location**: `docs/installation/`  
**Purpose**: Getting started with the project  
**Contents**:
- Environment setup guides
- Package manager comparisons
- Installation checklists
- Quick start guides

**Files**:
- `ENVIRONMENT_SETUP.md` - Complete environment configuration
- `EDITABLE_INSTALL.md` - Development mode installation
- `MAMBA_VS_PIP.md` - Package manager comparison
- `SETUP_CHECKLIST.md` - Step-by-step verification
- `GITHUB_SETUP.md` - Repository configuration
- `INSTALL_QUICKSTART.md` - Quick installation guide
- `SETUP_README.md` - Mamba/conda setup

### Tutorials & Learning
**Location**: `docs/tutorials/`  
**Purpose**: User guides and learning resources  
**Contents**:
- Comprehensive learning guides
- Usage examples
- Step-by-step tutorials
- Best practices

**Files**:
- `LEARNING_GUIDE.md` - Comprehensive system overview and learning path
- `USAGE_GUIDE.md` - Research agent usage examples

### Agentic Patterns
**Location**: `docs/patterns/`  
**Purpose**: Design patterns for building agents  
**Contents**:
- Pattern overviews
- Implementation guides
- Reflection patterns
- Structured critique frameworks

### Workflows
**Location**: `docs/workflows/`  
**Purpose**: Workflow implementations and guides  
**Contents**:
- CLI tool guides
- Output strategies
- Workflow patterns

### Architecture
**Location**: `docs/architecture/`  
**Purpose**: Project structure and organization  
**Contents**:
- Roadmap and vision
- Testing organization
- Project structure

### Data Management
**Location**: `docs/data_management/`  
**Purpose**: Data organization policies  
**Contents**:
- Dataset documentation patterns
- Manifest guidelines
- Git strategies for data

### Development
**Location**: `docs/development/`  
**Purpose**: Developer and contributor guides  
**Contents**:
- Collaboration guidelines
- Code quality standards
- Design principles
- Development workflows

**Files**:
- `AGENTS.md` - Codex collaboration guide and expectations

---

## Naming Conventions

### File Names
- Use `SCREAMING_SNAKE_CASE.md` for major documents
- Use `lowercase_with_underscores.md` for supporting docs
- Use descriptive names that indicate content

**Examples**:
- ✅ `LEARNING_GUIDE.md` - Major guide
- ✅ `USAGE_GUIDE.md` - Major guide
- ✅ `guidelines.md` - Supporting doc
- ✅ `data_patterns.md` - Supporting doc

### Directory Names
- Use `lowercase_with_underscores` for directories
- Group related documents together
- Keep hierarchy shallow (2-3 levels max)

**Examples**:
- ✅ `installation/`
- ✅ `data_management/`
- ✅ `tool_use/docs/`

---

## Document Types

### Learning Guides
**Location**: `docs/tutorials/`  
**Naming**: `*_GUIDE.md`  
**Purpose**: Comprehensive learning resources  
**Example**: `LEARNING_GUIDE.md`

### Usage Guides
**Location**: `docs/tutorials/`  
**Naming**: `*_GUIDE.md` or `USAGE_*.md`  
**Purpose**: How-to documentation  
**Example**: `USAGE_GUIDE.md`

### Setup Instructions
**Location**: `docs/installation/`  
**Naming**: `*_SETUP.md` or `INSTALL_*.md`  
**Purpose**: Installation and configuration  
**Examples**: `SETUP_README.md`, `INSTALL_QUICKSTART.md`

### Technical Specs
**Location**: `docs/architecture/` or `docs/development/`  
**Naming**: Descriptive names  
**Purpose**: Architecture and implementation details  
**Example**: `DOCUMENTATION_STRUCTURE.md`

### Collaboration Guides
**Location**: `docs/development/`  
**Naming**: Descriptive names  
**Purpose**: Developer collaboration and standards  
**Example**: `AGENTS.md`

---

## Recent Reorganization (Nov 7, 2024)

### Moved to `docs/tutorials/`
- ✅ `LEARNING_GUIDE.md` (was in root)
- ✅ `USAGE_GUIDE.md` (was in root)

### Moved to `docs/installation/`
- ✅ `INSTALL_QUICKSTART.md` (was in root)
- ✅ `SETUP_README.md` (was in root)

### Moved to `docs/development/`
- ✅ `AGENTS.md` (was in root)

### Moved to `docs/`
- ✅ `DOCUMENTATION_STRUCTURE.md` (was in root)

### Kept in Root
- ✅ `README.md` (only doc allowed in root)

---

## Finding Documentation

### By Topic

**Getting Started**
→ `docs/installation/INSTALL_QUICKSTART.md` or `docs/installation/SETUP_README.md`

**Learning the System**
→ `docs/tutorials/LEARNING_GUIDE.md`

**Using the Research Agent**
→ `docs/tutorials/USAGE_GUIDE.md`

**Agentic Patterns**
→ `docs/patterns/AGENTIC_PATTERNS.md`

**Data Management**
→ `docs/data_management/guidelines.md`

**Tool Use Patterns**
→ `tool_use/docs/data_patterns.md`

**Developer Collaboration**
→ `docs/development/AGENTS.md`

**Project Structure**
→ `docs/DOCUMENTATION_STRUCTURE.md`

### By Audience

**New Users**
1. Start with `README.md`
2. Read `docs/installation/INSTALL_QUICKSTART.md`
3. Follow `docs/tutorials/LEARNING_GUIDE.md`
4. Try examples in `docs/tutorials/USAGE_GUIDE.md`

**Developers**
1. Start with `README.md`
2. Check `docs/development/AGENTS.md` for collaboration guidelines
3. Review `docs/architecture/` for project structure
4. Refer to package-specific docs in `<package>/docs/`

**Contributors**
1. Start with `README.md`
2. Read `docs/development/AGENTS.md`
3. Review `docs/patterns/AGENTIC_PATTERNS.md`
4. Check `docs/architecture/AGENTIC_ROADMAP.md`

---

## Maintenance Guidelines

### Adding New Documentation

1. **Determine scope**:
   - Project-wide? → `docs/{category}/`
   - Package-specific? → `<package>/docs/`
   - Agent-specific? → `<package>/<agent>/*.md`
   - Never in project root (except README.md)

2. **Choose category**:
   - Installation/setup? → `docs/installation/`
   - Tutorial/guide? → `docs/tutorials/`
   - Design pattern? → `docs/patterns/`
   - Workflow? → `docs/workflows/`
   - Architecture? → `docs/architecture/`
   - Data management? → `docs/data_management/`
   - Developer guide? → `docs/development/`

3. **Follow naming conventions**:
   - Use descriptive names
   - Follow existing patterns
   - Update category README if needed

4. **Update indexes**:
   - Add to `docs/README.md`
   - Add to category README if exists
   - Update cross-references

### Updating Existing Documentation

1. Keep documents in their current location unless reorganizing
2. Update "Last Updated" dates
3. Maintain backward compatibility for links
4. Update index/README files if structure changes

### Removing Documentation

1. Check for references in other docs
2. Update links if moving/renaming
3. Consider archiving instead of deleting
4. Update category README and main index

---

## Quick Reference

| Need | Location |
|------|----------|
| Project overview | `README.md` |
| Installation | `docs/installation/` |
| Learning guides | `docs/tutorials/` |
| Usage examples | `docs/tutorials/USAGE_GUIDE.md` |
| Agentic patterns | `docs/patterns/` |
| Workflows | `docs/workflows/` |
| Architecture | `docs/architecture/` |
| Data management | `docs/data_management/` |
| Developer guides | `docs/development/` |
| Tool use docs | `tool_use/docs/` |
| ML agent docs | `tool_use/ml_agent/` |
| Email agent docs | `tool_use/email_agent/` |

---

## Benefits of This Organization

1. **Clean Root**: Only README.md in project root
2. **Easy Navigation**: Clear hierarchy and categories
3. **Scalability**: Easy to add new documentation
4. **Discoverability**: Logical grouping by topic/audience
5. **Maintainability**: Clear ownership and structure
6. **Consistency**: Follows established patterns from other projects

---

## Decision Tree

When creating new documentation, ask:

```
Is this the main project README?
  ├─ Yes → Keep in root as README.md
  └─ No ↓

Does it apply to the entire project?
  ├─ Yes → docs/{category}/
  │   ├─ Installation/setup? → docs/installation/
  │   ├─ Tutorial/guide? → docs/tutorials/
  │   ├─ Design pattern? → docs/patterns/
  │   ├─ Workflow? → docs/workflows/
  │   ├─ Architecture? → docs/architecture/
  │   ├─ Data management? → docs/data_management/
  │   └─ Developer guide? → docs/development/
  └─ No ↓

Does it apply to multiple agents in a package?
  ├─ Yes → <package>/docs/{topic}/
  └─ No ↓

Is it agent-specific?
  ├─ Yes → <package>/<agent>/*.md
  └─ No ↓

Is it data-specific?
  └─ Yes → <package>/<agent>/data/*.md
```

---

*For questions about documentation organization, see the main project README or the documentation index at `docs/README.md`.*
