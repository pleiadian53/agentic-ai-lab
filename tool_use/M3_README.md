# ADP Module 3: Tool Use Design Pattern

## Module summary
This module dives into the use of tools within agentic workflows, covering paradigms that include defining tool sets and instructing AI on tool calls. It explores syntaxes like the OpenAI and AI Suite open-source package syntaxes, and discusses emerging paradigms where AIs execute code (e.g., Python) to interface with tools.


## Proposed videos
- Video 1: Unpacking Tool Use in Agentic Workflows
- Video 2: Functions into tools
- Video 3: Tool use in AISuite
- Video 4: OpenAI function calling
- Video 5: Pydantic and tool use (Optional)
- Video 6: MCP as the future of tools?
- Video 7: Implementing tools in research workflow

## Proposed teaching notebooks
- Video 3 notebook (aisuite)
- Video 4 notebook (OpenAI function calling)

## Proposed labs
- Ungraded lab 1 (Functions to tools)
- Graded lab 1 (Implement functions)
- Graded lab 2 (Implement tools for research agent)

## Proposed Activities

### email_agent
Focused LLM tool implementation with `aisuite`, including frontend UI and notebook interface for backend interaction. Demonstrates how to build function calling tools for email operations (send, search, read, mark as read/unread) with a complete FastAPI service integration.

### research_agent_enhanced
**Enhanced Research Agent with Tool Use Pattern**

Building on the reflection pattern (M2) for iterative essay refinement, this implementation adds tool-calling capabilities to create a more sophisticated research workflow. The agent now combines:

- **Reflection Pattern** (from M2): Draft → Reflect → Revise cycle for quality improvement
- **Tool Use Pattern** (M3): Access to external information sources and validation tools

**Key Enhancements:**
- **Research Tools**: Web search (Tavily), academic search (arXiv), fact-checking APIs
- **Citation Tools**: Automatic citation generation, reference validation, bibliography formatting
- **Quality Tools**: Plagiarism detection, readability analysis, fact verification
- **Workflow Integration**: Tools are called during draft generation and revision phases

**Architecture:**
```
tool_use/
├── research_tools.py        # Web search, academic APIs, fact-checking
├── citation_tools.py         # Citation generation and validation
├── quality_tools.py          # Analysis and verification tools
└── examples/
    └── enhanced_research_agent.py  # Full workflow demonstration
```

**Workflow Enhancement:**
1. **Draft Phase**: Agent can search for information while writing
2. **Reflection Phase**: Agent validates facts and checks citations
3. **Revision Phase**: Agent improves based on both reflection AND tool-verified data

This demonstrates how tool use elevates the reflection pattern from "self-improvement" to "informed improvement with external validation."

### sql_agent
**Database Interaction Through Tool Use**

Refactored from educational notebooks to production-ready modules demonstrating database operations as tools. Compares different approaches (OpenAI function calling vs AISuite) while maintaining shared infrastructure.

**Key Features:**
- **Schema Discovery Tools**: Dynamic table inspection, column metadata, relationship mapping
- **Query Generation Tools**: Safe SQL generation with parameterization
- **Execution Tools**: Query execution with result formatting and error handling
- **Validation Tools**: Query safety checks, permission validation, result verification

**Architecture:**
```
tool_use/
├── database_tools.py         # Core database operation tools
├── sql_safety.py             # Query validation and safety checks
└── examples/
    ├── sql_agent_basic.py    # Simple query workflows
    └── sql_agent_advanced.py # Complex multi-table operations
```

**Demonstrates:**
- Tool-based database abstraction
- Safe query execution patterns
- Dynamic schema exploration
- Result formatting and presentation
- Error handling and recovery strategies

