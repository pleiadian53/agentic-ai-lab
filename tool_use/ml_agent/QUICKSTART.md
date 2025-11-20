# ML Agent Quick Start

Get the TCGA tumor classification agent running in 5 minutes!

## Prerequisites

- Python 3.10+ with `agentic-ai` environment activated
- Project installed in editable mode: `pip install -e .`
- OpenAI API key configured in project root `.env`

## Step 1: Download and Prepare Data (2 min)

```bash
cd tool_use/ml_agent
python scripts/download_tcga_data.py
```

**What this does:**
- Generates synthetic TCGA-like gene expression data
- Creates 500 samples across 5 cancer types
- Selects top 1000 variable genes
- Saves to `data/processed/tcga_processed.csv`

## Step 2: Train the Model (3 min)

```bash
python scripts/train_model.py
```

**What this does:**
- Trains XGBoost classifier on gene expression data
- Achieves ~92% accuracy
- Saves model to `models/tumor_classifier.pkl`
- Generates feature importance rankings

## Step 3: Start the Services

### Terminal 1 - ML Service

```bash
cd server
uvicorn ml_service:app --port 8002 --reload
```

Visit: <http://localhost:8002/docs> for interactive API docs

### Terminal 2 - LLM Service

```bash
cd server
uvicorn llm_service:app --port 8003 --reload
```

Visit: <http://localhost:8003/docs> for LLM interface docs

## Step 4: Test It!

### Test ML API Directly

```bash
# Get model info
curl http://localhost:8002/model/info

# Check health
curl http://localhost:8002/health
```

### Test with Natural Language

```bash
curl -X POST http://localhost:8003/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What cancer types can you predict?"}'
```

## What You Can Do

### Ask the LLM

- "What cancer types can you predict?"
- "Tell me about the tumor classification model"
- "How accurate is the model?"
- "What genes are most important for prediction?"

### Make Predictions

The LLM can orchestrate predictions through natural language!

**Example:**
```bash
curl -X POST http://localhost:8003/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I have a tumor sample. Can you help me classify it?"
  }'
```

The LLM will:
1. Check if ML service is healthy
2. Ask for gene expression data (or use example)
3. Call the prediction API
4. Explain the results in plain language

## Architecture

```
User Request
    ↓
LLM Service (Port 8003)
    ↓ (calls ML tools)
ML Service (Port 8002)
    ↓ (uses)
XGBoost Model
```

## Next Steps

1. **Explore the API docs**: <http://localhost:8002/docs>
2. **Try different prompts**: Ask the LLM about cancer types, biomarkers, etc.
3. **Check the README**: Full documentation in `README.md`
4. **Integrate with other agents**: Combine with email_agent or research_agent

## Troubleshooting

**Model not found?**

```bash
python scripts/train_model.py
```

**Service won't start?**

```bash
# Check if port is in use
lsof -i :8002
lsof -i :8003
```

**Import errors?**

```bash
cd /path/to/agentic-ai-lab
pip install -e .
```

## Summary

You now have a complete ML + LLM system that can:

✅ Classify tumors from gene expression data  
✅ Respond to natural language queries  
✅ Explain predictions in plain language  
✅ Orchestrate ML tools through LLM function calling  

This demonstrates the **tool use pattern** - LLMs orchestrating specialized ML models! 🎉
