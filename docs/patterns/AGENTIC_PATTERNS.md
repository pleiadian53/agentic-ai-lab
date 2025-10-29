# Agentic Workflow Patterns

This document describes the different agentic workflow design patterns implemented in this repository.

## Naming Convention

All research agent scripts follow the pattern:
```
run-{pattern}-research-agent
```

This makes it clear which design pattern is being used and allows for easy comparison between patterns.

## Implemented Patterns

### 1. Reflection Pattern ✅

**Command:** `run-reflection-research-agent`

**Script:** `scripts/run_reflection_research_agent.py`

**Library:** `reflection/research_agent/`

**Workflow:**
```
Draft → Reflect → Revise → Repeat
```

**Description:**
The reflection pattern uses an LLM to critique its own output and iteratively improve it. The workflow consists of:
1. **Draft** - Generate initial content
2. **Reflect** - Critique the draft with structured feedback
3. **Revise** - Improve based on feedback
4. **Repeat** - Continue until convergence or max iterations

**Use Cases:**
- Essay writing
- Code generation and refinement
- Creative writing
- Report generation

**Key Features:**
- Structured critique framework
- Iterative refinement (1-N rounds)
- Convergence detection
- Saves all drafts and feedback

**Example:**
```bash
run-reflection-research-agent "Should AI be regulated?" \
    --max-iterations 3 \
    --output-dir ./essays
```

**Status:** ✅ Production-ready

---

## Planned Patterns

### 2. Tool Use Pattern 🚧

**Command:** `run-tool-use-research-agent` (planned)

**Workflow:**
```
Query → Tool Selection → Tool Execution → Synthesis
```

**Description:**
The tool use pattern enables the agent to use external tools (web search, calculators, databases, APIs) to gather information and solve problems.

**Use Cases:**
- Research with web search
- Data analysis with SQL queries
- Mathematical computations
- API integrations

**Key Features:**
- Tool registry and selection
- Execution sandboxing
- Result synthesis
- Multi-tool orchestration

**Status:** 🚧 Planned

---

### 3. Multi-Agent Pattern 🚧

**Command:** `run-multiagent-research-agent` (planned)

**Workflow:**
```
Coordinator → Specialist Agents → Synthesis → Review
```

**Description:**
The multi-agent pattern uses multiple specialized agents working together, each with specific roles and expertise.

**Use Cases:**
- Complex research projects
- Peer review simulation
- Debate and argumentation
- Collaborative writing

**Key Features:**
- Agent specialization
- Inter-agent communication
- Consensus building
- Role-based prompting

**Status:** 🚧 Planned

---

### 4. Planning Pattern 🚧

**Command:** `run-planning-research-agent` (planned)

**Workflow:**
```
Goal → Plan → Execute → Monitor → Replan
```

**Description:**
The planning pattern creates a structured plan before execution, monitors progress, and adapts the plan as needed.

**Use Cases:**
- Long-form content creation
- Multi-step problem solving
- Project management
- Strategic analysis

**Key Features:**
- Hierarchical planning
- Progress tracking
- Dynamic replanning
- Goal decomposition

**Status:** 🚧 Planned

---

## Pattern Comparison

| Pattern | Complexity | Iterations | External Tools | Multi-Agent | Best For |
|---------|-----------|------------|----------------|-------------|----------|
| **Reflection** | Low | Yes | No | No | Self-improvement, refinement |
| **Tool Use** | Medium | Optional | Yes | No | Research, data gathering |
| **Multi-Agent** | High | Yes | Optional | Yes | Complex tasks, collaboration |
| **Planning** | High | Yes | Optional | Optional | Long-horizon tasks |

## Directory Structure

```
scripts/
├── run_reflection_research_agent.py      # ✅ Implemented
├── run_tool_use_research_agent.py        # 🚧 Planned
├── run_multiagent_research_agent.py      # 🚧 Planned
└── run_planning_research_agent.py        # 🚧 Planned

reflection/research_agent/                 # Reflection pattern library
├── config.py
├── prompts.py
├── llm.py
└── workflow.py

# Future pattern libraries
tool_use/research_agent/                   # 🚧 Planned
multiagent/research_agent/                 # 🚧 Planned
planning/research_agent/                   # 🚧 Planned
```

## Implementation Guidelines

### For New Patterns

When implementing a new pattern:

1. **Create library code** in appropriate directory
   - `{pattern}/research_agent/`
   - Follow modular structure (config, prompts, llm, workflow)

2. **Create driver script**
   - `scripts/run_{pattern}_research_agent.py`
   - Follow naming convention
   - Include comprehensive CLI options

3. **Register CLI command**
   - Add to `pyproject.toml` under `[project.scripts]`
   - Format: `run-{pattern}-research-agent = "scripts.run_{pattern}_research_agent:main"`

4. **Document the pattern**
   - Update this file
   - Create pattern-specific guide in `docs/`
   - Include examples and use cases

5. **Test thoroughly**
   - Create test scripts in `tests/{pattern}_research_agent/`
   - Verify output quality
   - Compare with other patterns

### Design Principles

All patterns should follow these principles:

✅ **Modularity** - Clean separation of concerns  
✅ **Reusability** - Library code can be imported  
✅ **CLI-first** - Easy to use from command line  
✅ **Configuration** - Flexible via dataclasses  
✅ **Artifact persistence** - Save all outputs  
✅ **Documentation** - Comprehensive guides  
✅ **Testing** - Automated test suites  
✅ **Consistency** - Follow established patterns  

## Migration Path

When patterns mature:

```
reflection/research_agent/ → src/research_agent_reflection/
tool_use/research_agent/   → src/research_agent_tool_use/
multiagent/research_agent/ → src/research_agent_multiagent/
planning/research_agent/   → src/research_agent_planning/
```

## References

- **Reflection Pattern:** `docs/RESEARCH_AGENT_GUIDE.md`
- **Original Notebook:** `reflection/C1M2_Assignment.ipynb`
- **Package Config:** `pyproject.toml`

## Contributing

When adding a new pattern:

1. Follow the naming convention
2. Implement library code first
3. Create driver script
4. Write comprehensive documentation
5. Add test suite
6. Update this file

## Summary

The agentic patterns framework provides a systematic way to implement and compare different workflow designs:

- ✅ **Clear naming** - Pattern name in command
- ✅ **Modular design** - Reusable library code
- ✅ **Consistent structure** - Same organization across patterns
- ✅ **Easy comparison** - Side-by-side evaluation
- ✅ **Production-ready** - CLI tools with full features

**Current status:** 1 pattern implemented (Reflection), 3 patterns planned (Tool Use, Multi-Agent, Planning)
