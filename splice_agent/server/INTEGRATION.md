# Chart Agent API Integration Guide

This guide shows how to integrate the Chart Agent API into your applications.

## Quick Start

### 1. Start the Service

```bash
cd chart_agent/server
python chart_service.py
```

Service runs on `http://localhost:8003`

### 2. Basic Usage

```python
import requests

# Generate chart code
response = requests.post("http://localhost:8003/analyze", json={
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show splice site distribution across chromosomes"
})

code = response.json()["code"]

# Execute code
response = requests.post("http://localhost:8003/execute", json={
    "code": code,
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "output_format": "pdf"
})

image_url = response.json()["image_path"]
print(f"Chart available at: http://localhost:8003{image_url}")
```

## Integration Patterns

### Pattern 1: Direct Generation (Fast)

**Use Case:** Quick exploratory analysis, prototyping

```python
def quick_chart(question: str, dataset: str):
    """Generate and execute chart in one step"""
    # Generate
    plan = requests.post(f"{BASE_URL}/analyze", json={
        "dataset_path": dataset,
        "question": question,
        "model": "gpt-4o-mini"  # Fast model
    }).json()
    
    # Execute immediately
    result = requests.post(f"{BASE_URL}/execute", json={
        "code": plan["code"],
        "dataset_path": dataset,
        "output_format": "png"
    }).json()
    
    return result["image_path"]
```

### Pattern 2: Human-in-the-Loop (Quality)

**Use Case:** Publication-ready figures, critical analysis

```python
def reviewed_chart(question: str, dataset: str):
    """Generate, review, optionally refine, then execute"""
    # Step 1: Generate
    plan = requests.post(f"{BASE_URL}/analyze", json={
        "dataset_path": dataset,
        "question": question,
        "model": "gpt-4o-mini"
    }).json()
    
    # Step 2: Critique
    critique = requests.post(f"{BASE_URL}/critique", json={
        "code": plan["code"],
        "domain_context": "Genomic analysis",
        "model": "gpt-5.1-codex-mini"  # Better critique
    }).json()
    
    # Step 3: Human review
    print(f"Quality: {critique['quality']}")
    print(f"Issues: {len(critique['issues'])}")
    
    if critique["needs_refinement"]:
        # Option A: Show issues to user, let them edit code
        # Option B: Auto-refine with another LLM call
        pass
    
    # Step 4: Execute
    result = requests.post(f"{BASE_URL}/execute", json={
        "code": plan["code"],
        "dataset_path": dataset,
        "output_format": "pdf"
    }).json()
    
    # Step 5: Generate caption
    insight = requests.post(f"{BASE_URL}/insight", json={
        "analysis_title": question,
        "image_path": result["image_path"],
        "dataset_context": "MANE splice sites"
    }).json()
    
    return {
        "image": result["image_path"],
        "caption": insight["caption"],
        "quality": critique["quality"]
    }
```

### Pattern 3: Iterative Refinement

**Use Case:** Complex visualizations requiring multiple iterations

```python
def iterative_chart(question: str, dataset: str, max_iterations: int = 3):
    """Refine chart through multiple critique cycles"""
    code = None
    
    for iteration in range(max_iterations):
        # Generate or refine
        if code is None:
            plan = requests.post(f"{BASE_URL}/analyze", json={
                "dataset_path": dataset,
                "question": question
            }).json()
            code = plan["code"]
        
        # Critique
        critique = requests.post(f"{BASE_URL}/critique", json={
            "code": code,
            "domain_context": "Genomic analysis"
        }).json()
        
        print(f"Iteration {iteration + 1}: {critique['quality']}")
        
        if critique["quality"] in ["excellent", "good"]:
            break
        
        # Refine based on critique
        # (In practice, you'd call LLM again with critique feedback)
        # For now, we'll just break
        break
    
    # Execute final version
    result = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "dataset_path": dataset,
        "output_format": "pdf"
    }).json()
    
    return result
```

## Frontend Integration

### React Example

