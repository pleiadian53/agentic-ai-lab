# Chart Agent API - Quick Start Guide

Get the Chart Agent API running in 5 minutes.

## Prerequisites

```bash
# Python 3.8+
python --version

# Required packages
pip install fastapi uvicorn openai python-dotenv duckdb pandas matplotlib seaborn
```

## Step 1: Set API Key

```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Or export directly
export OPENAI_API_KEY='your-key-here'
```

## Step 2: Start Service

```bash
cd chart_agent/server
python chart_service.py
```

You should see:
```
INFO:     Will watch for changes in these directories: ['/Users/.../chart_agent/server']
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:chart_service:Starting Chart Agent API...
INFO:chart_service:✓ OpenAI client initialized
INFO:chart_service:✓ Output directory: output/api_charts
INFO:chart_service:Chart Agent API ready!
INFO:     Application startup complete.
```

## Step 3: Test It

Open another terminal:

```bash
# Test health
curl http://localhost:8003/health

# List datasets
curl http://localhost:8003/datasets
```

## Step 4: Generate Your First Chart

```python
import requests

# Generate code
response = requests.post("http://localhost:8003/analyze", json={
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show the distribution of splice sites across chromosomes",
    "model": "gpt-4o-mini"
})

plan = response.json()
print("Generated code:")
print(plan["code"][:200], "...")

# Execute code
response = requests.post("http://localhost:8003/execute", json={
    "code": plan["code"],
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "output_format": "pdf"
})

result = response.json()
if result["success"]:
    print(f"✓ Chart created: http://localhost:8003{result['image_path']}")
else:
    print(f"✗ Failed: {result['error']}")
```

## Step 5: View Interactive Docs

Open your browser:

```
http://localhost:8003/docs
```

This shows the Swagger UI where you can test all endpoints interactively.

## Common Issues

### Port already in use

```bash
# Find what's using port 8003
lsof -i :8003

# Kill it or use a different port
python chart_service.py --port 8004
```

### OpenAI API key not found

```bash
# Verify it's set
echo $OPENAI_API_KEY

# Or check .env file
cat .env
```

### Dataset not found

```bash
# Verify dataset exists
ls -lh data/splice_sites_enhanced.tsv

# Check from project root
cd /path/to/agentic-ai-lab
ls -lh data/splice_sites_enhanced.tsv
```

## Next Steps

- Read [README.md](README.md) for complete API documentation
- See [INTEGRATION.md](INTEGRATION.md) for integration examples
- Run [test_client.py](test_client.py) for full workflow demo
- Check [SUMMARY.md](SUMMARY.md) for architecture overview

## Quick Examples

### Python

```python
import requests

BASE = "http://localhost:8003"

# Quick chart
def quick_chart(question):
    plan = requests.post(f"{BASE}/analyze", json={
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "question": question
    }).json()
    
    result = requests.post(f"{BASE}/execute", json={
        "code": plan["code"],
        "dataset_path": "data/splice_sites_enhanced.tsv"
    }).json()
    
    return f"{BASE}{result['image_path']}"

# Use it
url = quick_chart("Show top genes by splice site count")
print(f"Chart: {url}")
```

### cURL

```bash
# Generate code
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show splice site distribution"
  }' | jq .code

# Execute (save code to file first)
curl -X POST http://localhost:8003/execute \
  -H "Content-Type: application/json" \
  -d @request.json
```

### JavaScript

```javascript
// Generate and execute
async function generateChart(question) {
  // Generate code
  const planRes = await fetch('http://localhost:8003/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset_path: 'data/splice_sites_enhanced.tsv',
      question: question
    })
  });
  const plan = await planRes.json();
  
  // Execute
  const execRes = await fetch('http://localhost:8003/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code: plan.code,
      dataset_path: 'data/splice_sites_enhanced.tsv',
      output_format: 'png'
    })
  });
  const result = await execRes.json();
  
  return `http://localhost:8003${result.image_path}`;
}

// Use it
generateChart('Show top 10 genes').then(url => {
  console.log('Chart:', url);
  document.getElementById('chart').src = url;
});
```

## That's It!

You now have a running Chart Agent API. The service can:

- ✅ Generate chart code from natural language
- ✅ Critique code quality
- ✅ Execute code safely
- ✅ Generate publication-ready PDFs
- ✅ Create AI-generated captions

Happy charting! 📊
