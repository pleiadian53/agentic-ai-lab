# Quick Start Guide

Get up and running with the research agent in 5 minutes.

## Prerequisites

- Python 3.11+ (via mamba/conda)
- OpenAI API key
- Mamba or conda installed

## 1. Setup Environment

```bash
# Clone or navigate to the project
cd /path/to/agentic-ai-lab

# Create environment with all dependencies (including PDF generation)
mamba env create -f environment.yml

# Activate environment
mamba activate agentic-ai
```

## 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_key_here
EOF
```

## 3. Run Your First Essay

### Simple Topic (800-1500 words)

```bash
python scripts/run_reflection_research_agent.py \
    "What are the best practices for making chicken soup?"
```

### Technical Topic (4000-6000 words with PDF)

```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems" \
    --generate-pdf \
    --max-iterations 3 \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_technical_ingredients
```

## 4. View Your Results

Essays are saved in multiple formats:

```
essays/
└── [output-dir]/
    ├── [basename]_final.txt      # Formatted text (88-char line wrapping)
    ├── [basename]_final.md       # Markdown with metadata
    ├── [basename]_final.pdf      # PDF (if --generate-pdf used)
    ├── [basename]_v1.txt         # Initial draft
    ├── [basename]_v2.txt         # Revised version
    └── [basename]_feedback.md    # Complete feedback history
```

## Common Use Cases

### Recipe or How-To (800-1500 words)

```bash
python scripts/run_reflection_research_agent.py \
    "How to brew the perfect cup of coffee"
```

### Blog Post (1500-3000 words)

```bash
python scripts/run_reflection_research_agent.py \
    "The impact of remote work on productivity" \
    --min-words 1500 \
    --max-words 3000
```

### Research Paper (4000-6000 words)

```bash
python scripts/run_reflection_research_agent.py \
    "Quantum computing applications in cryptography" \
    --generate-pdf \
    --min-words 4000 \
    --max-words 6000 \
    --max-iterations 3
```

### Custom Models

```bash
python scripts/run_reflection_research_agent.py \
    "Your topic here" \
    --draft-model "openai:gpt-4o-mini" \
    --reflection-model "openai:o1-mini" \
    --revision-model "openai:gpt-4o"
```

## Key Options

| Option | Default | Description |
|--------|---------|-------------|
| `--min-words` | 800 | Minimum word count |
| `--max-words` | 6000 | Maximum word count |
| `--max-iterations` | 2 | Number of refinement cycles |
| `--generate-pdf` | False | Generate PDF output |
| `--wrap-width` | 88 | Line width for text wrapping |
| `--output-dir` | `./essays` | Output directory |

## Troubleshooting

### PDF Generation Fails

If you see errors about missing libraries:

```bash
# WeasyPrint should already be installed via environment.yml
# Verify it's working:
python -c "import weasyprint; print('✅ WeasyPrint OK')"

# If not, reinstall:
mamba install -c conda-forge weasyprint
```

### API Key Not Found

```bash
# Check .env file exists
ls -la .env

# Verify it contains your key
cat .env | grep OPENAI_API_KEY
```

### Essays Too Short/Long

Adjust word count parameters:

```bash
# For simple topics
--min-words 800 --max-words 1500

# For complex topics
--min-words 3000 --max-words 6000
```

## Next Steps

- **Full Documentation**: See `reflection/research_agent/README.md`
- **Word Count Philosophy**: See `essays/WORD_COUNT_PHILOSOPHY.md`
- **Usage Examples**: See `USAGE_GUIDE.md`
- **Environment Setup**: See `docs/installation/ENVIRONMENT_SETUP.md`

## Demo Scripts

Test the formatting without API calls:

```bash
# Demo text wrapping and markdown formatting
python scripts/demo_formatting.py

# Reformat existing essays
python scripts/test_formatting.py
```

## Example Output

After running the command, you'll see:

```
================================================================================
Research Agent: Reflection Pattern
================================================================================

🔧 Configuration:
   Topic: Your topic here
   Draft model: openai:gpt-4o-mini
   Reflection model: openai:gpt-4o
   Revision model: openai:gpt-4o
   Max iterations: 2
   Word count range: 800-6000
   Generate PDF: True

⚙️  Initializing workflow
⚙️  Starting draft-reflect-revise cycle: 2 iteration(s) max

[Progress updates...]

✨ Research agent workflow completed successfully!

📁 Output Files:
   • essay_final.txt (final essay)
   • essay_final.md
   • essay_final.pdf
   • essay_v1.txt
   • essay_v2.txt
   • essay_feedback.md (feedback and iterations)
```

## Tips

1. **Start simple**: Try a basic topic first to verify setup
2. **Use PDF for sharing**: `--generate-pdf` creates professional output
3. **Adjust iterations**: Complex topics benefit from `--max-iterations 3`
4. **Check feedback**: Review `*_feedback.md` to see the reflection process
5. **Customize word counts**: Match the range to your topic complexity

## Getting Help

```bash
# See all available options
python scripts/run_reflection_research_agent.py --help

# View examples in help text
python scripts/run_reflection_research_agent.py -h
```

---

**Ready to generate your first essay?** Run the simple example above and check the `essays/` directory for your results! 🚀
