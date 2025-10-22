# Chart Workflow Testing Guide

Guide for testing the refactored `reflection/chart_workflow` package with datasets of varying complexity.

## Overview

The chart workflow implements the **reflection design pattern** to generate high-quality, publication-ready visualizations through iterative refinement:

1. **Generate V1** - Initial chart from natural language instruction
2. **Execute** - Run generated code and create chart
3. **Reflect** - Multi-modal LLM critiques the visual output
4. **Refine V2** - Generate improved chart based on feedback

## Test Scripts

### 1. Quick Test (Bash Script)

**Purpose**: Fast validation with one simple and one complex dataset

**Prerequisites**:
```bash
# Activate the environment first
mamba activate agentic-ai
```

**Usage**:
```bash
./scripts/test_simple_workflow.sh
```

**What it tests**:
- ✅ Coffee sales quarterly comparison (simple temporal data)
- ✅ Splice sites distribution (complex genomic data)

**Output**: `test_outputs/quick_test/`

### 2. Comprehensive Test Suite (Python)

**Purpose**: Thorough testing with 7 different visualization scenarios

**Prerequisites**:
```bash
# Activate the environment first
mamba activate agentic-ai
```

**Usage**:
```bash
python scripts/test_chart_workflow.py
```

**What it tests**:

**Simple Dataset (Coffee Sales)**:
1. Quarterly comparison - Bar chart
2. Revenue trend - Line chart with moving average
3. Product distribution - Pie chart

**Complex Dataset (Splice Sites)**:
4. Type distribution by chromosome - Grouped bar chart
5. Strand distribution - Stacked bar chart
6. Positional analysis - Scatter plot
7. Gene biotype ranking - Horizontal bar chart

**Output**: `test_outputs/chart_workflow/`

### 3. Manual Testing (CLI Tool)

**Purpose**: Test specific scenarios interactively

**Prerequisites**:
```bash
# Activate the environment first
mamba activate agentic-ai
```

**Usage**:
```bash
python scripts/run_chart_workflow.py \
    "path/to/dataset.csv" \
    "Your chart instruction" \
    --generation-model "gpt-5.0-mini" \
    --reflection-model "o4-mini" \
    --output-dir "output/"
```

**Example - Coffee Sales**:
```bash
# After activating environment
python scripts/run_chart_workflow.py \
    "reflection/M2_UGL_1/coffee_sales.csv" \
    "Create a bar chart comparing Q1 coffee sales in 2024 and 2025" \
    --image-basename "coffee_comparison" \
    --output-dir "charts/"
```

**Example - Splice Sites**:
```bash
python scripts/run_chart_workflow.py \
    "data/splice_sites_enhanced.tsv" \
    "Create a scatter plot of splice site positions colored by type" \
    --image-basename "splice_positions" \
    --output-dir "charts/"
```

## Test Datasets

### 1. Simple Dataset: Coffee Sales

**File**: `reflection/M2_UGL_1/coffee_sales.csv`

**Schema**:
```
date, time, cash_type, card, price, coffee_name
```

**Characteristics**:
- Temporal data (dates, quarters)
- Categorical (coffee types, payment methods)
- Numerical (prices, quantities)
- ~1000 rows
- Clean, well-structured

**Good for testing**:
- Time series visualizations
- Categorical comparisons
- Aggregations and grouping
- Basic chart types (bar, line, pie)

### 2. Complex Dataset: Splice Sites

**File**: `data/splice_sites_enhanced.tsv`

**Schema**:
```
chrom, start, end, position, strand, site_type, gene_id, 
gene_name, gene_biotype, transcript_id, transcript_biotype, 
exon_id, exon_number, exon_rank
```

**Characteristics**:
- Multi-dimensional (14 columns)
- Genomic coordinates (chromosomes, positions)
- Hierarchical (genes → transcripts → exons)
- Categorical (site types, strands, biotypes)
- ~10,000+ rows
- Domain-specific (bioinformatics)

**Good for testing**:
- Complex multi-dimensional data
- Domain-specific terminology
- Large datasets
- Advanced chart types (scatter, heatmap, grouped/stacked bars)
- LLM's ability to understand biological context

## Expected Outcomes

### Quality Improvements (V1 → V2)

The reflection pattern should produce measurable improvements:

