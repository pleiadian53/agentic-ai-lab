# Documentation Structure

## Overview

This document describes the documentation organization strategy for the agentic-ai-lab project.

## Principles

1. **Global Scope** → `/docs/<topic>/`
2. **Package Scope** → `<package>/docs/<topic>/`
3. **Agent Scope** → `<package>/<agent>/*.md`
4. **Data Scope** → `<package>/<agent>/data/README.md`

## Directory Structure

```
agentic-ai-lab/
│
├── docs/                           # Global documentation
│   ├── README.md                   # Documentation index
│   ├── installation/               # Setup & environment
│   ├── patterns/                   # Agentic design patterns
│   ├── workflows/                  # Workflow guides
│   ├── architecture/               # Project structure
│   ├── libraries/                  # External library docs
│   └── data_management/            # Data organization policy
│       └── guidelines.md           # ✅ Moved from root
│
├── tool_use/                       # Tool use package
│   ├── docs/                       # Package-level docs
│   │   ├── README.md               # Tool use index
│   │   └── data_patterns.md        # ✅ Moved from ml_agent
│   │
│   ├── email_agent/                # Email agent
│   │   ├── README.md               # Agent guide
│   │   ├── QUICKSTART.md           # Quick setup
│   │   ├── CONFIGURATION.md        # Config details
│   │   └── server/
│   │       └── README.md           # Server architecture
│   │
│   └── ml_agent/                   # ML agent
│       ├── README.md               # Agent guide
│       ├── QUICKSTART.md           # Quick setup
│       └── data/
│           ├── README.md           # Data catalog
│           └── processed/
│               ├── tcga_processed.md    # Dataset docs
│               └── manifest.json        # File metadata
│
└── (other packages)/
    └── docs/                       # Package-specific docs
```

## Documentation Levels

### Level 1: Global (`/docs/`)

**Scope:** Project-wide policies, patterns, and setup

**Examples:**
- Installation guides
- Agentic design patterns
- Data management policy
- Project architecture

**When to use:**
- Applies to entire project
- Cross-package concerns
- General guidelines

### Level 2: Package (`<package>/docs/`)

**Scope:** Package-specific patterns and cross-agent docs

**Examples:**
- Tool use patterns
- Data documentation patterns
- Package architecture

**When to use:**
- Applies to multiple agents in package
- Package-level patterns
- Shared utilities

### Level 3: Agent (`<package>/<agent>/*.md`)

**Scope:** Agent-specific guides and documentation

**Examples:**
- Agent README
- Quick start guide
- Configuration guide
- Server architecture

**When to use:**
- Agent-specific functionality
- Setup instructions
- Usage examples

### Level 4: Data (`<package>/<agent>/data/`)

**Scope:** Dataset documentation and catalogs

**Examples:**
- Data catalog (README.md)
- Dataset documentation (*.md)
- Manifests (manifest.json)

**When to use:**
- Documenting datasets
- Data provenance
- Usage examples

## Migration Summary

### Files Moved

| Original Location | New Location | Reason |
|-------------------|--------------|--------|
| `/DATA_MANAGEMENT.md` | `/docs/data_management/guidelines.md` | Global policy |
| `/tool_use/ml_agent/DATA_PATTERNS.md` | `/tool_use/docs/data_patterns.md` | Package-level pattern |

### Files Created

| Location | Purpose |
|----------|---------|
| `/tool_use/docs/README.md` | Package documentation index |
| `/docs/data_management/` | Data management topic directory |

### Files Updated

| File | Change |
|------|--------|
| `/docs/README.md` | Added data management section |

## Navigation

### From Global to Package

```
/docs/README.md
  → Data Management section
    → /docs/data_management/guidelines.md (global policy)
    → /tool_use/docs/data_patterns.md (package pattern)
```

### From Package to Agent

```
/tool_use/docs/README.md
  → ML Agent section
    → /tool_use/ml_agent/README.md (agent guide)
    → /tool_use/ml_agent/QUICKSTART.md (quick setup)
    → /tool_use/ml_agent/data/README.md (data catalog)
```

### From Agent to Data

```
/tool_use/ml_agent/README.md
  → Data section
    → /tool_use/ml_agent/data/README.md (catalog)
    → /tool_use/ml_agent/data/processed/tcga_processed.md (dataset)
```

## Best Practices

### Choosing Documentation Location

**Ask these questions:**

1. **Does it apply to the entire project?**
   - Yes → `/docs/<topic>/`
   - No → Continue

2. **Does it apply to multiple agents in a package?**
   - Yes → `<package>/docs/<topic>/`
   - No → Continue

3. **Is it agent-specific?**
   - Yes → `<package>/<agent>/*.md`
   - No → Continue

4. **Is it data-specific?**
   - Yes → `<package>/<agent>/data/*.md`

### Cross-Referencing

Use relative paths for cross-references:

```markdown
<!-- From agent to global -->
See [Data Guidelines](../../docs/data_management/guidelines.md)

<!-- From agent to package -->
See [Data Patterns](../docs/data_patterns.md)

<!-- From package to agent -->
See [ML Agent](../ml_agent/README.md)
```

### Index Files

Each documentation directory should have an index:

- `/docs/README.md` - Global index
- `<package>/docs/README.md` - Package index
- `<package>/<agent>/data/README.md` - Data catalog

## Examples

### Example 1: Adding Global Documentation

**Topic:** Testing best practices (applies to all packages)

**Location:** `/docs/testing/best_practices.md`

**Update:** Add to `/docs/README.md` index

### Example 2: Adding Package Documentation

**Topic:** Tool use integration patterns (applies to all tool_use agents)

**Location:** `/tool_use/docs/integration_patterns.md`

**Update:** Add to `/tool_use/docs/README.md` index

### Example 3: Adding Agent Documentation

**Topic:** Email agent API reference

**Location:** `/tool_use/email_agent/API.md`

**Update:** Reference in `/tool_use/email_agent/README.md`

### Example 4: Adding Data Documentation

**Topic:** New dataset for ML agent

**Location:** `/tool_use/ml_agent/data/processed/new_dataset.md`

**Update:** Add to `/tool_use/ml_agent/data/README.md` catalog

## Benefits

### 1. Clean Project Root

- No documentation clutter
- Clear separation of concerns
- Easy to navigate

### 2. Logical Organization

- Global → Package → Agent → Data hierarchy
- Clear ownership and scope
- Predictable locations

### 3. Scalability

- Easy to add new packages
- Easy to add new agents
- Easy to add new datasets

### 4. Discoverability

- Index files at each level
- Clear cross-references
- Topic-based organization

## Migration Checklist

When moving documentation:

- [ ] Move file to appropriate location
- [ ] Update all cross-references
- [ ] Update index files
- [ ] Test all links
- [ ] Update any scripts that reference the file

## Summary

**Documentation hierarchy:**

```
Global (project-wide)
  ↓
Package (cross-agent)
  ↓
Agent (agent-specific)
  ↓
Data (dataset-specific)
```

**Key principle:** Keep documentation as close to its scope as possible, but no closer.

---

**Last Updated:** November 6, 2024
