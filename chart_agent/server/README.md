# Chart Agent FastAPI Service

REST API for generative visualization with reflection and insight generation.

## Overview

The Chart Agent API provides a **Human-in-the-Loop** workflow for data visualization:

1. **Analyze** (`POST /analyze`) - Generate chart code from natural language
2. **Critique** (`POST /critique`) - Review code quality via reflection
3. **Execute** (`POST /execute`) - Run code to produce plots
4. **Insight** (`POST /insight`) - Generate captions and insights

## Architecture

```
┌─────────────┐
│   Client    │
│ (UI/Agent)  │
└──────┬──────┘
       │
       ├──POST /analyze──────────┐
       │                         │
       │  ┌──────────────────────▼─────────┐
       │  │  Chart Generator (LLM)         │
       │  │  - Loads dataset (cached)      │
       │  │  - Generates Python code       │
       │  └──────────────────────┬─────────┘
       │                         │
       │◄────code (plan)─────────┘
       │
       ├──POST /critique─────────┐
       │                         │
       │  ┌──────────────────────▼─────────┐
       │  │  Code Critic (Reflection)      │
       │  │  - Reviews code quality        │
       │  │  - Identifies issues           │
       │  └──────────────────────┬─────────┘
       │                         │
       │◄────critique────────────┘
       │
       ├──POST /execute──────────┐
       │                         │
       │  ┌──────────────────────▼─────────┐
       │  │  Code Executor                 │
       │  │  - Runs code safely            │
       │  │  - Generates PDF/PNG           │
       │  └──────────────────────┬─────────┘
       │                         │
       │◄────image_path──────────┘
       │
       └──POST /insight──────────┐
                                 │
          ┌──────────────────────▼─────────┐
          │  Insight Generator (LLM)       │
          │  - Analyzes plot               │
          │  - Generates caption           │
          └──────────────────────┬─────────┘
                                 │
          ◄────caption────────────┘
```

## Installation

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart openai python-dotenv

# Ensure chart_agent is in PYTHONPATH
export PYTHONPATH=/path/to/agentic-ai-lab:$PYTHONPATH
```

## Running the Service

```bash
# Start the server
cd chart_agent/server
python chart_service.py

# Or with uvicorn directly
uvicorn chart_service:app --host 0.0.0.0 --port 8003 --reload
```

The API will be available at `http://localhost:8003`

**Interactive docs:** `http://localhost:8003/docs`

## API Endpoints

### 1. Generate Chart Code

**Endpoint:** `POST /analyze`

**Request:**
```json
{
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "question": "Show the distribution of splice sites across chromosomes",
  "context": "Focus on standard chromosomes only",
  "model": "gpt-4o-mini"
}
```

**Response:**
```json
{
  "code": "import matplotlib.pyplot as plt\nimport seaborn as sns\n...",
  "explanation": "This chart shows...",
  "libraries_used": ["matplotlib", "seaborn", "pandas"]
}
```

### 2. Critique Code

**Endpoint:** `POST /critique`

**Request:**
```json
{
  "code": "import matplotlib.pyplot as plt\n...",
  "domain_context": "Genomic splice site analysis",
  "model": "gpt-5.1-codex-mini"
}
```

**Response:**
```json
{
  "quality": "good",
  "strengths": ["Clear labels", "Proper filtering"],
  "issues": [
    {
      "severity": "minor",
      "issue": "Color scheme not colorblind-friendly",
      "suggestion": "Use seaborn colorblind palette"
    }
  ],
  "needs_refinement": true
}
```

### 3. Execute Code

**Endpoint:** `POST /execute`

**Request:**
```json
{
  "code": "import matplotlib.pyplot as plt\n...",
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "output_format": "pdf"
}
```

**Response:**
```json
{
  "success": true,
  "image_path": "/charts/chart_1234.pdf",
  "logs": "Execution completed successfully"
}
```

### 4. Generate Insights

**Endpoint:** `POST /insight`

**Request:**
```json
{
  "analysis_title": "Splice Site Distribution",
  "image_path": "/charts/chart_1234.pdf",
  "dataset_context": "MANE splice sites (369,918 sites, 18,200 genes)",
  "model": "gpt-5.1-codex-mini"
}
```

**Response:**
```json
{
  "caption": "Figure 1. Splice Site Distribution Across Chromosomes. The plot shows...",
  "key_insights": [
    "Chromosome 1 has the highest density of splice sites",
    "Donor and acceptor sites are perfectly balanced",
    "Alternative contigs show sparse coverage"
  ]
}
```

