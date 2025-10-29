# Research Agent: Reflection Pattern

## Overview

The Research Agent implements the **REFLECTION pattern** for essay writing - a workflow that iteratively drafts, critiques, and revises essays using LLMs. This is a refactored and enhanced version of the notebook `reflection/C1M2_Assignment.ipynb`.

**Pattern:** Reflection (Draft → Reflect → Revise → Repeat)

## Architecture

### Library Code (`reflection/research_agent/`)

```
reflection/research_agent/
├── __init__.py          # Package exports
├── config.py            # Configuration dataclass
├── prompts.py           # Prompt templates
├── llm.py              # LLM interaction functions
└── workflow.py          # Main orchestration logic
```

### Driver Script (`scripts/`)

```
scripts/
└── run_reflection_research_agent.py  # CLI entry point (reflection pattern)
```

**Future patterns:**
- `run_tool_use_research_agent.py` - Tool use pattern
- `run_multiagent_research_agent.py` - Multi-agent pattern
- `run_planning_research_agent.py` - Planning pattern

## Installation

```bash
# Install in editable mode
mamba activate agentic-ai
pip install -e .

# Verify installation
run-reflection-research-agent --help
```

## Quick Start

### Basic Usage

```bash
# Generate an essay with default settings (reflection pattern)
run-reflection-research-agent "Should social media platforms be regulated by the government?"
```

**Output:**
```
./essays/
├── essay_v1.txt           # Initial draft
├── essay_v2.txt           # Revised version
├── essay_final.txt        # Final essay
└── essay_feedback.md      # All feedback and iterations
```

### With Options

```bash
# Multiple iterations with custom output
run-reflection-research-agent "The impact of AI on education" \
    --max-iterations 3 \
    --output-dir ./my_essays \
    --essay-basename ai_education \
    --verbose
```

## Workflow Steps

### 1. **Draft Generation**
- Uses `draft_model` (default: `openai:gpt-4o-mini`)
- Generates initial essay (500-800 words)
- Includes introduction, body, conclusion

### 2. **Reflection/Critique**
- Uses `reflection_model` (default: `openai:gpt-4o`)
- Structured critique framework:
  - One-sentence verdict
  - Strengths
  - Structural issues
  - Clarity & precision
  - Argument quality
  - Style & tone
  - Top 5 fixes (prioritized)
  - Outline-level revision plan
  - Rubric scores (1-5)

### 3. **Revision**
- Uses `revision_model` (default: `openai:gpt-4o`)
- Applies feedback to improve essay
- Maintains core ideas and factual accuracy

### 4. **Iteration** (Optional)
- Repeats steps 2-3 for multiple refinements
- Convergence detection (stops if minimal changes)
- Configurable max iterations

## Configuration Options

### Model Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--draft-model` | `openai:gpt-4o-mini` | Model for initial draft |
| `--reflection-model` | `openai:gpt-4o` | Model for critique |
| `--revision-model` | `openai:gpt-4o` | Model for revision |

### Workflow Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--max-iterations` | `2` | Maximum iterations (draft + refinements) |
| `--no-stop-on-convergence` | (enabled) | Force all iterations |

### Output Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `./essays` | Output directory |
| `--essay-basename` | `essay` | Basename for files |
| `--no-save-artifacts` | (enabled) | Skip saving files |

### Temperature Settings

| Option | Default | Description |
|--------|---------|-------------|
| `--draft-temperature` | `1.0` | Creativity for drafting |
| `--reflection-temperature` | `1.0` | Creativity for critique |
| `--revision-temperature` | `0.7` | Control for revision |

### Display Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed progress |
| `--show-essays` | Display essay text |

## Output Files

### Essay Files

```
{basename}_v1.txt       # Iteration 1 (initial draft)
{basename}_v2.txt       # Iteration 2 (first revision)
{basename}_v3.txt       # Iteration 3 (second revision, if applicable)
{basename}_final.txt    # Final essay (copy of last iteration)
```

### Feedback File

```markdown
# Essay Feedback: {basename}

## Topic
[User's topic/question]

## Iterations

### Iteration 1
**Word Count:** 650
**Feedback:** Initial draft (no reflection)

### Iteration 2
**Word Count:** 720
**Feedback:**
[Structured critique with rubric scores]

## Final Essay
**Word Count:** 720
**Total Iterations:** 2
```

## Examples

### Example 1: Basic Essay

```bash
run-reflection-research-agent "Should social media platforms be regulated?"
```

**Output:**
- `./essays/essay_v1.txt` - Initial draft (~650 words)
- `./essays/essay_v2.txt` - Revised version (~700 words)
- `./essays/essay_final.txt` - Final essay
- `./essays/essay_feedback.md` - Complete feedback

### Example 2: Multiple Iterations

```bash
run-reflection-research-agent "The role of AI in healthcare" \
    --max-iterations 3 \
    --essay-basename healthcare_ai \
    --output-dir ./research_papers
```

