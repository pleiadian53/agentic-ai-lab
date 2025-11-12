# Research Agent Usage Guide

## Quick Start

### Basic Essay Generation

```bash
python scripts/run_reflection_research_agent.py "Your essay topic here"
```

### With Enhanced Formatting (Recommended)

```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems" \
    --min-words 1500 \
    --max-words 2500 \
    --max-iterations 3 \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_technical_ingredients
```

### With PDF Generation

```bash
# First, install PDF dependencies
pip install weasyprint markdown

# Then generate with PDF
python scripts/run_reflection_research_agent.py \
    "Your topic" \
    --generate-pdf \
    --min-words 1000 \
    --max-words 2000
```

## What's New

### 1. Proper Text Formatting
- Essays now have readable line breaks (88 characters per line by default)
- Paragraphs are properly separated with blank lines
- No more endless single-line paragraphs!

### 2. Flexible Word Counts
- Default range: 500-2000 words (previously fixed at 500-800)
- Adjust based on topic complexity
- Complex topics like AGI can use 1500-2500 words

### 3. Multiple Output Formats
- **TXT**: Formatted plain text
- **MD**: Markdown with metadata
- **PDF**: Professional PDF output (optional)

## Command-Line Options

### Essential Options

| Option | Description | Default |
|--------|-------------|---------|
| `topic` | Essay topic (required) | - |
| `--min-words` | Minimum word count | 500 |
| `--max-words` | Maximum word count | 2000 |
| `--max-iterations` | Refinement iterations | 2 |
| `--output-dir` | Output directory | `./essays` |
| `--essay-basename` | Base filename | `essay` |

### Formatting Options

| Option | Description | Default |
|--------|-------------|---------|
| `--generate-pdf` | Generate PDF output | False |
| `--wrap-width` | Line width for wrapping | 88 |

### Model Options

| Option | Description | Default |
|--------|-------------|---------|
| `--draft-model` | Model for drafting | `openai:gpt-4o-mini` |
| `--reflection-model` | Model for reflection | `openai:gpt-4o` |
| `--revision-model` | Model for revision | `openai:gpt-4o` |

## Examples

### Example 1: Simple Topic

```bash
python scripts/run_reflection_research_agent.py \
    "Benefits of regular exercise" \
    --min-words 500 \
    --max-words 800
```

### Example 2: Complex Topic (AGI)

```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems — such as reasoning, world model, planning, memory, tool use, multimodality, and self-reflection" \
    --min-words 1500 \
    --max-words 2500 \
    --max-iterations 3 \
    --generate-pdf \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_technical_ingredients
```

### Example 3: Using Different Models

```bash
python scripts/run_reflection_research_agent.py \
    "The future of quantum computing" \
    --draft-model "openai:gpt-4o-mini" \
    --reflection-model "openai:o1-mini" \
    --revision-model "openai:gpt-4o" \
    --min-words 1000 \
    --max-words 1500
```

### Example 4: Custom Line Width

```bash
python scripts/run_reflection_research_agent.py \
    "Climate change mitigation strategies" \
    --wrap-width 100 \
    --min-words 1200 \
    --max-words 1800
```

## Output Files

For each essay, the following files are generated:

```
essays/
└── [output-dir]/
    ├── [basename]_final.txt      # Final essay (formatted text)
    ├── [basename]_final.md       # Final essay (markdown)
    ├── [basename]_final.pdf      # Final essay (PDF, if --generate-pdf)
    ├── [basename]_v1.txt         # Iteration 1 (formatted)
    ├── [basename]_v1.md          # Iteration 1 (markdown)
    ├── [basename]_v2.txt         # Iteration 2 (formatted)
    ├── [basename]_v2.md          # Iteration 2 (markdown)
    └── [basename]_feedback.md    # Complete feedback history
```

## Word Count Recommendations

| Topic Type | Word Range | Example |
|------------|------------|---------|
| Simple/Focused | 500-800 | "Benefits of exercise" |
| Moderate Complexity | 800-1200 | "Impact of social media on teens" |
| Complex | 1200-1800 | "Climate change solutions" |
| Highly Complex | 1500-2500 | "AGI technical ingredients" |
| Research Paper | 2000-3000 | "Comprehensive analysis of..." |