### 5. List Datasets

**Endpoint:** `GET /datasets`

**Response:**
```json
{
  "datasets": [
    {
      "path": "data/splice_sites_enhanced.tsv",
      "name": "splice_sites_enhanced",
      "size_mb": 45.2,
      "cached": true
    }
  ],
  "total": 1,
  "cached": 1
}
```

## Example Workflow

### Python Client

```python
import requests

BASE_URL = "http://localhost:8003"

# Step 1: Generate code
response = requests.post(f"{BASE_URL}/analyze", json={
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show genes with most splice sites",
    "model": "gpt-4o-mini"
})
plan = response.json()
print("Generated code:")
print(plan["code"])

# Step 2: Critique (optional)
response = requests.post(f"{BASE_URL}/critique", json={
    "code": plan["code"],
    "domain_context": "Genomic analysis",
    "model": "gpt-4o-mini"
})
critique = response.json()
print(f"Quality: {critique['quality']}")
print(f"Issues: {len(critique['issues'])}")

# Step 3: Execute
response = requests.post(f"{BASE_URL}/execute", json={
    "code": plan["code"],
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "output_format": "pdf"
})
result = response.json()
if result["success"]:
    print(f"Chart saved: {result['image_path']}")
    
    # Step 4: Generate insights
    response = requests.post(f"{BASE_URL}/insight", json={
        "analysis_title": "Genes with Most Splice Sites",
        "image_path": result["image_path"],
        "dataset_context": "MANE splice sites dataset"
    })
    insight = response.json()
    print(f"Caption: {insight['caption']}")
```

### cURL Examples

```bash
# Generate code
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show splice site distribution",
    "model": "gpt-4o-mini"
  }'

# Execute code
curl -X POST http://localhost:8003/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import matplotlib.pyplot as plt\n...",
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "output_format": "pdf"
  }'

# Get chart
curl http://localhost:8003/charts/chart_1234.pdf -o chart.pdf
```

## Features

### 1. Dataset Caching
- Datasets are loaded once and cached in memory
- Subsequent requests reuse the cached dataset
- Efficient for large datasets (300k+ rows)

### 2. Model Flexibility
- Support for GPT-4, GPT-5 series
- Unified client handles both Chat Completions and Responses API
- Model selection per request

### 3. Human-in-the-Loop
- Generate code first, review before execution
- Critique provides structured feedback
- User can modify code before execution

### 4. Safe Execution
- Code runs in isolated namespace
- Captures stdout/stderr for debugging
- Non-interactive matplotlib backend

### 5. Publication-Ready Output
- PDF (vector) or PNG (raster) formats
- 300 DPI for PNG
- Proper styling with seaborn

## Configuration

Environment variables (`.env`):
```bash
OPENAI_API_KEY=your-key-here
```

## Error Handling

The API uses standard HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Dataset not found
- `500` - Internal error (execution failed)
- `503` - Service not ready (OpenAI client not initialized)

## Comparison with ML Agent

| Feature | ML Agent | Chart Agent |
|---------|----------|-------------|
| **Type** | Classifier | Generator |
| **Input** | Gene expression values | Natural language question |
| **Output** | Prediction + confidence | Code + plot + insights |
| **State** | Model weights (static) | Dataset (cached) |
| **Pattern** | Inference | Planning + Reflection |
| **Latency** | <100ms | 5-30s (LLM generation) |
| **Human-in-Loop** | No | Yes (review code) |

## Future Enhancements

1. **Streaming**: Stream code generation token-by-token
2. **Batch Analysis**: Generate multiple plots in one request
3. **Templates**: Pre-defined analysis templates
4. **History**: Store and retrieve previous analyses
5. **Collaboration**: Multi-user sessions
6. **Authentication**: API key management

## Troubleshooting

### Service won't start
```bash
# Check if port 8003 is available
lsof -i :8003

# Check OpenAI API key
echo $OPENAI_API_KEY
```

### Dataset not loading
```bash
# Verify dataset exists
ls -lh data/splice_sites_enhanced.tsv

# Check file permissions
chmod 644 data/splice_sites_enhanced.tsv
```

### Code execution fails
- Check logs in the `ExecutionResponse`
- Verify all required libraries are installed
- Ensure dataset schema matches code expectations

## License

Same as parent project (agentic-ai-lab).