**Visual Design**:
- ✅ Better color choices (distinct, accessible)
- ✅ Improved labels (clear, non-overlapping)
- ✅ Added legends (when needed)
- ✅ Better axis formatting

**Data Representation**:
- ✅ Appropriate chart type for data
- ✅ Correct aggregations
- ✅ Proper scaling
- ✅ Meaningful groupings

**Publication Quality**:
- ✅ Professional appearance
- ✅ High DPI (300)
- ✅ Clear titles
- ✅ Interpretable without explanation

### Success Criteria

A successful test should show:

1. **V1 generates valid code** - No syntax errors
2. **V1 creates a chart** - PNG file exists
3. **Reflection provides feedback** - Specific, actionable critique
4. **V2 incorporates feedback** - Visible improvements
5. **V2 is publication-ready** - Professional quality

### Common Improvements

**Simple Dataset (Coffee)**:
- V1: Basic bar chart, default colors
- V2: Grouped bars, distinct colors, legend, formatted axes

**Complex Dataset (Splice Sites)**:
- V1: Overcrowded plot, unclear labels
- V2: Filtered data, clear categories, informative legend

## Troubleshooting

### API Key Issues

**Error**: `OpenAIError: The api_key client option must be set`

**Solution**:
```bash
# Ensure .env file exists with valid keys
cat .env | grep OPENAI_API_KEY

# If missing, copy from example
cp .env.example .env
# Edit .env and add your actual API key
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'reflection'`

**Solution**:
```bash
# Ensure you're in the project root
cd /Users/pleiadian53/work/agentic-ai-public

# Activate environment
mamba activate agentic-ai

# Run from project root
python scripts/test_chart_workflow.py
```

### Model Not Found

**Error**: `InvalidRequestError: The model 'gpt-5.0-mini' does not exist`

**Solution**:
```bash
# Use available models
--generation-model "gpt-4o-mini"
--reflection-model "gpt-4o"
```

### Dataset Not Found

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`

**Solution**:
```bash
# Use absolute paths or run from project root
cd /Users/pleiadian53/work/agentic-ai-public
python scripts/test_chart_workflow.py
```

## Evaluation Criteria

When reviewing generated charts, assess:

### 1. Technical Correctness
- [ ] Code executes without errors
- [ ] Data is loaded correctly
- [ ] Calculations are accurate
- [ ] Chart type matches data

### 2. Visual Quality
- [ ] Colors are distinct and accessible
- [ ] Labels are readable and non-overlapping
- [ ] Legend is present (when needed)
- [ ] Axes are properly formatted
- [ ] Title is descriptive

### 3. Reflection Effectiveness
- [ ] Feedback identifies real issues
- [ ] Feedback is specific and actionable
- [ ] V2 addresses feedback points
- [ ] V2 shows measurable improvement

### 4. Publication Readiness
- [ ] Professional appearance
- [ ] High resolution (300 DPI)
- [ ] Clear without explanation
- [ ] Suitable for papers/presentations

## Example Output Structure

```
test_outputs/
├── quick_test/
│   ├── coffee_sales/
│   │   ├── coffee_q1_comparison_v1.png
│   │   └── coffee_q1_comparison_v2.png
│   └── splice_sites/
│       ├── splice_sites_distribution_v1.png
│       └── splice_sites_distribution_v2.png
└── chart_workflow/
    ├── coffee_sales_-_quarterly_comparison/
    │   ├── chart_v1.png
    │   └── chart_v2.png
    ├── coffee_sales_-_revenue_trend/
    │   ├── chart_v1.png
    │   └── chart_v2.png
    └── splice_sites_-_type_distribution/
        ├── chart_v1.png
        └── chart_v2.png
```

## Next Steps

After testing:

1. **Review Charts** - Compare V1 vs V2 for each test
2. **Analyze Feedback** - Read reflection comments
3. **Document Issues** - Note any failures or poor results
4. **Iterate** - Refine prompts or workflow as needed
5. **Add Tests** - Create new test cases for edge cases

## See Also

- [Chart Workflow API](../reflection/docs/api/visualization.md)
- [Reflection Pattern Guide](../reflection/docs/guides/reflection-pattern.md)
- [Utils Documentation](../reflection/docs/api/utils.md)