**Output:**
- 3 iterations with progressive refinement
- Convergence detection (may stop early if minimal changes)

### Example 3: Custom Models

```bash
run-reflection-research-agent "Climate change solutions" \
    --draft-model "openai:gpt-4o-mini" \
    --reflection-model "openai:o1-mini" \
    --revision-model "openai:gpt-4o" \
    --verbose
```

**Use case:** Use reasoning model (o1-mini) for deeper critique

### Example 4: Force All Iterations

```bash
run-reflection-research-agent "Ethical implications of gene editing" \
    --max-iterations 4 \
    --no-stop-on-convergence \
    --show-essays
```

**Use case:** Ensure all 4 iterations run regardless of convergence

## Comparison: Notebook vs. Refactored

| Aspect | Notebook | Refactored |
|--------|----------|------------|
| Structure | Single file | Modular packages |
| Reusability | Copy-paste | Import and use |
| CLI | No | Yes (`run-reflection-research-agent`) |
| Iterations | 1 refinement | Configurable (1-N) |
| Convergence | No | Yes (early stopping) |
| Output | Print only | Saves all artifacts |
| Feedback | Text | Structured markdown |
| Configuration | Hardcoded | Dataclass with defaults |
| Testing | Manual | Can write unit tests |

## Key Enhancements

### 1. **Modular Design**
- Separated concerns: config, prompts, LLM calls, workflow
- Easy to test and extend
- Reusable across projects

### 2. **Iterative Refinement**
- Not limited to 1 refinement
- Configurable max iterations
- Convergence detection

### 3. **Artifact Persistence**
- Saves all drafts
- Structured feedback markdown
- Easy to compare iterations

### 4. **Flexible Configuration**
- Different models for each step
- Temperature control
- Output customization

### 5. **Production-Ready**
- CLI with comprehensive options
- Error handling
- Progress tracking
- Verbose mode for debugging

## Programmatic Usage

### Python API

```python
from reflection.research_agent import ResearchAgentConfig, run_research_workflow
import aisuite as ai

# Create configuration
config = ResearchAgentConfig(
    draft_model="openai:gpt-4o-mini",
    reflection_model="openai:gpt-4o",
    max_iterations=3,
    output_dir="./my_essays",
)

# Initialize client
client = ai.Client()

# Run workflow
artifacts = run_research_workflow(
    topic="Should AI be regulated?",
    config=config,
    client=client,
)

# Access results
print(f"Final essay: {artifacts.final_essay}")
print(f"Word count: {artifacts.iterations[-1].word_count}")
print(f"Total iterations: {artifacts.total_iterations}")
```

### Iteration Results

```python
for iteration in artifacts.iterations:
    print(f"Iteration {iteration.iteration}:")
    print(f"  Words: {iteration.word_count}")
    if iteration.feedback:
        print(f"  Feedback: {iteration.feedback[:100]}...")
```

## Future Enhancements

### Planned Features

1. **Citation Integration**
   - Web search for sources
   - Automatic citation formatting
   - Fact-checking

2. **Multi-Agent Collaboration**
   - Separate agents for research, writing, editing
   - Peer review simulation

3. **Style Templates**
   - Academic, journalistic, creative
   - Customizable tone and structure

4. **Evaluation Metrics**
   - Readability scores
   - Argument strength analysis
   - Plagiarism detection

### Migration Path

When mature, move to production:

```
reflection/research_agent/ → src/research_agent/
```

**Criteria:**
- ✅ Comprehensive test coverage
- ✅ API stability
- ✅ Production patterns (logging, error handling)
- ✅ Documentation complete

## Troubleshooting

### Command Not Found

```bash
# Reinstall package
pip install -e .

# Verify
which run-reflection-research-agent
```

### Import Errors

```bash
# Ensure correct environment
mamba activate agentic-ai

# Verify package
pip show agentic-ai
```

### API Key Issues

```bash
# Check .env file
ls -la .env

# Verify keys
grep -E "OPENAI_API_KEY|ANTHROPIC_API_KEY" .env
```

## References

- **Original Notebook:** `reflection/C1M2_Assignment.ipynb`
- **Library Code:** `reflection/research_agent/`
- **Driver Script:** `scripts/run_research_agent.py`
- **Package Config:** `pyproject.toml` (line 125)

## Summary

The Research Agent provides a production-ready implementation of reflective essay writing:

✅ **Modular architecture** - Clean separation of concerns  
✅ **CLI interface** - Easy to use from command line  
✅ **Iterative refinement** - Configurable multi-round improvement  
✅ **Artifact persistence** - Saves all drafts and feedback  
✅ **Flexible configuration** - Different models, temperatures, iterations  
✅ **Convergence detection** - Automatic early stopping  
✅ **Structured feedback** - Markdown documentation  
✅ **Production patterns** - Error handling, progress tracking  

**The refactored research agent is ready for production use!** 🚀
