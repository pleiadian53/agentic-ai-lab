# Agentic AI Course Repo — Learning & Enhancement Roadmap

This roadmap is tailored for deep-diving the **agentic-ai-lab** starter and incrementally enhancing it while keeping parity with course labs.

## 0) Orientation
- App: FastAPI service (`main.py`) with simple task DB, background worker, and web UI (`templates/`, `static/`).
- Agent runtime in `src/`:
  - `agents.py`: orchestrates calls to OpenAI models; status updates; report assembly.
  - `planning_agent.py`: step planner / reflection prompts.
  - `research_tools.py`: web/PubMed/arXiv/PDF utilities (requests + pdfminer).

## 1) Learning checkpoints
1. **Run the app** (Docker or local): verify you can submit a research task and view step logs.
2. **Trace a full request** end-to-end; annotate code with comments for: plan → tool calls → draft → revise.
3. **Swap a component** (modularity drill): replace one tool (e.g., arXiv) with another (e.g., Crossref) without touching callers.

## 2) Enhancements (small PRs)
- [ ] **Model adapter layer** (`src/llm.py` new): unify `chat(model, messages, tools=None, ...)` so you can swap GPT/Claude/Gemini via ENV. Refactor `agents.py` to import this.
- [ ] **Config**: `config.py` + `.env` (pydantic) for model names, temperature, max_steps, timeouts.
- [ ] **Retry & rate-limit**: Decorators around network calls in `research_tools.py` (exponential backoff, 429 handling).
- [ ] **Better parsing**: Strict JSON output from models with `jsonschema` validation for the plan and references.
- [ ] **Reflection gates**: Implement pass/fail checks (min #sources, dedupe, citation confidence) in `planning_agent.py`. On fail, emit a fix and re-run the minimal step.
- [ ] **Citations**: Extract structured refs `{title, url, venue, year, authors}`. Deduplicate by DOI/URL domain + title Levenshtein.
- [ ] **Unit tests**: pytest for tools (mock HTTP). Example fixtures for arXiv XML → parsed entries.
- [ ] **Observability**: Per-step timing, token counts, and error tracebacks in the DB (add columns to `TaskStep`).

## 3) Feature adds (medium PRs)
- [ ] **Multi-agent split**: researcher (search), curator (filter), writer (synthesizer), reviewer (critic). Message bus = simple Python queue; log exchanges.
- [ ] **Parallel search**: fan-out to multiple sources (arXiv, PubMed, Wikipedia) with `asyncio.gather`; merge + rank by relevance.
- [ ] **PDF pipeline**: add fallback PDF text extraction with `pypdf` when pdfminer fails; chunk & summarize long papers.
- [ ] **Web browsing**: add `readability-lxml` for boilerplate removal, robots.txt respect, and domain blocklist.
- [ ] **Evaluation**: golden prompts + expected key points; automatic rubric scoring to regression-test changes.

## 4) Stretch (ties to SpliceSurveyor later)
- [ ] Add a **BioTools** module: PubMed E-utilities, ClinVar/DBASS search, gene synonym expansion; return structured JSON.
- [ ] Slot in a **domain planner** that tailors search terms to splicing (e.g., “cryptic splice” OR “pseudoexon”).

## 5) Suggested file changes
- `src/llm.py` (new): unified LLM client.
- `src/config.py` (new): pydantic settings.
- `src/agents.py`: route all model calls through `llm.py`; emit JSON logs.
- `src/planning_agent.py`: add reflection gates + repair actions.
- `src/research_tools.py`: add retries, new sources, stricter parsing.
- `tests/` (new): pytest suite for tools + planners.

## 6) Example JSON schemas
**Plan schema**:
```json
{
  "steps": [
    {"id":"search-1","tool":"arxiv","query":"...","success_criteria":[">=5 sources"]},
    {"id":"summarize-1","tool":"llm","inputs":["search-1.results"]}
  ]
}
```
**Reference schema**:
```json
{"title":"...", "url":"...", "doi":"...", "venue":"...", "year":2024, "authors":["..."]}
```

## 7) Commands
- Local: `uvicorn main:app --reload`
- Docker: `docker build -t agentic . && docker run -p 8000:8000 agentic`
- Tests (once added): `pytest -q`

---
Priority order: **Model adapter → Config → Retries → JSON schemas → Reflection gates → Tests → Multi-agent.**
