# Documentation Structure

This document provides a visual overview of the documentation organization.

## Directory Tree

```
docs/
├── README.md                           # 📖 Main documentation index
├── STRUCTURE.md                        # 📁 This file - structure overview
│
├── installation/                       # 🔧 Setup & Installation
│   ├── ENVIRONMENT_SETUP.md           # Complete environment guide
│   ├── EDITABLE_INSTALL.md            # Development mode installation
│   ├── MAMBA_VS_PIP.md                # Package manager comparison
│   ├── SETUP_CHECKLIST.md             # Step-by-step verification
│   └── GITHUB_SETUP.md                # Repository configuration
│
├── patterns/                           # 🎯 Agentic Design Patterns
│   ├── AGENTIC_PATTERNS.md            # All patterns overview
│   ├── RESEARCH_AGENT_GUIDE.md        # Reflection pattern guide
│   └── ENHANCED_REFLECTION_PROMPT.md  # Structured critique framework
│
├── workflows/                          # 🔄 Workflow Implementations
│   ├── DRIVER_SCRIPT_GUIDE.md         # CLI workflow tools
│   └── OUTPUT_STRATEGY.md             # Output organization
│
├── architecture/                       # 🏗️ Project Structure
│   ├── AGENTIC_ROADMAP.md             # Vision and roadmap
│   └── TEST_ORGANIZATION.md           # Testing conventions
│
└── libraries/                          # 📚 External Libraries
    ├── README.md                       # Libraries index
    ├── AGENT_LLM_TOOLS.md             # LLM providers (aisuite, etc.)
    ├── DATA_SCIENCE.md                # Data science libraries
    ├── DEPENDENCIES.md                # Core dependencies
    ├── JUPYTER.md                     # Jupyter tools
    └── WEB_FRAMEWORK.md               # Web frameworks
```

## Topic-Based Organization

### 🔧 Installation (5 docs)
Getting the project up and running.

- Environment setup and configuration
- Package management (mamba vs pip)
- Development mode installation
- Setup verification checklist
- Git and GitHub configuration

### 🎯 Patterns (3 docs)
Agentic AI design patterns.

- **Reflection Pattern** ✅ - Draft-Reflect-Revise workflow
- **Tool Use Pattern** 🚧 - Planned
- **Multi-Agent Pattern** 🚧 - Planned
- **Planning Pattern** 🚧 - Planned

### 🔄 Workflows (2 docs)
Specific workflow implementations.

- Chart generation workflow
- Research agent workflow
- Driver scripts and CLI tools
- Output organization strategies

### 🏗️ Architecture (2 docs)
Project organization and structure.

- Project roadmap and vision
- Testing organization and conventions
- Code structure guidelines

### 📚 Libraries (6 docs)
External dependencies and tools.

- LLM providers (aisuite, openai, anthropic)
- Data science tools (pandas, numpy)
- Jupyter and notebook tools
- Web frameworks
- Core dependencies

## Navigation Paths

### For New Users
```
1. installation/ENVIRONMENT_SETUP.md
2. installation/SETUP_CHECKLIST.md
3. patterns/AGENTIC_PATTERNS.md
4. workflows/DRIVER_SCRIPT_GUIDE.md
```

### For Contributors
```
1. installation/EDITABLE_INSTALL.md
2. architecture/TEST_ORGANIZATION.md
3. architecture/AGENTIC_ROADMAP.md
4. patterns/AGENTIC_PATTERNS.md
```

### For Pattern Developers
```
1. patterns/AGENTIC_PATTERNS.md
2. patterns/RESEARCH_AGENT_GUIDE.md
3. patterns/ENHANCED_REFLECTION_PROMPT.md
4. architecture/TEST_ORGANIZATION.md
```

## Documentation Stats

| Category | Files | Status |
|----------|-------|--------|
| Installation | 5 | ✅ Complete |
| Patterns | 3 | ✅ 1 implemented, 3 planned |
| Workflows | 2 | ✅ Complete |
| Architecture | 2 | ✅ Complete |
| Libraries | 6 | ✅ Complete |
| **Total** | **18** | **16 complete, 2 in progress** |

## Benefits of This Structure

### ✅ Clear Organization
- Related docs grouped together
- Easy to find what you need
- Logical topic hierarchy

### ✅ Scalable
- New patterns → `patterns/`
- New workflows → `workflows/`
- New libraries → `libraries/`

### ✅ Maintainable
- Each category has clear scope
- No mixing of unrelated topics
- Easy to update and expand

### ✅ Discoverable
- Index with descriptions
- Cross-references between docs
- Multiple navigation paths

## Adding New Documentation

### 1. Choose the Right Category

```bash
# Installation/setup docs
docs/installation/NEW_SETUP_GUIDE.md

# Pattern documentation
docs/patterns/NEW_PATTERN_GUIDE.md

# Workflow guides
docs/workflows/NEW_WORKFLOW_GUIDE.md

# Architecture/structure
docs/architecture/NEW_ARCHITECTURE_DOC.md

# Library references
docs/libraries/NEW_LIBRARY_GUIDE.md
```

### 2. Update the Index

Add your new doc to `docs/README.md` in the appropriate section.

### 3. Add Cross-References

Link to related documentation within your new doc.

### 4. Follow Conventions

- Use UPPERCASE for main docs
- Include clear examples
- Add status indicators (✅ 🚧 ⏳)
- Cross-reference related docs

## Quick Reference

| Need | Location |
|------|----------|
| Setup environment | `installation/ENVIRONMENT_SETUP.md` |
| Install in dev mode | `installation/EDITABLE_INSTALL.md` |
| Understand patterns | `patterns/AGENTIC_PATTERNS.md` |
| Use reflection pattern | `patterns/RESEARCH_AGENT_GUIDE.md` |
| Run workflows | `workflows/DRIVER_SCRIPT_GUIDE.md` |
| Find outputs | `workflows/OUTPUT_STRATEGY.md` |
| Project roadmap | `architecture/AGENTIC_ROADMAP.md` |
| Testing guide | `architecture/TEST_ORGANIZATION.md` |
| Library reference | `libraries/README.md` |

## Related Files

- **Main README:** `../README.md`
- **Install Guide:** `../INSTALL_QUICKSTART.md`
- **Learning Guide:** `../LEARNING_GUIDE.md`

---

**Last Updated:** October 28, 2025