```javascript
// ChartGenerator.jsx
import React, { useState } from 'react';

function ChartGenerator() {
  const [question, setQuestion] = useState('');
  const [code, setCode] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const generateChart = async () => {
    setLoading(true);
    
    // Step 1: Generate code
    const planResponse = await fetch('http://localhost:8003/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_path: 'data/splice_sites_enhanced.tsv',
        question: question,
        model: 'gpt-4o-mini'
      })
    });
    
    const plan = await planResponse.json();
    setCode(plan.code);
    
    // Step 2: Execute
    const execResponse = await fetch('http://localhost:8003/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: plan.code,
        dataset_path: 'data/splice_sites_enhanced.tsv',
        output_format: 'png'
      })
    });
    
    const result = await execResponse.json();
    if (result.success) {
      setImageUrl(`http://localhost:8003${result.image_path}`);
    }
    
    setLoading(false);
  };

  return (
    <div>
      <h2>Chart Generator</h2>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="What do you want to visualize?"
      />
      <button onClick={generateChart} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Chart'}
      </button>
      
      {code && (
        <div>
          <h3>Generated Code</h3>
          <pre>{code}</pre>
        </div>
      )}
      
      {imageUrl && (
        <div>
          <h3>Result</h3>
          <img src={imageUrl} alt="Generated chart" />
        </div>
      )}
    </div>
  );
}

export default ChartGenerator;
```

### Streamlit Example

```python
# app.py
import streamlit as st
import requests

st.title("Chart Agent Interface")

BASE_URL = "http://localhost:8003"

# Input
dataset = st.selectbox("Dataset", ["data/splice_sites_enhanced.tsv"])
question = st.text_input("What do you want to visualize?")
model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-5.1-codex-mini"])

if st.button("Generate Chart"):
    with st.spinner("Generating code..."):
        # Generate
        response = requests.post(f"{BASE_URL}/analyze", json={
            "dataset_path": dataset,
            "question": question,
            "model": model
        })
        plan = response.json()
    
    # Show code
    st.subheader("Generated Code")
    st.code(plan["code"], language="python")
    
    # Critique
    with st.spinner("Reviewing code..."):
        response = requests.post(f"{BASE_URL}/critique", json={
            "code": plan["code"],
            "domain_context": "Genomic analysis",
            "model": model
        })
        critique = response.json()
    
    st.subheader("Code Quality")
    st.write(f"**Quality:** {critique['quality']}")
    st.write(f"**Strengths:** {len(critique['strengths'])}")
    for strength in critique['strengths']:
        st.write(f"- ✓ {strength}")
    
    if critique['issues']:
        st.write(f"**Issues:** {len(critique['issues'])}")
        for issue in critique['issues']:
            st.write(f"- [{issue['severity']}] {issue['issue']}")
    
    # Execute
    if st.button("Execute Code"):
        with st.spinner("Generating chart..."):
            response = requests.post(f"{BASE_URL}/execute", json={
                "code": plan["code"],
                "dataset_path": dataset,
                "output_format": "png"
            })
            result = response.json()
        
        if result["success"]:
            st.subheader("Result")
            st.image(f"{BASE_URL}{result['image_path']}")
            
            # Generate caption
            with st.spinner("Generating insights..."):
                response = requests.post(f"{BASE_URL}/insight", json={
                    "analysis_title": question,
                    "image_path": result["image_path"],
                    "dataset_context": "MANE splice sites"
                })
                insight = response.json()
            
            st.subheader("Caption")
            st.write(insight["caption"])
            
            st.subheader("Key Insights")
            for i, insight_text in enumerate(insight["key_insights"], 1):
                st.write(f"{i}. {insight_text}")
        else:
            st.error(f"Execution failed: {result['error']}")
```

## Agent-to-Agent Communication

### LangChain Tool

```python
from langchain.tools import Tool
import requests

def chart_agent_tool(question: str) -> str:
    """Generate a chart from natural language"""
    response = requests.post("http://localhost:8003/analyze", json={
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "question": question,
        "model": "gpt-4o-mini"
    })
    
    plan = response.json()
    
    # Execute
    response = requests.post("http://localhost:8003/execute", json={
        "code": plan["code"],
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "output_format": "png"
    })
    
    result = response.json()
    
    if result["success"]:
        return f"Chart generated: http://localhost:8003{result['image_path']}"
    else:
        return f"Failed to generate chart: {result['error']}"

