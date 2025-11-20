# Splice Agent - AI-Powered Splice Site Analysis

**Splice Agent** is a specialized framework for genomic splice site prediction and analysis using Large Language Models (LLMs). Built on the Chart Agent foundation, it provides domain-specific tools for alternative splicing research, transcript structure analysis, and biological insight generation.

## 🎯 Key Features

- **🧬 Domain-Specific Analysis** - Predefined templates for common splice site analyses
- **🤖 AI-Powered Insights** - LLM-generated visualizations with biological context
- **📊 Publication-Ready Charts** - High-quality plots using matplotlib/seaborn
- **🔬 Exploratory Research** - Ask custom questions about your splice site data
- **🚀 REST API** - FastAPI service for integration with other tools
- **📈 Code-as-Plan** - Generate executable Python code for reproducibility

## 🧬 What is Splice Site Analysis?

Splice sites are genomic positions where introns are removed during RNA splicing. Understanding splice site patterns is crucial for:

- **Alternative Splicing Research** - Protein diversity and gene regulation
- **Transcript Annotation** - Identifying and validating transcript structures
- **Disease Genomics** - Splice site mutations in genetic disorders
- **Drug Discovery** - Targeting splicing mechanisms
- **Evolutionary Biology** - Splice site conservation across species

## 🚀 Quick Start

### Option 1: REST API Service (Recommended)

**Start the service:**

```bash
cd splice_agent/server
mamba run -n agentic-ai python splice_service.py
```

**Access the API:**
- Swagger UI: http://localhost:8004/docs
- API Root: http://localhost:8004

**Example API call:**

```bash
curl -X POST http://localhost:8004/analyze/template \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "analysis_type": "high_alternative_splicing",
    "model": "gpt-4o-mini"
  }'
```

### Option 2: Python Library

```python
from splice_agent import create_dataset
from splice_agent.splice_analysis import generate_analysis_insight
from openai import OpenAI

# Load dataset
dataset = create_dataset("data/splice_sites_enhanced.tsv")

# Generate analysis
client = OpenAI()
result = generate_analysis_insight(
    dataset=dataset,
    analysis_type="high_alternative_splicing",
    client=client,
    model="gpt-4o-mini"
)

# Save and execute code
with open("analysis.py", "w") as f:
    f.write(result["chart_code"])

# Execute to generate chart
exec(result["chart_code"])
```

## 📊 Predefined Analysis Templates

### 1. High Alternative Splicing
**Identifies genes with the most splice sites**

Genes with many splice sites often undergo extensive alternative splicing, crucial for protein diversity.

```python
analysis_type = "high_alternative_splicing"
```

### 2. Genomic Distribution
**Visualizes splice site distribution across chromosomes**

Reveals gene density and transcript complexity patterns across the genome.

```python
analysis_type = "splice_site_genomic_view"
```

### 3. Exon Complexity
**Analyzes transcript structure by exon count**

Shows relationship between exon count and splice site density.

```python
analysis_type = "exon_complexity"
```

### 4. Strand Bias
**Analyzes strand distribution of splice sites**

Reveals genomic organization and potential annotation biases.

```python
analysis_type = "strand_bias"
```

### 5. Transcript Diversity
**Identifies genes with most transcript isoforms**

High transcript diversity indicates complex alternative splicing patterns.

```python
analysis_type = "gene_transcript_diversity"
```

## 🔬 Exploratory Analysis

Ask custom research questions:

```python
from splice_agent.splice_analysis import generate_exploratory_insight

result = generate_exploratory_insight(
    dataset=dataset,
    research_question="What is the relationship between gene length and splice site density?",
    client=client
)
```

**Example questions:**
- "How do splice sites distribute across different gene biotypes?"
- "Which chromosomes have the highest alternative splicing rates?"
- "What is the average exon count for highly expressed genes?"
- "Are there differences in splice site patterns between coding and non-coding RNAs?"

## 📦 Installation

### Prerequisites

```bash
# Python 3.9+
python --version

# Use existing agentic-ai environment (recommended)
mamba activate agentic-ai

# OR create new environment
mamba create -n splice-agent python=3.11
mamba activate splice-agent
```

### Install Dependencies

**If using `agentic-ai` environment:**
```bash
# No installation needed - all dependencies already present!
cd splice_agent
```

**If using new environment:**
```bash
cd splice_agent
pip install -r requirements.txt
```

> **Note**: The `splice_agent` uses the same dependencies as `chart_agent`, so the existing `agentic-ai` environment (defined in `environment.yml` and `pyproject.toml`) already has everything needed.

### Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

## 🗂️ Project Structure

```
splice_agent/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── data_access.py               # Dataset loading and querying
├── planning.py                  # Chart code generation
├── llm_client.py                # OpenAI API client
├── utils.py                     # Utility functions
├── splice_analysis.py           # Splice-specific analysis templates
│
├── server/                      # FastAPI service
│   ├── splice_service.py        # Main API service
│   ├── schemas.py               # Pydantic models
│   ├── config.py                # Configuration
│   └── manage.py                # Service management
│
├── examples/                    # Example scripts
│   ├── analyze_splice_sites.py  # CLI analysis tool
│   └── quick_start.py           # Quick start examples
│
├── data/                        # Data directory (add your datasets)
│   └── splice_sites_enhanced.tsv
│
├── docs/                        # Documentation
│   ├── API.md                   # API documentation
│   ├── BIOLOGY.md               # Biological background
│   └── TUTORIAL.md              # Step-by-step tutorial
│
└── tests/                       # Unit tests
    └── test_splice_analysis.py
```

