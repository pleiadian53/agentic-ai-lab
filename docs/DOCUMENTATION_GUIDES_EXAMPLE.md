# Documentation Organization

**Last Updated**: November 6, 2025

---

## Overview

This document describes the organization of documentation in the MetaSpliceAI project. All documentation follows a clear hierarchy to keep the project root clean and make information easy to find.

---

## Directory Structure

```
meta-spliceai/
├── README.md                          # Main project README (ONLY doc in root)
│
├── docs/
│   ├── DOCUMENTATION_ORGANIZATION.md  # This file
│   │
│   ├── base_models/                   # Base model documentation
│   │   ├── README.md                  # Index of base model docs
│   │   ├── FINAL_ARCHITECTURE_SUMMARY.md
│   │   ├── OPENSPLICEAI_STATUS_FINAL.md
│   │   ├── OPENSPLICEAI_INTEGRATION_SUMMARY.md
│   │   ├── BASE_MODEL_PASS_WORKFLOW.md
│   │   ├── BASE_MODEL_DATA_MAPPING.md
│   │   ├── GENOME_BUILD_COMPATIBILITY.md
│   │   ├── GENOME_BUILD_EVOLUTION_INSIGHTS.md
│   │   ├── DIRECTORY_STRUCTURE_VERSIONING.md
│   │   ├── GRCH37_SETUP_COMPLETE_GUIDE.md
│   │   └── GRCH37_DOWNLOAD_GUIDE.md
│   │
│   ├── development/                   # Developer documentation
│   │   ├── BASE_MODEL_SELECTION_AND_ROUTING.md
│   │   ├── BASE_MODEL_DIRECTORY_ROUTING.md
│   │   ├── MANE_VS_ENSEMBL_SPLICE_SITES.md
│   │   ├── OPENSPLICEAI_MODELS_INFO.md
│   │   ├── REGISTRY_REFACTOR_SUMMARY.md
│   │   └── ...
│   │
│   ├── tutorials/                     # User tutorials
│   │   ├── BASE_MODEL_WORKFLOW_GUIDE.md
│   │   └── ...
│   │
│   ├── analysis/                      # Analysis documentation
│   ├── data/                          # Data documentation
│   ├── datasets/                      # Dataset documentation
│   ├── installation/                  # Installation guides
│   └── ...
│
└── meta_spliceai/                     # Package-level docs
    ├── openspliceai/
    │   └── docs/                      # OpenSpliceAI-specific docs
    ├── splice_engine/
    │   └── docs/                      # Splice engine docs
    └── ...
```

---

## Documentation Categories

### 1. Project Root
**Location**: `/`  
**Purpose**: Only the main README.md  
**Rule**: Keep this directory clean - no other documentation files

### 2. Base Models
**Location**: `docs/base_models/`  
**Purpose**: Documentation about base model integration, genomic builds, and multi-model support  
**Contents**:
- Architecture summaries
- Integration status reports
- Workflow guides
- Setup guides
- Build compatibility docs

### 3. Development
**Location**: `docs/development/`  
**Purpose**: Technical documentation for developers  
**Contents**:
- Architecture details
- Design decisions
- Implementation guides
- API documentation

### 4. Tutorials
**Location**: `docs/tutorials/`  
**Purpose**: Step-by-step user guides  
**Contents**:
- Workflow tutorials
- Usage examples
- Best practices

### 5. Package-Specific
**Location**: `meta_spliceai/{package}/docs/`  
**Purpose**: Documentation specific to a particular package/module  
**Contents**:
- Package-specific guides
- Module documentation
- Implementation details

---

## Naming Conventions

### File Names
- Use `SCREAMING_SNAKE_CASE.md` for major documents
- Use `lowercase_with_underscores.md` for supporting docs
- Use descriptive names that indicate content

### Directory Names
- Use `lowercase_with_underscores` for directories
- Group related documents together
- Keep hierarchy shallow (2-3 levels max)

---

## Document Types

### Status Reports
**Location**: `docs/base_models/` or `docs/development/`  
**Naming**: `*_STATUS_*.md` or `*_SUMMARY.md`  
**Purpose**: Current state of features/integrations

### Guides
**Location**: `docs/tutorials/` or `docs/base_models/`  
**Naming**: `*_GUIDE.md` or `*_WORKFLOW.md`  
**Purpose**: How-to documentation

