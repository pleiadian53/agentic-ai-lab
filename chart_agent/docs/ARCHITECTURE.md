# Chart Agent Architecture

## System Overview

The Chart Agent is a multi-layered system for AI-powered data visualization, combining code generation, reflection, and execution capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Swagger  │  │  React   │  │Streamlit │  │   cURL   │     │
│  │    UI    │  │   App    │  │   App    │  │  Scripts │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
                    HTTP/REST API
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                   FastAPI Service Layer                       │
│  ┌──────────────────────┴───────────────────────────┐         │
│  │           chart_service.py (Main App)            │         │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │         │
│  │  │  Analyze   │  │  Execute   │  │  Critique  │  │         │
│  │  │  Endpoint  │  │  Endpoint  │  │  Endpoint  │  │         │
│  │  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  │         │
│  └─────────┼────────────────┼────────────────┼──────┘         │
│            │                │                │                │
│  ┌─────────┼────────────────┼────────────────┼───────┐        │
│  │         ▼                ▼                ▼       │        │
│  │   ChartGenerator   CodeExecutor    CodeCritic     │        │
│  └─────────┼────────────────┼────────────────┼───────┘        │
└────────────┼────────────────┼────────────────┼────────────────┘
             │                │                │
             └────────────────┴────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                   Core Library Layer                          │
│  ┌──────────────────────┴───────────────────────────┐         │
│  │              planning.py                         │         │
│  │  ┌────────────────────────────────────────────┐  │         │
│  │  │  generate_chart_code()                     │  │         │
│  │  │  - Builds LLM prompt                       │  │         │
│  │  │  - Calls OpenAI API                        │  │         │
│  │  │  - Returns executable code                 │  │         │
│  │  └────────────────────────────────────────────┘  │         │
│  └──────────────────────────────────────────────────┘         │
│                                                               │
│  ┌──────────────────────────────────────────────────┐         │
│  │              data_access.py                      │         │
│  │  ┌────────────────────────────────────────────┐  │         │
│  │  │  DuckDBDataset, CSVDataset, etc.           │  │         │
│  │  │  - Unified dataset interface               │  │         │
│  │  │  - Schema introspection                    │  │         │
│  │  │  - Query execution                         │  │         │
│  │  └────────────────────────────────────────────┘  │         │
│  └──────────────────────────────────────────────────┘         │
│                                                               │
│  ┌──────────────────────────────────────────────────┐         │
│  │              utils.py                            │         │
│  │  - Model management                              │         │
│  │  - Code validation                               │         │
│  │  - Execution helpers                             │         │
│  └──────────────────────────────────────────────────┘         │
└─────────────────────────┬─────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                   External Services                           │
│  ┌──────────────────────┴───────────────────────────┐         │
│  │              OpenAI API                          │         │
│  │  - GPT-4o, GPT-5 models                          │         │
│  │  - Code generation                               │         │
│  │  - Critique & refinement                         │         │
│  └──────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Frontend Layer

**Purpose:** User interaction and visualization

**Components:**
- **Swagger UI** - Auto-generated API documentation and testing
- **React App** - Custom web application with full UI control
- **Streamlit App** - Python-based rapid prototyping interface
- **cURL Scripts** - Command-line automation and CI/CD integration

**Communication:** HTTP REST API calls to FastAPI service

---

### FastAPI Service Layer

**Purpose:** HTTP API gateway and request orchestration

**Key Files:**
- `chart_service.py` - Main FastAPI application
- `schemas.py` - Pydantic request/response models
- `config.py` - Centralized configuration

**Endpoints:**
- `POST /analyze` - Generate chart code from natural language
- `POST /execute` - Execute code and generate chart image
- `POST /critique` - Critique code quality and suggest improvements
- `POST /insight` - Generate captions and insights
- `GET /datasets` - List available datasets
- `GET /health` - Service health check

**Features:**
- Request validation (Pydantic)
- Error handling and custom error messages
- CORS support for browser access
- Static file serving for generated charts
- Dataset caching for performance

---

### Core Library Layer

**Purpose:** Business logic and LLM integration

#### planning.py

**Responsibilities:**
- Build prompts for chart generation
- Call OpenAI API with appropriate parameters
- Parse and clean generated code
- Detect chart library and type

**Key Functions:**
- `generate_chart_code()` - Main code generation function
- `_build_prompt()` - Construct LLM prompt with dataset context
- `_clean_generated_code()` - Remove markdown formatting
- `_detect_library()` - Identify plotting library used

#### data_access.py

