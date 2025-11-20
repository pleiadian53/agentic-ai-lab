# Chart Agent - Intelligent Data Visualization

An agentic system for automated chart generation and refinement, combining **code-as-plan** flexibility with **reflection-based** quality improvement.

## 🎯 Current Status

**✅ Core Features Implemented:**
- Code-as-plan pattern for flexible chart generation
- Reflection pattern for iterative quality improvement (in examples)
- Multiple data sources (CSV, SQLite, DuckDB, DataFrame, Excel)
- Model management with dynamic recommendations (GPT-5 ready!)
- Utility functions for model selection, code validation, and execution
- Domain-specific example: Genomic splice site analysis
- **🆕 FastAPI REST API Service** - Production-ready web service with Swagger UI
- **🆕 Human-in-the-loop workflow** - Review code before execution
- **🆕 Multi-format output** - PDF, PNG chart generation

**📝 In Development:**
- Standalone reflection module
- Sandboxed execution environment
- General-purpose CLI
- Comprehensive test suite
- Frontend integrations (React, Streamlit)

## Overview

The Chart Agent generates high-quality visualizations from datasets using a two-phase workflow:

1. **Generation Phase** (Code-as-Plan)
   - LLM analyzes dataset and user requirements
   - Generates Python plotting code (matplotlib/seaborn/plotly)
   - Code is immediately executable with provided data

2. **Reflection Phase** (Critique & Refine) - *Optional*
   - LLM critiques the generated chart code
   - Identifies issues (clarity, accuracy, aesthetics, domain relevance)
   - Generates improved version based on feedback
   - Iterates until quality threshold met or max iterations reached

## Features

- **Flexible Generation:** Code-as-plan allows complex, adaptive chart logic
- **Quality Assurance:** Optional reflection ensures charts meet best practices
- **Multi-Format Support:** CSV, SQLite, DuckDB, pandas DataFrames, Excel
- **Multiple Libraries:** matplotlib, seaborn, plotly (auto-selected based on chart type)
- **Model Selection:** Dynamic recommendations for GPT-4o-mini (default), GPT-5, Codex
- **Configurable Reflection:** Control iteration depth, model selection, and critique criteria
- **Utility Functions:** Model listing, code validation, HTML display, execution helpers

## Quick Start

### Option 1: REST API Service (Recommended for Production)

The Chart Agent provides a production-ready FastAPI service with Swagger UI for easy testing and integration.

**Start the service:**
```bash
cd chart_agent/server
mamba run -n agentic-ai python manage.py start
```

**Access the API:**
- **Swagger UI**: http://localhost:8003/docs
- **API Base**: http://localhost:8003
- **Health Check**: http://localhost:8003/health

**Quick API Example:**
```bash
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show the top 20 genes with the most splice sites",
    "model": "gpt-4o-mini"
  }'
```

**Full Documentation:**
- [Quick Start Guide](server/QUICKSTART.md)
- [Service Management](server/SERVICE_MANAGEMENT.md)
- [Integration Guide](server/INTEGRATION.md)
- [Frontend Tutorials](docs/frontend/) - React, Streamlit, Swagger UI

### Option 2: Python Library (For Direct Integration)

#### Prerequisites

1. **Install dependencies:**
   ```bash
   cd /path/to/agentic-ai-lab
   pip install -e .
   ```

2. **Set up OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
   
   Or add to `.env` file in repository root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
   
   Get your API key from: https://platform.openai.com/api-keys

### Basic Usage

```python
from openai import OpenAI
from chart_agent import chart_agent, CSVDataset

client = OpenAI()
dataset = CSVDataset("data/coffee_sales.csv")

result = chart_agent(
    dataset=dataset,
    user_request="Create a bar chart showing total sales by product category",
    client=client,
    use_reflection=True,
    max_reflections=2
)

if result["success"]:
    result["final_chart"].show()  # Display chart
    print(f"Iterations: {result['reflection_count']}")
```

### CLI Usage

```bash
# Generate chart with reflection
run-chart-agent \
    --data data/coffee_sales.csv \
    --prompt "Show monthly sales trends" \
    --reflect \
    --output charts/sales_trend.png

# Quick generation without reflection
run-chart-agent \
    --data data/coffee_sales.csv \
    --prompt "Bar chart of top 10 products" \
    --no-reflect
```