### Technical Specs
**Location**: `docs/development/`  
**Naming**: Descriptive names  
**Purpose**: Architecture and implementation details

### Setup Instructions
**Location**: `docs/base_models/` or `docs/installation/`  
**Naming**: `*_SETUP_*.md` or `*_DOWNLOAD_*.md`  
**Purpose**: Installation and configuration

---

## Recent Reorganization (Nov 6, 2025)

### Moved to `docs/base_models/`
- ✅ `FINAL_ARCHITECTURE_SUMMARY.md` (was in root)
- ✅ `OPENSPLICEAI_STATUS_FINAL.md` (was in root)
- ✅ `OPENSPLICEAI_INTEGRATION_SUMMARY.md` (was in root)
- ✅ `OPENSPLICEAI_TEST_RESULTS.md` (created)
- ✅ `OPENSPLICEAI_TESTING_STATUS.md` (created)
- ✅ `OPENSPLICEAI_TESTING_GUIDE.md` (created)
- ✅ `BASE_MODEL_COMPARISON_GUIDE.md` (created)
- ✅ `BASE_MODEL_COMPARISON_COMPLETE.md` (created)
- ✅ `BASE_MODEL_OUTPUT_DESIGN.md` (created)
- ✅ `UNIVERSAL_BASE_MODEL_SUPPORT.md` (created)
- ✅ `GRCH38_MANE_VALIDATION_COMPLETE.md` (created)

### Moved to `docs/development/`
- ✅ `REGISTRY_REFACTOR_SUMMARY.md` (was in root)
- ✅ `MANE_GTF_PARSER_FIX.md` (created)

### Moved to `scripts/testing/runners/`
- ✅ `run_openspliceai_tests.sh` (was in root)

### Kept in Root
- ✅ `README.md` (only doc allowed in root)

---

## Finding Documentation

### By Topic

**Base Models & Multi-Model Support**
→ `docs/base_models/`

**OpenSpliceAI Integration**
→ `docs/base_models/OPENSPLICEAI_STATUS_FINAL.md`

**Architecture & Design**
→ `docs/development/` or `docs/base_models/FINAL_ARCHITECTURE_SUMMARY.md`

**User Workflows**
→ `docs/tutorials/`

**Installation & Setup**
→ `docs/installation/` or `docs/base_models/GRCH37_SETUP_COMPLETE_GUIDE.md`

### By Audience

**End Users**
1. Start with `README.md`
2. Check `docs/tutorials/`
3. Refer to `docs/base_models/` for specific models

**Developers**
1. Start with `README.md`
2. Check `docs/development/`
3. Refer to package-specific docs in `meta_spliceai/{package}/docs/`

**Contributors**
1. Start with `README.md`
2. Check `docs/development/`
3. Review architecture docs in `docs/base_models/FINAL_ARCHITECTURE_SUMMARY.md`

---

## Maintenance Guidelines

### Adding New Documentation

1. **Determine scope**:
   - Project-wide? → `docs/{category}/`
   - Package-specific? → `meta_spliceai/{package}/docs/`
   - Never in project root (except README.md)

2. **Choose category**:
   - Base model related? → `docs/base_models/`
   - Developer/technical? → `docs/development/`
   - User tutorial? → `docs/tutorials/`
   - Other? → Appropriate `docs/{category}/`

3. **Follow naming conventions**:
   - Use descriptive names
   - Follow existing patterns
   - Update category README if needed

### Updating Existing Documentation

1. Keep documents in their current location unless reorganizing
2. Update "Last Updated" dates
3. Maintain backward compatibility for links
4. Update index/README files if structure changes

### Removing Documentation

1. Check for references in other docs
2. Update links if moving/renaming
3. Consider archiving instead of deleting
4. Update category README

---

## Quick Reference

| Need | Location |
|------|----------|
| Project overview | `README.md` |
| Base model docs | `docs/base_models/` |
| Technical specs | `docs/development/` |
| User tutorials | `docs/tutorials/` |
| Setup guides | `docs/installation/` or `docs/base_models/` |
| Package docs | `meta_spliceai/{package}/docs/` |

---

## Benefits of This Organization

1. **Clean Root**: Only README.md in project root
2. **Easy Navigation**: Clear hierarchy and categories
3. **Scalability**: Easy to add new documentation
4. **Discoverability**: Logical grouping by topic/audience
5. **Maintainability**: Clear ownership and structure

---

*For questions about documentation organization, see the main project README or contact the maintainers.*


