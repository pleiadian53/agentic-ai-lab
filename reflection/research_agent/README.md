# Research Agent with Reflective Writing

A sophisticated essay generation system using the **REFLECTION pattern** for iterative draft-reflect-revise workflows.

## Features

### Core Capabilities
- **Iterative Refinement**: Draft → Reflect → Revise cycle with configurable iterations
- **Convergence Detection**: Automatic early stopping when essays stabilize
- **Multi-Model Support**: Use different models for drafting, reflection, and revision
- **Structured Feedback**: Comprehensive critique framework with rubric scoring

### Output Formatting (New!)
- **Proper Line Wrapping**: Essays formatted with readable line breaks (default: 88 characters)
- **Multiple Formats**: Text, Markdown, and optional PDF output
- **Flexible Word Counts**: Configurable word count ranges (500-2000+ words)
- **Beautiful PDFs**: Professional formatting with proper typography and spacing

## Installation

### Basic Installation
```bash
# Core dependencies (already in main project)
pip install aisuite python-dotenv
```

### PDF Generation (Optional)
Choose one of the following options:

**Option 1: WeasyPrint (Recommended)**
```bash
pip install -r requirements-pdf.txt
```

**Option 2: Pandoc**
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc texlive-xetex
```

**Option 3: markdown-pdf**
```bash
npm install -g markdown-pdf
```

## Usage

### Basic Usage
```bash
python scripts/run_reflection_research_agent.py "Your essay topic here"
```

### With PDF Generation
```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems" \
    --generate-pdf \
    --max-words 2000 \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_technical_ingredients
```

### Complex Topics with Higher Word Counts
```bash
python scripts/run_reflection_research_agent.py \
    "The philosophical implications of consciousness in AGI" \
    --min-words 1000 \
    --max-words 2500 \
    --max-iterations 3 \
    --generate-pdf
```

### Custom Models and Settings
```bash
python scripts/run_reflection_research_agent.py \
    "Climate change mitigation strategies" \
    --draft-model "openai:gpt-4o-mini" \
    --reflection-model "openai:o1-mini" \
    --revision-model "openai:gpt-4o" \
    --max-iterations 3 \
    --wrap-width 100
```

## Command-Line Options

### Required Arguments
- `topic`: Essay topic or question to address

### Model Configuration
- `--draft-model`: Model for initial draft (default: `openai:gpt-4o-mini`)
- `--reflection-model`: Model for reflection (default: `openai:gpt-4o`)
- `--revision-model`: Model for revision (default: `openai:gpt-4o`)

### Output Configuration
- `--output-dir`: Output directory (default: `./essays`)
- `--essay-basename`: Base name for files (default: `essay`)
- `--generate-pdf`: Generate PDF versions of essays
- `--wrap-width`: Line width for text wrapping (default: 88)
- `--no-save-artifacts`: Skip saving drafts and feedback

### Workflow Configuration
- `--max-iterations`: Maximum refinement iterations (default: 2)
- `--min-words`: Minimum target word count (default: 500)
- `--max-words`: Maximum target word count (default: 2000)
- `--no-stop-on-convergence`: Force all iterations even when converged

### Temperature Settings
- `--draft-temperature`: Draft generation temperature (default: 1.0)
- `--reflection-temperature`: Reflection temperature (default: 1.0)
- `--revision-temperature`: Revision temperature (default: 0.7)

### Display Options
- `--verbose`: Show detailed progress and outputs
- `--show-essays`: Display essay text for each iteration

## Output Files

For each essay generation, the following files are created:

### Text Files (Always Generated)
- `{basename}_final.txt`: Final essay with proper line wrapping
- `{basename}_v1.txt`: Initial draft (formatted)
- `{basename}_v2.txt`: First revision (formatted)
- `{basename}_vN.txt`: Additional revisions (formatted)

### Markdown Files (Always Generated)
- `{basename}_final.md`: Final essay with metadata
- `{basename}_v1.md`: Initial draft with metadata
- `{basename}_feedback.md`: Complete feedback and iteration history

### PDF Files (Optional)
- `{basename}_final.pdf`: Final essay as PDF
- `{basename}_v1.pdf`: Initial draft as PDF
- `{basename}_v2.pdf`: Revisions as PDF

## Word Count Guidelines

The system supports flexible word counts based on topic complexity. **Default: 800-6000 words**.

The LLM uses its judgment—complex topics naturally require more comprehensive treatment:

| Topic Complexity | Recommended Range | Example |
|-----------------|-------------------|---------|
| Simple/Practical | 800-1500 words | "Best chicken soup recipe" |
| Moderate | 1500-3000 words | "Impact of social media" |
| Complex | 3000-5000 words | "Climate change solutions" |
| Highly Complex | 4000-6000+ words | "Technical ingredients for AGI" |

**Philosophy**: We don't artificially restrict or pad essays. The model determines appropriate length based on topic depth and feedback quality. Simple topics like recipes may only need 800-1000 words, while technical topics like AGI deserve 4000-6000+ words.

## Text Formatting

Essays are now formatted with:
- **Proper line wrapping** at 88 characters (configurable)
- **Paragraph preservation** with blank lines between paragraphs
- **Readable structure** for both terminal and PDF viewing
- **Consistent formatting** across all output formats

### Before (Old Format)
```
**The Main Technical Ingredients Needed for AGI Systems** The pursuit of Artificial General Intelligence (AGI) is one of the most ambitious goals in artificial intelligence. Unlike narrow AI, which is designed for specific tasks, AGI aims to emulate human cognitive abilities, including reasoning, learning, and adaptability across various contexts...
```

### After (New Format)
```
**The Main Technical Ingredients Needed for AGI Systems**

