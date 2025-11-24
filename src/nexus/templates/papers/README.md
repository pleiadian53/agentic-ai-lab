# Template Papers Repository

This directory contains template papers used for style transfer in research report generation.

## Overview

Template papers serve as style guides for generating research reports. The system analyzes the structure, formatting, citation style, and writing patterns of these papers to create reports that match their style.

## Directory Structure

```
papers/
├── README.md                    # This file
├── openspliceai.pdf            # Example: OpenSpliceAI paper
├── alphafold.pdf               # Example: AlphaFold Nature paper
└── metadata/                   # Extracted metadata
    ├── openspliceai.json       # Structure and style info
    └── alphafold.json
```

## Adding New Template Papers

### Step 1: Add the PDF

Place your template paper in this directory:

```bash
cp /path/to/your/paper.pdf papers/your_paper.pdf
```

### Step 2: Extract Metadata

Run the template analyzer:

```bash
nexus template analyze papers/your_paper.pdf
```

This will create `metadata/your_paper.json` with extracted information:

- Section structure (Abstract, Introduction, Methods, etc.)
- Citation style
- Figure and table placement patterns
- Writing style characteristics
- Typical length and formatting

### Step 3: Review and Edit Metadata

Review the generated metadata file and make any necessary adjustments:

```json
{
  "title": "Your Paper Title",
  "sections": [
    "Abstract",
    "Introduction",
    "Methods",
    "Results",
    "Discussion",
    "References"
  ],
  "citation_style": "nature",
  "has_supplementary": true,
  "typical_length": "8-10 pages",
  "figure_count": 5,
  "table_count": 2,
  "writing_style": {
    "tone": "technical",
    "person": "first-person-plural",
    "tense": "past-results-present-discussion",
    "formality": "high"
  },
  "formatting": {
    "font": "serif",
    "line_spacing": 1.5,
    "margins": "1 inch",
    "column_count": 2
  }
}
```

### Step 4: Use the Template

The template is now available for use:

```bash
# CLI
nexus research "Your topic" --template papers/your_paper.pdf --pdf

# Python
from nexus.agents.research import ResearchAgent
from nexus.templates import StyleTransferEngine

agent = ResearchAgent()
style_engine = StyleTransferEngine()

template = style_engine.analyze_template("papers/your_paper.pdf")
report = agent.generate(topic="Your topic", template=template)
```

## Template Quality Guidelines

### Good Template Papers

- **Clear structure**: Well-defined sections
- **Consistent style**: Uniform formatting throughout
- **High quality**: Published in reputable venues
- **Relevant domain**: Matches your research area
- **Appropriate length**: 5-15 pages ideal

### What Gets Extracted

1. **Section Structure**
   - Section titles and hierarchy
   - Typical section lengths
   - Order and flow

2. **Citation Style**
   - In-text citation format
   - Reference list format
   - Citation density

3. **Visual Elements**
   - Figure placement and captions
   - Table formatting
   - Equation styling

4. **Writing Style**
   - Tone and formality
   - Person (first/third)
   - Tense usage
   - Sentence structure patterns

5. **Formatting**
   - Font and typography
   - Spacing and margins
   - Column layout
   - Header/footer style

## Example Templates

### Nature Paper Style

- Two-column layout
- High formality
- Past tense for results
- Extensive supplementary materials
- Numbered citations

### arXiv Preprint Style

- Single-column layout
- Technical tone
- Present tense common
- Detailed methods
- Author-year citations

### Conference Paper Style

- Two-column layout
- Page limits (6-8 pages)
- Condensed format
- Emphasis on novelty
- Numbered citations

## Troubleshooting

### Metadata Extraction Failed

If automatic extraction fails:

1. Check PDF is not scanned/image-based
2. Verify PDF is not password-protected
3. Manually create metadata JSON using examples
4. Contact support with PDF details

### Style Transfer Not Working

If style transfer produces poor results:

1. Verify metadata is accurate
2. Check template paper quality
3. Ensure content matches template domain
4. Try a different template paper

## Best Practices

1. **Use domain-specific templates**: Match template to research area
2. **Keep templates updated**: Add recent papers regularly
3. **Maintain metadata quality**: Review and refine extracted metadata
4. **Test templates**: Generate sample reports to verify quality
5. **Document custom templates**: Add notes about special characteristics

## Contributing

To contribute new template papers:

1. Ensure you have rights to use the paper
2. Add high-quality PDF
3. Generate and verify metadata
4. Submit pull request with both PDF and metadata
5. Include usage notes if special handling needed
