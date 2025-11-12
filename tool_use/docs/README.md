# Tool Use Documentation

Documentation specific to the `tool_use` package and its agents.

## Overview

The `tool_use` package demonstrates agentic patterns where LLMs orchestrate specialized tools and services. Each agent showcases different integration patterns.

## Agents

### 📧 [Email Agent](../email_agent/)

Simulated email system with LLM-powered email management.

**Documentation:**
- [QUICKSTART.md](../email_agent/QUICKSTART.md) - Quick setup guide
- [CONFIGURATION.md](../email_agent/CONFIGURATION.md) - Configuration details
- [server/README.md](../email_agent/server/README.md) - Server architecture

**Pattern:** LLM orchestrates email operations (send, read, search, delete)

### 🧬 [ML Agent](../ml_agent/)

TCGA tumor classification with ML + LLM integration.

**Documentation:**
- [README.md](../ml_agent/README.md) - Complete guide
- [QUICKSTART.md](../ml_agent/QUICKSTART.md) - 5-minute setup
- [data/README.md](../ml_agent/data/README.md) - Data catalog

**Pattern:** LLM orchestrates ML predictions through natural language

## Cross-Cutting Documentation

### Data Management

- **[Data Patterns](./data_patterns.md)** - Dataset documentation patterns
- **[Data Guidelines](../../docs/data_management/guidelines.md)** - Project-wide data policy

### Tool Use Patterns

Each agent demonstrates:

1. **Service Architecture** - FastAPI services with clear APIs
2. **Tool Definition** - Python functions wrapped for LLM use
3. **LLM Orchestration** - Natural language → tool calls
4. **Multi-Service** - Coordinating multiple specialized services

## Directory Structure

```
tool_use/
├── docs/
│   ├── README.md           # This file
│   └── data_patterns.md    # Data documentation patterns
│
├── email_agent/
│   ├── QUICKSTART.md
│   ├── CONFIGURATION.md
│   ├── server/
│   │   └── README.md
│   └── ...
│
└── ml_agent/
    ├── README.md
    ├── QUICKSTART.md
    ├── data/
    │   └── README.md
    └── ...
```

## Adding New Agents

When creating a new agent:

1. **Create agent directory**: `tool_use/new_agent/`
2. **Add documentation**:
   - `README.md` - Complete guide
   - `QUICKSTART.md` - Quick setup
   - `server/README.md` - Server architecture (if applicable)
3. **Follow data patterns**: See [data_patterns.md](./data_patterns.md)
4. **Update this index**: Add entry above

## Documentation Standards

### Agent-Level Documentation

Each agent should have:

- ✅ **README.md** - Complete guide with examples
- ✅ **QUICKSTART.md** - 5-10 minute setup guide
- ✅ **Configuration docs** - Environment variables, settings
- ✅ **Data catalog** - If using datasets (see data_patterns.md)

### Package-Level Documentation

Tool use patterns and cross-cutting concerns live in `tool_use/docs/`:

- Data management patterns
- Common integration patterns
- Shared utilities documentation

## Quick Links

### For Users

- [Email Agent Quick Start](../email_agent/QUICKSTART.md)
- [ML Agent Quick Start](../ml_agent/QUICKSTART.md)

### For Developers

- [Data Patterns](./data_patterns.md)
- [Data Management Guidelines](../../docs/data_management/guidelines.md)
- [Project Documentation Index](../../docs/README.md)

## Related Documentation

- **Project Docs**: [/docs/README.md](../../docs/README.md)
- **Agentic Patterns**: [/docs/patterns/AGENTIC_PATTERNS.md](../../docs/patterns/AGENTIC_PATTERNS.md)
- **Data Management**: [/docs/data_management/guidelines.md](../../docs/data_management/guidelines.md)

---

**Last Updated:** November 6, 2024