The pursuit of Artificial General Intelligence (AGI) is one of the most ambitious
goals in artificial intelligence. Unlike narrow AI, which is designed for
specific tasks, AGI aims to emulate human cognitive abilities, including
reasoning, learning, and adaptability across various contexts...
```

## Programmatic Usage

```python
from pathlib import Path
from reflection.research_agent import (
    ResearchAgentConfig,
    run_research_workflow,
)
import aisuite as ai

# Configure the workflow
config = ResearchAgentConfig(
    draft_model="openai:gpt-4o-mini",
    reflection_model="openai:gpt-4o",
    revision_model="openai:gpt-4o",
    max_iterations=3,
    min_words=1000,
    max_words=2000,
    generate_pdf=True,
    wrap_width=88,
    output_dir=Path("./essays"),
    essay_basename="my_essay",
)

# Run the workflow
client = ai.Client()
artifacts = run_research_workflow(
    topic="Your essay topic here",
    config=config,
    client=client,
)

# Access results
print(f"Final essay: {artifacts.final_essay}")
print(f"Total iterations: {artifacts.total_iterations}")
print(f"Output path: {artifacts.final_essay_path}")
```

## Architecture

### Workflow Pattern
```
┌─────────────┐
│ Draft       │ ← Initial essay generation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Reflect     │ ← Structured critique and feedback
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Revise      │ ← Incorporate feedback
└──────┬──────┘
       │
       ▼
   Converged? ──No──▶ Repeat Reflect → Revise
       │
      Yes
       │
       ▼
┌─────────────┐
│ Format      │ ← Text wrapping, Markdown, PDF
└─────────────┘
```

### Module Structure
- `config.py`: Configuration dataclass
- `prompts.py`: Prompt templates for each step
- `llm.py`: LLM interaction functions
- `workflow.py`: Main orchestration logic
- `formatting.py`: Text formatting and PDF generation
- `utils.py`: Helper utilities

## Reflection Framework

The reflection step uses a structured critique format:

1. **One-Sentence Verdict**: Overall assessment
2. **Strengths**: What works well
3. **Structural Issues**: Organization and flow
4. **Clarity & Precision**: Language and readability
5. **Argument Quality**: Logic and evidence
6. **Style & Tone**: Voice and formatting
7. **Most Important Fixes**: Top 5 prioritized improvements
8. **Outline-Level Revision Plan**: Structural recommendations
9. **Rubric Scores**: Quantitative assessment (1-5 scale)

## Best Practices

### For Complex Topics
- Use higher word counts (1500-2500)
- Increase max iterations (3-4)
- Consider using stronger models for reflection (e.g., `o1-mini`)

### For Production Use
- Enable PDF generation for professional output
- Set appropriate wrap width for your target medium
- Use convergence detection to save API costs
- Save all artifacts for audit trails

### For Development
- Use `--verbose` to debug issues
- Use `--show-essays` to inspect intermediate outputs
- Start with lower word counts for faster iteration

## Troubleshooting

### PDF Generation Fails
- Ensure you have installed one of the PDF generation tools
- Check the error message for specific missing dependencies
- Try a different PDF generation method

### Essays Too Short/Long
- Adjust `--min-words` and `--max-words` parameters
- Complex topics naturally require more words
- The model will aim for the specified range but may vary slightly

### Convergence Too Early
- Use `--no-stop-on-convergence` to force all iterations
- Increase temperature for more variation
- Check if feedback is too lenient

## Examples

See the `essays/` directory for example outputs, including:
- `agi_systems/`: Essays on AGI technical ingredients
- Various topics with different word counts and formats

## Contributing

When adding new features:
1. Update this README
2. Add tests if applicable
3. Ensure backward compatibility
4. Update type hints and docstrings

## License

See main project LICENSE file.