**Responsibilities:**
- Abstract dataset access across formats
- Provide schema introspection
- Execute queries efficiently

**Key Classes:**
- `ChartDataset` - Base abstract class
- `DuckDBDataset` - High-performance columnar data
- `CSVDataset` - Simple CSV files
- `SQLiteDataset` - SQL database access
- `DataFrameDataset` - In-memory pandas DataFrames

**Key Methods:**
- `get_schema_description()` - Dataset structure for LLM
- `get_summary_stats()` - Row/column counts and metadata
- `query()` - Execute SQL queries
- `get_sample_data()` - Preview rows

#### utils.py

**Responsibilities:**
- Model management and recommendations
- Code validation and execution
- Display helpers

**Key Functions:**
- `get_available_models()` - List supported LLM models
- `get_recommended_models()` - Suggest models for tasks
- `validate_chart_code()` - Check code safety
- `execute_chart_code()` - Run code in controlled environment

---

### External Services

#### OpenAI API

**Models Used:**
- `gpt-4o-mini` - Default, fast and cost-effective
- `gpt-4o` - More capable for complex charts
- `gpt-5` - Latest model with enhanced reasoning
- `gpt-5-mini` - Fast GPT-5 variant
- `gpt-5.1-codex-mini` - Optimized for code generation

**API Calls:**
- Chat completions for code generation
- Structured outputs for critiques
- Temperature control for creativity vs consistency

---

## Data Flow

### Workflow 1: Generate Chart Code

```
User Request
    │
    ▼
Frontend (React/Streamlit/cURL)
    │
    │ POST /analyze
    │ {
    │   "dataset_path": "data/file.tsv",
    │   "question": "Show top 20 items",
    │   "model": "gpt-4o-mini"
    │ }
    ▼
FastAPI Service
    │
    ▼
ChartGenerator.generate_plan()
    │
    ├─► Load dataset (data_access.py)
    │   └─► DuckDBDataset.get_schema_description()
    │
    ├─► Build prompt (planning.py)
    │   └─► Include schema, question, context
    │
    ├─► Call OpenAI API
    │   └─► generate_chart_code()
    │
    └─► Return code + metadata
        │
        ▼
Response
{
  "code": "import matplotlib...",
  "explanation": "Generated bar chart...",
  "libraries_used": ["matplotlib", "pandas"]
}
```

### Workflow 2: Execute Chart Code

```
Generated Code
    │
    ▼
Frontend
    │
    │ POST /execute
    │ {
    │   "code": "import matplotlib...",
    │   "dataset_path": "data/file.tsv",
    │   "output_format": "pdf"
    │ }
    ▼
FastAPI Service
    │
    ▼
CodeExecutor.execute()
    │
    ├─► Load dataset
    │   └─► Read CSV/TSV into DataFrame
    │
    ├─► Execute code in subprocess
    │   ├─► Inject dataset as 'df'
    │   ├─► Capture stdout/stderr
    │   └─► Save plot to file
    │
    └─► Return result
        │
        ▼
Response
{
  "success": true,
  "image_path": "/charts/chart_1234.pdf",
  "logs": "Chart generated successfully"
}
```

### Workflow 3: Critique and Refine

```
Generated Code
    │
    ▼
Frontend
    │
    │ POST /critique
    │ {
    │   "code": "import matplotlib...",
    │   "domain_context": "Genomics research"
    │ }
    ▼
FastAPI Service
    │
    ▼
CodeCritic.critique()
    │
    ├─► Build critique prompt
    │   └─► Include code + domain context
    │
    ├─► Call OpenAI API
    │   └─► Request structured feedback
    │
    └─► Return critique
        │
        ▼
Response
{
  "quality": "good",
  "issues": ["Missing error handling"],
  "suggestions": ["Add try-except blocks"],
  "domain_relevance": "high"
}
```

## Design Patterns

### 1. Code-as-Plan Pattern

**Concept:** Generate executable code instead of configuration

**Benefits:**
- Maximum flexibility
- No DSL limitations
- Easy to review and modify
- Leverages existing libraries

**Implementation:**
- LLM generates Python code
- Code uses standard libraries (matplotlib, seaborn)
- User can review before execution
- Code is immediately runnable

### 2. Human-in-the-Loop

**Concept:** User reviews generated code before execution

**Benefits:**
- Safety and control
- Learning opportunity
- Customization point
- Trust building

**Implementation:**
- `/analyze` returns code without executing
- User reviews in UI
- User approves
- `/execute` runs the code

### 3. Reflection Pattern

**Concept:** LLM critiques its own output