# Register as LangChain tool
chart_tool = Tool(
    name="ChartGenerator",
    func=chart_agent_tool,
    description="Generate publication-quality charts from natural language questions about genomic data"
)
```

### Multi-Agent System

```python
class AnalysisOrchestrator:
    """Orchestrates multiple agents including Chart Agent"""
    
    def __init__(self):
        self.chart_api = "http://localhost:8003"
        self.ml_api = "http://localhost:8002"  # ML Agent
    
    def analyze_dataset(self, dataset: str, questions: list):
        """Run comprehensive analysis"""
        results = []
        
        for question in questions:
            # Generate chart
            chart = self._generate_chart(question, dataset)
            
            # Generate insights
            insights = self._generate_insights(chart["image_path"], question)
            
            results.append({
                "question": question,
                "chart": chart,
                "insights": insights
            })
        
        return results
    
    def _generate_chart(self, question: str, dataset: str):
        response = requests.post(f"{self.chart_api}/analyze", json={
            "dataset_path": dataset,
            "question": question
        })
        plan = response.json()
        
        response = requests.post(f"{self.chart_api}/execute", json={
            "code": plan["code"],
            "dataset_path": dataset,
            "output_format": "pdf"
        })
        
        return response.json()
    
    def _generate_insights(self, image_path: str, question: str):
        response = requests.post(f"{self.chart_api}/insight", json={
            "analysis_title": question,
            "image_path": image_path,
            "dataset_context": "MANE splice sites"
        })
        
        return response.json()
```

## Error Handling

### Robust Client

```python
class ChartAgentClient:
    """Robust client with retry and error handling"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate_chart(self, dataset: str, question: str, 
                      model: str = "gpt-4o-mini", 
                      max_retries: int = 3):
        """Generate chart with retry logic"""
        for attempt in range(max_retries):
            try:
                # Generate code
                response = self.session.post(
                    f"{self.base_url}/analyze",
                    json={
                        "dataset_path": dataset,
                        "question": question,
                        "model": model
                    },
                    timeout=60
                )
                response.raise_for_status()
                plan = response.json()
                
                # Execute
                response = self.session.post(
                    f"{self.base_url}/execute",
                    json={
                        "code": plan["code"],
                        "dataset_path": dataset,
                        "output_format": "pdf"
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                if result["success"]:
                    return result
                else:
                    raise Exception(result["error"])
            
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Timeout, retrying ({attempt + 1}/{max_retries})...")
                    continue
                raise
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying ({attempt + 1}/{max_retries})...")
                    continue
                raise
        
        raise Exception("Max retries exceeded")
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib

class CachedChartClient:
    """Client with local caching"""
    
    def __init__(self, base_url: str, cache_dir: str = ".chart_cache"):
        self.base_url = base_url
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def generate_chart(self, dataset: str, question: str):
        """Generate chart with caching"""
        # Create cache key
        cache_key = hashlib.md5(
            f"{dataset}:{question}".encode()
        ).hexdigest()
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache
        if cache_file.exists():
            print("Using cached result")
            with open(cache_file) as f:
                return json.load(f)
        
        # Generate new
        response = requests.post(f"{self.base_url}/analyze", json={
            "dataset_path": dataset,
            "question": question
        })
        plan = response.json()
        
        response = requests.post(f"{self.base_url}/execute", json={
            "code": plan["code"],
            "dataset_path": dataset,
            "output_format": "pdf"
        })
        result = response.json()
        
        # Cache result
        with open(cache_file, 'w') as f:
            json.dump(result, f)
        
        return result
```

## Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  chart-agent:
    build: ./chart_agent/server
    ports:
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    restart: unless-stopped
```

### Kubernetes

```yaml
# chart-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chart-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chart-agent
  template:
    metadata:
      labels:
        app: chart-agent
    spec:
      containers:
      - name: chart-agent
        image: chart-agent:latest
        ports:
        - containerPort: 8003
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: chart-agent-service
spec:
  selector:
    app: chart-agent
  ports:
  - port: 80
    targetPort: 8003
  type: LoadBalancer
```

## Security Considerations

1. **API Key Management**: Use environment variables, never hardcode
2. **Input Validation**: Validate dataset paths to prevent directory traversal
3. **Code Execution**: Run in sandboxed environment (consider Docker)
4. **Rate Limiting**: Implement rate limits to prevent abuse
5. **Authentication**: Add API key authentication for production

## Monitoring

```python
# Add to chart_service.py
from prometheus_client import Counter, Histogram
import time

# Metrics
chart_requests = Counter('chart_requests_total', 'Total chart requests')
chart_duration = Histogram('chart_duration_seconds', 'Chart generation duration')

@app.post("/analyze")
def analyze(request: AnalysisRequest):
    chart_requests.inc()
    start_time = time.time()
    
    try:
        # ... existing code ...
        return plan
    finally:
        chart_duration.observe(time.time() - start_time)
```

## Next Steps

1. **Authentication**: Add API key or OAuth
2. **Batch Processing**: Support multiple charts in one request
3. **Streaming**: Stream code generation token-by-token
4. **Templates**: Pre-defined analysis templates
5. **Collaboration**: Multi-user sessions with shared state
