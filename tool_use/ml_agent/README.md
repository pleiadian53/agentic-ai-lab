## ML Agent: TCGA Tumor Classification with LLM Integration

A complete example of the **tool use pattern** combining machine learning and large language models. This agent uses XGBoost to classify tumors from TCGA gene expression data, with an LLM interface for natural language interaction.

### 🎯 What This Demonstrates

1. **ML Model Serving** - FastAPI service for tumor classification
2. **Tool Use Pattern** - LLM orchestrates ML predictions through function calling
3. **Real-World Data** - TCGA-inspired gene expression profiles
4. **Multi-Service Architecture** - ML service + LLM service working together

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
│         "Classify this tumor sample"                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              LLM Service (Port 8003)                    │
│  - Understands natural language                         │
│  - Orchestrates ML tools                                │
│  - Explains results                                     │
└────────────────────┬────────────────────────────────────┘
                     │ Calls ML tools
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ML Service (Port 8002)                     │
│  - Serves XGBoost model                                 │
│  - Predicts cancer type                                 │
│  - Returns probabilities & biomarkers                   │
└────────────────────┬────────────────────────────────────┘
                     │ Uses
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Trained XGBoost Model                          │
│  - 1000 gene features                                   │
│  - 5 cancer types (BRCA, LUAD, LUSC, PRAD, COAD)       │
│  - ~90% accuracy                                        │
└─────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```
ml_agent/
├── config.py                    # Configuration management
├── ml_tools.py                  # ML tools for LLM integration
├── README.md                    # This file
├── requirements.txt             # Python dependencies
│
├── scripts/
│   ├── download_tcga_data.py   # Download & preprocess TCGA data
│   └── train_model.py          # Train XGBoost classifier
│
├── server/
│   ├── ml_service.py           # FastAPI ML prediction service
│   ├── llm_service.py          # FastAPI LLM orchestration service
│   └── schemas.py              # Pydantic models
│
├── data/
│   ├── raw/                    # Raw TCGA data
│   └── processed/              # Preprocessed data
│
├── models/
│   ├── tumor_classifier.pkl    # Trained model
│   └── model_metadata.json     # Model info
│
└── notebooks/
    └── ml_agent_demo.ipynb     # Interactive demo
```

### 🚀 Quick Start

#### 1. Download and Prepare Data

```bash
cd tool_use/ml_agent
python scripts/download_tcga_data.py
```

This generates synthetic TCGA-like gene expression data for 5 cancer types.

**Output:**
```
✅ Generated 500 samples across 5 cancer types
✅ 5000 genes → 1000 top variable genes selected
✅ Data saved to data/processed/tcga_processed.csv
```

#### 2. Train the Model

```bash
python scripts/train_model.py
```

Trains an XGBoost classifier on the gene expression data.

**Output:**
```
Training XGBoost classifier...
Test Accuracy: 0.9200
Cross-validation: 0.8950 (+/- 0.0234)

Classification Report:
              precision    recall  f1-score   support
        BRCA     0.95      0.92      0.93        25
        LUAD     0.88      0.91      0.89        22
        LUSC     0.93      0.89      0.91        19
        PRAD     0.90      0.94      0.92        18
        COAD     0.92      0.93      0.92        16

✅ Model saved to models/tumor_classifier.pkl
```

#### 3. Start the ML Service

```bash
cd server
uvicorn ml_service:app --port 8002 --reload
```

**Terminal 1 - ML Service:**
```
INFO:     Uvicorn running on http://127.0.0.1:8002
INFO:     Model loaded successfully!
INFO:       Version: 1.0.0
INFO:       Classes: ['BRCA', 'COAD', 'LUAD', 'LUSC', 'PRAD']
INFO:       Features: 1000
```

#### 4. Start the LLM Service

```bash
# In a new terminal
cd server
uvicorn llm_service:app --port 8003 --reload
```

**Terminal 2 - LLM Service:**
```
INFO:     Uvicorn running on http://127.0.0.1:8003
INFO:     Application startup complete.
```

### 🧪 Usage Examples

#### Direct ML API

```bash
# Check ML service health
curl http://localhost:8002/health

# Get model info
curl http://localhost:8002/model/info

# Make a prediction
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gene_expression": {
      "GENE_00001": 5.23,
      "GENE_00002": 3.45,
      "GENE_00100": 7.89
    },
    "sample_id": "SAMPLE_001"
  }'
```

**Response:**
```json
{
  "predicted_cancer_type": "BRCA",
  "confidence": 0.87,
  "probabilities": {
    "BRCA": 0.87,
    "LUAD": 0.06,
    "LUSC": 0.03,
    "PRAD": 0.02,
    "COAD": 0.02
  },
  "sample_id": "SAMPLE_001",
  "top_biomarkers": [
    {"gene": "GENE_00234", "score": 0.0456},
    {"gene": "GENE_00567", "score": 0.0389},
    ...
  ]
}
```

#### Natural Language Interface (LLM)