## Package Structure

```
chart_agent/
├── __init__.py              # ✅ Package initialization with exports
├── data_access.py           # ✅ Dataset abstraction layer (CSV, SQL, DuckDB, etc.)
├── planning.py              # ✅ LLM-based chart code generation
├── utils.py                 # ✅ Utility functions (model listing, display, execution, validation)
├── server/                  # ✅ FastAPI REST API Service
│   ├── chart_service.py         # ✅ Main FastAPI application
│   ├── schemas.py               # ✅ Pydantic request/response models
│   ├── config.py                # ✅ Centralized configuration
│   ├── manage.py                # ✅ Service management CLI
│   ├── stop_service.sh          # ✅ Graceful shutdown script
│   ├── test_client.py           # ✅ Python API client example
│   ├── test_analyze.py          # ✅ Direct endpoint testing
│   ├── test_http.py             # ✅ HTTP request testing
│   ├── test_full_workflow.py    # ✅ Complete workflow demo
│   ├── QUICKSTART.md            # ✅ Getting started guide
│   ├── SERVICE_MANAGEMENT.md    # ✅ Deployment & operations
│   ├── INTEGRATION.md           # ✅ Integration patterns
│   └── SUMMARY.md               # ✅ Architecture overview
├── examples/                # ✅ Usage examples and demos
│   ├── analyze_splice_sites.py  # ✅ Domain-specific driver with reflection pattern
│   ├── utils_demo.py            # ✅ Utility functions demo
│   └── README.md                # ✅ Examples documentation
├── data/                    # ✅ Data storage
│   ├── llm/                     # ✅ LLM model information
│   │   ├── available_models.json  # ✅ Saved model list with recommendations
│   │   └── README.md              # ✅ Model documentation
│   └── mane/                    # ✅ Genomic data
│       └── GRCh38/
│           └── splice_sites_enhanced.tsv
├── docs/                    # ✅ Frontend & Integration Tutorials
│   ├── frontend/
│   │   ├── SWAGGER_UI.md        # ✅ Swagger UI guide
│   │   ├── REACT.md             # ✅ React integration tutorial
│   │   ├── STREAMLIT.md         # ✅ Streamlit app tutorial
│   │   └── CURL.md              # ✅ Command-line usage
│   └── ARCHITECTURE.md          # ✅ System design & patterns
└── tests/                   # 🧪 Test suite (planned)
    ├── test_data_access.py
    ├── test_planning.py
    └── test_utils.py
```

### Implementation Status

**✅ Implemented:**
- **Core functionality**: Data access, planning, utilities
- **Code-as-plan pattern**: LLM generates executable visualization code
- **Reflection pattern**: Implemented in `analyze_splice_sites.py` example
- **Model management**: Save/load model lists, dynamic recommendations
- **Multiple data sources**: CSV, SQLite, DuckDB, DataFrame, Excel
- **Utility functions**: Model listing, HTML display, code execution, validation

**📝 Planned (Future Work):**
- **`execution.py`**: Sandboxed code execution environment
- **`reflection.py`**: Standalone reflection module (currently in examples)
- **`agent.py`**: Main orchestration with full agentic loop
- **`cli.py`**: Command-line interface for general use
- **Comprehensive test suite**: Unit and integration tests

**Note**: Reflection functionality is fully implemented in the `analyze_splice_sites.py` example, demonstrating the pattern. A standalone `reflection.py` module would generalize this for reuse across different domains.

## Workflow

### Phase 1: Generation (Code-as-Plan)

```
User Request + Dataset
        ↓
[LLM Planning]
  - Analyze dataset schema
  - Understand user intent
  - Select appropriate chart type
  - Generate plotting code
        ↓
[Sandbox Execution]
  - Execute code safely
  - Capture chart object
  - Handle errors
        ↓
Initial Chart
```

### Phase 2: Reflection (Optional)