## PDF Generation Setup

### Option 1: WeasyPrint (Recommended)

```bash
pip install weasyprint markdown
```

Pros:
- Pure Python, easy to install
- High-quality output
- Good typography

### Option 2: Pandoc

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc texlive-xetex

# Windows
choco install pandoc
```

Pros:
- Very powerful
- Many output formats
- Academic-quality PDFs

### Option 3: markdown-pdf

```bash
npm install -g markdown-pdf
```

Pros:
- Simple and fast
- Good for basic PDFs

## Troubleshooting

### Issue: Essays too short

**Solution**: Increase `--max-words`

```bash
--min-words 1000 --max-words 2000
```

### Issue: Essays too long

**Solution**: Decrease `--max-words`

```bash
--min-words 500 --max-words 1000
```

### Issue: PDF generation fails

**Solution**: Install PDF dependencies

```bash
pip install weasyprint markdown
```

Or use a different method (see PDF Generation Setup above).

### Issue: Text not wrapping properly

**Solution**: Adjust `--wrap-width`

```bash
--wrap-width 100  # For wider displays
--wrap-width 72   # For narrower displays
```

### Issue: Not enough iterations

**Solution**: Increase `--max-iterations`

```bash
--max-iterations 4
```

## Testing the Formatting

### Demo Script

```bash
python scripts/demo_formatting.py
```

This shows before/after examples of text formatting.

### Reformat Existing Essays

```bash
python scripts/test_formatting.py
```

This reformats existing essays in `essays/agi_systems/` with proper line wrapping.

## Best Practices

### For Complex Topics
1. Use higher word counts (1500-2500)
2. Increase iterations (3-4)
3. Consider using stronger reflection models (e.g., `o1-mini`)
4. Enable PDF generation for professional output

### For Production Use
1. Always save artifacts (`--save-artifacts` is default)
2. Use descriptive basenames
3. Organize by topic in subdirectories
4. Generate PDFs for distribution

### For Development
1. Start with lower word counts for faster iteration
2. Use `--verbose` to debug issues
3. Use `--show-essays` to inspect outputs
4. Test with simple topics first

## Advanced Usage

### Programmatic API

```python
from pathlib import Path
from reflection.research_agent import (
    ResearchAgentConfig,
    run_research_workflow,
)
import aisuite as ai

config = ResearchAgentConfig(
    draft_model="openai:gpt-4o-mini",
    reflection_model="openai:gpt-4o",
    revision_model="openai:gpt-4o",
    max_iterations=3,
    min_words=1500,
    max_words=2500,
    generate_pdf=True,
    wrap_width=88,
    output_dir=Path("./essays"),
    essay_basename="my_essay",
)

client = ai.Client()
artifacts = run_research_workflow(
    topic="Your topic here",
    config=config,
    client=client,
)

print(f"Final essay: {artifacts.final_essay_path}")
```

### Custom Formatting

```python
from reflection.research_agent.formatting import (
    wrap_text,
    save_formatted_essay,
)

# Wrap existing text
wrapped = wrap_text(essay_text, width=88, preserve_paragraphs=True)

# Save in multiple formats
files = save_formatted_essay(
    essay_text=essay_text,
    output_path=Path("output/my_essay"),
    topic="My Topic",
    word_count=1234,
    wrap_width=88,
    generate_pdf=True,
)
```

## Environment Setup

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_api_key_here

# Optional: Other provider keys
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install aisuite python-dotenv

# Optional: PDF generation
pip install weasyprint markdown
```

## Documentation

- **Full Documentation**: `reflection/research_agent/README.md`
- **Formatting Improvements**: `essays/FORMATTING_IMPROVEMENTS.md`
- **Code Examples**: `scripts/demo_formatting.py`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the full documentation in `reflection/research_agent/README.md`
3. Run the demo script to verify setup: `python scripts/demo_formatting.py`