```bash
# Ask about the model
curl -X POST http://localhost:8003/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What cancer types can you predict?"
  }'

# Get model information
curl -X POST http://localhost:8003/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tell me about the tumor classification model"
  }'

# Make a prediction with explanation
curl -X POST http://localhost:8003/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I have a sample with high expression of GENE_00234 and GENE_00567. What cancer type might this be?"
  }'
```

**LLM Response:**
```
Based on the gene expression profile you provided, I'll analyze this sample.

Let me check the model's prediction...

The model predicts this is most likely **Breast Invasive Carcinoma (BRCA)** 
with 87% confidence.

Here's what this means:
- BRCA is the most common type of breast cancer
- The high confidence (87%) suggests strong evidence for this classification
- The genes you mentioned (GENE_00234, GENE_00567) are among the top biomarkers

Other possibilities (with lower probabilities):
- Lung Adenocarcinoma (LUAD): 6%
- Lung Squamous Cell Carcinoma (LUSC): 3%

This prediction should be confirmed with additional clinical tests.
```

### 🔧 Configuration

Edit `config.py` or set environment variables:

```bash
# LLM Configuration
DEFAULT_LLM_MODEL=openai:gpt-4o
OPENAI_API_KEY=your_key_here

# Server Ports
ML_SERVER_PORT=8002
ML_LLM_SERVER_PORT=8003

# Model Configuration
N_TOP_GENES=1000
MODEL_TYPE=xgboost
```

### 📊 Cancer Types

The model predicts 5 TCGA cancer types:

| Code | Name | Description |
|------|------|-------------|
| **BRCA** | Breast Invasive Carcinoma | Most common breast cancer |
| **LUAD** | Lung Adenocarcinoma | Most common lung cancer |
| **LUSC** | Lung Squamous Cell Carcinoma | Non-small cell lung cancer |
| **PRAD** | Prostate Adenocarcinoma | Most common prostate cancer |
| **COAD** | Colon Adenocarcinoma | Most common colon cancer |

### 🎓 Key Concepts Demonstrated

#### 1. **Tool Use Pattern**

The LLM has access to ML tools as functions:

```python
# LLM can call these tools
tools = [
    ml_tools.predict_tumor_type,      # Make predictions
    ml_tools.get_model_info,          # Get model metadata
    ml_tools.get_cancer_types,        # List cancer types
    ml_tools.get_required_genes,      # List required genes
    ml_tools.check_ml_service_health  # Check service status
]
```

#### 2. **Multi-Service Architecture**

- **ML Service**: Stateless prediction API
- **LLM Service**: Orchestration and explanation layer
- **Separation of Concerns**: ML logic separate from NL interface

#### 3. **Real-World ML Pipeline**

```
Data Download → Preprocessing → Training → Serving → Inference
```

Each step is modular and can be run independently.

### 🧬 Gene Expression Data

The model uses **1000 top variable genes** selected from ~5000 total genes.

**Input Format:**
```json
{
  "gene_expression": {
    "GENE_00001": 5.23,  // Log-transformed expression value
    "GENE_00002": 3.45,
    "GENE_00003": 7.89,
    // ... 997 more genes
  }
}
```

**Missing genes** are handled gracefully (filled with 0).

### 📈 Model Performance

Typical performance on synthetic TCGA data:

- **Test Accuracy**: ~92%
- **Cross-Validation**: ~89% (±2%)
- **Per-Class F1**: 0.89-0.93

**Feature Importance:**
- Top 10 genes contribute ~40% of prediction power
- Model uses gradient boosting for robust predictions

### 🔍 API Documentation

Interactive API docs available at:

- **ML Service**: http://localhost:8002/docs
- **LLM Service**: http://localhost:8003/docs

### 🐛 Troubleshooting

**Model not found:**
```bash
# Train the model first
python scripts/train_model.py
```

**ML service unreachable:**
```bash
# Check if service is running
curl http://localhost:8002/health

# Restart service
uvicorn server.ml_service:app --port 8002 --reload
```

**Import errors:**
```bash
# Install in editable mode
cd /path/to/agentic-ai-lab
pip install -e .
```

### 🎯 Next Steps

1. **Try the notebook**: `notebooks/ml_agent_demo.ipynb`
2. **Integrate with real TCGA data**: Modify `download_tcga_data.py`
3. **Add more cancer types**: Update `TCGA_CANCER_TYPES` in config
4. **Try different models**: Change `MODEL_TYPE` to `random_forest` or `neural_network`
5. **Deploy to production**: Use Docker + Kubernetes

### 📚 Learn More

- **TCGA**: https://www.cancer.gov/tcga
- **XGBoost**: https://xgboost.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **AISuite**: https://github.com/andrewyng/aisuite

### 🤝 Integration with Other Agents

This ML agent can be combined with other agents:

```python
# Email agent + ML agent
"Send me an email with the tumor classification results"

# Research agent + ML agent  
"Research the top biomarkers and explain their role in cancer"
```

The tool use pattern makes agents composable! 🎉

---

**Built with**: Python, XGBoost, FastAPI, AISuite, TCGA data
