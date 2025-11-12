# Research Agent Output Formatting Improvements

## Summary

The research agent now generates properly formatted essays with:

1. **Readable line wrapping** (88 characters by default)
2. **Multiple output formats** (TXT, Markdown, PDF)
3. **Flexible word counts** (500-2000+ words based on topic complexity)

## What Changed

### Before
- Essays saved as single long lines per paragraph
- Fixed word count (500-800 words)
- Only plain text output
- Hard to read in text editors

### After
- Proper line wrapping with paragraph preservation
- Configurable word counts (500-2000+ words)
- Multiple formats: TXT, Markdown, and optional PDF
- Professional formatting suitable for reading and distribution

## New Command-Line Options

```bash
# Generate with PDF output
python scripts/run_reflection_research_agent.py "Your topic" --generate-pdf

# Adjust word count for complex topics
python scripts/run_reflection_research_agent.py "AGI systems" \
    --min-words 1000 \
    --max-words 2500

# Custom line width
python scripts/run_reflection_research_agent.py "Your topic" --wrap-width 100
```

## Example Output Comparison

### Old Format (Hard to Read)
```
**The Main Technical Ingredients Needed for AGI Systems** The pursuit of Artificial General Intelligence (AGI) is one of the most ambitious goals in artificial intelligence. Unlike narrow AI, which is designed for specific tasks, AGI aims to emulate human cognitive abilities, including reasoning, learning, and adaptability across various contexts. This essay outlines the essential technical components necessary for constructing AGI systems: reasoning, world modeling, planning, memory, tool use, multimodality, and self-reflection. Integrating these components is crucial for developing a truly versatile and intelligent artificial system.
```

### New Format (Readable)
```
**The Main Technical Ingredients Needed for AGI Systems**

The pursuit of Artificial General Intelligence (AGI) is one of the most ambitious
goals in artificial intelligence. Unlike narrow AI, which is designed for
specific tasks, AGI aims to emulate human cognitive abilities, including
reasoning, learning, and adaptability across various contexts. This essay
outlines the essential technical components necessary for constructing AGI
systems: reasoning, world modeling, planning, memory, tool use, multimodality,
and self-reflection. Integrating these components is crucial for developing a
truly versatile and intelligent artificial system.
```

## File Structure

Each essay now generates multiple files:

```
essays/
└── agi_systems/
    ├── agi_technical_ingredients_final.txt      # Formatted text
    ├── agi_technical_ingredients_final.md       # Markdown with metadata
    ├── agi_technical_ingredients_final.pdf      # Optional PDF
    ├── agi_technical_ingredients_v1.txt         # Iteration 1 (formatted)
    ├── agi_technical_ingredients_v1.md          # Iteration 1 (markdown)
    ├── agi_technical_ingredients_v2.txt         # Iteration 2 (formatted)
    ├── agi_technical_ingredients_v2.md          # Iteration 2 (markdown)
    └── agi_technical_ingredients_feedback.md    # Complete feedback history
```

## PDF Generation

To enable PDF output, install one of:

```bash
# Option 1: WeasyPrint (recommended)
pip install weasyprint markdown

# Option 2: Pandoc (system package)
brew install pandoc  # macOS

# Option 3: markdown-pdf (npm)
npm install -g markdown-pdf
```

## Word Count Guidelines

| Topic Complexity | Recommended Range | Example |
|-----------------|-------------------|---------|
| Simple | 500-800 words | "Benefits of exercise" |
| Moderate | 800-1200 words | "Impact of social media" |
| Complex | 1200-1800 words | "Climate change solutions" |
| Highly Complex | 1500-2500 words | "AGI technical ingredients" |

## Testing the New Features

### Reformat Existing Essays

```bash
python scripts/test_formatting.py
```

This will reformat existing essays in `essays/agi_systems/` with proper line wrapping.

### Generate New Essay with All Features

```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems" \
    --generate-pdf \
    --min-words 1500 \
    --max-words 2500 \
    --max-iterations 3 \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_ingredients_v2
```

## Technical Implementation

### New Modules

- **`formatting.py`**: Text wrapping, markdown formatting, PDF generation
- **Updated `config.py`**: Added `generate_pdf`, `wrap_width`, `min_words`, `max_words`
- **Updated `prompts.py`**: Flexible word count parameters
- **Updated `workflow.py`**: Integration with formatting utilities

### Key Functions

```python
from reflection.research_agent.formatting import (
    wrap_text,              # Wrap text with paragraph preservation
    format_essay_as_markdown,  # Convert to markdown with metadata
    generate_pdf_from_markdown,  # Generate PDF from markdown
    save_formatted_essay,   # Save in multiple formats
)
```

## Benefits

1. **Readability**: Essays are now easy to read in any text editor
2. **Professional Output**: PDF generation for distribution
3. **Flexibility**: Word counts adapt to topic complexity
4. **Backward Compatible**: Existing code continues to work
5. **Multiple Formats**: Choose the format that suits your needs

## Next Steps

- Test with different topics and word counts
- Experiment with PDF generation
- Adjust wrap width for your preferred reading experience
- Use higher word counts for complex topics like AGI

## Documentation

See `reflection/research_agent/README.md` for complete documentation.
