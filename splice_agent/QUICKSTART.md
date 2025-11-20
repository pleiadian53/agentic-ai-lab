# Splice Agent - Quick Start Guide

Get started with splice site analysis in 5 minutes!

## 📋 Prerequisites

1. **Python 3.9+**
2. **OpenAI API Key** - Get one at https://platform.openai.com/api-keys
3. **Splice Site Dataset** - TSV/CSV file with genomic coordinates

## 🚀 Installation

### Step 1: Set Up Environment

**Option A: Use Existing `agentic-ai` Environment (Recommended)**

```bash
# Activate the existing environment
mamba activate agentic-ai

# Navigate to splice_agent directory
cd splice_agent

# All dependencies are already installed!
```

**Option B: Create Standalone Environment**

```bash
# Create new conda environment
mamba create -n splice-agent python=3.11
mamba activate splice-agent

# Navigate to splice_agent directory
cd splice_agent

# Install dependencies
pip install -r requirements.txt
```

> **Note**: The `agentic-ai` environment already contains all required dependencies (OpenAI, FastAPI, DuckDB, matplotlib, pandas, seaborn, etc.), so you can use it directly for `splice_agent`.

### Step 2: Configure API Key

**Option A: Use Existing Project .env (Recommended)**

```bash
# The .env file at the project root (agentic-ai-lab/.env) is already used
# No action needed if OPENAI_API_KEY is already set there
```

**Option B: Create Local .env**

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

> **Note**: Python's `dotenv` will automatically search parent directories for `.env` files, so the project root `.env` will be found automatically.

### Step 3: Add Your Data

```bash
# Place your splice site dataset in the data/ directory
# Example: data/splice_sites_enhanced.tsv
```

## 🎯 Usage Options

### Option 1: REST API (Recommended)

**Start the service:**

```bash
cd server
python splice_service.py
```

**Access Swagger UI:**

Open http://localhost:8004/docs in your browser

**Try an analysis:**

1. Click on `/analyze/template`
2. Click "Try it out"
3. Use this example request:

```json
{
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "analysis_type": "high_alternative_splicing",
  "model": "gpt-4o-mini"
}
```

4. Click "Execute"
5. Copy the generated code from the response
6. Save it to a `.py` file and run it!

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
    client=client
)

# Save code
with open("analysis.py", "w") as f:
    f.write(result["chart_code"])

# Execute
exec(result["chart_code"])
```

### Option 3: Command-Line Tool

```bash
# Run quick start examples
python examples/quick_start.py

# Run full analysis suite
python -m splice_agent.examples.analyze_splice_sites \
    --data data/splice_sites_enhanced.tsv \
    --analysis all \
    --output-dir output/analyses
```

## 📊 Available Analyses

### 1. High Alternative Splicing
Identifies genes with the most splice sites (potential for alternative splicing)

```bash
analysis_type = "high_alternative_splicing"
```

### 2. Genomic Distribution
Visualizes splice site distribution across chromosomes

```bash
analysis_type = "splice_site_genomic_view"
```

### 3. Exon Complexity
Analyzes transcript structure by exon count

```bash
analysis_type = "exon_complexity"
```

### 4. Strand Bias
Analyzes strand distribution of splice sites

```bash
analysis_type = "strand_bias"
```

### 5. Transcript Diversity
Identifies genes with most transcript isoforms

```bash
analysis_type = "gene_transcript_diversity"
```

## 🔬 Custom Research Questions

Ask your own questions:

```python
from splice_agent.splice_analysis import generate_exploratory_insight

result = generate_exploratory_insight(
    dataset=dataset,
    research_question="How do splice sites distribute by gene biotype?",
    client=client
)
```

**Example questions:**
- "What is the relationship between gene length and splice site density?"
- "Which chromosomes have the highest alternative splicing rates?"
- "How do donor and acceptor sites differ in their genomic distribution?"

## 🌐 API Examples

### List Available Analyses

```bash
curl http://localhost:8004/analyses
```

### Template Analysis

```bash
curl -X POST http://localhost:8004/analyze/template \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "analysis_type": "high_alternative_splicing",
    "model": "gpt-4o-mini"
  }'
```

### Exploratory Analysis

```bash
curl -X POST http://localhost:8004/analyze/exploratory \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "research_question": "What is the distribution of splice sites across chromosomes?",
    "model": "gpt-4o-mini"
  }'
```

## 📁 Data Format

Your dataset should have these columns:

**Required:**
- `chrom` - Chromosome (chr1, chr2, ..., chrX, chrY)
- `position` - Genomic position
- `site_type` - donor or acceptor
- `strand` - + or -

**Optional:**
- `gene_name` - Gene symbol (TP53, BRCA1, etc.)
- `transcript_id` - Transcript identifier
- `exon_rank` - Exon number

**Example:**

```
chrom  position  site_type  strand  gene_name  transcript_id  exon_rank
chr1   12345     donor      +       TP53       NM_000546.6    5
chr1   12678     acceptor   +       TP53       NM_000546.6    6
```

## 🎓 Next Steps

1. **Try the examples** - Run `python examples/quick_start.py`
2. **Explore the API** - Open http://localhost:8004/docs
3. **Read the docs** - See [README.md](README.md) for detailed information
4. **Customize analyses** - Modify generated code to fit your needs
5. **Add new templates** - Extend `splice_analysis.py` with your own analyses

## 🐛 Troubleshooting

### API Key Not Found

```bash
# Make sure .env file exists and contains:
OPENAI_API_KEY=sk-your-actual-key-here

# Or export it:
export OPENAI_API_KEY=sk-your-actual-key-here
```

### Dataset Not Found

```bash
# Check the path is relative to project root
# Example: data/splice_sites_enhanced.tsv
# NOT: /full/path/to/data/splice_sites_enhanced.tsv
```

### Port Already in Use

```bash
# Change port in .env:
SPLICE_AGENT_PORT=8005

# Or in splice_service.py:
uvicorn.run(..., port=8005)
```

### Import Errors

```bash
# Make sure you're in the right environment
mamba activate splice-agent

# Reinstall dependencies
pip install -r requirements.txt
```

## 💡 Tips

1. **Start with templates** - Use predefined analyses before custom questions
2. **Review generated code** - Always check the code before executing
3. **Use appropriate models** - `gpt-4o-mini` for speed, `gpt-4o` for quality
4. **Cache datasets** - The API caches loaded datasets for performance
5. **Batch processing** - Generate multiple analyses at once for efficiency

## 📚 More Resources

- [Full README](README.md) - Complete documentation
- [API Reference](docs/API.md) - Detailed API documentation
- [Biology Background](docs/BIOLOGY.md) - Splice site biology primer
- [Examples](examples/) - More example scripts

---

**Questions?** Open an issue on GitHub or check the [documentation](README.md)!
