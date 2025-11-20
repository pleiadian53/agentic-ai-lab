# Evaluation Package Documentation

This directory contains comprehensive documentation for the evaluation package and related concepts.

## Documents

### [TOOL_CALLING_ARCHITECTURE.md](./TOOL_CALLING_ARCHITECTURE.md)

**Comprehensive guide to tool calling architecture in LLM agents.**

Explains the dual representation pattern used in `eval/M4/research_tools.py`:
- Why you need both Python functions AND JSON schemas
- How the LLM uses schemas to make decisions
- How your code executes the actual functions
- Complete examples and best practices

**Read this if:**
- You're building LLM agents with tool-calling capabilities
- You want to understand the M4 notebook's research_tools.py design
- You're adding new tools to an agent
- You're debugging tool-calling issues

### [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

**Quick reference card for tool calling.**

A condensed, practical guide with:
- Minimal working example
- Schema template
- Common mistakes checklist
- Quick troubleshooting

**Read this if:**
- You need a quick reminder of the pattern
- You're implementing a new tool right now
- You want a template to copy-paste

### [VISUAL_GUIDE.md](./VISUAL_GUIDE.md)

**Visual diagrams and flowcharts for tool calling.**

Includes:
- Complete system architecture diagram
- Step-by-step flow visualization
- Information flow diagrams
- Common mistake illustrations

**Read this if:**
- You're a visual learner
- You want to understand the big picture
- You're teaching others about tool calling
- You need to debug complex tool-calling issues

### [AISUITE_VS_RAW_API.md](./AISUITE_VS_RAW_API.md)

**Comparison of AISuite (M4 notebook) vs. Raw OpenAI API approaches.**

Explains:
- Why M4 notebook doesn't use explicit `tool_def` dictionaries
- How AISuite automatically generates schemas from functions
- When to use each approach
- What happens behind the scenes

**Read this if:**
- You're wondering why M4 uses `tools=[function]` instead of `tools=[schema]`
- You want to understand AISuite's automatic schema generation
- You're deciding between AISuite and raw API for your project
- You want to know what the architecture docs are really explaining

## Related Documentation

### In Parent Directory

- **[../README.md](../README.md)** - Main evaluation package documentation
  - Domain evaluation API
  - Usage examples
  - Integration patterns

- **[../INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md)** - Integration with research_agent
  - Design recommendations
  - Integration patterns
  - Example implementations

- **[../BIOLOGY_DOMAINS_GUIDE.md](../BIOLOGY_DOMAINS_GUIDE.md)** - Biology-specific domains
  - Computational biology domains
  - RNA therapeutics domains
  - Genomics domains
  - Usage examples for life sciences

## Quick Links

### For Beginners
1. Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
2. Read [TOOL_CALLING_ARCHITECTURE.md](./TOOL_CALLING_ARCHITECTURE.md) for depth
3. See [../README.md](../README.md) for evaluation package usage

### For Advanced Users
1. [TOOL_CALLING_ARCHITECTURE.md](./TOOL_CALLING_ARCHITECTURE.md) - Design patterns
2. [../INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) - Integration strategies
3. [../BIOLOGY_DOMAINS_GUIDE.md](../BIOLOGY_DOMAINS_GUIDE.md) - Domain-specific usage

## Topics Covered

### Tool Calling Architecture
- Function implementation vs. schema definition
- LLM decision-making process
- Tool mapping and execution
- OpenAPI schema format
- Best practices and common pitfalls

### Evaluation Package
- Domain-based source evaluation
- Component-level evaluation
- Integration with research workflows
- Biology-specific domain sets

## Contributing

To add new documentation:

1. Create a new `.md` file in this directory
2. Add it to this README with description
3. Link to it from relevant parent docs
4. Follow the existing documentation style

## External Resources

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [JSON Schema Documentation](https://json-schema.org/)
- [AISuite Documentation](https://github.com/andrewyng/aisuite)