## 🧪 Example Workflow

### 1. Load Your Data

```python
from splice_agent import create_dataset

# Supports TSV, CSV, Parquet, SQLite
dataset = create_dataset("data/splice_sites_enhanced.tsv")

# Inspect schema
print(dataset.get_schema_description())
```

### 2. Generate Analysis

```python
from splice_agent.splice_analysis import generate_analysis_insight
from openai import OpenAI

client = OpenAI()

# Use predefined template
result = generate_analysis_insight(
    dataset=dataset,
    analysis_type="high_alternative_splicing",
    client=client,
    model="gpt-4o-mini"
)

print(f"Title: {result['title']}")
print(f"Description: {result['description']}")
print(f"\nGenerated code:\n{result['chart_code']}")
```

### 3. Execute and Visualize

```python
# Save code
with open("splice_analysis.py", "w") as f:
    f.write(result["chart_code"])

# Execute
exec(result["chart_code"])
# This generates and displays the chart
```

### 4. Customize and Iterate

```python
# Review the generated code
# Modify as needed
# Re-execute

# Or use reflection for automated refinement
result = generate_analysis_insight(
    dataset=dataset,
    analysis_type="high_alternative_splicing",
    client=client,
    enable_reflection=True,
    max_iterations=3
)
```

## 🌐 API Endpoints

### GET /analyses
List available analysis templates

```bash
curl http://localhost:8004/analyses
```

### POST /analyze/template
Generate analysis using predefined template

```bash
curl -X POST http://localhost:8004/analyze/template \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "analysis_type": "high_alternative_splicing",
    "model": "gpt-4o-mini"
  }'
```

### POST /analyze/exploratory
Generate custom exploratory analysis

```bash
curl -X POST http://localhost:8004/analyze/exploratory \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "research_question": "What is the distribution of splice sites by chromosome?",
    "model": "gpt-4o-mini"
  }'
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
SPLICE_AGENT_PORT=8004
SPLICE_AGENT_HOST=0.0.0.0
SPLICE_AGENT_DATA_DIR=data/
SPLICE_AGENT_OUTPUT_DIR=output/splice_charts
```

### Supported Models

- `gpt-4o-mini` - Fast and cost-effective (default)
- `gpt-4o` - More capable for complex analyses
- `gpt-5-mini` - Latest fast model
- `gpt-5` - Latest capable model
- `gpt-5.1-codex-mini` - Optimized for code generation

## 📚 Data Format

Splice Agent expects datasets with the following columns:

**Required:**
- `chrom` - Chromosome (e.g., chr1, chr2, ..., chrX, chrY)
- `position` - Genomic position (0-based or 1-based)
- `site_type` - Splice site type (donor or acceptor)
- `strand` - Strand (+ or -)

**Optional but recommended:**
- `gene_name` - Gene symbol (e.g., TP53, BRCA1)
- `gene_id` - Gene identifier
- `transcript_id` - Transcript identifier
- `exon_rank` - Exon number in transcript

**Example data:**

```tsv
chrom	position	site_type	strand	gene_name	transcript_id	exon_rank
chr1	12345	donor	+	TP53	NM_000546.6	5
chr1	12678	acceptor	+	TP53	NM_000546.6	6
```

## 🎓 Learning Resources

### Documentation
- [API Documentation](docs/API.md) - Complete API reference
- [Biology Background](docs/BIOLOGY.md) - Splice site biology primer
- [Tutorial](docs/TUTORIAL.md) - Step-by-step guide

### Examples
- [analyze_splice_sites.py](examples/analyze_splice_sites.py) - Full CLI tool
- [quick_start.py](examples/quick_start.py) - Quick examples

### Related Projects
- [Chart Agent](../chart_agent/README.md) - General-purpose chart generation
- [Bio-Agentic-AI](https://github.com/yourusername/bio-agentic-ai) - Multi-omics analysis suite

## 🤝 Contributing

Splice Agent is designed to be extensible. Contributions welcome!

**Add new analysis templates:**
1. Add template to `splice_analysis.py::ANALYSIS_TEMPLATES`
2. Include SQL query, chart prompt, and biological context
3. Test with sample data
4. Submit PR

**Add new data sources:**
1. Implement `ChartDataset` interface in `data_access.py`
2. Add format detection logic
3. Test with real data
4. Submit PR

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built on [Chart Agent](../chart_agent) framework
- Powered by OpenAI GPT models
- Inspired by genomics research community

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: your.email@example.com

## 🚀 Future Enhancements

- [ ] Splice site prediction models (MaxEntScan, SpliceAI)
- [ ] Sequence motif analysis
- [ ] Conservation scoring
- [ ] Mutation impact prediction
- [ ] Integration with genomic databases (Ensembl, UCSC)
- [ ] Batch processing for multiple datasets
- [ ] Interactive dashboards
- [ ] Export to publication formats

## 🔬 Use Cases

### Alternative Splicing Research
Identify genes with complex splicing patterns and analyze isoform diversity.

### Transcript Annotation
Validate and refine transcript structures using splice site patterns.

### Disease Genomics
Analyze splice site mutations and their impact on gene expression.

### Drug Discovery
Target splicing mechanisms for therapeutic intervention.

### Evolutionary Biology
Study splice site conservation and evolution across species.

---

**Ready to analyze splice sites?** Start with the [Quick Start](#-quick-start) guide or explore the [API documentation](docs/API.md)!
