# Chart Agent — Documentation

> **Status**: Active development.
> For the reflection package docs, see `reflection/docs/`.
> Source code: `chart_agent/`, `reflection/chart_workflow/`

---

## What is the Chart Agent?

The Chart Agent is an AI-powered data visualization system that combines code generation, reflection, and execution to produce high-quality charts. It runs as a FastAPI service and implements the **Reflection Pattern**: generate → execute → reflect → refine.

```text
User Request
    ↓
Analyze Endpoint     — understand data and intent
    ↓
Execute Endpoint     — generate and run chart code
    ↓
Critique Endpoint    — LLM reviews the visual output
    ↓
Refined Chart (V2)
```

---

## Documents

### Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design, layers, and component overview
- **[LLM_INSIGHT_STRATEGY.md](LLM_INSIGHT_STRATEGY.md)** — How the agent derives insights from chart outputs

### Frontend Integration

- **[frontend/README.md](frontend/README.md)** — Frontend options overview
- **[frontend/SWAGGER_UI.md](frontend/SWAGGER_UI.md)** — Interactive API testing via Swagger
- **[frontend/REACT.md](frontend/REACT.md)** — React frontend integration
- **[frontend/STREAMLIT.md](frontend/STREAMLIT.md)** — Streamlit frontend integration
- **[frontend/CURL.md](frontend/CURL.md)** — cURL examples for direct API calls

### API Reference

- **[api/utils.md](api/utils.md)** — Core utility functions (data loading, LLM interaction, display)

### Design

- **[design/styling-system.md](design/styling-system.md)** — Custom HTML/CSS styling for Jupyter notebooks

---

## Related

- Architecture: `docs/architecture/AGENTIC_ROADMAP.md`
- Reflection pattern: `docs/patterns/RESEARCH_AGENT_GUIDE.md`
- Source: `chart_agent/`, `reflection/chart_workflow/`