```
Initial Chart + Code
        ↓
[LLM Critique]
  - Evaluate clarity
  - Check accuracy
  - Assess aesthetics
  - Identify improvements
        ↓
[LLM Refinement]
  - Generate improved code
  - Address critique points
        ↓
[Sandbox Execution]
  - Execute refined code
        ↓
Improved Chart
        ↓
[Quality Check]
  - Meets threshold? → Done
  - Needs work? → Iterate (max N times)
```

## Example Scenarios

### Sales Analysis

```python
result = chart_agent(
    dataset=CSVDataset("coffee_sales.csv"),
    user_request="Show quarterly sales trends with moving average",
    use_reflection=True
)
```

### Customer Segmentation

```python
result = chart_agent(
    dataset=SQLiteDataset("customers.db", "SELECT age, income, segment FROM customers"),
    user_request="Create a scatter plot showing customer segments by age and income",
    use_reflection=True
)
```

### Multi-Panel Dashboard

```python
result = chart_agent(
    dataset=df,  # pandas DataFrame
    user_request="Create a 2x2 dashboard: sales by region, top products, monthly trends, and category breakdown",
    use_reflection=True,
    max_reflections=3
)
```

## Configuration

### Reflection Settings

```python
result = chart_agent(
    dataset=dataset,
    user_request=prompt,
    use_reflection=True,
    max_reflections=3,          # Max iteration count
    reflection_criteria=[        # Custom critique criteria
        "clarity",
        "accuracy",
        "aesthetics",
        "accessibility"
    ],
    quality_threshold=0.8        # Stop if quality score > threshold
)
```

### Library Selection

```python
result = chart_agent(
    dataset=dataset,
    user_request=prompt,
    preferred_library="plotly",  # Force specific library
    # Options: "matplotlib", "seaborn", "plotly", "auto"
)
```

## Comparison with Existing Workflows

| Feature | chartgen | reflection/chart_workflow | chart_agent (New) |
|---------|----------|--------------------------|-------------------|
| **Code Generation** | ✅ Notebook-based | ✅ Module-based | ✅ Production-ready |
| **Reflection** | ❌ No | ✅ Yes | ✅ Yes (configurable) |
| **Data Formats** | CSV only | CSV only | CSV, SQLite, DataFrame |
| **Sandboxing** | ❌ No | ✅ Yes | ✅ Yes |
| **Error Handling** | Basic | Good | Comprehensive |
| **Reusability** | Low | Medium | High |
| **CLI** | ❌ No | ❌ No | ✅ Yes |
| **Tests** | ❌ No | ❌ No | ✅ Yes |

## Advanced Usage

### Custom Critique Criteria

```python
from chart_agent import chart_agent, CritiqueCriteria

custom_criteria = CritiqueCriteria(
    clarity="Are labels clear and readable?",
    accuracy="Does the chart accurately represent the data?",
    aesthetics="Is the color scheme professional?",
    accessibility="Is the chart accessible to colorblind users?",
    domain_specific="Does it follow financial reporting standards?"
)

result = chart_agent(
    dataset=dataset,
    user_request=prompt,
    critique_criteria=custom_criteria
)
```

### Streaming Reflection

```python
for iteration in chart_agent_stream(dataset, prompt):
    print(f"Iteration {iteration['count']}")
    print(f"Critique: {iteration['critique']}")
    iteration['chart'].show()
```

## Design Patterns Used

### 1. Code-as-Plan (from customer_service)
- **Flexibility:** LLM generates arbitrary plotting logic
- **Adaptability:** Can handle complex, multi-step visualizations
- **Power:** Full Python/matplotlib/seaborn/plotly capabilities

### 2. Reflection (from chart_workflow)
- **Quality Assurance:** Iterative improvement
- **Best Practices:** Enforces visualization principles
- **Error Recovery:** Fixes issues through critique

### 3. Data Abstraction
- **Unified Interface:** Works with CSV, SQLite, DataFrames
- **Schema Detection:** Automatic column type inference
- **Lazy Loading:** Efficient memory usage

## Next Steps

- See `docs/USAGE.md` for detailed API reference
- See `docs/EXAMPLES.md` for more examples
- Try the CLI: `run-chart-agent --help`
- Extend with custom chart types or libraries

## License

Part of the agentic-ai-lab repository.