**Benefits:**
- Quality improvement
- Iterative refinement
- Self-correction
- Best practices enforcement

**Implementation:**
- Generate initial code
- Critique code quality
- Regenerate based on feedback
- Repeat until satisfied

### 4. Dataset Abstraction

**Concept:** Unified interface for multiple data sources

**Benefits:**
- Format independence
- Easy to add new sources
- Consistent API
- Optimized per format

**Implementation:**
- `ChartDataset` base class
- Format-specific implementations
- Common methods (schema, query, sample)
- Automatic format detection

## Configuration Management

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
CHART_AGENT_PORT=8003
CHART_AGENT_HOST=0.0.0.0
CHART_AGENT_DATA_DIR=data/
CHART_AGENT_OUTPUT_DIR=output/api_charts
```

### Config Module (config.py)

**Centralized settings:**
- Project root path
- Data directory location
- Output directory location
- Supported file formats
- CORS origins
- Server settings

**Path Resolution:**
- All paths relative to project root
- Works regardless of CWD
- Consistent across modules

## Security Considerations

### Current Implementation

**Protections:**
- Input validation (Pydantic)
- SQL injection prevention (parameterized queries)
- Path traversal prevention (resolve to project root)
- Code execution in subprocess (isolated)

**Limitations:**
- No authentication
- No rate limiting
- Code execution not sandboxed
- Open CORS (allows all origins)

### Production Recommendations

1. **Authentication**
   - Add API key validation
   - Implement OAuth2/JWT
   - User-based quotas

2. **Sandboxing**
   - Docker containers per execution
   - Resource limits (CPU, memory, time)
   - Network isolation

3. **Rate Limiting**
   - Per-user limits
   - Per-endpoint limits
   - Exponential backoff

4. **Input Sanitization**
   - Whitelist allowed imports
   - Validate file paths
   - Check code for dangerous operations

5. **Monitoring**
   - Log all requests
   - Track errors and failures
   - Alert on anomalies

## Performance Optimization

### Current Optimizations

1. **Dataset Caching**
   - Cache loaded datasets in memory
   - Avoid repeated file reads
   - Clear cache on service restart

2. **Async Operations**
   - FastAPI async support
   - Non-blocking I/O
   - Concurrent request handling

3. **Efficient Data Access**
   - DuckDB for large datasets
   - Columnar storage
   - Query pushdown

### Future Optimizations

1. **Code Caching**
   - Cache generated code by question hash
   - Reuse for similar questions
   - Invalidate on dataset changes

2. **Parallel Execution**
   - Multiple chart generation in parallel
   - Batch processing support
   - Queue-based architecture

3. **CDN Integration**
   - Serve charts from CDN
   - Reduce server load
   - Faster global access

## Extensibility Points

### Adding New Data Sources

1. Implement `ChartDataset` interface
2. Add format detection logic
3. Register in `data_access.py`
4. Update documentation

### Adding New Endpoints

1. Define Pydantic schemas in `schemas.py`
2. Implement handler in `chart_service.py`
3. Add tests
4. Update OpenAPI docs

### Adding New Models

1. Add to `ModelType` enum in `schemas.py`
2. Update model recommendations in `utils.py`
3. Test with various chart types
4. Document capabilities

### Adding New Chart Libraries

1. Update prompt templates in `planning.py`
2. Add library detection logic
3. Test code generation
4. Document usage patterns

## Testing Strategy

### Unit Tests

- Data access layer
- Prompt building
- Code validation
- Path resolution

### Integration Tests

- API endpoints
- End-to-end workflows
- Error handling
- Response validation

### Performance Tests

- Load testing
- Concurrent requests
- Large dataset handling
- Memory usage

## Deployment Architecture

### Development

```
Local Machine
├── FastAPI (port 8003)
├── React Dev Server (port 3000)
└── Streamlit (port 8501)
```

### Production

```
┌─────────────────────────────────────┐
│          Load Balancer              │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼────┐
│ API    │      │ API     │
│ Server │      │ Server  │
│   #1   │      │   #2    │
└───┬────┘      └────┬────┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │   File Storage  │
    │   (Charts)      │
    └─────────────────┘
```

## Related Documentation

- [FastAPI Service](../server/QUICKSTART.md)
- [Frontend Tutorials](frontend/README.md)
- [Swagger UI Guide](frontend/SWAGGER_UI.md)
- [React Integration](frontend/REACT.md)
- [Streamlit Tutorial](frontend/STREAMLIT.md)
- [cURL Guide](frontend/CURL.md)
