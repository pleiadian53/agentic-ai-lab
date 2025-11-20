# Chart Agent Examples

## Splice Site Analysis Driver

Domain-specific chart generation for genomic splice site data using guided LLM prompts.

### Quick Start

```bash
# Ensure API key is set
export OPENAI_API_KEY='your-key-here'
# Or it will auto-load from .env file

# Run all analyses
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis all

# Run with standard chromosomes only (recommended - excludes 1,340 sites on alt contigs)
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis all \
    --standard-only

# Run with reflection (uses same model for both generation and critique)
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis all \
    --reflect

# Run with reflection using different models (better critique quality)
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis all \
    --reflect \
    --model gpt-4o-mini \
    --reflection-model gpt-5.1

# Testing workflow: cheap model for generation, better model for critique
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis high_alternative_splicing \
    --model gpt-4o-mini \
    --reflect \
    --reflection-model gpt-5.1

# Run specific analysis
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis high_alternative_splicing

# Exploratory mode (custom question)
mamba run -n agentic-ai python -m chart_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis exploratory \
    --question "Which chromosomes have the most balanced donor/acceptor ratios?"
```

### Available Analyses

1. **high_alternative_splicing** - Top 20 genes with most splice sites (with exon complexity)
2. **splice_site_genomic_view** - Genomic position view with exon structure (chr17 TP53 region)
3. **site_type_distribution** - Donor vs acceptor by chromosome
4. **chromosome_coverage** - Splice site distribution across chromosomes
5. **exon_complexity_analysis** - Transcript complexity: exon count vs splice sites (NEW)
6. **top_genes_heatmap** - Heatmap of splice patterns in top genes

### Output

Generated chart code is saved to `output/splice_analysis/`:
- `high_alternative_splicing.py`
- `splice_site_genomic_view.py`
- `site_type_distribution.py`
- `chromosome_coverage.py`
- `exon_complexity_analysis.py`
- `top_genes_heatmap.py`

### Execute Generated Charts

```bash
cd output/splice_analysis
python high_alternative_splicing.py
```

### Options

```
--data PATH              Path to splice sites TSV file (default: data/splice_sites_enhanced.tsv)
--analysis TYPE          Analysis type: all, exploratory, or specific analysis name
--question TEXT          Research question for exploratory mode
--model MODEL            OpenAI model for code generation (default: gpt-4o-mini)
--reflection-model MODEL OpenAI model for reflection/critique (default: same as --model)
                         💡 Smart default: If --reflect is used without this flag,
                         the same model as --model will be used for both
--reflect                Enable reflection pattern: generate → critique → refine
                         Improves quality but increases cost and time
--max-iterations N       Maximum reflection iterations (default: 2)
--output-dir PATH        Output directory (default: output/splice_analysis)
--standard-only          Filter to standard chromosomes only (chr1-22, chrX, chrY)
                         Excludes 1,340 sites (0.4%) on alternative contigs/fix patches
                         Recommended for cleaner, faster analyses
```

### Smart Defaults

The script uses intelligent defaults to minimize verbosity:

1. **Reflection Model**: If `--reflect` is enabled without `--reflection-model`, it defaults to the same model as `--model`
   ```bash
   # These are equivalent:
   --reflect --model gpt-4o-mini
   --reflect --model gpt-4o-mini --reflection-model gpt-4o-mini
   ```

2. **Max Iterations**: Defaults to 2 iterations when `--reflect` is enabled

3. **Generation Model**: Defaults to `gpt-4o-mini` (cost-effective for development)

### Usage Patterns

**Quick prototyping** (simplest):
```bash
--analysis all --reflect
# Uses gpt-4o-mini for both generation and reflection
```

**Quality optimization** (recommended):
```bash
--analysis all --reflect --model gpt-4o-mini --reflection-model gpt-5.1
# Cheap generation, expensive critique
```

**Production** (highest quality):
```bash
--analysis all --reflect --model gpt-5.1
# Uses gpt-5.1 for both (most expensive)
```

### Key Features

- **Code-as-Plan Pattern**: LLM generates executable visualization code
- **Reflection Pattern**: Optional critique and refinement for higher quality
- **Flexible Model Selection**: Use different models for generation vs reflection
- **Template-Based Analysis**: Pre-defined SQL queries + visualization specs
- **Domain Context**: Genomic-specific prompts guide LLM
- **DuckDB Integration**: Efficient handling of 370K+ splice sites
- **Type Safety**: Handles mixed-type columns (chr: 1,2,3,X,Y)
- **Exploratory Mode**: Two-step LLM analysis for novel questions

### Dataset

MANE (Matched Annotation from NCBI and EBI) splice sites - GRCh38:
- **369,918 splice sites** from 18,200 genes and 18,264 transcripts
- **Perfectly balanced:** 184,959 donor + 184,959 acceptor sites
- **65 chromosomes:** 24 standard + 41 alternative/fix patches (99.6% on standard)
- **Exon information:** exon_rank field (1-363, avg 11.64 exons/transcript)
- **New columns:** `gene_name` (direct gene symbol), `exon_rank` (exon position)

See `data/splice_sites_enhanced_summary.md` for complete schema details.

### Troubleshooting

**API Key Error:**
```
export OPENAI_API_KEY='your-key-here'
```

**Environment:**
```bash
mamba activate agentic-ai
```
